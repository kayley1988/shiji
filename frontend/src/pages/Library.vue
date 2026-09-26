<template>
  <div class="library-page">
    <!-- 顶部导航 -->
    <header class="library-header">
      <div class="header-left">
        <van-icon name="bookmark" size="22" />
        <h1>藏书阁</h1>
      </div>
      <div class="header-right">
        <van-icon name="search" size="22" @click="showSearch = true" />
        <van-icon name="plus" size="22" @click="showCreateShelf = true" />
      </div>
    </header>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card" @click="activeTab = 'quotes'">
        <span class="stat-num">{{ stats.quote_count }}</span>
        <span class="stat-label">金句卡片</span>
      </div>
      <div class="stat-card" @click="activeTab = 'shelves'">
        <span class="stat-num">{{ stats.shelf_count }}</span>
        <span class="stat-label">书架</span>
      </div>
      <div class="stat-card" @click="activeTab = 'collections'">
        <span class="stat-num">{{ stats.collection_count }}</span>
        <span class="stat-label">收藏</span>
      </div>
    </div>

    <!-- 快捷分类 -->
    <div class="quick-categories">
      <div 
        class="category-item" 
        v-for="dynasty in dynasties" 
        :key="dynasty.name"
        @click="navigateToDynasty(dynasty.name)"
      >
        <span class="category-icon">{{ dynasty.icon }}</span>
        <span class="category-name">{{ dynasty.name }}</span>
        <span class="category-count">{{ dynasty.count }}</span>
      </div>
    </div>

    <!-- Tab 切换 -->
    <van-tabs v-model:active="activeTab" swipeable>
      <!-- 金句卡片 -->
      <van-tab title="金句卡片" name="quotes">
        <div class="tab-content">
          <div class="section-header">
            <span>我的金句</span>
            <van-button size="small" plain @click="$router.push('/library/quote/create')">
              <van-icon name="plus" /> 创建
            </van-button>
          </div>
          
          <div class="quote-grid" v-if="quotes.length">
            <div 
              class="quote-card" 
              v-for="quote in quotes" 
              :key="quote.id"
              @click="viewQuote(quote)"
            >
              <div class="quote-image" v-if="quote.image_url">
                <img :src="quote.image_url" :alt="quote.content" />
              </div>
              <div class="quote-content">
                <p class="quote-text">「{{ quote.content }}」</p>
                <p class="quote-meta">
                  <span v-if="quote.poem_title">《{{ quote.poem_title }}》</span>
                  <span v-if="quote.author"> — {{ quote.author }}</span>
                </p>
              </div>
              <div class="quote-style-tag">{{ quote.style }}</div>
            </div>
          </div>
          
          <van-empty v-else description="还没有金句卡片" image="search">
            <template #image>
              <span style="font-size: 64px">📜</span>
            </template>
            <van-button type="primary" size="small" @click="$router.push('/library/quote/create')">
              创建第一张金句卡片
            </van-button>
          </van-empty>
        </div>
      </van-tab>

      <!-- 书架 -->
      <van-tab title="书架" name="shelves">
        <div class="tab-content">
          <div class="section-header">
            <span>我的书架</span>
            <van-button size="small" plain @click="showCreateShelf = true">
              <van-icon name="plus" /> 新建书架
            </van-button>
          </div>
          
          <div class="shelf-list" v-if="shelves.length">
            <div 
              class="shelf-card"
              v-for="shelf in shelves"
              :key="shelf.id"
              @click="viewShelf(shelf)"
            >
              <div class="shelf-icon">{{ shelf.icon || '📚' }}</div>
              <div class="shelf-info">
                <h3>{{ shelf.name }}</h3>
                <p>{{ shelf.description || `${shelf.item_count} 件收藏` }}</p>
              </div>
              <van-icon name="arrow" size="16" class="shelf-arrow" />
            </div>
          </div>
          
          <van-empty v-else description="还没有书架" image="search">
            <template #image>
              <span style="font-size: 64px">🏠</span>
            </template>
            <van-button type="primary" size="small" @click="showCreateShelf = true">
              创建第一个书架
            </van-button>
          </van-empty>
        </div>
      </van-tab>

      <!-- 分类 -->
      <van-tab title="分类" name="collections">
        <div class="tab-content">
          <!-- 朝代分类 -->
          <div class="category-section">
            <h3 class="section-title">📖 朝代</h3>
            <div class="dynasty-grid">
              <div 
                class="dynasty-card"
                v-for="dynasty in dynasties"
                :key="dynasty.name"
                @click="navigateToDynasty(dynasty.name)"
              >
                <span class="dynasty-icon">{{ dynasty.icon }}</span>
                <span class="dynasty-name">{{ dynasty.name }}</span>
                <span class="dynasty-count">{{ dynasty.count }}首</span>
              </div>
            </div>
          </div>

          <!-- 主题分类 -->
          <div class="category-section">
            <h3 class="section-title">🎯 主题</h3>
            <div class="theme-grid">
              <div 
                class="theme-chip"
                v-for="theme in themes"
                :key="theme.slug"
                @click="navigateToTheme(theme.slug)"
              >
                {{ theme.icon }} {{ theme.name }}
              </div>
            </div>
          </div>

          <!-- 诗人专辑 -->
          <div class="category-section">
            <h3 class="section-title">👤 诗人</h3>
            <div class="author-list">
              <div 
                class="author-card"
                v-for="author in topAuthors"
                :key="author.id"
                @click="navigateToAuthor(author.name)"
              >
                <img v-if="author.avatar_url" :src="author.avatar_url" class="author-avatar" />
                <div v-else class="author-avatar-placeholder">
                  {{ author.name.charAt(0) }}
                </div>
                <div class="author-info">
                  <span class="author-name">{{ author.name }}</span>
                  <span class="author-dynasty">{{ author.dynasty }}</span>
                </div>
                <span class="author-count">{{ author.poem_count }}首</span>
              </div>
            </div>
            <van-button plain block @click="$router.push('/library/authors')">
              查看全部诗人
            </van-button>
          </div>
        </div>
      </van-tab>

      <!-- 阅读历史 -->
      <van-tab title="历史" name="history">
        <div class="tab-content">
          <div class="history-list" v-if="history.length">
            <div 
              class="history-item"
              v-for="item in history"
              :key="item.id"
              @click="openItem(item)"
            >
              <div class="history-icon">
                {{ item.item_type === 'poem' ? '📜' : item.item_type === 'golden_quote' ? '💫' : '📝' }}
              </div>
              <div class="history-info">
                <h4>{{ item.title }}</h4>
                <p>{{ item.author }}</p>
              </div>
              <span class="history-time">{{ formatTime(item.read_at) }}</span>
            </div>
          </div>
          <van-empty v-else description="还没有阅读记录" />
        </div>
      </van-tab>
    </van-tabs>

    <!-- 创建书架弹窗 -->
    <van-popup v-model:show="showCreateShelf" position="bottom" round>
      <div class="create-shelf-popup">
        <h3>创建书架</h3>
        <van-form @submit="createShelf">
          <van-cell-group inset>
            <van-field
              v-model="newShelf.name"
              name="name"
              label="书架名"
              placeholder="给我的书架起个名字"
            />
            <van-field
              v-model="newShelf.description"
              name="description"
              label="描述"
              placeholder="这个书架用来放什么？"
            />
            <van-field name="icon" label="图标">
              <template #input>
                <van-radio-group v-model="newShelf.icon" direction="horizontal">
                  <van-radio name="📚">📚</van-radio>
                  <van-radio name="📖">📖</van-radio>
                  <van-radio name="🏠">🏠</van-radio>
                  <van-radio name="💫">💫</van-radio>
                  <van-radio name="🎯">🎯</van-radio>
                </van-radio-group>
              </template>
            </van-field>
          </van-cell-group>
          <div class="popup-actions">
            <van-button plain @click="showCreateShelf = false">取消</van-button>
            <van-button type="primary" native-type="submit">创建</van-button>
          </div>
        </van-form>
      </div>
    </van-popup>

    <!-- 搜索弹窗 -->
    <van-popup v-model:show="showSearch" position="top" style="height: 100%">
      <div class="search-popup">
        <van-search
          v-model="searchKeyword"
          placeholder="搜索诗词、金句、诗人"
          show-action
          @search="doSearch"
          @cancel="showSearch = false"
        />
        <div class="search-results" v-if="searchResults">
          <div class="result-section" v-if="searchResults.poems.length">
            <h4>诗词</h4>
            <div 
              class="result-item"
              v-for="poem in searchResults.poems"
              :key="poem.id"
              @click="$router.push(`/poem/${poem.id}`)"
            >
              <span class="result-title">{{ poem.title }}</span>
              <span class="result-meta">{{ poem.author }}</span>
            </div>
          </div>
          <div class="result-section" v-if="searchResults.golden_quotes.length">
            <h4>金句卡片</h4>
            <div 
              class="result-item"
              v-for="quote in searchResults.golden_quotes"
              :key="quote.id"
              @click="viewQuote(quote)"
            >
              <span class="result-title">{{ quote.content }}</span>
              <span class="result-meta">{{ quote.author }}</span>
            </div>
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { api } from '../api'

const router = useRouter()

// 状态
const activeTab = ref('quotes')
const showCreateShelf = ref(false)
const showSearch = ref(false)
const searchKeyword = ref('')

// 数据
const stats = reactive({
  shelf_count: 0,
  quote_count: 0,
  collection_count: 0,
  total_reading_minutes: 0
})

const dynasties = ref<any[]>([])
const themes = ref<any[]>([
  { slug: 'love', name: '爱情', icon: '💕' },
  { slug: 'nature', name: '自然', icon: '🌿' },
  { slug: 'sentiment', name: '思乡', icon: '🏠' },
  { slug: 'friendship', name: '友情', icon: '🤝' },
  { slug: 'war', name: '边塞', icon: '⚔️' },
  { slug: 'landscape', name: '山水', icon: '🏔️' },
])

const quotes = ref<any[]>([])
const shelves = ref<any[]>([])
const history = ref<any[]>([])
const topAuthors = ref<any[]>([])
const searchResults = ref<any>(null)

// 新建书架
const newShelf = reactive({
  name: '',
  description: '',
  icon: '📚'
})

// 加载统计数据
async function loadStats() {
  try {
    const res = await api.library.getStats()
    if (res.success) {
      Object.assign(stats, res.stats)
    }
  } catch (err) {
    console.error('加载统计失败', err)
  }
}

// 加载朝代数据
async function loadDynasties() {
  try {
    const res = await api.library.getDynasties()
    if (res.success) {
      dynasties.value = res.dynasties
    }
  } catch (err) {
    console.error('加载朝代失败', err)
  }
}

// 加载金句卡片
async function loadQuotes() {
  try {
    const res = await api.library.getGoldenQuotes()
    if (res.success) {
      quotes.value = res.quotes
    }
  } catch (err) {
    console.error('加载金句失败', err)
  }
}

// 加载书架
async function loadShelves() {
  try {
    const res = await api.library.getBookshelves()
    if (res.success) {
      shelves.value = res.bookshelves
    }
  } catch (err) {
    console.error('加载书架失败', err)
  }
}

// 加载阅读历史
async function loadHistory() {
  try {
    const res = await api.library.getReadingHistory()
    if (res.success) {
      history.value = res.history
    }
  } catch (err) {
    console.error('加载历史失败', err)
  }
}

// 加载热门诗人
async function loadTopAuthors() {
  try {
    const res = await api.library.getAuthors()
    if (res.success) {
      topAuthors.value = res.authors.slice(0, 6)
    }
  } catch (err) {
    console.error('加载诗人失败', err)
  }
}

// 创建书架
async function createShelf() {
  if (!newShelf.name.trim()) {
    showToast('请输入书架名称')
    return
  }
  
  try {
    const res = await api.library.createBookshelf({
      name: newShelf.name,
      description: newShelf.description,
      icon: newShelf.icon
    })
    
    if (res.success) {
      showToast('创建成功')
      showCreateShelf.value = false
      newShelf.name = ''
      newShelf.description = ''
      loadShelves()
      loadStats()
    }
  } catch (err) {
    showToast('创建失败')
  }
}

// 搜索
async function doSearch() {
  if (!searchKeyword.value.trim()) return
  
  try {
    const res = await api.library.search({ q: searchKeyword.value })
    if (res.success) {
      searchResults.value = res.results
    }
  } catch (err) {
    console.error('搜索失败', err)
  }
}

// 查看金句卡片
function viewQuote(quote: any) {
  router.push(`/library/quote/${quote.id}`)
}

// 查看书架
function viewShelf(shelf: any) {
  router.push(`/library/shelf/${shelf.id}`)
}

// 导航到朝代
function navigateToDynasty(dynasty: string) {
  router.push(`/library/dynasty/${encodeURIComponent(dynasty)}`)
}

// 导航到主题
function navigateToTheme(slug: string) {
  router.push(`/library/theme/${slug}`)
}

// 导航到诗人
function navigateToAuthor(name: string) {
  router.push(`/library/author/${encodeURIComponent(name)}`)
}

// 打开条目
function openItem(item: any) {
  if (item.item_type === 'poem') {
    router.push(`/poem/${item.item_id}`)
  } else if (item.item_type === 'golden_quote') {
    router.push(`/library/quote/${item.item_id}`)
  }
}

// 格式化时间
function formatTime(isoString: string) {
  if (!isoString) return ''
  const date = new Date(isoString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadStats()
  loadDynasties()
  loadQuotes()
  loadShelves()
  loadHistory()
  loadTopAuthors()
})
</script>

<style scoped>
.library-page {
  min-height: 100vh;
  background: var(--paper, #FAF8F3);
  padding-bottom: 20px;
}

/* 头部 */
.library-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--card, #FFFFFF);
  border-bottom: 1px solid var(--line, #E8E4DC);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-left h1 {
  font-size: 20px;
  margin: 0;
  color: var(--ink-dark, #2C2C2C);
  font-family: var(--font-display, serif);
}

.header-right {
  display: flex;
  gap: 16px;
  color: var(--ink-mist, #7A8A8A);
}

/* 统计行 */
.stats-row {
  display: flex;
  padding: 16px 20px;
  gap: 12px;
  background: var(--card, #FFFFFF);
  margin: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(44,44,44,0.06);
}

.stat-card {
  flex: 1;
  text-align: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.stat-card:active {
  background: var(--line-light, #F0EDE6);
}

.stat-num {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: var(--cinnabar, #D4AF37);
  font-family: var(--font-display, serif);
}

.stat-label {
  font-size: 12px;
  color: var(--ink-mist, #7A8A8A);
  margin-top: 4px;
}

/* 快捷分类 */
.quick-categories {
  display: flex;
  padding: 12px 16px;
  gap: 10px;
  overflow-x: auto;
  background: var(--card, #FFFFFF);
  margin: 0 16px 12px;
  border-radius: 12px;
  -webkit-overflow-scrolling: touch;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 14px;
  background: var(--paper-warm, #F5F1E8);
  border-radius: 10px;
  white-space: nowrap;
  cursor: pointer;
  min-width: 64px;
}

.category-item:active {
  background: var(--line, #E8E4DC);
}

.category-icon {
  font-size: 22px;
}

.category-name {
  font-size: 12px;
  color: var(--ink-dark, #2C2C2C);
  font-weight: 500;
}

.category-count {
  font-size: 10px;
  color: var(--ink-mist, #7A8A8A);
}

/* Tab 内容 */
.tab-content {
  padding: 16px 20px;
  min-height: 60vh;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header span {
  font-size: 16px;
  font-weight: 600;
  color: var(--ink-dark, #2C2C2C);
}

/* 金句卡片网格 */
.quote-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.quote-card {
  background: var(--card, #FFFFFF);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(44,44,44,0.06);
  cursor: pointer;
  position: relative;
}

.quote-card:active {
  transform: scale(0.98);
}

.quote-image {
  width: 100%;
  height: 120px;
  overflow: hidden;
}

.quote-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.quote-content {
  padding: 12px;
}

.quote-text {
  font-size: 13px;
  line-height: 1.7;
  color: var(--ink, #3D3D3D);
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-family: var(--font-serif, serif);
}

.quote-meta {
  font-size: 11px;
  color: var(--ink-mist, #7A8A8A);
  margin: 0;
}

.quote-style-tag {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 2px 8px;
  background: rgba(212,175,55,0.85);
  color: white;
  font-size: 10px;
  border-radius: 10px;
}

/* 书架列表 */
.shelf-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.shelf-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: var(--card, #FFFFFF);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(44,44,44,0.06);
  cursor: pointer;
}

.shelf-card:active {
  background: var(--line-light, #F0EDE6);
}

.shelf-icon {
  font-size: 32px;
}

.shelf-info {
  flex: 1;
}

.shelf-info h3 {
  margin: 0;
  font-size: 15px;
  color: var(--ink-dark, #2C2C2C);
}

.shelf-info p {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--ink-mist, #7A8A8A);
}

.shelf-arrow {
  color: var(--line, #E8E4DC);
}

/* 朝代网格 */
.dynasty-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.dynasty-card {
  text-align: center;
  padding: 16px 8px;
  background: var(--card, #FFFFFF);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(44,44,44,0.06);
  cursor: pointer;
  transition: all 0.2s;
}

.dynasty-card:active {
  transform: scale(0.96);
  background: var(--line-light, #F0EDE6);
}

.dynasty-icon {
  display: block;
  font-size: 26px;
  margin-bottom: 6px;
}

.dynasty-name {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: var(--ink-dark, #2C2C2C);
  font-family: var(--font-display, serif);
}

.dynasty-count {
  display: block;
  font-size: 11px;
  color: var(--ink-mist, #7A8A8A);
  margin-top: 4px;
}

/* 主题标签 */
.theme-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.theme-chip {
  padding: 8px 14px;
  background: rgba(212,175,55,0.08);
  color: var(--cinnabar, #D4AF37);
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  font-weight: 500;
}

.theme-chip:active {
  background: rgba(212,175,55,0.15);
}

/* 诗人列表 */
.author-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.author-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--card, #FFFFFF);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(44,44,44,0.06);
  cursor: pointer;
}

.author-card:active {
  background: var(--line-light, #F0EDE6);
}

.author-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: cover;
}

.author-avatar-placeholder {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--cinnabar, #D4AF37), #a83230);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
}

.author-info {
  flex: 1;
}

.author-name {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--ink-dark, #2C2C2C);
}

.author-dynasty {
  display: block;
  font-size: 12px;
  color: var(--ink-mist, #7A8A8A);
  margin-top: 2px;
}

.author-count {
  font-size: 12px;
  color: var(--ink-mist, #7A8A8A);
}

/* 历史记录 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--card, #FFFFFF);
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(44,44,44,0.04);
  cursor: pointer;
}

.history-item:active {
  background: var(--line-light, #F0EDE6);
}

.history-icon {
  font-size: 24px;
}

.history-info {
  flex: 1;
}

.history-info h4 {
  margin: 0;
  font-size: 14px;
  color: var(--ink-dark, #2C2C2C);
}

.history-info p {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--ink-mist, #7A8A8A);
}

.history-time {
  font-size: 11px;
  color: var(--line, #E8E4DC);
}

/* 创建书架弹窗 */
.create-shelf-popup {
  padding: 20px;
}

.create-shelf-popup h3 {
  margin: 0 0 16px;
  text-align: center;
  font-family: var(--font-display, serif);
  color: var(--ink-dark, #2C2C2C);
}

.popup-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
  gap: 12px;
}

.popup-actions button {
  flex: 1;
}

/* 搜索弹窗 */
.search-popup {
  padding-top: 46px;
}

.search-results {
  padding: 16px;
}

.result-section {
  margin-bottom: 20px;
}

.result-section h4 {
  margin: 0 0 10px;
  font-size: 14px;
  color: var(--ink-light, #5A5A5A);
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: var(--card, #FFFFFF);
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(44,44,44,0.04);
}

.result-item:active {
  background: var(--line-light, #F0EDE6);
}

.result-title {
  font-size: 14px;
  color: var(--ink-dark, #2C2C2C);
}

.result-meta {
  font-size: 12px;
  color: var(--ink-mist, #7A8A8A);
}
</style>
