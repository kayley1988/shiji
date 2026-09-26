# 诗语雅集 MVP 任务清单

## P0 - 核心对战（必须交付）

### 后端
- [ ] 1. 项目初始化：Flask + Flask-SocketIO + SQLite
- [ ] 2. 数据库迁移：users, rooms, room_members, game_turns, answer_submissions, game_results, poems, poem_lines, tags, poem_line_tags, solar_terms, daily_themes
- [ ] 3. 匿名身份 API：POST /v1/auth/anonymous
- [ ] 4. 节气主题 API：GET /v1/daily-theme
- [ ] 5. 房间 CRUD：创建/加入/离开/开始
- [ ] 6. Socket.IO 房间订阅与快照
- [ ] 7. 回合状态机：PLAYING → 判题 → 淘汰/计分 → 推进
- [ ] 8. 答案判题服务：精确命中 + 重复检测 + 超时
- [ ] 9. 结算 API：GET /v1/rooms/:id/result
- [ ] 10. 战绩 API：GET /v1/me/profile

### 前端
- [ ] 11. 项目初始化：Vue3 + TS + Vite + Vant UI
- [ ] 12. 匿名登录 + Token 存储
- [ ] 13. 首页：节气卡 + 玩法入口
- [ ] 14. 创建房间页：模式/关键词/时间/人数
- [ ] 15. 等待区：成员列表 + 开始按钮
- [ ] 16. 对战房间：计时 + 输入框 + 提交 + 淘汰展示
- [ ] 17. 结算页：胜负 + 得分 + 再来一局
- [ ] 18. 个人中心：段位 + 统计

## P1 - 文化延伸（体验加分）

### 后端
- [ ] 19. 诗句收藏 API
- [ ] 20. 节气详情 API（含诗词列表）

### 前端
- [ ] 21. 收藏功能：诗词收藏
- [ ] 22. 节气详情页：诗词地图雏形
- [ ] 23. 冷门诗句科普卡（淘汰时展示）

## P2 - 体验完善（可后置）

- [ ] 24. 浏览器语音识别（文字填入，不上传）
- [ ] 25. 练习模式（单人/AI）
- [ ] 26. 每日任务
- [ ] 27. 基础埋点

## 不做（一期）
- AI 成图
- 好友关系
- 支付/会员
- 复杂 UGC

## 技术栈
- 前端：Vue 3 + TS + Vite + Vant UI
- 后端：Python Flask + Flask-SocketIO
- 数据库：SQLite
- 实时：Socket.IO
