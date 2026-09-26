# 诗语雅集

> 让每一次社交，都有国风诗意。

一个基于二十四节气和飞花令的国风文化对战游戏。

## 产品定位

**诗语雅集** 是一个以飞花令对战为核心的文化体验产品，以节气五行主题增强当日玩法差异，让用户在娱乐中感受诗词魅力。

核心体验闭环：**对战 → 输赢 → 解锁诗句 → 文化延伸**

## 一期范围

### 核心功能
- [x] 飞花令对战（2-8人，文字输入，计时，判题，淘汰，结算）
- [x] 节气主题（数据+展示）
- [x] 匿名身份 + 战绩（单设备）
- [x] 诗词收藏 + 节气收藏

### 技术栈
- 前端：Vue 3 + TypeScript + Vite + Vant UI
- 后端：Python Flask + Flask-SocketIO
- 数据库：SQLite
- 实时：Socket.IO

### 不做（一期）
- AI 成图
- 好友关系
- 支付/会员
- 复杂社交

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt
python app.py
```

服务启动在 http://localhost:5000

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

## 项目结构

```
shiji/
├── backend/
│   ├── app.py              # Flask 主应用
│   ├── config.py           # 配置
│   ├── models.py           # 数据库模型
│   ├── data/
│   │   ├── solar_terms.py  # 24节气数据
│   │   └── poems.py        # 初始诗词数据
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/          # 页面组件
│   │   ├── stores/         # Pinia 状态
│   │   ├── api/            # API 客户端
│   │   └── socket.ts       # Socket.IO 客户端
│   ├── package.json
│   └── vite.config.ts
├── TASKS.md                # 任务清单
└── 诗语雅集_AI-Coding_PRD.md
```

## 数据来源

诗词数据来自 [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) 项目（MIT License）。

## License

MIT
