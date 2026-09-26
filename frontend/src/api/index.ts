import axios, { AxiosError, AxiosResponse } from 'axios'

const baseURL = '/api'

const client = axios.create({
  baseURL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

// 请求拦截器：添加 token
client.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：自动 unwrap 数据层
client.interceptors.response.use(
  (res: AxiosResponse) => {
    // 如果返回的是 {data: ...} 格式，unwrap 到 data 层
    // 如果返回的是 {success: ...} 格式，直接返回
    if (res.data && typeof res.data === 'object' && 'data' in res.data) {
      return res.data
    }
    return res.data
  },
  (err: AxiosError) => {
    const res = err.response
    if (res?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.reload()
    }
    return Promise.reject(err)
  }
)

// ── 工具：Flask 统一外层 { data: {...} }，所以取用时 res.data.data ──
// 后端返回 {success, ...} 或 {data: {...}}, 统一 unwrap
type FlaskData<T> = { data: T }
function wrap<T>(r: AxiosResponse): any {
  return r.data?.data ?? r.data
}

export const api = {
  // ── 认证 ─────────────────────────────────
  anonymousLogin: () =>
    client.post('/v1/auth/anonymous', {}),

  // 邮箱注册
  authRegister: (email: string, password: string, nickname?: string) =>
    client.post<FlaskData<any>>('/v1/auth/register', { email, password, nickname }),

  // 邮箱登录
  authLogin: (email: string, password: string) =>
    client.post<FlaskData<any>>('/v1/auth/login', { email, password }),

  // ── 统计 ─────────────────────────────────
  getMyStats: () =>
    client.get<FlaskData<any>>('/v1/me/stats'),

  // 管理统计（需 admin token）
  getAdminStats: () =>
    client.get<FlaskData<any>>('/v1/admin/stats'),

  // 管理员用户列表
  getAdminUsers: (params?: { page?: number; page_size?: number; role?: string }) =>
    client.get<FlaskData<any>>('/v1/admin/users', { params }),

  // 设置用户角色
  setUserRole: (userId: string, role: string) =>
    client.post<FlaskData<any>>(`/v1/admin/users/${userId}/role`, { role }),

  // ── 每日主题 ─────────────────────────────
  getDailyTheme: (date?: string) =>
    client.get<FlaskData<any>>('/v1/daily-theme', { params: { date } }),
  // 返回 data.data: { date, solar_term, keywords, imagery, ... }

  // ── 房间 ─────────────────────────────────
  createRoom: (data: {
    mode: string
    keywords: string[]
    time_limit_sec: number
    max_players: number
  }) => client.post<FlaskData<any>>('/v1/rooms', data),
  // 返回 data.data: { room_id, code, keywords, ... }

  getRoom: (roomId: string) =>
    client.get<FlaskData<any>>(`/v1/rooms/${roomId}`),
  // 返回 data.data: { room_id, members, status, ... }

  joinRoom: (roomId: string, code?: string) =>
    client.post<FlaskData<any>>(`/v1/rooms/${roomId}/join`, { code }),
  // 返回 data.data: { room_id, ... }

  leaveRoom: (roomId: string) =>
    client.post<FlaskData<any>>(`/v1/rooms/${roomId}/leave`),

  startRoom: (roomId: string) =>
    client.post<FlaskData<any>>(`/v1/rooms/${roomId}/start`),

  getRoomByCode: (code: string) =>
    client.get<FlaskData<any>>('/v1/rooms/by-code', { params: { code } }),

  getRoomResult: (roomId: string) =>
    client.get<FlaskData<any>>(`/v1/rooms/${roomId}/result`),
  // 返回 data.data: { room_id, results: [...] }

  // ── 个人中心 ─────────────────────────────
  getProfile: () =>
    client.get<FlaskData<any>>('/v1/me/profile'),

  getRecords: (limit = 20, offset = 0) =>
    client.get<FlaskData<any>>('/v1/me/records', { params: { limit, offset } }),

  getFavorites: (type?: string) =>
    client.get<FlaskData<any>>('/v1/me/favorites', { params: { type } }),

  addFavorite: (type: string, id: string) =>
    client.put<FlaskData<any>>(`/v1/me/favorites/${type}/${id}`),

  removeFavorite: (type: string, id: string) =>
    client.delete<FlaskData<any>>(`/v1/me/favorites/${type}/${id}`),

  // ── 诗词 ─────────────────────────────────
  getPoems: (keyword?: string, limit = 20) =>
    client.get<FlaskData<any>>('/v1/poems', { params: { keyword, limit } }),

  getPoemDetail: (poemId: string) =>
    client.get<FlaskData<any>>(`/v1/poems/${poemId}`),

  // 色·诗匹配（用关键字从诗库搜索）
  getColorPoems: (keyword: string, limit = 5) =>
    client.get<FlaskData<any>>('/v1/poems', { params: { keyword, limit } }),
  // 返回 data.data: { poems: [...] }

  // 收藏（别名，保持命名一致）
  deleteFavorite: (type: string, id: string) =>
    client.delete<FlaskData<any>>(`/v1/me/favorites/${type}/${id}`),

  // ── 节气 ─────────────────────────────────
  getSolarTerms: () =>
    client.get<FlaskData<any>>('/v1/solar-terms'),

  getSolarTermDetail: (termId: string) =>
    client.get<FlaskData<any>>(`/v1/solar-terms/${termId}`),

  // ── 徽章 ─────────────────────────────────
  getBadgeList: () =>
    client.get<FlaskData<any>>('/v1/badges'),

  getUserBadges: (userId?: string) =>
    client.get<FlaskData<any>>(`/v1/users/${userId}/badges`),

  // ── 诗词品鉴 ─────────────────────────────
  getExploreFilters: () =>
    client.get<FlaskData<{ dynasties: string[]; imagery: string[] }>>('/v1/explore/filters'),
  // 返回 data.data: { dynasties: [...], imagery: [...] }

  getExplorePoems: (params: {
    dynasty?: string
    author?: string
    tag_type?: string
    tag_name?: string
    page?: number
    page_size?: number
  }) => client.get<FlaskData<{
    poems: any[]
    total: number
    page: number
    page_size: number
    total_pages: number
  }>>('/v1/explore/poems', { params }),
  // 返回 data.data: { poems: [...], total, ... }

  getExploreDaily: () =>
    client.get<FlaskData<{ poems: any[]; solar_term: any }>>('/v1/explore/daily'),
  // 返回 data.data: { poems: [...], solar_term: {...} }

  // ── 飞花令 Solo ─────────────────────────
  getPracticeLines: (params: { keyword?: string[]; limit?: number }) =>
    client.get<FlaskData<any>>('/v1/solo/poems', { params: { keyword: params.keyword?.[0], limit: params.limit } }),

  getPracticeKeywords: () =>
    client.get<FlaskData<any>>('/v1/solo/keywords'),

  practicePeek: (params: { keyword: string; page?: number; page_size?: number }) =>
    client.get<FlaskData<any>>('/v1/solo/poems', { params: { keyword: params.keyword, limit: params.page_size || 10 } }),

  practiceValidate: (data: { line: string; keyword: string }) =>
    client.post<FlaskData<any>>('/v1/solo/validate', { answer: data.line, keyword: data.keyword }),

  // ── AI 解读 ─────────────────────────────
  aiPoemExplain: (data: {
    poem: string
    source: string
    title?: string
    author?: string
    dynasty?: string
    poem_id?: string
    colorName?: string
    note?: string
    user_query?: string
  }) => client.post<FlaskData<any>>('/v1/ai/poem-explain', data, { timeout: 60000 }),

  // ── 诗人雅集（角色卡 + 角色扮演对话）──────
  getPoetCards: () =>
    client.get<FlaskData<any>>('/v1/poet/cards'),

  poetChat: (data: { poet_id: string; messages: { role: string; content: string }[] }) =>
    client.post<FlaskData<any>>('/v1/poet/chat', data, { timeout: 60000 }),

  poetRoundtable: (data: { poet_ids: string[]; topic?: string; rounds?: number }) =>
    client.post<FlaskData<any>>('/v1/poet/roundtable', data, { timeout: 120000 }),

  poetFeihualing: (data: { poet_ids: string[]; keyword: string; exclude_lines?: string[] }) =>
    client.post<FlaskData<any>>('/v1/poet/feihualing', data, { timeout: 120000 }),

  // ── 静心诗境 ───────────────────────────
  getAmbientPoem: () =>
    client.get<FlaskData<any>>('/v1/poem/ambient'),
  // 返回 data.data: { poem_id, title, author, dynasty, lines: string[], intro, solar_term }

  // ── 诗签筒 ─────────────────────────────
  getFortune: (mood: string) =>
    client.get<FlaskData<any>>('/v1/poem/fortune', { params: { mood } }),
  // 返回 data.data: { poem_id, title, author, dynasty, line, mood }

  // ── 私人诗摘 ───────────────────────────
  getPoemNotes: () =>
    client.get<FlaskData<any>>('/v1/poem/notes'),
  // 返回 data.data: { notes: [{ id, poem_id, line_text, poem_title, poet_name, note, mood_tag, created_at }] }

  addPoemNote: (data: {
    poem_id?: string
    line_text: string
    poem_title: string
    poet_name: string
    note: string
    mood_tag: string
  }) =>
    client.post<FlaskData<any>>('/v1/poem/notes', data),

  updatePoemNote: (noteId: string, data: { note: string; mood_tag: string }) =>
    client.put<FlaskData<any>>(`/v1/poem/notes/${noteId}`, data),

  deletePoemNote: (noteId: string) =>
    client.delete<FlaskData<any>>(`/v1/poem/notes/${noteId}`),

  // ── 题库闯关 ───────────────────────────
  getChallengeDimensions: () =>
    client.get<FlaskData<any>>('/v1/challenge/dimensions'),
  // 返回 data.data: { dynasties, factions, themes, forms }

  startChallenge: (data: {
    dynasty?: string
    faction?: string
    theme?: string
    form?: string
    count?: number
  }) =>
    client.post<FlaskData<any>>('/v1/challenge/start', data),

  submitChallenge: (data: { session_id: string; answers: { line_id: string; answer: string }[] }) =>
    client.post<FlaskData<any>>('/v1/challenge/submit', data),
  // 返回 data.data: { total, correct, score, exp_gain, results }

  // ═══════════════════════════════════════════════════════
  // 接尾飞花令
  // ═══════════════════════════════════════════════════════

  // 创建接尾游戏房间
  createTailConnectRoom: (data: {
    difficulty?: string
    max_players?: number
  }) => client.post<FlaskData<any>>('/v1/tail-connect/rooms', data),

  // 加入接尾游戏房间
  joinTailConnectRoom: (roomId: string, code?: string) =>
    client.post<FlaskData<any>>(`/v1/tail-connect/rooms/${roomId}/join`, { code }),

  // 获取接尾游戏状态
  getTailConnectState: (roomId: string) =>
    client.get<FlaskData<any>>(`/v1/tail-connect/rooms/${roomId}`),

  // 开始接尾游戏
  startTailConnect: (roomId: string) =>
    client.post<FlaskData<any>>(`/v1/tail-connect/rooms/${roomId}/start`),

  // 提交接尾答案
  submitTailConnectAnswer: (roomId: string, data: { answer: string; turn_id: string }) =>
    client.post<FlaskData<any>>(`/v1/tail-connect/rooms/${roomId}/submit`, data),

  // 获取已用诗句
  getTailConnectUsedLines: (roomId: string) =>
    client.get<FlaskData<any>>(`/v1/tail-connect/rooms/${roomId}/used-lines`),

  // ═══════════════════════════════════════════════════════
  // AI 生图
  // ═══════════════════════════════════════════════════════

  // 创建生图任务
  createArtTask: (data: {
    poem_id: string
    poem_text: string
    style: string
    custom_prompt?: string
  }) => client.post<FlaskData<any>>('/v1/art/generate', data),

  // 获取生图任务状态
  getArtTaskStatus: (taskId: string) =>
    client.get<FlaskData<any>>(`/v1/art/tasks/${taskId}`),

  // 获取用户生图配额
  getArtQuota: () =>
    client.get<FlaskData<any>>('/v1/art/quota'),

  // 获取用户生图历史
  getArtHistory: (params?: { status?: string; limit?: number }) =>
    client.get<FlaskData<any>>('/v1/art/history', { params }),

  // 删除生图任务
  deleteArtTask: (taskId: string) =>
    client.delete<FlaskData<any>>(`/v1/art/tasks/${taskId}`),

  // ═══════════════════════════════════════════════════════
  // 诗词详情
  // ═══════════════════════════════════════════════════════

  // 获取诗句详情
  getPoem: (poemId: string) =>
    client.get<FlaskData<any>>(`/v1/poems/${poemId}`),

  // 获取诗句赏析
  getPoemExplanation: (poemId: string) =>
    client.get<FlaskData<any>>(`/v1/poems/${poemId}/explanation`),

  // 获取拍立得模板
  getPolaroidTemplates: () =>
    client.get<FlaskData<any>>('/v1/poems/polaroid-templates'),

  // 生成生图提示词
  generateArtPrompt: (data: { poem_id: string; style: string }) =>
    client.post<FlaskData<any>>('/v1/poems/generate-prompt', data),

  // ═══════════════════════════════════════════════════════
  // 每日推荐
  // ═══════════════════════════════════════════════════════

  // 获取每日推荐诗句
  getDailyPoem: () =>
    client.get<FlaskData<any>>('/v1/poems/daily'),

  // 获取随机诗句
  getRandomPoem: (params?: { keyword?: string; difficulty?: string }) =>
    client.get<FlaskData<any>>('/v1/poems/random', { params }),

  // ═══════════════════════════════════════════════════════
  // 诗词生成器 (AI 自由生成)
  // ═══════════════════════════════════════════════════════

  poetry: {
    // 生成诗句
    generate: (data: { mode: string; keyword?: string; difficulty?: string }) =>
      client.post<FlaskData<any>>('/v1/poetry/generate', data),

    // 验证答案
    validate: (data: { answer: string; mode: string; keyword?: string; expected?: string }) =>
      client.post<FlaskData<any>>('/v1/poetry/validate', data),

    // 获取关键字列表
    getKeywords: () =>
      client.get<FlaskData<any>>('/v1/poetry/keywords'),

    // 获取诗词统计
    getStats: () =>
      client.get<FlaskData<any>>('/v1/poetry/stats')
  },

  // ═══════════════════════════════════════════════════════
  // 藏书阁
  // ═══════════════════════════════════════════════════════

  library: {
    // 统计
    getStats: () =>
      client.get<FlaskData<any>>('/v1/library/stats'),

    // 书架
    getBookshelves: () =>
      client.get<FlaskData<any>>('/v1/library/bookshelves'),

    createBookshelf: (data: { name: string; description?: string; icon?: string }) =>
      client.post<FlaskData<any>>('/v1/library/bookshelves', data),

    updateBookshelf: (id: string, data: any) =>
      client.put<FlaskData<any>>(`/v1/library/bookshelves/${id}`, data),

    deleteBookshelf: (id: string) =>
      client.delete<FlaskData<any>>(`/v1/library/bookshelves/${id}`),

    // 书架内容
    getShelfItems: (shelfId: string, params?: { page?: number; type?: string }) =>
      client.get<FlaskData<any>>(`/v1/library/bookshelves/${shelfId}/items`, { params }),

    addShelfItem: (shelfId: string, data: any) =>
      client.post<FlaskData<any>>(`/v1/library/bookshelves/${shelfId}/items`, data),

    removeShelfItem: (shelfId: string, itemId: string) =>
      client.delete<FlaskData<any>>(`/v1/library/bookshelves/${shelfId}/items/${itemId}`),

    // 金句卡片
    getGoldenQuotes: (params?: { page?: number }) =>
      client.get<FlaskData<any>>('/v1/library/golden-quotes', { params }),

    createGoldenQuote: (data: {
      content: string;
      poem_line_id?: string;
      poem_title?: string;
      author?: string;
      style?: string;
      title?: string;
      note?: string;
      tags?: string[];
    }) =>
      client.post<FlaskData<any>>('/v1/library/golden-quotes', data),

    getGoldenQuote: (id: string) =>
      client.get<FlaskData<any>>(`/v1/library/golden-quotes/${id}`),

    updateGoldenQuote: (id: string, data: any) =>
      client.put<FlaskData<any>>(`/v1/library/golden-quotes/${id}`, data),

    deleteGoldenQuote: (id: string) =>
      client.delete<FlaskData<any>>(`/v1/library/golden-quotes/${id}`),

    // 诗词分类
    getCategories: () =>
      client.get<FlaskData<any>>('/v1/library/categories'),

    getPoemsByCategory: (slug: string, params?: { page?: number }) =>
      client.get<FlaskData<any>>(`/v1/library/poems/by-category/${slug}`, { params }),

    getPoemsByDynasty: (dynasty: string, params?: { page?: number; form?: string }) =>
      client.get<FlaskData<any>>(`/v1/library/poems/by-dynasty/${encodeURIComponent(dynasty)}`, { params }),

    getPoemsByAuthor: (name: string, params?: { page?: number }) =>
      client.get<FlaskData<any>>(`/v1/library/poems/by-author/${encodeURIComponent(name)}`, { params }),

    getAuthors: (params?: { page?: number; dynasty?: string }) =>
      client.get<FlaskData<any>>('/v1/library/authors', { params }),

    getDynasties: () =>
      client.get<FlaskData<any>>('/v1/library/dynasties'),

    // 阅读历史
    getReadingHistory: (params?: { page?: number }) =>
      client.get<FlaskData<any>>('/v1/library/reading-history', { params }),

    addReadingHistory: (data: { item_type: string; item_id: string; title?: string; author?: string }) =>
      client.post<FlaskData<any>>('/v1/library/reading-history', data),

    // 搜索
    search: (params: { q: string }) =>
      client.get<FlaskData<any>>('/v1/library/search', { params })
  },

  // ═══════════════════════════════════════════════════════
  // 单人飞花令练习
  // ═══════════════════════════════════════════════════════

  // 获取关键字列表
  getSoloKeywords: () =>
    client.get<FlaskData<any>>('/v1/solo/keywords'),

  // 获取关键字对应诗句
  getSoloPoems: (keyword: string, limit?: number) =>
    client.get<FlaskData<any>>('/v1/solo/poems', { params: { keyword, limit } }),

  // 验证答案
  validateSoloAnswer: (data: { answer: string; keyword: string; mode?: string }) =>
    client.post<FlaskData<any>>('/v1/solo/validate', data),

  // 获取提示
  getSoloSuggestion: (keyword: string) =>
    client.get<FlaskData<any>>('/v1/solo/suggestion', { params: { keyword } }),

  // 获取闯关等级
  getChallengeLevels: () =>
    client.get<FlaskData<any>>('/v1/solo/challenge/levels'),

  // 保存练习统计
  saveSoloStats: (data: any) =>
    client.post<FlaskData<any>>('/v1/solo/stats', data)
}
