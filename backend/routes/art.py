"""
AI 生图 API 路由
"""
import os
import json
import uuid
import time
import hashlib
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, request, jsonify, g, send_file
from werkzeug.utils import secure_filename

from config import Config, ART_PROMPTS, POLAROID_STYLES
from services.art_service import ArtService, ArtStatus, ArtTask

art_bp = Blueprint('art', __name__, url_prefix='/v1/art')

# 内存存储（实际应使用数据库）
_task_store = {}
_user_quota = {}  # user_id -> used_count
_quota_reset_times = {}  # user_id -> reset_timestamp


def require_auth(f):
    """简单的认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'UNAUTHORIZED'}), 401
        g.token = token
        g.user_id = token  # 简化：token 即 user_id
        return f(*args, **kwargs)
    return decorated


def _check_quota(user_id: str) -> dict:
    """检查配额"""
    daily_limit = 3
    now = time.time()
    
    # 检查是否需要重置
    reset_time = _quota_reset_times.get(user_id, 0)
    if now > reset_time:
        _user_quota[user_id] = 0
        _quota_reset_times[user_id] = now + 24 * 60 * 60  # 次日重置
    
    used = _user_quota.get(user_id, 0)
    remaining = max(0, daily_limit - used)
    
    return {
        'allowed': remaining > 0,
        'remaining': remaining,
        'daily_limit': daily_limit,
        'reset_at': _quota_reset_times.get(user_id, now + 24 * 60 * 60)
    }


def _consume_quota(user_id: str) -> bool:
    """消耗配额"""
    quota = _check_quota(user_id)
    if not quota['allowed']:
        return False
    
    _user_quota[user_id] = _user_quota.get(user_id, 0) + 1
    return True


def _build_art_prompt(poem_text: str, style: str) -> str:
    """构建生图提示词"""
    style_prefixes = {
        'shuimo': 'Traditional Chinese ink wash painting (Shuimo), minimalist black ink on rice paper',
        'gongbi': 'Traditional Chinese Gongbi fine painting, delicate brushwork, vibrant colors',
        'dunhuang': 'Dunhuang cave fresco style, vibrant colors, Buddhist art influence',
        'modern': 'Modern Chinese art fusion, contemporary interpretation, elegant design',
        'landscape': 'Classical Chinese landscape painting (Shanshui), literati style',
        'default': 'Traditional Chinese poetry illustration, serene atmosphere, classical art'
    }
    
    style_prefix = style_prefixes.get(style, style_prefixes['default'])
    
    # 清理诗词文本
    clean_text = poem_text.replace('\n', '，').replace(' ', '')
    
    prompt = f"""
{style_prefix}.

Poetry: {clean_text}

Requirements:
- Traditional Chinese art style
- Serene, contemplative atmosphere
- Minimalist composition
- Black ink with subtle color accents acceptable
- High quality, detailed
- Vertical scroll format suitable
- No text or characters in the image
- Inspired by Tang/Song dynasty aesthetics
""".strip()
    
    return prompt


@art_bp.route('/quota', methods=['GET'])
@require_auth
def get_quota():
    """获取用户生图配额"""
    quota = _check_quota(g.user_id)
    return jsonify({'data': quota})


@art_bp.route('/generate', methods=['POST'])
@require_auth
def create_task():
    """创建生图任务"""
    data = request.get_json() or {}
    
    poem_id = data.get('poem_id')
    poem_text = data.get('poem_text')
    style = data.get('style', 'shuimo')
    custom_prompt = data.get('custom_prompt')
    
    if not poem_id or not poem_text:
        return jsonify({'error': 'INVALID_PARAMS', 'message': '缺少必要参数'}), 400
    
    # 检查配额
    quota = _check_quota(g.user_id)
    if not quota['allowed']:
        return jsonify({
            'error': 'QUOTA_EXCEEDED',
            'message': f'今日生成次数已用完（{quota["daily_limit"]}次/天）',
            'remaining': 0
        }), 429
    
    # 构建提示词
    if custom_prompt:
        prompt = custom_prompt
    else:
        prompt = _build_art_prompt(poem_text, style)
    
    # 创建任务
    task_id = str(uuid.uuid4())
    task = {
        'id': task_id,
        'user_id': g.user_id,
        'poem_id': poem_id,
        'poem_text': poem_text,
        'style': style,
        'prompt': prompt,
        'status': 'queued',
        'result_url': None,
        'created_at': datetime.now().isoformat(),
        'completed_at': None
    }
    
    _task_store[task_id] = task
    
    # 消耗配额
    _consume_quota(g.user_id)
    
    return jsonify({
        'data': {
            'task_id': task_id,
            'status': 'queued',
            'prompt': prompt,
            'quota_remaining': _check_quota(g.user_id)['remaining']
        }
    })


@art_bp.route('/tasks/<task_id>', methods=['GET'])
@require_auth
def get_task_status(task_id):
    """获取任务状态"""
    task = _task_store.get(task_id)
    if not task:
        return jsonify({'error': 'TASK_NOT_FOUND'}), 404
    
    # 验证用户
    if task['user_id'] != g.user_id:
        return jsonify({'error': 'FORBIDDEN'}), 403
    
    result = {
        'task_id': task['id'],
        'status': task['status'],
        'poem_id': task['poem_id'],
        'style': task['style'],
        'created_at': task['created_at']
    }
    
    if task['status'] == 'succeeded':
        result['result_url'] = task['result_url']
        result['completed_at'] = task['completed_at']
    
    if task['status'] == 'failed':
        result['error'] = task.get('error', 'Unknown error')
    
    return jsonify({'data': result})


@art_bp.route('/tasks/<task_id>/submit', methods=['POST'])
@require_auth
def submit_task(task_id):
    """提交任务到 AI 服务"""
    task = _task_store.get(task_id)
    if not task:
        return jsonify({'error': 'TASK_NOT_FOUND'}), 404
    
    if task['user_id'] != g.user_id:
        return jsonify({'error': 'FORBIDDEN'}), 403
    
    if task['status'] not in ['queued', 'failed']:
        return jsonify({'error': 'INVALID_STATUS', 'message': f'任务状态为 {task["status"]}'}), 400
    
    # 标记为处理中
    task['status'] = 'processing'
    
    # 检查是否有 API Key
    api_key = Config.DEEPSEEK_API_KEY
    
    if not api_key:
        # Mock 模式
        import random
        time.sleep(1)
        
        # 模拟生成结果
        mock_urls = [
            f'/api/art/mock/{task_id}.png',
            f'https://picsum.photos/seed/{task_id}/512/512'
        ]
        
        task['status'] = 'succeeded'
        task['result_url'] = random.choice(mock_urls)
        task['completed_at'] = datetime.now().isoformat()
        
        return jsonify({
            'data': {
                'task_id': task_id,
                'status': 'succeeded',
                'result_url': task['result_url'],
                'message': 'Mock 模式：模拟生成成功'
            }
        })
    
    # 实际调用 AI 服务
    try:
        import requests
        
        response = requests.post(
            'https://api.deepseek.com/v1/images/generations',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'deepseek-image-1',
                'prompt': task['prompt'],
                'n': 1,
                'size': '1024x1024'
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            image_url = result.get('data', [{}])[0].get('url')
            
            task['status'] = 'succeeded'
            task['result_url'] = image_url
            task['completed_at'] = datetime.now().isoformat()
            
            return jsonify({
                'data': {
                    'task_id': task_id,
                    'status': 'succeeded',
                    'result_url': image_url
                }
            })
        else:
            task['status'] = 'failed'
            task['error'] = f"API error: {response.status_code}"
            
            return jsonify({
                'error': 'API_ERROR',
                'message': f'AI 服务返回错误: {response.status_code}'
            }), 500
    
    except Exception as e:
        task['status'] = 'failed'
        task['error'] = str(e)
        
        return jsonify({
            'error': 'PROCESSING_ERROR',
            'message': str(e)
        }), 500


@art_bp.route('/tasks/<task_id>/retry', methods=['POST'])
@require_auth
def retry_task(task_id):
    """重试失败的任务"""
    task = _task_store.get(task_id)
    if not task:
        return jsonify({'error': 'TASK_NOT_FOUND'}), 404
    
    if task['user_id'] != g.user_id:
        return jsonify({'error': 'FORBIDDEN'}), 403
    
    if task['status'] != 'failed':
        return jsonify({'error': 'INVALID_STATUS', 'message': '只能重试失败的任务'}), 400
    
    task['status'] = 'queued'
    task.pop('error', None)
    
    return jsonify({
        'data': {
            'task_id': task_id,
            'status': 'queued',
            'message': '任务已重新提交'
        }
    })


@art_bp.route('/history', methods=['GET'])
@require_auth
def get_history():
    """获取用户的生图历史"""
    limit = request.args.get('limit', 20, type=int)
    status = request.args.get('status')
    
    tasks = [
        task for task in _task_store.values()
        if task['user_id'] == g.user_id
    ]
    
    if status:
        tasks = [t for t in tasks if t['status'] == status]
    
    # 按时间倒序
    tasks.sort(key=lambda t: t['created_at'], reverse=True)
    
    return jsonify({
        'data': [
            {
                'task_id': t['id'],
                'poem_id': t['poem_id'],
                'poem_text': t['poem_text'][:30] + '...' if len(t['poem_text']) > 30 else t['poem_text'],
                'style': t['style'],
                'status': t['status'],
                'result_url': t.get('result_url'),
                'created_at': t['created_at']
            }
            for t in tasks[:limit]
        ]
    })


@art_bp.route('/tasks/<task_id>', methods=['DELETE'])
@require_auth
def delete_task(task_id):
    """删除任务"""
    task = _task_store.get(task_id)
    if not task:
        return jsonify({'error': 'TASK_NOT_FOUND'}), 404
    
    if task['user_id'] != g.user_id:
        return jsonify({'error': 'FORBIDDEN'}), 403
    
    del _task_store[task_id]
    
    return jsonify({
        'data': {
            'status': 'deleted',
            'message': '任务已删除'
        }
    })


@art_bp.route('/mock/<task_id>.png', methods=['GET'])
def mock_image(task_id):
    """Mock 图片生成（开发测试用）"""
    # 生成简单的占位图片
    from io import BytesIO
    
    try:
        # 使用 PIL 生成简单图片
        from PIL import Image, ImageDraw, ImageFont
        
        # 创建图片
        img = Image.new('RGB', (512, 512), color=(248, 244, 232))
        draw = ImageDraw.Draw(img)
        
        # 画一些装饰
        draw.rectangle([20, 20, 492, 492], outline=(139, 115, 85), width=2)
        
        # 添加文字
        try:
            font = ImageFont.truetype("msyh.ttc", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((256, 256), "诗词意境", fill=(139, 115, 85), anchor='mm', font=font)
        
        # 保存到 BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return send_file(buffer, mimetype='image/png')
    
    except ImportError:
        # 如果没有 PIL，返回简单占位符
        return jsonify({
            'message': 'Mock image (PIL not available)',
            'task_id': task_id
        })


@art_bp.route('/styles', methods=['GET'])
def get_styles():
    """获取支持的风格列表"""
    styles = [
        {'id': 'shuimo', 'name': '水墨画', 'description': '传统水墨风格，意境深远'},
        {'id': 'gongbi', 'name': '工笔画', 'description': '精细勾勒，色彩鲜艳'},
        {'id': 'dunhuang', 'name': '敦煌风', 'description': '敦煌壁画风格，色彩斑斓', 'vip': True},
        {'id': 'modern', 'name': '现代风', 'description': '现代中式风格，简约时尚'},
        {'id': 'landscape', 'name': '山水画', 'description': '经典山水画意境'}
    ]
    
    return jsonify({'data': styles})


@art_bp.route('/polaroid-templates', methods=['GET'])
def get_polaroid_templates():
    """获取拍立得边框模板"""
    templates = [
        {
            'id': 'classic',
            'name': '经典拍立得',
            'description': '纯白边框，简约经典',
            'frame_color': '#f5f5f5',
            'border_width': 12,
            'shadow': True
        },
        {
            'id': 'vintage',
            'name': '复古胶片',
            'description': '米色做旧效果，时光感',
            'frame_color': '#e8dcc8',
            'border_width': 16,
            'shadow': True,
            'tilt': -2
        },
        {
            'id': 'ink',
            'name': '水墨古卷',
            'description': '宣纸质感，水墨边框',
            'frame_color': '#f8f4e8',
            'border_width': 20,
            'shadow': False,
            'pattern': 'bamboo'
        },
        {
            'id': 'modern',
            'name': '现代简约',
            'description': '窄边框，时尚设计',
            'frame_color': '#ffffff',
            'border_width': 8,
            'shadow': True
        }
    ]
    
    return jsonify({'data': templates})
