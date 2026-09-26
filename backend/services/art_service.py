"""
AI 生图服务 - 诗词意境图片生成
支持多种 AI 服务提供商（DeepSeek、OpenAI 等）
"""
import os
import json
import time
import logging
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import base64
import hashlib

import requests

logger = logging.getLogger(__name__)


class ArtProvider(Enum):
    """AI 图片生成服务商"""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    MOCK = "mock"  # 本地 mock 模式


class ArtStatus(Enum):
    """生成任务状态"""
    QUEUED = "queued"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ArtTask:
    """生图任务"""
    id: str
    user_id: str
    poem_id: str
    poem_text: str
    style: str
    provider: str
    prompt: str
    status: ArtStatus
    result_url: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: float = None
    completed_at: Optional[float] = None
    retry_count: int = 0


class ArtService:
    """
    AI 生图服务
    
    功能：
    1. 接收诗词和风格，生成 AI 提示词
    2. 调用 AI 服务生成图片
    3. 管理生成任务状态
    4. 缓存和去重
    """
    
    # 支持的风格
    SUPPORTED_STYLES = {
        'default': 'Traditional Chinese ink painting style',
        'gongbi': 'Traditional Chinese Gongbi fine painting, delicate brushwork',
        'shuimo': 'Chinese ink wash painting (Shuimo), minimalist black ink',
        'dunhuang': 'Dunhuang cave fresco style, vibrant colors',
        'modern': 'Modern Chinese art fusion, contemporary interpretation',
        'landscape': 'Classical Chinese landscape painting (Shanshui)',
        'figure': 'Traditional Chinese figure painting',
        'bird_flower': 'Chinese bird and flower painting (Huaniaohua)',
    }
    
    # DeepSeek API 配置
    DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/images/generations'
    
    def __init__(self, db_session=None):
        self.db = db_session
        self._task_cache: Dict[str, ArtTask] = {}
        self._user_quota: Dict[str, int] = {}  # 用户配额
    
    @property
    def api_key(self) -> Optional[str]:
        """获取 API Key"""
        from config import Config
        return Config.DEEPSEEK_API_KEY
    
    def check_quota(self, user_id: str) -> Dict:
        """
        检查用户生图配额
        
        Returns:
            {'allowed': bool, 'remaining': int, 'reset_at': timestamp}
        """
        # 免费用户每天 3 次
        daily_limit = 3
        used = self._user_quota.get(user_id, 0)
        remaining = max(0, daily_limit - used)
        
        return {
            'allowed': remaining > 0,
            'remaining': remaining,
            'daily_limit': daily_limit,
            'reset_at': self._get_daily_reset_timestamp()
        }
    
    def _get_daily_reset_timestamp(self) -> float:
        """获取每日重置时间戳（午夜 UTC）"""
        import time
        now = time.time()
        day_seconds = 24 * 60 * 60
        midnight = now - (now % day_seconds) + day_seconds
        return midnight
    
    def _consume_quota(self, user_id: str) -> bool:
        """消耗配额"""
        if not self.check_quota(user_id)['allowed']:
            return False
        
        self._user_quota[user_id] = self._user_quota.get(user_id, 0) + 1
        return True
    
    def create_task(self, user_id: str, poem_id: str, poem_text: str,
                   style: str = 'default', 
                   custom_prompt: str = None) -> Dict:
        """
        创建生图任务
        
        Args:
            user_id: 用户ID
            poem_id: 诗句ID
            poem_text: 诗句文本
            style: 风格
            custom_prompt: 自定义提示词（可选）
        
        Returns:
            任务信息
        """
        # 检查配额
        quota = self.check_quota(user_id)
        if not quota['allowed']:
            return {
                'error': 'QUOTA_EXCEEDED',
                'message': f'今日生成次数已用完（{quota["daily_limit"]}次/天）',
                'remaining': 0
            }
        
        # 检查风格
        if style not in self.SUPPORTED_STYLES:
            style = 'default'
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 生成提示词
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self._build_prompt(poem_text, style)
        
        # 创建任务
        task = ArtTask(
            id=task_id,
            user_id=user_id,
            poem_id=poem_id,
            poem_text=poem_text,
            style=style,
            provider=ArtProvider.DEEPSEEK.value if self.api_key else ArtProvider.MOCK.value,
            prompt=prompt,
            status=ArtStatus.QUEUED,
            created_at=time.time()
        )
        
        # 缓存任务
        self._task_cache[task_id] = task
        
        # 消耗配额
        self._consume_quota(user_id)
        
        return {
            'task_id': task_id,
            'status': task.status.value,
            'prompt': prompt,
            'quota_remaining': self.check_quota(user_id)['remaining']
        }
    
    def _build_prompt(self, poem_text: str, style: str) -> str:
        """
        构建 AI 生图提示词
        
        提示词设计原则：
        1. 明确中国风绘画风格
        2. 包含诗词内容描述
        3. 添加质量修饰词
        """
        style_prefix = self.SUPPORTED_STYLES.get(style, self.SUPPORTED_STYLES['default'])
        
        # 移除换行符
        clean_text = poem_text.replace('\n', '，').replace(' ', '')
        
        prompt = f"""
{style_prefix}.

Poetry content: {clean_text}

Requirements:
- Traditional Chinese art style
- Serene, elegant atmosphere
- Minimalist composition
- Black ink with subtle red/gold accents acceptable
- High detail, 4K quality
- Vertical scroll format suitable
- No text or characters in the image
- Inspired by Tang/Song dynasty aesthetics
""".strip()
        
        return prompt
    
    def submit_task(self, task_id: str) -> Dict:
        """
        提交任务到 AI 服务
        
        Returns:
            提交结果
        """
        task = self._task_cache.get(task_id)
        if not task:
            return {'error': 'TASK_NOT_FOUND'}
        
        if task.status != ArtStatus.QUEUED:
            return {'error': 'INVALID_STATUS', 'message': f'任务状态为 {task.status.value}'}
        
        # Mock 模式
        if task.provider == ArtProvider.MOCK.value:
            return self._process_mock(task)
        
        # DeepSeek API
        if task.provider == ArtProvider.DEEPSEEK.value:
            return self._process_deepseek(task)
        
        return {'error': 'UNSUPPORTED_PROVIDER'}
    
    def _process_mock(self, task: ArtTask) -> Dict:
        """Mock 模式：模拟生成"""
        task.status = ArtStatus.PROCESSING
        
        # 模拟处理时间
        time.sleep(1)
        
        # 生成 mock 图片 URL
        mock_url = f"/api/art/mock/{task.id}.png"
        
        task.status = ArtStatus.SUCCEEDED
        task.result_url = mock_url
        task.completed_at = time.time()
        
        return {
            'task_id': task.id,
            'status': task.status.value,
            'result_url': mock_url,
            'message': 'Mock 生成成功（实际需配置 AI 服务）'
        }
    
    def _process_deepseek(self, task: ArtTask) -> Dict:
        """调用 DeepSeek API 生成图片"""
        if not self.api_key:
            return {'error': 'API_KEY_MISSING', 'message': '未配置 DeepSeek API Key'}
        
        task.status = ArtStatus.PROCESSING
        
        try:
            # 注意：DeepSeek 可能不支持图片生成，这里使用 OpenAI 兼容接口作为示例
            # 实际使用时需要根据具体 API 调整
            response = requests.post(
                self.DEEPSEEK_API_URL,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-image-1',
                    'prompt': task.prompt,
                    'n': 1,
                    'size': '1024x1024'
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                image_url = result.get('data', [{}])[0].get('url')
                
                task.status = ArtStatus.SUCCEEDED
                task.result_url = image_url
                task.completed_at = time.time()
                
                return {
                    'task_id': task.id,
                    'status': task.status.value,
                    'result_url': image_url
                }
            else:
                task.status = ArtStatus.FAILED
                task.error_code = 'API_ERROR'
                task.error_message = f"API 返回错误: {response.status_code}"
                
                return {
                    'error': 'API_ERROR',
                    'message': task.error_message
                }
        
        except requests.exceptions.Timeout:
            task.status = ArtStatus.FAILED
            task.error_code = 'TIMEOUT'
            task.error_message = 'AI 服务响应超时'
            return {'error': 'TIMEOUT', 'message': 'AI 服务响应超时，请稍后重试'}
        
        except Exception as e:
            task.status = ArtStatus.FAILED
            task.error_code = 'INTERNAL_ERROR'
            task.error_message = str(e)
            logger.error(f"AI 生成失败: {e}")
            return {'error': 'INTERNAL_ERROR', 'message': str(e)}
    
    def get_task_status(self, task_id: str) -> Dict:
        """获取任务状态"""
        task = self._task_cache.get(task_id)
        if not task:
            return {'error': 'TASK_NOT_FOUND'}
        
        result = {
            'task_id': task.id,
            'status': task.status.value,
            'poem_id': task.poem_id,
            'style': task.style,
            'created_at': task.created_at
        }
        
        if task.status == ArtStatus.SUCCEEDED:
            result['result_url'] = task.result_url
            result['completed_at'] = task.completed_at
        
        if task.status == ArtStatus.FAILED:
            result['error_code'] = task.error_code
            result['error_message'] = task.error_message
            # 提供重试建议
            if task.retry_count < 3:
                result['retry_suggestion'] = '可以重试'
        
        return result
    
    def retry_task(self, task_id: str) -> Dict:
        """重试失败的任务"""
        task = self._task_cache.get(task_id)
        if not task:
            return {'error': 'TASK_NOT_FOUND'}
        
        if task.status != ArtStatus.FAILED:
            return {'error': 'INVALID_STATUS', 'message': '只能重试失败的任务'}
        
        if task.retry_count >= 3:
            return {'error': 'MAX_RETRIES', 'message': '已达最大重试次数'}
        
        task.retry_count += 1
        task.status = ArtStatus.QUEUED
        task.error_code = None
        task.error_message = None
        
        return self.submit_task(task_id)
    
    def cancel_task(self, task_id: str) -> Dict:
        """取消任务"""
        task = self._task_cache.get(task_id)
        if not task:
            return {'error': 'TASK_NOT_FOUND'}
        
        if task.status in [ArtStatus.QUEUED, ArtStatus.PROCESSING]:
            task.status = ArtStatus.CANCELLED
            return {'status': 'cancelled', 'message': '任务已取消'}
        
        return {'error': 'INVALID_STATUS', 'message': '任务无法取消'}
    
    def list_user_tasks(self, user_id: str, status: str = None, 
                       limit: int = 20) -> List[Dict]:
        """获取用户的生图任务列表"""
        tasks = [
            task for task in self._task_cache.values()
            if task.user_id == user_id
        ]
        
        if status:
            tasks = [t for t in tasks if t.status.value == status]
        
        # 按时间倒序
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        return [
            {
                'task_id': t.id,
                'poem_id': t.poem_id,
                'poem_text': t.poem_text[:20] + '...' if len(t.poem_text) > 20 else t.poem_text,
                'style': t.style,
                'status': t.status.value,
                'result_url': t.result_url if t.status == ArtStatus.SUCCEEDED else None,
                'created_at': t.created_at
            }
            for t in tasks[:limit]
        ]
    
    def delete_task(self, task_id: str, user_id: str) -> Dict:
        """删除任务（用户只能删除自己的）"""
        task = self._task_cache.get(task_id)
        if not task:
            return {'error': 'TASK_NOT_FOUND'}
        
        if task.user_id != user_id:
            return {'error': 'FORBIDDEN', 'message': '无权删除此任务'}
        
        # 从缓存中移除
        del self._task_cache[task_id]
        
        return {'status': 'deleted', 'message': '任务已删除'}


# 简化的任务存储（实际应使用数据库）
_task_store: Dict[str, ArtTask] = {}


def save_task(task: ArtTask):
    """保存任务到持久存储"""
    _task_store[task.id] = task


def get_task(task_id: str) -> Optional[ArtTask]:
    """获取任务"""
    return _task_store.get(task_id)


def list_tasks(user_id: str = None, status: ArtStatus = None) -> List[ArtTask]:
    """列出任务"""
    tasks = list(_task_store.values())
    
    if user_id:
        tasks = [t for t in tasks if t.user_id == user_id]
    
    if status:
        tasks = [t for t in tasks if t.status == status]
    
    return tasks
