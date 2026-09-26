# 诗语雅集｜AI Coding 实施 PRD（一期 MVP）

> **文档版本**：v1.0  
> **产品名称**：诗语雅集  
> **Slogan**：让每一次社交，都有国风诗意。  
> **目标端**：移动端 H5 优先（兼容微信内置浏览器）  
> **一句话目标**：基于“四季＋节气＋五行＋地域＋场景＋难度＋热度”的传统文化标签底座，交付一个可供 2–8 人实时进行节气五行飞花令、积累战绩并将已解锁诗句生成国风插画的 MVP。

---

## 1. 文档信息与阅读约定

- 本文面向产品、设计、前后端与 AI Coding 工具，描述**一期可直接实施**的产品范围与契约。
- “**已确认**”来自原始需求；“**建议/待确认**”为实施默认值，不得在未确认前当作业务事实或收费承诺。
- 一期严格遵循最小可用范围：文化底座、节气五行飞花令、2–8 人实时对战、AI 诗句成画、个人战绩与收藏。
- 本文不提供可运行代码；实现时应以本文接口、状态机、字段及验收标准为准。

---

## 2. 原始需求摘要（已确认）

1. 产品定位为国风文化社交产品，底层为结构化传统文化标签库；标签维度包括：`season`、`solar_term`、`element`、`region`、`scene`、`difficulty`、`heat`。
2. 核心用户为 18–45 岁的国风/诗词爱好者、年轻聚会群体、亲子家庭、文旅人群、知识成长型用户。
3. 解决语言表达匮乏、聚会互动低质、诗词学习枯燥、景区文化理解不足等痛点。
4. 一期核心玩法为节气五行飞花令；支持 2–8 人实时对战。
5. 首页含当日节气卡、今日诗词任务、积分/段位进度、经典飞花令和节气五行飞花令入口。
6. 房间由房主设定关键词（自定义或系统推荐）、答题时间（10/15/20 秒）、人数（2–8）；支持文字和语音输入。语音一期允许使用浏览器语音识别降级。
7. 房间需有击鼓传花动画、回合倒计时；超时、重复、错误淘汰；淘汰后展示冷门诗词科普；最后存活者获胜；五行意象命中加分翻倍。
8. 每日根据日期得出节气、季节、主五行，并推荐主题关键字与诗句意象；示例映射：立春-木-春/风/柳/芽，夏至-火-炎/日/荷，秋分-金-秋/月/霜，冬至-水-雪/寒/夜。
9. 用户解锁或答对冷门诗句后可生成古风插画；免费图带水印，会员可高清无水印及工笔/水墨/敦煌风格；可保存和分享；本地开发需有可替换 AI 服务适配器及 mock 模式。
10. 个人中心包含段位（萌新、秀才、举人、进士、翰林、雅客）、总对局数、胜利数、答对诗句数、冷门诗句解锁数、AI 插画收藏集、收藏诗句与节气主题。
11. 基础诗词可参考 GitHub `chinese-poetry`；只使用允许分发的数据，保留来源和许可元数据；不得将“开源”直接等同于“无版权风险”。
12. 推荐技术栈：Vue 3 + TypeScript + Vite + Vant UI；后端 Python Flask + Flask-SocketIO；一期 SQLite，后续迁移 MySQL；实时协议 Socket.IO。
13. AI 服务预留即梦 API 适配器；密钥仅可置于后端环境变量。
14. 答案校验必须采用“**题库命中优先＋模糊匹配待审核/不计分**”；禁止 LLM 直接判题。
15. 音频不得默认上传，必须先获得用户明确同意。
16. 一期**不做**：景点、AR、美食、复杂 UGC、社群广场、支付闭环；可预留会员/生成次数产品接口。

---

## 3. 默认假设与待确认项

### 3.1 已确认需求

以第 2 节为准。特别强调：AI 成图可展示会员能力，但支付闭环不属于一期；语音应优先本地浏览器识别，不能默认保存或上传录音。

### 3.2 建议默认假设（待产品确认）

| 项目 | 默认建议 | 影响 |
|---|---|---|
| 登录 | 游客可浏览；创建/加入房间及沉淀战绩时使用微信授权或手机号/匿名临时身份，先以匿名访客 ID 落地 | 需确认正式登录方式 |
| 时区 | 以 `Asia/Shanghai` 计算当日节气 | 海外用户显示一致性 |
| 初始题库 | 先导入审核通过、许可可核验的诗句子集，不全量上线 | 内容运营成本 |
| 关键词 | 自定义关键词仅允许 1–6 个汉字，且须在词库/审核规则范围内才能计分 | 防止无答案题目 |
| 回合顺序 | 按入房顺序随机洗牌；每局固定循环 | 公平性与可解释性 |
| 淘汰规则 | 首次无效即淘汰，不设置复活 | 一期规则简洁 |
| 计分 | 局内分与个人累计经验分分离 | 防刷与段位平衡 |
| AI 配额 | 建议免费账户每日 1 次 mock/实际生成额度，会员权益仅展示接口状态 | 不构成已确认商业规则 |
| 分享 | 一期提供 Web Share/下载图片/复制链接降级，不保证所有微信分享能力 | 平台差异 |
| 内容审核 | 模糊匹配答案记录为待审核，不进入排行榜/经验结算 | 答案安全 |

### 3.3 开放确认问题

1. 正式登录是否必须接入微信 OAuth，还是一期匿名 ID 即可？
2. “经典飞花令”是否与节气五行飞花令共用房间机制，仅关闭节气/五行加成？本文按此建议设计。
3. 自定义关键词是否限制为系统推荐词的组合？若完全开放，需明确无题库命中的处理。
4. 段位阈值、经验值、免费生成额度、会员价格和权益是否由运营另行确定？
5. 诗词题库的具体许可审核责任人、审查流程与下线 SLA 是什么？
6. AI 图片的存储期限、分享有效期、删除机制及第三方服务数据条款需确认。

---

## 4. 背景、目标、非目标与成功指标

### 4.1 背景

传统诗词具备丰富情绪和社交表达价值，但用户在聚会中缺少轻量、即时、低门槛的互动形式。诗语雅集将节气、五行和意象转化为可玩、可学、可沉淀的实时飞花令，让文化标签同时服务游戏推荐与未来文旅、美食、雅集场景扩展。

### 4.2 一期目标（已确认方向）

- 建成可追溯、可审核的诗词及标签基础数据底座。
- 让用户可在 H5 内完成建房、匹配/邀请、对战、结算、查看战绩的最短闭环。
- 用节气五行主题增强当日玩法差异和诗词学习反馈。
- 让已解锁冷门诗句产生可收藏的 AI 图像内容。

### 4.3 非目标（一期明确不做）

- 不上线景区导览、地点 POI、AR 打卡、文旅线路。
- 不上线美食内容、菜品推荐或餐饮交易。
- 不做用户发帖、评论、私信、关注、社群广场等复杂 UGC/社交网络。
- 不做支付、订单、自动续费和完整会员闭环。
- 不由 LLM 判断飞花令答案正误，不把语音原始音频当作默认上传素材。
- 不承诺覆盖所有古诗词、所有节气别名或所有方言语音识别。

### 4.4 建议成功指标（待确认基线与目标值）

| 指标 | 建议口径 | 建议目标（待确认） |
|---|---|---|
| 对局完成率 | 已结算对局数 / 已开始对局数 | ≥70% |
| 建房后开局率 | 实际开始房间 / 已创建房间 | ≥55% |
| 答案有效率 | 题库精确命中答案 / 所有提交答案 | ≥60% |
| 首局完成率 | 新用户首日完成至少一局 / 新用户 | ≥35% |
| 次日留存 | 次日活跃新用户 / 首日新用户 | ≥20% |
| AI 触发率 | 发起生成用户 / 解锁冷门诗句用户 | ≥15% |
| AI 成功率 | 成功生成任务 / 已受理任务 | ≥95%（mock 除外） |
| 实时异常率 | 因服务异常结束的局数 / 开始局数 | <1% |

---

## 5. 用户与用户故事

| 用户 | 核心诉求 | 一期用户故事 |
|---|---|---|
| 国风/诗词爱好者 | 有深度地玩诗词、发现冷门佳句 | 作为诗词爱好者，我想按立春和木意象挑战飞花令，以发现与主题相关的陌生诗句。 |
| 年轻聚会用户 | 快速破冰、避免冷场 | 作为聚会组织者，我想 1 分钟创建 4 人房并设置 15 秒回合，使朋友立即参与。 |
| 亲子家庭 | 寓教于乐 | 作为家长，我想使用系统推荐关键词，避免孩子面对过难题目。 |
| 文旅人群 | 获取文化氛围和可分享内容 | 作为旅行者，我想把答对的诗句生成国风图片保存分享。 |
| 知识成长型用户 | 获得看得见的成长 | 作为学习者，我想查看胜率、答题数与段位进度，规划下一次练习。 |
| 内容运营/审核者 | 保证正确与合规 | 作为运营者，我想查看模糊提交和来源许可，决定是否纳入题库。 |

---

## 6. 范围与路线图

### 6.1 一期 MVP（必须交付）

1. 诗词、节气、标签、来源许可元数据的数据模型和导入/审核能力。
2. 首页当日节气卡、任务卡、双玩法入口。
3. 经典飞花令与节气五行飞花令（共用房间、回合、结算能力）。
4. 2–8 人 Socket.IO 实时房间；文字提交与浏览器语音识别文本填充。
5. 精确题库命中校验、重复判定、淘汰、冷门知识卡、结算、个人战绩。
6. 冷门诗句解锁、AI 成图适配器/mock、收藏、下载/分享降级。
7. 基础埋点、异常状态、权限与隐私提示。

### 6.2 二期（建议，待确认）

- 更完整的节气词库、难度自适应与主题挑战。
- 好友邀请、房间口令、观战、断线托管优化。
- 人工审核后台、题库运营工作台、模糊答案审核回流。
- 真正的微信登录/分享能力与对象存储/CDN。
- 会员权益与支付闭环（需独立 PRD、法务与支付合规）。

### 6.3 三期（建议，待确认）

- 文旅地点/路线与地域标签联动、景区文化讲解。
- AR、雅集活动、主题社群与受控 UGC。
- 美食/器物等文化内容扩展；复用统一标签体系。

---

## 7. 信息架构与页面清单

```text
首页
├─ 当日节气详情/主题说明
├─ 经典飞花令 → 创建房间 / 加入房间 → 实时房间 → 结算
├─ 节气五行飞花令 → 创建房间 / 加入房间 → 实时房间 → 结算
├─ AI 诗句成画 → 生成配置 → 任务状态 → 插画详情
└─ 我的
   ├─ 战绩与段位
   ├─ 收藏诗句
   ├─ 收藏节气主题
   └─ AI 插画收藏集
```

| 页面 | 路由建议 | 访问条件 | 目的 |
|---|---|---|---|
| 首页 | `/` | 公开 | 展示日主题并进入玩法 |
| 节气详情 | `/solar-terms/:id` | 公开 | 解释季节、五行、关键词、意象 |
| 创建房间 | `/rooms/create` | 临时身份即可 | 配置模式、人数、时间、关键词 |
| 加入房间 | `/rooms/join/:code` | 临时身份即可 | 校验口令并进入等待区 |
| 等待区/房间 | `/rooms/:roomId` | 房间成员 | 等待、实时对战、淘汰展示 |
| 结算 | `/rooms/:roomId/result` | 房间成员 | 胜负、得分、解锁、再来一局 |
| AI 成画 | `/art/create?poemId=` | 已解锁资格 | 选择风格并提交任务 |
| 插画详情 | `/artworks/:id` | 所有者/有效分享者 | 查看、下载、分享、删除 |
| 我的 | `/me` | 临时身份即可 | 段位、统计、入口 |
| 我的收藏 | `/me/collections` | 临时身份即可 | 管理诗句/主题/插画 |

---

## 8. 页面与模块详细规格

### 8.1 首页

- **布局**：顶部品牌与“我的”头像入口；第一屏为当日节气卡；其下为今日任务卡；底部为两个主玩法按钮与轻量导航。
- **当日节气卡**：展示“今日：{节气}”“{季节} · {主五行}”“主题字：{keyword}”“最佳意象：{imagery}”，配抽象国风纹样，点击进入节气详情。
- **今日任务**：显示任务名称、完成状态、建议积分/经验（若积分规则未确认，标注“预计奖励”）、当前段位进度条。点击进入对应玩法或我的战绩。
- **入口文案**：`经典飞花令`（传统关键词对战）；`节气五行飞花令`（今日主题、五行意象加成）。点击先进入创建房间，可提供“加入房间”次入口。
- **交互**：日主题由服务端返回，客户端不得自行硬编码日期规则；加载时显示骨架屏；接口失败展示“暂未获取今日雅题，点击重试”。

### 8.2 创建房间

- **布局**：模式选择、关键词区、回合时间、人数、规则摘要、创建按钮。
- **模式**：经典模式不启用节气/五行倍分；节气五行模式默认当日主题，允许从系统推荐中选择关键词。
- **关键词**：系统推荐标签可多选（建议最多 3 个）；自定义单词输入 1–6 汉字。若无可判分题库，创建按钮禁用并解释“该主题暂无可用题库，请换一个关键词”。
- **时间**：10、15、20 秒单选，默认 15 秒（建议默认，待确认）。
- **人数**：2–8 人单选，默认 4 人（建议默认，待确认）。
- **创建后**：服务端创建成功返回 `roomId`、`roomCode`、成员令牌，跳转等待区；分享仅分享邀请码/链接，不暴露鉴权令牌。

### 8.3 等待区与实时房间

- **等待区**：显示房主、席位、成员在线状态、设置摘要、邀请码复制、开始按钮（仅房主，且人数达到最小 2 人）。成员可退出；房主退出触发房主转移或解散，规则见第 9 节。
- **对战布局**：顶部显示主题/回合/剩余存活人数；中区展示当前玩家与击鼓传花动画；下区为倒计时、已用答案提示、文本输入、语音按钮、提交按钮；侧/底部为成员状态。
- **提交**：仅当前存活且轮到自己的成员可提交；文本最长建议 80 字，客户端先做空白和长度拦截，服务端为唯一判定源。
- **语音**：点击前展示“语音将由浏览器本地识别为文字；除非你另行授权，不上传录音”。浏览器不支持时显示“当前浏览器不支持语音识别，请使用文字输入”。识别结果进入输入框，用户必须确认提交。
- **淘汰态**：输入区禁用；展示“本轮未通过，暂作观战”；展示一张与当日节气相关的冷门诗词科普卡。淘汰者继续接收房间事件。

### 8.4 结算页

- 展示胜者、排名/淘汰原因、局内得分、答对数、五行加成次数、新解锁冷门诗句。
- 新解锁诗句提供“生成国风插画”按钮；无资格时隐藏或解释资格条件。
- 操作：`再来一局`（房主创建同配置新房/或回等待区，建议新房以避免状态复用）、`返回首页`、`查看战绩`。

### 8.5 AI 诗句成画与详情

- **生成页**：展示不可编辑的诗句、作者、标题、来源；选择风格：免费默认风格、工笔/水墨/敦煌（会员能力，未确认权益时展示锁态）；展示水印/高清说明；提交前说明生成会调用后端 AI 服务，服务故障可稍后重试。
- **任务页**：排队、生成中、成功、失败四态；轮询 REST 或 Socket 推送均可，建议 REST 查询 + 短轮询；严禁前端直连即梦 API。
- **详情**：图片、诗句出处、生成风格、创建时间、下载、系统分享、删除。免费图下载/分享应保留水印；高质量无水印必须由后端按权益签发。

### 8.6 我的与收藏

- 顶部展示昵称、段位徽章、段位进度。统计卡显示总对局、胜利、答对、冷门解锁。
- Tab：插画收藏集、收藏诗句、收藏节气主题。空状态提供返回首页/开始对局的行动按钮。
- 收藏切换为幂等操作；删除插画为软删除，分享链接随之失效（建议，待确认）。

---

## 9. 实时飞花令详细规则

### 9.1 房间生命周期与状态机

`CREATED → WAITING → STARTING → PLAYING → SETTLING → FINISHED`；异常分支：`DISSOLVED`、`EXPIRED`。

- `CREATED`：创建完成，服务端写入配置和房主。
- `WAITING`：允许加入、离开、房主修改未锁定配置。
- `STARTING`：人数校验、玩家列表锁定、随机确定顺序，广播开局倒计时。
- `PLAYING`：按回合接受答案，服务端时间为权威。
- `SETTLING`：计算胜负、统计、解锁与记录，禁止提交。
- `FINISHED`：结算结果可查；建议保留 24 小时（待确认）。
- `DISSOLVED`：房主主动解散、等待超时或无法满足继续条件。
- `EXPIRED`：保留期结束后归档或清理实时状态。

### 9.2 开始、座位与回合

1. 人数必须为 2–8 且不超过创建配置；开局时至少 2 名在线成员。
2. 仅房主可开始。开始后成员名单、模式、关键词、时间和人数上限锁定。
3. 服务端使用安全随机数对存活玩家顺序洗牌，记录 `turnOrder` 和 `roundNo`。
4. 每回合指定一名当前玩家，生成递增的 `turnId` 和 `turnDeadlineAt`；客户端只按服务端时间显示倒计时。
5. 当前玩家可在截止前提交多次，但每次必须带唯一 `clientRequestId`；仅第一个被服务端顺序处理的有效提交可结束该回合。
6. 通过后记分并转到下一存活者；失败（超时、重复、错误）后淘汰该玩家，再从其后的下一存活者开始。

### 9.3 答案判定（安全规则）

1. 服务端先规范化输入：去首尾空格、统一全半角/常见标点、保留原始文本用于审计；不得擅自改写诗句语义。
2. 以当前模式、关键词、可用题库、审核通过状态、许可状态筛出候选诗句。
3. **精确题库命中优先**：规范化后的提交须命中候选诗句正文或经人工审核维护的等价别名；并满足当前关键词规则，才判定 `VALID`。
4. 若命中本局已成功使用的 `poem_line_id`，判定 `DUPLICATE` 并淘汰。
5. 若只达到编辑距离/局部片段等模糊条件，判定 `PENDING_REVIEW`：保存审计记录、提示“待收录核验，本局不计分”，并按错误淘汰；不得由 LLM 自动转正。
6. 未命中或不含主题关键词，判定 `INVALID` 并淘汰。
7. 禁止把大模型输出作为正误裁决；大模型如未来用于运营辅助，只能生成待人工审核候选，不进入实时判题链路。

### 9.4 计分与胜负

- 建议基础有效答案局内分：10 分（待确认）。
- 命中当前节气主五行相关意象标签时，基础分**翻倍**为 20 分（已确认“加分翻倍”，具体基础值待确认）。
- 重复、错误、超时均为 0 分且淘汰。
- 最后一名存活者胜；若一轮处理后无人存活，则按本局累计分高者胜；同分按最后一次有效答案时间更早者优先，仍同分则并列（建议，待确认）。
- 个人经验、段位变更须由结算事务统一写入，不能在客户端计算。

### 9.5 重连、离开、解散与异常

- Socket 断开后保留玩家席位，建议重连宽限 30 秒（待确认）；重连需使用房间成员令牌并恢复快照。
- 当前玩家在截止前未重连，按超时淘汰；非当前玩家断线不暂停全局。
- 等待区房主离开：优先转让给最早加入的在线成员；无其他成员则解散（建议，待确认）。
- 对战中房主离开不影响对局，房主权限转移仅影响后续房间操作。
- 服务端重启/进程故障：一期可将进行中房间标为 `ABORTED` 并结算为无效局，明确提示；生产环境后续需 Redis 消息队列/会话恢复。
- 等待区建议 15 分钟无人开局自动解散；对战超过最大允许时长应终止并标记异常（阈值待确认）。

---

## 10. 节气五行规则与算法伪代码

### 10.1 规则数据

- 节气表应为可运营配置，至少包含：名称、开始时间（中国时区）、所属季节、主五行、推荐关键词、推荐意象、描述。
- 示例：立春→春季/木→春、风、柳、芽；夏至→夏季/火→炎、日、荷；秋分→秋季/金→秋、月、霜；冬至→冬季/水→雪、寒、夜。
- 每个诗句拥有意象标签数组和七类结构化标签，且必须有审核状态与许可元数据。

### 10.2 伪代码（不可直接运行）

```text
输入：服务器当前时间 now（Asia/Shanghai）、已审核可分发的节气配置、已审核可用诗句题库

1. 在节气配置中找到开始时间不晚于 now 且最接近 now 的节气 currentTerm。
2. 读取 currentTerm.season 和 currentTerm.primaryElement。
3. 从 currentTerm.recommendedKeywords 选择推荐词：
   - 首页展示可返回全部推荐词；
   - 创建节气五行房时，优先推荐题库覆盖量足够的词；
   - 覆盖量不足的词不允许作为可计分主题。
4. 查询审核通过、许可可用、未下线的诗句；按关键词命中、节气/季节标签、意象标签计算候选集。
5. 对候选集按难度适配与热度做展示排序；排序仅影响推荐，不改变判题正确性。
6. 回答命中精确题库后：若诗句意象标签含 currentTerm.primaryElement 对应意象或明确 element 标签命中，则标记 elementBonus=true，基础分翻倍。
7. 返回：节气、季节、主五行、推荐关键词、最佳意象、候选数、版本号。
```

说明：节气计算优先使用经过验证的节气配置/算法服务。不要用简单固定公历日期替代真实节气边界。所有配置响应携带版本，保证一局内使用同一版本。

---

## 11. AI 生成、收藏、分享、权限与降级

1. **资格**：仅已解锁诗句或本局答对的冷门诗句可发起生成。服务端重新校验 `user_id + poem_line_id`，客户端传参不可作为资格依据。
2. **请求**：前端提交诗句 ID、风格、清晰度请求、幂等键；后端取受控诗句文案与风格模板，创建生成任务。
3. **适配器**：定义统一服务能力：提交任务、查询任务、取消任务（如供应商支持）。本地 `mock` 适配器生成固定/本地占位结果和可控延迟；即梦适配器仅在后端通过环境变量读取密钥。
4. **权益**：免费结果强制水印；高清、无水印、工笔/水墨/敦煌为会员能力接口。若会员系统未接入，返回明确的 `FEATURE_UNAVAILABLE` 或锁态，不伪造已购买状态。
5. **存储**：图片对象存储地址不得直接暴露长期写权限；下载/分享使用短期签名 URL 或后端代理（建议）。
6. **失败与重试**：供应商超时、内容安全拦截、配额不足、存储失败应区分错误码。相同幂等键重复调用返回同一任务，不重复扣次数。
7. **收藏与删除**：生成成功即写入插画收藏；用户可删除自己的作品。删除后客户端不可访问，后端按数据留存政策处理源文件。
8. **分享**：优先调用平台系统分享；不可用时提供下载和复制短链接。分享页只展示被允许公开的图片与诗句出处，不暴露用户统计/身份。

---

## 12. 数据模型（SQLite 一期）

通用约定：主键建议 `TEXT` UUID/ULID；时间使用 UTC ISO-8601 或 epoch 毫秒且统一；枚举以 `TEXT` 存储并由应用层校验；SQLite 开启外键约束。迁移必须版本化，避免直接改生产表。

| 表名 | 关键字段 | 关键约束 | 索引建议 |
|---|---|---|---|
| `users` | `id, auth_provider, provider_subject, nickname, avatar_url, rank, exp, created_at` | `(auth_provider, provider_subject)` 唯一；匿名身份可为空 subject 但必须有设备/会话映射 | `provider_subject`、`rank` |
| `user_sessions` | `id, user_id, refresh_token_hash, expires_at, revoked_at` | token 仅存 hash | `user_id`、`expires_at` |
| `solar_terms` | `id, name, start_at_cn, season, primary_element, description, config_version, active` | 名称+配置版本唯一；季节/五行枚举校验 | `start_at_cn`、`active` |
| `solar_term_keywords` | `id, solar_term_id, keyword, sort_order, enabled` | 同节气关键词唯一 | `(solar_term_id, enabled)` |
| `poems` | `id, title, author, dynasty, source_name, source_url, license_name, license_url, distribution_allowed, review_status` | 仅 `distribution_allowed=1` 且审核通过才可上线 | `(review_status, distribution_allowed)` |
| `poem_lines` | `id, poem_id, line_no, content, normalized_content, is_rare, review_status, source_locator` | `(poem_id,line_no)` 唯一；规范化文本不可为空 | `normalized_content` 唯一性需结合业务审查；`is_rare,review_status` |
| `tags` | `id, type, name, normalized_name, active` | `type` 仅七类标签；`(type, normalized_name)` 唯一 | `(type, active)` |
| `poem_line_tags` | `poem_line_id, tag_id, confidence, reviewed_by` | 联合主键；仅审核标签用于判分 | `tag_id`、`poem_line_id` |
| `poem_line_aliases` | `id, poem_line_id, normalized_alias, review_status` | 仅人工审核 alias 可精确命中 | `normalized_alias,review_status` |
| `daily_themes` | `date_cn, solar_term_id, keyword_snapshot_json, config_version` | `date_cn` 唯一 | `solar_term_id` |
| `rooms` | `id, code, host_user_id, mode, status, keyword_snapshot_json, term_snapshot_json, time_limit_sec, max_players, config_version, created_at` | `code` 唯一；人数 2–8；时间仅 10/15/20 | `status,created_at`、`host_user_id` |
| `room_members` | `id, room_id, user_id, seat_no, role, alive, connection_state, joined_at, eliminated_at, eliminate_reason` | `(room_id,user_id)` 唯一；`seat_no` 唯一 | `(room_id,alive)`、`user_id` |
| `game_turns` | `id, room_id, turn_no, round_no, player_id, deadline_at, status, submitted_at` | `(room_id,turn_no)` 唯一 | `(room_id,status)` |
| `answer_submissions` | `id, room_id, turn_id, user_id, client_request_id, raw_text, normalized_text, result, matched_line_id, reason, created_at` | `(user_id,client_request_id)` 唯一；每回合处理顺序可锁定 | `(room_id,turn_id)`、`matched_line_id` |
| `room_used_lines` | `room_id, poem_line_id, submission_id` | `(room_id,poem_line_id)` 唯一，防重复竞态 | `submission_id` |
| `game_results` | `id, room_id, user_id, placement, score, correct_count, element_bonus_count, is_winner` | `(room_id,user_id)` 唯一 | `user_id, created_at` |
| `user_poem_unlocks` | `user_id, poem_line_id, unlock_reason, unlocked_at` | 联合唯一，重复解锁幂等 | `user_id` |
| `user_favorites` | `id, user_id, target_type, target_id, created_at` | `(user_id,target_type,target_id)` 唯一 | `user_id,target_type` |
| `art_generation_tasks` | `id, user_id, poem_line_id, provider, style, quality, status, idempotency_key, provider_task_id, error_code, created_at` | `(user_id,idempotency_key)` 唯一 | `status,created_at`、`provider_task_id` |
| `artworks` | `id, task_id, user_id, poem_line_id, storage_key, watermark, visibility, deleted_at` | `task_id` 唯一 | `user_id,deleted_at` |
| `audit_events` | `id, actor_type, actor_id, action, entity_type, entity_id, payload_json, created_at` | 敏感操作必记审计 | `entity_type,entity_id` |

数据内容最小字段要求：每条诗句至少保存正文、作者、朝代、标题、关键词、七类标签关联、来源、许可、是否冷门、意象、审核状态；作者/朝代/标题可经由 `poems` 关联读取，但对外 API 必须完整返回。

---

## 13. REST API 规格建议

通用：JSON；认证使用 `Authorization: Bearer <access_token>` 或临时会话令牌；成功响应建议 `{ "data": ..., "requestId": "..." }`；失败响应 `{ "error": { "code": "...", "message": "...", "details": {} }, "requestId": "..." }`。所有会改变状态的请求接受 `Idempotency-Key` 或 body 中 `clientRequestId`。

| Method / Path | 请求要点 | 成功响应要点 | 错误码 |
|---|---|---|---|
| `POST /v1/auth/anonymous` | 设备/临时会话信息 | user、accessToken、expiresAt | `INVALID_REQUEST` |
| `GET /v1/daily-theme` | 可选日期（仅运营调试） | 日期、节气、季节、五行、关键词、意象、配置版本 | `THEME_NOT_FOUND` |
| `GET /v1/solar-terms/:id` | 无 | 节气详情与推荐词 | `NOT_FOUND` |
| `GET /v1/rooms/recommendations` | `mode, keyword?` | 可创建关键词、题库覆盖摘要 | `NO_ELIGIBLE_CONTENT` |
| `POST /v1/rooms` | `mode, keywords, timeLimitSec, maxPlayers` | roomId、code、memberToken、状态 | `INVALID_ROOM_CONFIG`,`NO_ELIGIBLE_CONTENT` |
| `GET /v1/rooms/:id` | 成员令牌/认证 | 房间快照、成员、当前回合（按权限脱敏） | `ROOM_NOT_FOUND`,`NOT_ROOM_MEMBER` |
| `POST /v1/rooms/:id/join` | `code, clientRequestId` | 成员令牌、房间快照 | `ROOM_FULL`,`ROOM_NOT_JOINABLE`,`INVALID_ROOM_CODE` |
| `POST /v1/rooms/:id/leave` | `clientRequestId` | 最新房间状态 | `ROOM_STATE_CONFLICT` |
| `POST /v1/rooms/:id/start` | `clientRequestId` | 开局确认/开始时间 | `NOT_HOST`,`MIN_PLAYERS_NOT_MET`,`ROOM_STATE_CONFLICT` |
| `GET /v1/rooms/:id/result` | 成员身份 | 结算、个人结果、解锁列表 | `RESULT_NOT_READY` |
| `GET /v1/me/profile` | 无 | 段位、经验、统计 | `UNAUTHORIZED` |
| `GET /v1/me/records` | 分页 | 对局记录 | `INVALID_CURSOR` |
| `GET /v1/me/favorites` | `type,cursor` | 收藏列表 | `INVALID_CURSOR` |
| `PUT /v1/me/favorites/:type/:id` | 幂等键 | 收藏状态 | `TARGET_NOT_FOUND` |
| `DELETE /v1/me/favorites/:type/:id` | 幂等键 | 已取消收藏 | `TARGET_NOT_FOUND` |
| `POST /v1/art-generation-tasks` | `poemLineId, style, quality, clientRequestId` | taskId、status、是否水印 | `NOT_ELIGIBLE`,`FEATURE_UNAVAILABLE`,`QUOTA_EXCEEDED` |
| `GET /v1/art-generation-tasks/:id` | 无 | 状态、失败原因、成功作品 ID | `NOT_TASK_OWNER` |
| `GET /v1/artworks/:id` | 无/分享 token | 作品元信息、受控访问 URL | `NOT_FOUND`,`ARTWORK_DELETED` |
| `DELETE /v1/artworks/:id` | 幂等键 | 删除确认 | `NOT_ARTWORK_OWNER` |

推荐错误码补充：`UNAUTHORIZED`、`FORBIDDEN`、`VALIDATION_ERROR`、`RATE_LIMITED`、`IDEMPOTENCY_CONFLICT`、`ROOM_EXPIRED`、`TURN_NOT_ACTIVE`、`TURN_DEADLINE_PASSED`、`ANSWER_PENDING_REVIEW`、`AI_PROVIDER_UNAVAILABLE`、`CONTENT_POLICY_BLOCKED`、`INTERNAL_ERROR`。

---

## 14. Socket.IO 事件契约

连接命名空间建议 `/game`。握手携带 access token 或 room member token；所有事件包含 `requestId`，服务端事件包含 `eventId`、`serverTime`、`roomVersion`。客户端按 `roomVersion` 忽略旧事件，必要时调用房间快照恢复。

| 方向 / 事件 | 字段要点 | 服务端行为与幂等 |
|---|---|---|
| C→S `room:subscribe` | `roomId, memberToken, requestId` | 校验成员后加入 socket room；重复订阅返回同一快照 |
| S→C `room:snapshot` | room、members、phase、currentTurn、self | 全量恢复事件；不得包含他人私密令牌 |
| C→S `room:ready` | `roomId, requestId` | 一期可仅记录准备态；重复幂等 |
| C→S `room:start` | `roomId, clientRequestId` | 仅房主；使用请求 ID 去重，成功广播开局 |
| S→C `game:started` | `startedAt, turnOrderSummary, themeSnapshot` | 所有人收到同一配置快照 |
| S→C `turn:started` | `turnId, turnNo, playerId, deadlineAt, timeLimitSec` | 服务端时间权威；仅展示当前玩家身份 |
| C→S `answer:submit` | `roomId, turnId, text, clientRequestId` | 原子校验 turn、玩家、截止时间、重复；同 key 返回原结果 |
| S→C `answer:result` | `turnId, userId, result, scoreDelta, matchedLineSummary?, reason` | 对 `PENDING_REVIEW` 不下发未审核全文匹配候选 |
| S→C `player:eliminated` | `userId, reason, rarePoemCard?` | 淘汰后不再允许提交 |
| S→C `turn:ended` | `turnId, nextPlayerId?, usedCount` | 仅在结果持久化后广播 |
| S→C `game:finished` | `roomId, results, finishedAt` | 至多一次最终结算；客户端重复接收可覆盖显示 |
| C→S `room:leave` | `roomId, clientRequestId` | 幂等离开；广播成员变化 |
| S→C `room:member-changed` | member、reason | 等待区实时更新 |
| S→C `room:dissolved` | `reason, redirectPath` | 终止本房间交互 |
| S→C `system:error` | `requestId?, code, message, recoverable` | 可恢复错误引导重试/拉快照 |
| C→S `room:resync` | `roomId,lastRoomVersion` | 返回最新 `room:snapshot`，幂等 |

防竞态关键点：答案提交必须在数据库事务内校验当前 `turnId`、截止时间和 `room_used_lines` 唯一约束；不得依赖客户端“已提交”状态。Socket 重发、断线重连、HTTP/Socket 双通道重复调用均通过请求 ID/唯一约束吸收。

---

## 15. 前端组件、目录与设计系统建议

### 15.1 目录建议

```text
src/
  api/                 REST 客户端、错误映射
  socket/              Socket 连接、事件订阅、重连与版本控制
  pages/               Home、RoomCreate、Room、Result、Art、Profile、Collections
  components/
    theme/             SolarTermCard、ThemeKeywordChips
    game/              PlayerSeat、DrumAnimation、TurnTimer、AnswerComposer、RarePoemCard
    art/               ArtStylePicker、GenerationStatus、ArtworkCard
    common/            EmptyState、ErrorState、NetworkBanner、PermissionSheet
  stores/              auth、room、profile、theme
  composables/         useSpeechRecognition、useRoomSocket、useIdempotentRequest
  types/               API、Socket、领域枚举
  assets/              非版权风险自制纹样与图标
```

### 15.2 组件边界

- 前端负责展示、输入校验、倒计时视觉、语音识别文本填入、请求重试与状态恢复。
- 后端负责身份、权限、题库筛选、答案正误、计分、淘汰、回合推进、解锁、权益、生成任务和审计。
- 前端不得存储 AI 密钥、完整题库判分逻辑、可被篡改的战绩结算逻辑；不得将浏览器语音结果直接视为正确答案。

### 15.3 设计系统

- 风格为“克制国风”：宣纸暖白背景、墨色正文、朱砂/青绿作为有限强调色；国风装饰不得降低文字对比度。
- 正文字号建议至少 16px，关键倒计时至少 28px；点击热区至少 44×44px。
- 使用 Vant UI 作为基础交互组件，定制 token 而非大面积替换可访问行为。
- 动画应支持 `prefers-reduced-motion`；击鼓传花动画不应阻塞答题、不得依赖动画结束开始计时。
- 所有图标具备文字标签或 `aria-label`；颜色不能是唯一状态提示；错误信息使用清晰文字与可重试动作。
- 移动优先，安全区适配，微信内置浏览器中避免依赖不稳定 API；弱网优先展示最近服务端快照。

---

## 16. 状态设计

| 场景 | 界面与行动 |
|---|---|
| 首屏加载 | 节气卡/任务卡骨架屏，不展示伪数据 |
| 空收藏/空战绩 | 解释价值＋“开始一局飞花令”按钮 |
| 网络断开 | 顶部弱网条；禁用提交；自动重连后拉取 `room:snapshot` |
| 接口错误 | 保留已加载内容，显示错误卡与重试；不要清空用户输入 |
| 房间已满 | 显示“雅席已满”，提供返回首页/输入其他邀请码 |
| 房间不可加入/已结束 | 说明状态，跳转首页 |
| 当前非答题者 | 输入区只读，显示“静候 {昵称} 作答” |
| 答案重复 | 结果弹层明确“本局已有人使用此句”，展示淘汰和科普卡 |
| 答案待审核 | 明确“未收录为可判定答案，本局不计分”；不得提示可绕过技巧 |
| 语音权限未授予 | 解释用途，允许继续文字输入；拒绝后不反复强弹 |
| 浏览器不支持语音 | 隐藏/禁用语音按钮，说明可用文字作答 |
| AI 排队/生成中 | 显示任务状态，可离开页面后在收藏集查看 |
| AI 失败 | 区分可重试/不可重试；不重复扣配额；保留诗句与重试入口 |
| 会员能力不可用 | 显示锁态和“功能即将开放/请使用免费带水印生成”，不出现支付按钮 |
| 无权限访问作品 | 说明作品不存在、已删除或无访问权限，不泄露拥有者信息 |

---

## 17. 权限、隐私与内容合规

1. 最小化收集：一期只收集运行所需身份、昵称/头像（如授权）、对局和收藏数据；不要为语音功能默认采集、上传或保存音频。
2. 语音权限需在用户点击语音按钮后请求，并明确说明浏览器识别用途；若未来需上传音频，必须增加独立、明确、可撤回同意与留存期限说明。
3. AI 密钥、供应商凭据、对象存储写权限仅在后端环境变量/密钥管理服务中；日志不得记录 token、密钥、原始敏感凭据。
4. 诗词内容必须保留 `source_name/source_url/license_name/license_url/distribution_allowed/review_status`。上线仅使用许可允许分发、且经过项目审查的内容；“仓库公开”不是版权结论。
5. 建立内容下线能力：发现许可、事实、敏感内容问题时，按诗句/作品立即下线并使判题候选失效；保留审计记录。
6. AI 图片需经过供应商内容安全能力与本产品策略；用户应可删除自己生成作品。分享默认不公开用户隐私资料。
7. API 限流：创建房间、提交答案、发起生成、分享链接均按用户/IP/设备多维限流；记录异常频率，不以客户端时间做风控依据。
8. 未成年人场景如面向亲子用户，需另行确认年龄提示、监护人同意、数据处理与内容分级要求；一期不应默认宣称已满足所有未成年人法规。

---

## 18. 埋点事件与指标口径

所有事件含：`event_id`、`event_time_server_or_client`、`user_id/anonymous_id`、`session_id`、`page`、`app_version`、`network_type`；对局相关含 `room_id`、`mode`、`solar_term`、`element`、`config_version`。不得把原始音频作为埋点字段。

| 事件 | 触发时机 | 核心属性 |
|---|---|---|
| `home_view` | 首页展示 | daily_theme_id |
| `game_entry_click` | 点击玩法入口 | mode |
| `room_create_submit` / `room_created` | 提交/成功创建 | mode,time_limit,max_players,keyword_type |
| `room_join_attempt` / `room_joined` | 加入尝试/成功 | room_id, result_code |
| `game_started` | 服务端确认开局 | player_count,mode |
| `answer_submitted` | 提交已被服务端接收 | turn_id,input_method,text_length |
| `answer_judged` | 服务端判定 | result,reason,element_bonus,latency_ms |
| `player_eliminated` | 淘汰 | reason,turn_no |
| `game_finished` | 结算 | placement,score,correct_count,abnormal_flag |
| `rare_poem_unlocked` | 解锁 | poem_line_id,unlock_reason |
| `art_generate_requested` / `art_generate_result` | 发起/结果 | style,quality,status,error_code |
| `favorite_changed` | 收藏/取消收藏 | target_type,action |
| `speech_permission_result` | 权限结果 | granted, browser_support |
| `socket_reconnect` / `room_resync` | 重连/恢复 | attempts,room_version_gap |

指标口径：活跃用户按去重 `user_id/anonymous_id`；对局“开始”以服务端 `game_started` 为准，“完成”以 `game_finished` 为准；答案有效率只统计服务器最终 `VALID`；AI 成功率只统计最终任务状态，不把客户端展示成功当事实。

---

## 19. 验收标准

1. **当日主题**：Given 中国时区某日有有效节气配置，When 请求首页主题，Then 返回对应节气、季节、主五行、至少一个关键词和意象，并携带配置版本。
2. **创建限制**：Given 用户设置人数 1 或 9，When 创建房间，Then 服务端返回配置错误且不创建房间。
3. **入房上限**：Given 房间已达到 maxPlayers，When 新用户加入，Then 返回 `ROOM_FULL` 且成员数不增加。
4. **开局权限**：Given 非房主用户，When 调用开始，Then 返回 `NOT_HOST`，房间仍为等待状态。
5. **回合权威**：Given 回合截止时间已过，When 当前玩家发送答案，Then 服务端判为超时/拒绝，不以客户端倒计时为依据。
6. **精确命中**：Given 已审核题库存在符合关键词的完整诗句，When 当前玩家提交其规范化等价文本，Then 判定 `VALID` 并推进回合。
7. **重复淘汰**：Given 本局已有成功使用的诗句，When 另一玩家提交同一诗句，Then 判定 `DUPLICATE`、得分 0、该玩家淘汰。
8. **模糊安全**：Given 输入仅与题库诗句近似但不精确命中，When 提交，Then 记录 `PENDING_REVIEW`、本局不计分并淘汰；系统不调用 LLM 作为裁决。
9. **五行加成**：Given 有效答案的已审核意象标签命中当前主五行，When 判分，Then `elementBonus=true` 且分数为基础分两倍。
10. **结算唯一性**：Given 同一结算事件被重复投递，When 服务端处理，Then 每个用户仅有一条该房间结果、经验仅增加一次。
11. **重连**：Given 成员短暂断线后在宽限期内使用有效成员令牌重连，When 订阅房间，Then 收到最新快照且不能重复占席。
12. **语音隐私**：Given 用户未点击并授权语音，When 进入房间，Then 产品不会请求麦克风权限或上传音频。
13. **AI 权限**：Given 用户未解锁目标冷门诗句，When 发起成图，Then 服务端返回 `NOT_ELIGIBLE` 且不创建任务。
14. **AI 密钥**：Given 前端生产构建产物，When 检索配置，Then 不包含即梦 API 密钥或供应商私密 token。
15. **免费水印**：Given 免费能力生成成功，When 获取作品，Then 作品标记 `watermark=true`，下载资源保留水印。
16. **来源合规**：Given 诗句 `distribution_allowed=false` 或审核未通过，When 主题推荐/判题查询，Then 该诗句不被返回或判为正确答案。
17. **无障碍**：Given 用户启用减少动态效果，When 进入实时房间，Then 击鼓动画降级且不影响回合信息阅读。

---

## 20. 30 天开发排期（按可交付物）

> 资源假设待确认：至少 1 前端、1 后端、1 产品/设计支持、1 测试/兼任测试；内容审核与 AI 服务账号为外部依赖。排期以工作日计，可并行。

| 时间 | 可交付物 | 完成定义 |
|---|---|---|
| Day 1–3 | 项目基线与领域设计 | 仓库、环境分层、SQLite migration 基线、枚举、API/Socket 契约评审、数据许可清单模板 |
| Day 4–6 | 文化底座与日主题 | 节气配置、诗句/标签/许可导入链路、审核状态过滤、`daily-theme` API、首页静态/动态骨架 |
| Day 7–10 | 身份、首页、建房入房 | 匿名会话、首页、创建/加入/等待区、房间配置校验、基础埋点 |
| Day 11–15 | 实时对战主链路 | Socket 认证订阅、房间状态机、回合计时、文字提交、精确命中/重复/超时淘汰、结算快照 |
| Day 16–18 | 规则完善与韧性 | 五行倍分、冷门科普卡、重连/重同步、事务幂等、限流与异常状态 |
| Day 19–21 | 战绩与收藏 | 个人中心、段位/统计、诗句/主题收藏、结果页、基础验收用例 |
| Day 22–24 | AI 成画能力 | 服务适配器接口、mock 模式、任务状态、资格校验、收藏集、下载/分享降级、水印逻辑 |
| Day 25–26 | 语音与移动端体验 | 浏览器语音识别文本填入、明确同意提示、权限降级、微信浏览器/安全区适配 |
| Day 27–28 | 联调与质量 | 压测 2–8 人房、断线与重复提交测试、数据许可抽检、错误码与埋点核验 |
| Day 29 | UAT 与修复 | 按第 19 节验收，修复 P0/P1，生成已知问题清单 |
| Day 30 | MVP 发布包 | 部署说明、环境变量清单、数据库迁移、回滚方案、内容来源清单、监控看板与发布记录 |

---

## 21. 风险、依赖与开放问题

| 风险/依赖 | 影响 | 缓解措施 |
|---|---|---|
| 诗词来源许可不清 | 内容下架、法律风险 | 建立逐条许可元数据、分发许可审查、可快速下线机制；不因 GitHub 开源标签放宽审查 |
| 题库覆盖不足 | 自定义关键词无可玩性 | 创建前查询覆盖量；仅开放可判分关键词；持续运营补库 |
| 模糊判题争议 | 用户体验受损/作弊 | 精确题库优先、待审核不计分、提供明确文案与审核后台队列 |
| Socket 单进程扩展性 | 并发房间不稳定 | 一期限制规模；后续引入 Redis message queue、粘性会话、分布式锁 |
| 弱网/微信兼容 | 回合误判感知 | 服务端截止时间权威、重同步快照、客户端只做视觉倒计时 |
| 浏览器语音能力差异 | 语音不可用 | 文本主路径完整；按支持检测降级；不承诺所有浏览器可用 |
| AI 供应商可用性/审核 | 成图失败或延迟 | mock 适配器、异步任务、可重试分类、供应商降级提示 |
| AI 版权与风格风险 | 合规风险 | 采用供应商合规条款；风格命名/提示词审核；保留任务审计 |
| 刷分/脚本提交 | 段位失真 | 服务端判题、请求幂等、限流、异常检测、不可预测回合与题库筛选 |
| 会员未定 | 功能边界混乱 | 仅保留权益判定接口和锁态，不实现支付或承诺权益细节 |

---

## 22. 给 AI Coding 工具的实施提示与分阶段任务清单

### 22.1 实施原则

1. 先建立领域模型、迁移、状态机和契约测试，再做视觉页面；不要把规则散落在 Vue 组件中。
2. 用 TypeScript 类型和 Python schema/DTO 共享同一枚举语义；REST 与 Socket 事件均建立版本化契约文档。
3. 所有对战状态以服务端为单一事实来源。客户端可预测动画，但不得预测正误、得分、淘汰或最终胜负。
4. 答案判题只查询审核通过且许可可分发的确定性题库；禁用 LLM 判题路径。模糊文本只进审核记录。
5. 所有写操作实现幂等：房间创建、加入、开局、答案提交、收藏、生成任务、删除操作均需请求 ID/唯一约束。
6. 不在任何前端配置、源码、日志、错误响应中出现 AI 私钥；以环境变量注入后端，并为 mock/真实适配器提供显式开关。
7. 使用真实节气数据或经验证算法，不使用简单按月份映射；对局开始时固化主题配置快照。
8. 先确保文本输入可完整玩通，再接语音；语音仅负责把识别文本放入输入框，必须由用户确认提交。
9. 所有内容输出遵循可访问性与移动优先标准；减少动画设置不能影响游戏计时与信息可读性。
10. 为关键状态机、判题、并发重复提交、重连、许可过滤、AI 资格校验写自动化测试；不要只测试页面截图。

### 22.2 建议分阶段任务

**阶段 A：基础与数据（P0）**
- 初始化 Vue3/TS/Vite/Vant 与 Flask/Flask-SocketIO 工程，配置开发、测试、生产环境变量边界。
- 创建 SQLite 迁移及第 12 节核心表；实现数据导入校验，导入时强制来源、许可、审核字段齐全。
- 实现节气主题服务、题库筛选服务、答案规范化与精确匹配服务；为许可/审核过滤写单测。

**阶段 B：身份与静态体验（P0）**
- 实现匿名会话及安全 token 生命周期。
- 实现首页、节气详情、创建/加入房间和等待区，接入 REST 错误态、骨架屏和空态。
- 实现日主题和系统推荐关键词接口，禁止无题库覆盖主题直接开局。

**阶段 C：实时游戏（P0）**
- 实现 Socket 鉴权、订阅、房间快照、版本号与断线重同步。
- 实现房间/回合状态机、服务端倒计时、原子答案提交、重复唯一约束、淘汰和结算。
- 实现经典模式与节气五行模式差异；严格验证五行意象翻倍。
- 完成多客户端并发测试：同一答案、同一回合双提交、重复 event、截止边界提交。

**阶段 D：个人沉淀与 AI（P1）**
- 实现战绩、段位展示（阈值配置化）、解锁、收藏。
- 定义 AI 适配器，先接 mock；实现任务状态、资格/配额/权益接口、水印标记和作品删除。
- 真实即梦接入仅在密钥与供应商审核完成后启用；保留一键回退 mock/关闭生成的开关。

**阶段 E：体验、合规与上线（P0）**
- 接入浏览器语音识别降级与同意提示；确认不上传音频的网络请求证据。
- 完成埋点、限流、审计、错误映射、可访问性检查、微信浏览器和弱网测试。
- 执行第 19 节验收并输出：部署手册、迁移手册、内容来源与许可清单、已知问题、回滚方案。

### 22.3 明确禁止的实现捷径

- 禁止把答案正误交给任意 LLM 或把“语义相近”自动计为正确。
- 禁止客户端自行计算最终得分、淘汰、主题日期或段位。
- 禁止默认录音、上传音频，或在未同意时请求麦克风。
- 禁止将 `chinese-poetry` 或其他公开仓库直接全量上线而不记录来源/许可/审核状态。
- 禁止在一期加入支付、社群广场、景点、AR、美食、复杂 UGC 等非范围功能。
- 禁止前端直连即梦 API 或暴露任何供应商密钥。

---

## 附：关键领域枚举建议

- `mode`：`CLASSIC`、`SOLAR_TERM_ELEMENT`
- `room_status`：`CREATED`、`WAITING`、`STARTING`、`PLAYING`、`SETTLING`、`FINISHED`、`DISSOLVED`、`EXPIRED`、`ABORTED`
- `answer_result`：`VALID`、`DUPLICATE`、`INVALID`、`PENDING_REVIEW`、`LATE`、`NOT_YOUR_TURN`
- `eliminate_reason`：`TIMEOUT`、`DUPLICATE`、`INVALID`、`PENDING_REVIEW`、`DISCONNECT_TIMEOUT`
- `review_status`：`DRAFT`、`PENDING`、`APPROVED`、`REJECTED`、`OFFLINE`
- `art_task_status`：`QUEUED`、`PROCESSING`、`SUCCEEDED`、`FAILED`、`CANCELLED`
- `rank`：`萌新`、`秀才`、`举人`、`进士`、`翰林`、`雅客`

> 本 PRD 的未确认数值（如经验、配额、会员权益、超时宽限与留存期限）应配置化，并在产品确认后写入运营配置与验收用例；上线前不得将建议值包装为已承诺规则。
