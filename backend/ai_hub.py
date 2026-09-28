"""AI 统一接入层（ai_hub）

所有 AI 功能的账号、Key、功能开关、模型调用，唯一入口都在这里：
- 后端任何模块不得自行读取 *_API_KEY，必须通过 ai_hub.get_api_key()
- 任何模块不得自行直连模型 API，必须通过 ai_hub.chat()
- 功能开关由 /v1/ai/settings（设置页）管理，持久化在 ai_settings.json

目前 Provider：DeepSeek（deepseek-chat）。未来新增 Provider（通义/智谱等），
只改这里 + /v1/ai/settings，业务代码零改动。
"""
import json
import os
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, 'ai_settings.json')

PROVIDER = 'DeepSeek'
API_URL = 'https://api.deepseek.com/chat/completions'
MODEL = 'deepseek-chat'
KEY_ENV_NAME = 'DEEPSEEK_API_KEY'

# 功能开关注册表：key → 中文名（设置页展示）
FEATURES = {
    'explain': 'AI 诗词解读',
    'roundtable': '诗人圆桌',
}


class AIError(Exception):
    """AI 调用失败（网络/超时/配额等）"""


# ============ Key 管理（唯一读取口） ============

# 占位符识别：这些开头的值视为「未配置」，不算有效 Key
_PLACEHOLDER_PREFIXES = ('your-', 'xxx', 'sk-xxx', 'here', '填入', '请输入')


def get_api_key():
    """统一取 Key：环境变量（.env 注入）优先，其次 Config（启动时快照）。
    占位符值一律视为未配置。"""
    key = None
    try:
        from config import Config
        key = os.environ.get(KEY_ENV_NAME) or getattr(Config, KEY_ENV_NAME, None)
    except Exception:
        key = os.environ.get(KEY_ENV_NAME)
    if not key:
        return None
    key = key.strip()
    if not key or key.lower().startswith(_PLACEHOLDER_PREFIXES):
        return None
    return key


def is_ready():
    return bool(get_api_key())


def update_env_key(value):
    """更新 backend/.env 中的 Key（不存在则追加），并同步运行时环境"""
    env_path = os.path.join(BASE_DIR, '.env')
    lines = []
    if os.path.exists(env_path):
        with open(env_path, encoding='utf-8') as f:
            lines = f.read().splitlines()
    replaced = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f'{KEY_ENV_NAME}=') or line.strip().startswith(f'# {KEY_ENV_NAME}='):
            lines[i] = f'{KEY_ENV_NAME}={value}'
            replaced = True
            break
    if not replaced:
        lines.append(f'{KEY_ENV_NAME}={value}')
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    os.environ[KEY_ENV_NAME] = value
    try:
        from config import Config
        setattr(Config, KEY_ENV_NAME, value)
    except Exception:
        pass


# ============ 功能开关 ============

def load_settings():
    try:
        with open(SETTINGS_FILE, encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {}
    feats = {k: bool(data.get('features', {}).get(k, True)) for k in FEATURES}
    return {'features': feats}


def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def feature_enabled(feature):
    return load_settings()['features'].get(feature, True)


# ============ 模型调用（唯一直连口） ============

def chat(messages, max_tokens=600, temperature=0.9, timeout=60):
    """调用对话模型，返回回复文本；失败抛 AIError"""
    api_key = get_api_key()
    if not api_key:
        raise AIError('AI 服务未配置 Key，请在「我的 → AI 设置」中填入')
    try:
        req = urllib.request.Request(
            API_URL,
            data=json.dumps({
                'model': MODEL,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
            }).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode('utf-8'))
        return result['choices'][0]['message']['content']
    except AIError:
        raise
    except Exception as e:
        raise AIError(str(e))
