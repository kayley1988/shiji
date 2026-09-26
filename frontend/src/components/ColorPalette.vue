<template>
  <div class="palette-page bg-xuanzhi">

    <!-- 顶部导航 -->
    <header class="app-nav">
      <button class="nav-back" @click="$router.back()">
        <van-icon name="arrow-left" />
      </button>
      <span class="nav-title">中国传统色</span>
      <span class="nav-right"></span>
    </header>

    <!-- 简介 -->
    <div class="intro-card animate-fadeUp">
      <p class="intro-text">「色之极雅，不过中国色」</p>
      <p class="intro-sub">每一种颜色，皆有诗句为证</p>
    </div>

    <!-- 分类 Tab -->
    <van-tabs v-model:active="activeTab" class="palette-tabs" swipeable sticky offset-top="52" @change="onTabChange">
      <van-tab
        v-for="cat in categories"
        :key="cat.key"
        :title="cat.label"
        :name="cat.key"
      >
        <div class="color-meta">
          <span class="color-count">{{ byCategory(cat.key).length }} 色</span>
        </div>
        <div class="color-grid">
          <div
            v-for="(color, i) in byCategory(cat.key)"
            :key="color.name"
            class="color-block animate-fadeUp"
            :style="{ animationDelay: `${i * 0.04}s` }"
          >
            <!-- 色块（点击打开全屏诗集） -->
            <div
              class="block-swatch"
              :style="{ background: color.hex }"
              @click="openFullscreen(color)"
            >
              <span class="swatch-name">{{ color.name }}</span>
              <span class="swatch-hex">{{ color.hex }}</span>
              <div class="swatch-overlay">
                <van-icon name="expand" size="20" color="#fff" />
                <span class="swatch-poem-count" v-if="poemCache[color.name]?.length">
                  {{ poemCache[color.name].length }} 首
                </span>
              </div>
            </div>
            <!-- 诗句预览 -->
            <div class="block-poem">
              <template v-if="poemCache[color.name]?.length">
                <p class="poem-line">
                  「{{ poemCache[color.name][0].matched_line }}」
                </p>
                <p class="poem-source">
                  —— {{ poemCache[color.name][0].title }}
                  <span class="poem-dynasty">{{ poemCache[color.name][0].dynasty }}</span>
                  · {{ poemCache[color.name][0].author }}
                </p>
                <p class="poem-keyword" v-if="poemCache[color.name].length > 1">
                  <van-tag type="primary" plain>
                    +{{ poemCache[color.name].length - 1 }} 首
                  </van-tag>
                  <span class="swipe-hint" @click="openFullscreen(color)">点击查看全部 →</span>
                </p>
              </template>
              <template v-else>
                <p class="poem-line">「{{ color.poem || '正在加载诗句...' }}」</p>
                <p class="poem-source">{{ color.source || '' }}</p>
                <p v-if="poemLoadingSet.has(color.name)" class="poem-loading">
                  <van-loading type="spinner" size="12px" />
                </p>
              </template>
              <p v-if="color.note" class="poem-note">{{ color.note }}</p>

              <!-- 操作按钮 -->
              <div class="poem-actions">
                <button
                  class="action-btn"
                  :class="{ active: speakingMap[color.name] }"
                  @click="onSpeak(color)"
                  :title="speakingMap[color.name] ? '停止' : '朗读'"
                >
                  <van-icon :name="speakingMap[color.name] ? 'stop-circle-o' : 'volume-o'" />
                  <span>{{ speakingMap[color.name] ? '停止' : '朗读' }}</span>
                </button>
                <button class="action-btn ai-btn" @click="openAi(color)" title="AI 解读">
                  <van-icon name="chat-o" />
                  <span>解读</span>
                </button>
                <button
                  class="action-btn fav-btn"
                  :class="{ 'fav-active': favoriteSet.has(color.name) }"
                  @click="toggleFav(color)"
                  :title="favoriteSet.has(color.name) ? '取消收藏' : '收藏'"
                >
                  <van-icon :name="favoriteSet.has(color.name) ? 'star' : 'star-o'" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </van-tab>
    </van-tabs>

    <!-- ══════════════════════════════════════════════
         全屏诗集 Modal
    ══════════════════════════════════════════════ -->
    <van-popup
      v-model:show="fsVisible"
      position="right"
      :style="{ width: '100vw', height: '100vh', background: 'transparent' }"
      :overlay-style="{ background: 'rgba(0,0,0,0.6)' }"
      closeable
      close-icon="close"
      class="fullscreen-poem-popup"
    >
      <!-- 全屏背景 = 颜色 -->
      <div
        class="fs-container"
        :style="{
          background: fsColor?.hex || 'var(--qinglu)',
          '--text-on-bg': fsTextColor,
        }"
        @click.stop
      >
        <!-- 顶部信息 -->
        <div class="fs-header">
          <div class="fs-title-wrap">
            <h2 class="fs-color-name">{{ fsColor?.name }}</h2>
            <p class="fs-hex">{{ fsColor?.hex }}</p>
          </div>
          <p v-if="fsColor?.note" class="fs-note">{{ fsColor.note }}</p>
        </div>

        <!-- 关键词标签 -->
        <div class="fs-keywords" v-if="fsKeywords.length">
          <span
            v-for="kw in fsKeywords"
            :key="kw"
            class="fs-kw-tag"
            :style="{ background: 'rgba(255,255,255,0.2)', color: '#fff' }"
          >{{ kw }}</span>
        </div>

        <!-- 诗集列表 -->
        <div class="fs-poem-list">
          <!-- Loading -->
          <div v-if="fsLoading" class="fs-loading">
            <van-loading type="spinner" size="32px" color="#fff" />
            <span>正在匹配诗句...</span>
          </div>
          <!-- 空状态 -->
          <div v-else-if="!fsPoems.length" class="fs-empty">
            <p class="fs-empty-icon">🍃</p>
            <p class="fs-empty-text">暂无匹配诗句</p>
            <p class="fs-empty-sub">数据库正在更新，敬请期待</p>
          </div>
          <!-- 诗句卡片 -->
          <div v-show="!fsLoading && fsPoems.length" class="fs-poem-cards">
            <div
              v-for="(poem, idx) in fsPoems"
              :key="poem.poem_id"
              class="fs-poem-card animate-fadeUp"
              :style="{ animationDelay: `${idx * 0.08}s` }"
            >
              <!-- 诗句全文 -->
              <div class="fs-poem-text">
                <p
                  v-for="(line, li) in poem.lines"
                  :key="li"
                  class="fs-line"
                  :class="{ 'matched': poem.matched_kw && line.includes(poem.matched_kw) }"
                >{{ line }}</p>
              </div>

              <!-- 匹配高亮 -->
              <div class="fs-match-bar" v-if="poem.matched_line !== poem.lines[0]">
                <div class="match-icon">✦</div>
                <p class="fs-matched-line">「{{ poem.matched_line }}」</p>
              </div>

              <!-- 出处 -->
              <div class="fs-poem-meta">
                <span class="fs-poem-title">{{ poem.title }}</span>
                <span class="fs-poem-author">
                  <span class="fs-dynasty">{{ poem.dynasty }}</span>
                  {{ poem.author }}
                </span>
              </div>

              <!-- 操作 -->
              <div class="fs-poem-actions">
                <button class="fs-action-btn" @click="fsSpeak(poem)">
                  <van-icon :name="fsSpeakingId === poem.poem_id ? 'stop-circle-o' : 'volume-o'" />
                  <span>{{ fsSpeakingId === poem.poem_id ? '停止' : '朗读' }}</span>
                </button>
                <button class="fs-action-btn" @click="fsFav(fsColor!, poem)">
                  <van-icon :name="fsFavSet.has(poem.poem_id) ? 'star' : 'star-o'" />
                  <span>{{ fsFavSet.has(poem.poem_id) ? '已藏' : '收藏' }}</span>
                </button>
                <button class="fs-action-btn" @click="fsAi(poem)">
                  <van-icon name="chat-o" />
                  <span>解读</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 关闭按钮（底部） -->
        <div class="fs-footer">
          <van-button
            plain
            size="small"
            :color="'rgba(255,255,255,0.7)'"
            :text-color="'#fff'"
            @click="fsVisible = false"
            style="border-color: rgba(255,255,255,0.5); background: rgba(255,255,255,0.1);"
          >
            关闭
          </van-button>
        </div>
      </div>
    </van-popup>

    <!-- AI 解读弹窗 -->
    <van-popup
      v-model:show="aiDialogVisible"
      position="bottom"
      round
      class="ai-dialog"
      closeable
    >
      <div v-if="aiColor" class="ai-dialog-content">
        <div class="ai-header">
          <div class="ai-swatch" :style="{ background: aiColor.hex }"></div>
          <div class="ai-title">
            <h3>{{ aiColor.name }}</h3>
            <p class="ai-hex">{{ aiColor.hex }}</p>
          </div>
        </div>

        <div class="ai-quote">
          <p>「{{ getPoem(aiColor) }}」</p>
          <p class="ai-source">—— {{ getSource(aiColor) }}</p>
        </div>

        <van-divider />

        <div class="ai-body">
          <div v-if="aiLoading" class="ai-loading">
            <van-loading type="spinner" size="24px" />
            <span>AI 解读中，请稍候...</span>
          </div>

          <template v-else-if="aiSections.length">
            <div
              v-for="(section, i) in aiSections"
              :key="i"
              class="ai-section animate-fadeUp"
              :style="{ animationDelay: `${i * 0.06}s` }"
            >
              <div class="ai-section-label">
                <span class="section-icon">{{ sectionIcons[i % sectionIcons.length] }}</span>
                <span>{{ section.title }}</span>
              </div>
              <p class="ai-section-text">{{ section.body }}</p>
            </div>
          </template>

          <div v-else-if="aiContent" class="ai-text">{{ aiContent }}</div>
          <van-empty v-else description="暂无解读" />
        </div>
      </div>
    </van-popup>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { showToast } from 'vant'
import { CHINESE_COLORS } from '../styles/chinese-colors'
import { speak, stop, speaking } from '../composables/useSpeech'
import { api } from '../api'
import type { ChineseColor } from '../styles/chinese-colors'

type Category = ChineseColor['category']

const activeTab = ref<Category>('red')

const categories: { key: Category; label: string }[] = [
  { key: 'red',      label: '赤' },
  { key: 'yellow',   label: '黄' },
  { key: 'green',    label: '青' },
  { key: 'blue',     label: '蓝' },
  { key: 'purple',   label: '紫' },
  { key: 'white',    label: '白' },
  { key: 'black',    label: '玄' },
  { key: 'mineral',  label: '金石' },
  { key: 'imagery',  label: '意象' },
  { key: 'solar',    label: '节气' },
]

function byCategory(cat: Category) {
  return CHINESE_COLORS.filter(c => c.category === cat)
}

// ── 动态诗句加载 ──────────────────────────────
/** 已加载的诗句缓存：key = 颜色名，value = 多首诗数组 */
const poemCache = reactive<Record<string, Array<{
  poem_id: string
  title: string
  author: string
  dynasty: string
  lines: string[]
  matched_line: string
  matched_kw: string
}>>>({})

/** 正在加载中的颜色名集合 */
const poemLoadingSet = reactive(new Set<string>())

/** 辅助：获取当前显示的首句诗文本 */
function getPoem(color: ChineseColor): string {
  const poems = poemCache[color.name]
  if (poems?.length) return poems[0].matched_line
  return color.poem || ''
}

/** 辅助：获取当前显示的出处文本 */
function getSource(color: ChineseColor): string {
  const poems = poemCache[color.name]
  if (poems?.length) return `${poems[0].title} · ${poems[0].author}`
  return color.source || ''
}

/** 为单个颜色加载多首诗句 */
async function loadPoem(color: ChineseColor) {
  if (poemCache[color.name]?.length || poemLoadingSet.has(color.name)) return

  poemLoadingSet.add(color.name)
  try {
    const res = await api.get('/poem/color-match', {
      params: { color_name: color.name, limit: 5 }
    })
    if (res.data?.code === 200 && res.data?.data?.poems?.length) {
      poemCache[color.name] = res.data.poems
    }
  } catch (e) {
    console.warn(`[ColorPalette] 色·诗匹配失败: ${color.name}`, e)
  } finally {
    poemLoadingSet.delete(color.name)
  }
}

/** 加载当前 Tab 下所有颜色的诗句 */
function loadPoemForTab(tab: Category) {
  byCategory(tab).forEach(color => loadPoem(color))
}

/** Tab 切换时加载该 Tab 的诗句 */
function onTabChange(tab: Category | string) {
  loadPoemForTab(tab as Category)
}

// ── 全屏诗集 ──────────────────────────────
const fsVisible = ref(false)
const fsColor = ref<ChineseColor | null>(null)
const fsTextColor = computed(() => (fsColor.value ? getTextColor(fsColor.value.hex) : '#fff'))
const fsPoems = ref<typeof poemCache[string]>([])
const fsKeywords = ref<string[]>([])
const fsSpeakingId = ref('')
const fsFavSet = ref(new Set<string>())
const fsLoading = ref(false)

/** 根据背景色自动判断文字颜色 */
function getTextColor(hex: string): string {
  const h = hex.replace('#', '')
  const r = parseInt(h.slice(0, 2), 16)
  const g = parseInt(h.slice(2, 4), 16)
  const b = parseInt(h.slice(4, 6), 16)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return luminance > 0.45 ? 'rgba(0,0,0,0.75)' : 'rgba(255,255,255,0.9)'
}

async function openFullscreen(color: ChineseColor) {
  fsColor.value = color
  fsSpeakingId.value = ''
  fsFavSet.value = new Set()
  fsVisible.value = true

  // 已有缓存则直接用
  if (poemCache[color.name]?.length) {
    fsPoems.value = [...poemCache[color.name]]
    fsKeywords.value = (poemCache[color.name][0] as any)?._keywords || []
    return
  }

  // 未缓存：loading + 强制请求（用 axios 直调，避免 api.get 类型问题）
  fsPoems.value = []
  fsLoading.value = true
  fsKeywords.value = []
  try {
    const { default: axios } = await import('axios')
    const r = await axios.get('/api/v1/poem/color-match', {
      params: { color_name: color.name, limit: 5 },
      timeout: 10000,
    })
    const payload = r.data
    if (payload?.code === 200 && payload?.data?.poems?.length) {
      const poems = payload.data.poems
      poemCache[color.name] = poems
      fsPoems.value = [...poems]
      fsKeywords.value = payload.data.keywords || []
    } else {
      fsPoems.value = []
    }
  } catch (e) {
    console.warn('[ColorPalette] 色·诗加载失败', color.name, e)
    fsPoems.value = []
  } finally {
    fsLoading.value = false
  }
}

function fsSpeak(poem: typeof fsPoems.value[0]) {
  const text = poem.lines.join('，') + `，${poem.title}，${poem.dynasty}，${poem.author}`
  if (fsSpeakingId.value === poem.poem_id && speaking.value) {
    stop()
    fsSpeakingId.value = ''
  } else {
    Object.keys(speakingMap).forEach(k => { speakingMap[k] = false })
    speak(text)
    fsSpeakingId.value = poem.poem_id
  }
}

async function fsFav(_color: ChineseColor, poem: typeof fsPoems.value[0]) {
  try {
    await api.put(`/me/favorites/poem/${poem.poem_id}`)
    fsFavSet.value.add(poem.poem_id)
    showToast('已收藏此诗')
  } catch {
    showToast('收藏失败')
  }
}

function fsAi(poem: typeof fsPoems.value[0]) {
  aiColor.value = fsColor.value
  aiContent.value = ''
  aiDialogVisible.value = true

  aiLoading.value = true
  fetch('/api/v1/ai/poem-explain', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      poem: poem.matched_line,
      source: `${poem.title} · ${poem.author}`,
      colorName: fsColor.value?.name || '',
      note: fsColor.value?.note || '',
      user_query: '请从以下五个维度进行深入赏析，要求文字优美、专业：\n1. 意境之美\n2. 诗人事迹\n3. 创作背景\n4. 色彩溯源\n5. 诵读要点',
    })
  }).then(r => r.json())
    .then(d => {
      const raw = d.data?.content || d.content || ''
      aiContent.value = raw.replace(/^#{1,6}\s+/gm, '## ').replace(/\*\*/g, '「').replace(/\*/g, '').replace(/`{1,3}/g, '').trim() || '暂无解读'
    })
    .catch(() => { aiContent.value = '解读服务暂时不可用' })
    .finally(() => { aiLoading.value = false })
}

// ── 朗读 ──────────────────────────────────────
const speakingMap = reactive<Record<string, boolean>>({})

function onSpeak(color: ChineseColor) {
  const poems = poemCache[color.name]
  const poemText = poems?.length
    ? poems[0].lines.join('，')
    : getPoem(color)
  const sourceText = getSource(color)
  const text = poemText ? `${poemText}，${sourceText}` : ''

  if (!text || text.length < 4) {
    showToast('暂无诗句内容')
    return
  }

  if (speakingMap[color.name] && speaking.value) {
    stop()
    speakingMap[color.name] = false
  } else {
    Object.keys(speakingMap).forEach(k => { speakingMap[k] = false })
    speak(text)
    speakingMap[color.name] = true
  }
}

// ── AI 解读 ───────────────────────────────────
const aiDialogVisible = ref(false)
const aiColor = ref<ChineseColor | null>(null)
const aiContent = ref('')
const aiLoading = ref(false)

const sectionIcons = ['🌸', '🪶', '📜', '🎨', '🎤']
const aiSections = computed(() => {
  if (!aiContent.value) return []
  const parts = aiContent.value.split(/(?:^|\n)(?=#{1,3}\s+)/)
  return parts
    .map(p => {
      const m = p.match(/^#{1,3}\s+(.+?)\n([\s\S]*)$/)
      if (m) return { title: m[1].trim(), body: m[2].trim() }
      const trimmed = p.trim()
      if (trimmed) return { title: '', body: trimmed }
      return null
    })
    .filter(Boolean) as { title: string; body: string }[]
})

// ── 收藏 ───────────────────────────────────
const favoriteSet = ref(new Set<string>())

onMounted(async () => {
  loadPoemForTab(activeTab.value)

  try {
    const res = await api.get('/me/favorites', { params: { type: 'color' } })
    const colors = res.data?.favorites?.map((f: any) => f.color_name) || []
    colors.forEach((n: string) => favoriteSet.value.add(n))
  } catch {}
})

onUnmounted(() => {
  stop()
})

async function toggleFav(color: ChineseColor) {
  const name = color.name
  try {
    if (favoriteSet.value.has(name)) {
      await api.delete(`/me/favorites/color/${encodeURIComponent(name)}`)
      favoriteSet.value.delete(name)
      showToast('已取消收藏')
    } else {
      await api.put(`/me/favorites/color/${encodeURIComponent(name)}`)
      favoriteSet.value.add(name)
      showToast('已收藏')
    }
  } catch {
    showToast('操作失败')
  }
}

async function openAi(color: ChineseColor) {
  aiColor.value = color
  aiDialogVisible.value = true
  aiContent.value = ''

  const poemText = getPoem(color) || color.poem || ''
  const sourceText = getSource(color) || color.source || ''

  aiLoading.value = true
  try {
    const res = await fetch('/api/v1/ai/poem-explain', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        poem: poemText,
        source: sourceText,
        colorName: color.name,
        note: color.note || '',
        user_query: '请从以下五个维度进行深入赏析，要求文字优美、专业：\n1. 意境之美：分析诗句营造的意境与情感\n2. 诗人事迹：诗人的生平简介及其与本诗的关联\n3. 创作背景：诗作的创作年代、历史情境与文化语境\n4. 色彩溯源：该颜色在传统文化中的象征意义与历史渊源\n5. 诵读要点：朗诵时的节奏、语调与情感把控建议',
      })
    })
    const data = await res.json()
    const raw = data.data?.content || data.content || ''
    aiContent.value = raw
      .replace(/^#{1,6}\s+/gm, '## ')
      .replace(/\*\*/g, '「')
      .replace(/\*/g, '')
      .replace(/`{1,3}/g, '')
      .trim() || '暂无解读内容'
  } catch {
    aiContent.value = '解读服务暂时不可用，请稍后再试。'
  } finally {
    aiLoading.value = false
  }
}
</script>

<style scoped>
.palette-page { min-height: 100vh; padding-bottom: 40px; }

/* 顶部导航 */
.app-nav {
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
  background: rgba(248,252,248,0.94);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(158,142,126,0.15);
}
.nav-back {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  background: none; border: none;
  color: var(--ink); font-size: 20px; cursor: pointer;
  border-radius: var(--radius-sm);
}
.nav-title { font-family: var(--font-display); font-size: 18px; color: var(--ink); }
.nav-right { width: 36px; }

/* 简介 */
.intro-card {
  margin: 16px; padding: 20px;
  background: linear-gradient(135deg, rgba(60,102,78,0.05), rgba(90,143,117,0.02));
  border: 1px solid rgba(60,102,78,0.06);
  border-radius: var(--radius-md);
  text-align: center;
}
.intro-text {
  font-family: var(--font-display);
  font-size: 18px; color: var(--ink);
  margin-bottom: 4px;
}
.intro-sub { font-size: 13px; color: var(--stone); }

/* 分类计数 */
.color-meta { padding: 10px 16px 0; }
.color-count { font-size: 12px; color: var(--stone); }

/* Tab */
.palette-tabs :deep(.van-tabs__nav) { background: var(--card-bg); }
.palette-tabs :deep(.van-tab) {
  font-family: var(--font-display);
  font-size: 15px; color: var(--stone);
}
.palette-tabs :deep(.van-tab--active) { color: var(--qinglu); font-weight: 600; }
.palette-tabs :deep(.van-tabs__line) { background: var(--qinglu); }

/* 色块网格 */
.color-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 16px;
}

.color-block {
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  background: var(--card);
}

/* 色块 */
.block-swatch {
  height: 100px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 4px;
  position: relative;
  cursor: pointer;
  transition: transform 0.2s;
}
.block-swatch:active { transform: scale(0.97); }
.swatch-name {
  font-family: var(--font-display);
  font-size: 18px; color: #fff;
  text-shadow: 0 1px 4px rgba(0,0,0,0.3);
}
.swatch-hex {
  font-family: var(--font-sans);
  font-size: 11px; color: rgba(255,255,255,0.85);
  letter-spacing: 1px;
}
.swatch-overlay {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: rgba(0,0,0,0.25);
  opacity: 0; transition: opacity 0.2s;
  gap: 2px;
}
.block-swatch:hover .swatch-overlay,
.block-swatch:active .swatch-overlay { opacity: 1; }
.swatch-poem-count {
  font-size: 11px; color: #fff;
  background: rgba(255,255,255,0.2);
  padding: 2px 8px; border-radius: 10px;
}

/* 诗句 */
.block-poem { padding: 10px 12px 12px; }
.poem-line {
  font-family: var(--font-serif);
  font-size: 12px; color: var(--ink);
  line-height: 1.6; margin-bottom: 4px;
}
.poem-source { font-size: 10px; color: var(--stone-light); }
.poem-dynasty {
  font-size: 10px; color: var(--qinglu);
  background: rgba(60,102,78,0.06);
  padding: 0 4px; border-radius: 3px;
  margin-left: 2px;
}
.poem-keyword { margin-top: 4px; display: flex; align-items: center; gap: 6px; }
.swipe-hint {
  font-size: 10px; color: var(--stone);
  cursor: pointer; text-decoration: underline;
}
.swipe-hint:hover { color: var(--qinglu); }
.poem-loading {
  display: flex; align-items: center;
  height: 20px;
}
.poem-note { font-size: 10px; color: var(--stone); margin-top: 4px; font-style: italic; }

/* 操作按钮 */
.poem-actions { display: flex; gap: 8px; margin-top: 8px; }
.action-btn {
  display: flex; align-items: center; gap: 4px;
  padding: 3px 10px;
  background: var(--card-mid);
  border: 1px solid rgba(158,142,126,0.15);
  border-radius: var(--radius-full);
  font-size: 11px; color: var(--stone);
  cursor: pointer; transition: all 0.2s;
}
.action-btn:hover { background: var(--qinglu); color: #fff; border-color: var(--qinglu); }
.action-btn.active { background: var(--qinglu); color: #fff; border-color: var(--qinglu); }
.ai-btn { color: var(--shiliu); }
.ai-btn:hover { background: var(--shiliu); border-color: var(--shiliu); }
.fav-btn { padding: 3px 8px; }
.fav-btn.fav-active { color: var(--qinglu); border-color: var(--qinglu); background: rgba(60,102,78,0.06); }
.fav-btn:hover { color: var(--qinglu); border-color: var(--qinglu); background: rgba(60,102,78,0.06); }

/* ══════════════════════════════════════════════
   全屏诗集样式
═════════════════════════════════════════════ */
.fullscreen-poem-popup :deep(.van-popup__close-icon) {
  color: rgba(255,255,255,0.8) !important;
  top: 16px; right: 16px;
}

.fs-container {
  width: 100vw; height: 100vh;
  overflow-y: auto;
  padding: 60px 20px 40px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 顶部信息 */
.fs-header {
  text-align: center;
  padding: 8px 0 4px;
}
.fs-color-name {
  font-family: var(--font-display);
  font-size: 36px;
  color: #fff;
  text-shadow: 0 2px 12px rgba(0,0,0,0.4);
  margin-bottom: 4px;
}
.fs-hex {
  font-family: monospace;
  font-size: 13px;
  color: rgba(255,255,255,0.7);
  letter-spacing: 2px;
}
.fs-note {
  font-size: 13px;
  color: rgba(255,255,255,0.75);
  margin-top: 8px;
  font-style: italic;
  text-shadow: 0 1px 4px rgba(0,0,0,0.3);
}

/* 关键词 */
.fs-keywords {
  display: flex; flex-wrap: wrap; gap: 8px;
  justify-content: center;
  padding: 0 8px;
}
.fs-kw-tag {
  font-size: 12px;
  padding: 3px 12px;
  border-radius: 12px;
  backdrop-filter: blur(4px);
}

/* 诗集 */
.fs-poem-list {
  display: flex; flex-direction: column; gap: 20px;
  max-width: 640px; margin: 0 auto; width: 100%;
}
.fs-poem-cards {
  display: flex; flex-direction: column; gap: 20px;
}

.fs-poem-card {
  background: rgba(255,255,255,0.12);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 16px;
  padding: 20px;
  transition: transform 0.2s;
}
.fs-poem-card:hover {
  transform: translateY(-2px);
  background: rgba(255,255,255,0.16);
}

/* 诗句正文 */
.fs-poem-text {
  display: flex; flex-direction: column; gap: 4px;
  margin-bottom: 12px;
}
.fs-line {
  font-family: var(--font-serif);
  font-size: 18px;
  color: rgba(255,255,255,0.85);
  line-height: 1.8;
  text-align: center;
}
.fs-line.matched {
  color: #fff;
  font-weight: 600;
  text-shadow: 0 0 12px rgba(255,255,255,0.5);
}

/* 匹配高亮 */
.fs-match-bar {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 10px 12px;
  background: rgba(255,255,255,0.1);
  border-radius: 10px;
  margin-bottom: 12px;
}
.match-icon {
  color: #ffd700;
  font-size: 14px;
  flex-shrink: 0;
  margin-top: 2px;
}
.fs-matched-line {
  font-family: var(--font-serif);
  font-size: 14px;
  color: rgba(255,255,255,0.9);
  line-height: 1.7;
}

/* 出处 */
.fs-poem-meta {
  display: flex; align-items: baseline; gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.fs-poem-title {
  font-family: var(--font-display);
  font-size: 15px; color: rgba(255,255,255,0.95);
}
.fs-poem-author {
  font-size: 13px; color: rgba(255,255,255,0.65);
}
.fs-dynasty {
  font-size: 11px;
  background: rgba(255,255,255,0.15);
  padding: 1px 6px; border-radius: 4px;
  margin-right: 4px;
}

/* 操作按钮 */
.fs-poem-actions {
  display: flex; gap: 8px; flex-wrap: wrap;
}
.fs-action-btn {
  display: flex; align-items: center; gap: 4px;
  padding: 5px 14px;
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: var(--radius-full);
  color: rgba(255,255,255,0.9);
  font-size: 12px; cursor: pointer;
  transition: all 0.2s;
  backdrop-filter: blur(4px);
}
.fs-action-btn:hover {
  background: rgba(255,255,255,0.25);
  border-color: rgba(255,255,255,0.5);
}
.fs-action-btn:active { transform: scale(0.95); }

/* Loading */
.fs-loading {
  display: flex; flex-direction: column;
  align-items: center; gap: 12px;
  padding: 60px 0;
  color: rgba(255,255,255,0.8);
  font-size: 14px;
}
/* 空状态 */
.fs-empty {
  display: flex; flex-direction: column;
  align-items: center; gap: 8px;
  padding: 60px 0;
}
.fs-empty-icon { font-size: 48px; }
.fs-empty-text {
  font-family: var(--font-display);
  font-size: 18px; color: rgba(255,255,255,0.9);
}
.fs-empty-sub { font-size: 13px; color: rgba(255,255,255,0.5); }

/* 底部关闭 */
.fs-footer {
  text-align: center;
  padding: 12px 0 24px;
  margin-top: auto;
}

/* ══════════════════════════════════════════════
   AI 解读弹窗
═════════════════════════════════════════════ */
.ai-dialog { max-height: 70vh; }
.ai-dialog-content { padding: 20px; }
.ai-header { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
.ai-swatch { width: 48px; height: 48px; border-radius: 8px; flex-shrink: 0; }
.ai-title h3 { font-family: var(--font-display); font-size: 18px; color: var(--ink); margin: 0; }
.ai-hex { font-size: 12px; color: var(--stone); }
.ai-quote {
  padding: 14px; margin-bottom: 12px;
  background: var(--card-bg);
  border-radius: 10px;
  border-left: 3px solid var(--qinglu);
}
.ai-quote p { font-family: var(--font-serif); font-size: 14px; color: var(--ink); line-height: 1.7; }
.ai-source { font-size: 12px; color: var(--stone); margin-top: 4px; }
.ai-loading { display: flex; align-items: center; gap: 8px; padding: 16px 0; color: var(--stone); }
.ai-body { max-height: 50vh; overflow-y: auto; }
.ai-section { margin-bottom: 14px; }
.ai-section-label { font-weight: 600; font-size: 14px; color: var(--ink); margin-bottom: 4px; }
.section-icon { margin-right: 4px; }
.ai-section-text { font-size: 13px; color: var(--stone); line-height: 1.7; }
.ai-text { font-size: 13px; color: var(--stone); line-height: 1.7; white-space: pre-wrap; }
</style>