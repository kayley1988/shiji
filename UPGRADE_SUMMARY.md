# 诗语雅集 · 升级改造总结

> 本文档记录 2024 年对诗语雅集项目的安全修复、功能升级与架构优化。

---

## 一、高优先级修复（已完成 ✅）

### 1. 安全问题修复

#### 1.1 移除硬编码密钥
**问题**：数据库密码、API Key 硬编码在代码中
```python
# ❌ 之前
DEEPSEEK_API_KEY = 'sk-xxx'
SECRET_KEY = 'shiyayaji-secret-2024'
DATABASE_URL = 'mysql://root:xxx@...'
```

**修复**：强制环境变量验证
```python
# ✅ 现在
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SEC�️ SECRET_KEY 环境变量未设置！")
```

#### 1.2 CORS 配置收紧
```python
# ❌ 之前
CORS(app, origins="*")

# ✅ 现在
CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)
```

#### 1.3 环境变量配置
| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | Flask 密钥（必填） | 无 |
| `DATABASE_URL` | 数据库连接 | `sqlite:///shiyayaji.db` |
| `CORS_ORIGINS` | 允许的源（逗号分隔） | `localhost:3000` |
| `DEEPSEEK_API_KEY` | AI 服务密钥 | 无（功能受限） |
| `REDIS_URL` | Redis（可选） | 无 |

---

## 二、功能升级（已完成 ✅）

### 2. 接尾飞花令游戏

#### 玩法设计
```
接尾飞花令规则：
1. 系统给出一个起始字（如「月」）
2. 玩家说出包含这个字的诗句（如「海上生明月」）
3. 下一位玩家用上一句的尾字继续（「月」→「明日」）
4. 循环往复，超时/错误/重复则淘汰
```

#### 计分规则
| 条件 | 加分 |
|------|------|
| 基础答对 | +15 分 |
| 连续答对 N 句 | +N×2 分 |
| 剩余时间 > 5秒 | +3 分 |
| 包含节气意象 | +5 分 |

#### 核心文件
```
backend/
├── services/
│   └── tail_connect_service.py   # 接尾逻辑
└── routes/
    └── tail_connect.py          # API 路由

frontend/
├── components/game/
│   └── TailConnectGame.vue      # 游戏界面
├── pages/
│   └── TailConnect.vue          # 房间页面
└── composables/
    └── useSpeechRecognition.ts   # 语音识别
```

### 2.2 拍立得诗词卡片

#### 边框样式
| 风格 | 特点 | 适用场景 |
|------|------|----------|
| 经典拍立得 | 纯白边框 | 日常分享 |
| 复古胶片 | 米色做旧 | 怀旧情怀 |
| 水墨古卷 | 宣纸质感 | 诗词意境 |
| 现代简约 | 窄边框 | 时尚设计 |

#### 生成流程
```
用户选择诗句 → 选择风格 → 生成提示词 → 调用 AI → 生成图片 → 套用边框 → 保存/分享
```

### 2.3 语音输入

#### 技术实现
```typescript
// 使用浏览器原生 Web Speech API
// 仅将识别结果转为文字，不上传任何音频
const { isListening, transcript, start, stop } = useSpeechRecognition()

// 隐私提示
'语音将由浏览器本地识别为文字，不会上传任何音频数据'
```

#### 支持情况
- ✅ Chrome/Edge（完整支持）
- ⚠️ Safari（部分支持）
- ❌ Firefox（不支持）

---

## 三、架构升级（进行中 🔄）

### 3.1 后端目录结构
```
backend/
├── app.py                 # 主应用入口
├── config.py              # 配置（已重构）
├── models.py             # 数据模型
├── routes/               # 🔄 新增：API 路由
│   ├── __init__.py
│   ├── tail_connect.py   # 接尾游戏 API
│   ├── art.py            # AI 生图 API
│   └── poems.py          # 诗词查询 API
├── services/             # 🔄 新增：业务逻辑
│   ├── __init__.py
│   ├── game_service.py   # 游戏核心服务
│   ├── poem_service.py   # 诗词服务
│   ├── tail_connect_service.py
│   └── art_service.py     # AI 生图服务
├── data/                 # 静态数据
│   ├── solar_terms.py
│   └── poems.py
└── nlp/                  # 文本处理
    └── char_convert.py
```

### 3.2 前端目录结构
```
frontend/src/
├── components/
│   ├── game/
│   │   ├── PolaroidCard.vue      # 🔄 新增
│   │   └── TailConnectGame.vue   # 🔄 新增
│   └── ...
├── composables/
│   ├── useSpeechRecognition.ts    # 🔄 新增
│   └── ...
├── pages/
│   ├── TailConnect.vue           # 🔄 新增
│   ├── PoemCard.vue              # 🔄 新增
│   └── ...
└── api/
    └── index.ts                  # 已扩展
```

---

## 四、API 文档

### 4.1 接尾飞花令 API

#### 创建房间
```http
POST /v1/tail-connect/rooms
Content-Type: application/json

{
  "difficulty": "medium",
  "max_players": 8
}

# Response
{
  "data": {
    "room_id": "uuid",
    "code": "123456",
    "start_char": "月",
    "my_user_id": "token"
  }
}
```

#### 加入房间
```http
POST /v1/tail-connect/rooms/{room_id}/join
{
  "code": "123456",
  "nickname": "李白"
}
```

#### 提交答案
```http
POST /v1/tail-connect/rooms/{room_id}/submit
{
  "answer": "海上生明月"
}

# Response
{
  "data": {
    "result": "VALID",
    "score_delta": 15,
    "next_char": "月",
    "message": "正确！+15分"
  }
}
```

### 4.2 AI 生图 API

#### 创建任务
```http
POST /v1/art/generate
{
  "poem_id": "p001",
  "poem_text": "春眠不觉晓...",
  "style": "shuimo"
}

# Response
{
  "data": {
    "task_id": "uuid",
    "status": "queued",
    "quota_remaining": 2
  }
}
```

#### 提交任务
```http
POST /v1/art/tasks/{task_id}/submit

# Response
{
  "data": {
    "status": "succeeded",
    "result_url": "https://..."
  }
}
```

#### 获取配额
```http
GET /v1/art/quota

# Response
{
  "data": {
    "remaining": 2,
    "daily_limit": 3,
    "reset_at": "2024-01-02T00:00:00"
  }
}
```

---

### 2.4 单人飞花令练习

#### 模式设计
| 模式 | 描述 | 计时 |
|------|------|------|
| 自由练习 | 随意说出含关键字的诗句 | ❌ |
| 限时挑战 | 每题计时答题 | ✅ 10/15/20秒 |
| 接尾练习 | 单人接龙模式 | ✅ 8秒 |
| 闯关模式 | 逐步提升难度 | ✅ |

#### 核心功能
- 30个常用关键字选择
- 语音输入支持
- 错题回顾
- 正确率统计

#### 核心文件
```
backend/routes/solo.py       # 单人练习 API
frontend/pages/SoloFeihua.vue  # 单人练习页面
```

### 2.5 语音对战模式

#### 核心设计
```
┌─────────────────────────────────────────────────────┐
│  AI 朗读题目  →  你语音回答  →  AI判定  →  轮流对战  │
└─────────────────────────────────────────────────────┘
```

#### 三种对战模式

| 模式 | 玩法 | 示例 |
|------|------|------|
| 🔥 飞花令 | 说出含关键字的诗句 | 关键字「月」→ 「床前明月光」 |
| 💬 接句 | AI出上句，你接下句 | 「床前明月光」→ 「疑是地上霜」 |
| 🔗 接尾 | 用指定字开头接句 | 开头「月」→ 「月落乌啼霜满天」 |

#### 技术实现
- **TTS (Text-to-Speech)**: Web Speech API SpeechSynthesis
- **ASR (语音识别)**: Web Speech API SpeechRecognition
- **语音降级**: 浏览器不支持时降级为手动输入

#### TTS 优化
- 智能选择最佳中文语音（微软/谷歌优先）
- 支持语音预览
- 可切换多种中文音色

#### 题库枯竭时 AI 自由生成
```
题库有 → 使用题库诗句
题库无 → AI 根据格律模板生成
         └── 五言/七言绝句模板
         └── 意象组合（风花雪月等）
         └── 符合平仄对仗
```

#### 核心文件
```
frontend/src/
├── components/game/VoiceBattle.vue     # 语音对战组件
├── composables/useSpeechSynthesis.ts   # 语音合成 Hook
├── pages/VoiceBattle.vue               # 语音对战页面
└── router.ts                          # 路由已添加

backend/routes/
├── poetry_generator.py                  # AI 诗句生成 API
└── app.py                             # 已注册蓝图
```

#### 界面特色
- AI 头像 + 波形动画（正在说话）
- 玩家头像 + 波形动画（正在聆听）
- 对话气泡轮播
- 实时计时条（超时警告）
- AI 智能评论（鼓励/调侃）

---

## 五、藏书阁模块（新增）

### 5.1 核心功能

```
┌─────────────────────────────────────────────────────────────┐
│                        藏书阁                               │
├─────────────────────────────────────────────────────────────┤
│  📚 书架管理                                               │
│     ├── 创建书架（自定义名称、图标、描述）                    │
│     ├── 收藏诗词、金句、诗人专辑                             │
│     └── 多书架分类整理                                      │
├─────────────────────────────────────────────────────────────┤
│  💫 金句卡片                                               │
│     ├── 从诗句创建拍立得风格卡片                            │
│     ├── AI 生成意境图片                                    │
│     ├── 自定义标题、笔记、标签                              │
│     └── 多种风格（经典/复古/水墨/现代）                      │
├─────────────────────────────────────────────────────────────┤
│  📖 诗词分类                                               │
│     ├── 按朝代（唐/宋/元/明/清...）                        │
│     ├── 按诗人专辑                                        │
│     ├── 按主题（爱情/自然/思乡/边塞...）                   │
│     └── 5万+ 诗词数据库                                    │
├─────────────────────────────────────────────────────────────┤
│  📜 阅读历史                                               │
│     └── 自动记录浏览足迹                                   │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 数据模型

```
数据库表：
├── golden_quotes        # 金句卡片
├── bookshelves          # 书架
├── bookshelf_items      # 书架条目
├── poem_categories      # 诗词分类
├── author_profiles      # 诗人专辑
└── reading_history      # 阅读历史
```

### 5.3 API 端点

```
GET  /v1/library/stats              # 统计数据
GET  /v1/library/bookshelves        # 书架列表
POST /v1/library/bookshelves        # 创建书架
GET  /v1/library/golden-quotes      # 金句卡片
POST /v1/library/golden-quotes      # 创建卡片
GET  /v1/library/categories         # 分类
GET  /v1/library/dynasties          # 朝代统计
GET  /v1/library/authors             # 诗人列表
GET  /v1/library/search             # 搜索
```

### 5.4 核心文件

```
backend/
├── models_library.py        # 藏书阁数据模型
└── routes/
    └── library.py          # 藏书阁 API

frontend/src/
├── pages/
│   └── Library.vue         # 藏书阁主页
└── api/index.ts            # 已添加 library API
```

---

## 六、待完成事项

### 高优先级
- [ ] 完善单元测试
- [ ] 添加日志系统（结构化日志）
- [ ] 数据库迁移工具（Alembic）

### 中优先级
- [ ] Redis 缓存集成
- [ ] Swagger API 文档
- [ ] 前端依赖升级

### 低优先级
- [ ] Docker 部署配置
- [ ] CI/CD 流水线
- [ ] 性能监控

---

## 六、启动说明

### 后端启动
```bash
cd backend

# 设置环境变量（必填）
set SECRET_KEY=your-secure-random-string
set DATABASE_URL=sqlite:///shiyayaji.db

# 安装依赖
pip install -r requirements.txt

# 启动
python app.py
```

### 前端启动
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 七、技术栈版本

### 当前版本
| 组件 | 版本 |
|------|------|
| Python | 3.11+ |
| Flask | 3.0+ |
| Vue | 3.4+ |
| Vite | 5.0+ |
| Vant | 4.8+ |

### 建议升级
| 组件 | 当前 | 建议 |
|------|------|------|
| Vue | 3.4.x | 3.5.x |
| Vite | 5.0.x | 6.0.x |
| Vant | 4.8.x | 4.10.x |
| TypeScript | 5.3.x | 5.4.x |

---

*文档更新日期：2024年*
