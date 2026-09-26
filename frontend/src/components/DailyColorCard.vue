<template>
  <Teleport to="body">
    <div class="color-card-overlay" @click.self="$emit('close')">
      <div class="color-card" :style="cardStyle">

        <!-- 关闭按钮 -->
        <button class="close-btn" @click="$emit('close')" aria-label="关闭">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M4 4l12 12M16 4L4 16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </button>

        <!-- 加载状态 -->
        <div class="loading-state" v-if="loading">
          <p class="loading-text">墨香徐来…</p>
        </div>

        <!-- 色卡主体 -->
        <template v-else-if="todayTheme">
          <!-- 宣纸纹理层 -->
          <div class="paper-texture"></div>

          <!-- 顶部：节气 + 关键词 -->
          <div class="card-header animate-item" data-step="1">
            <div class="solar-term-badge" v-if="todayTheme.solar_term">
              <span class="st-icon">❄️</span>
              <span class="st-name">{{ todayTheme.solar_term.name }}</span>
              <span class="st-element" v-if="todayTheme.solar_term.element">
                五行·{{ todayTheme.solar_term.element }}
              </span>
            </div>
            <div class="keyword-row" v-if="todayTheme.keywords?.length">
              <span class="keyword" v-for="kw in todayTheme.keywords.slice(0, 5)" :key="kw">{{ kw }}</span>
            </div>
          </div>

          <!-- 主色名 -->
          <div class="main-color animate-item" data-step="2">
            <div class="color-reveal-ring" :style="{ borderColor: mainColor.hex }"></div>
            <div class="color-name">
              <span class="color-char">{{ mainColor.name }}</span>
              <span class="color-pinyin">{{ mainColor.pinyin }}</span>
            </div>
          </div>

          <!-- 诗文展示（多首滑动） -->
          <div class="poem-area animate-item" data-step="3">
            <div class="poem-carousel" v-if="poems.length">
              <div class="poem-card" :key="currentPoemIndex">
                <div class="poem-text">「{{ currentPoem.line }}」</div>
                <div class="poem-meta">
                  <span class="poem-dynasty">{{ currentPoem.dynasty }}</span>
                  <span class="poem-sep">·</span>
                  <span class="poem-author">{{ currentPoem.author }}</span>
                </div>
                <div class="poem-title" v-if="currentPoem.title">《{{ currentPoem.title }}》</div>
              </div>
            </div>
            <!-- 滑动指示 -->
            <div class="carousel-dots" v-if="poems.length > 1">
              <span
                v-for="i in poems.length"
                :key="i"
                class="dot"
                :class="{ active: i - 1 === currentPoemIndex }"
                @click="currentPoemIndex = i - 1"
              ></span>
            </div>
          </div>

          <!-- 印章 -->
          <div class="seal-area animate-item" data-step="4" v-if="currentPoem.author">
            <div class="poem-seal">詩</div>
          </div>

          <!-- 操作按钮 -->
          <div class="card-actions animate-item" data-step="5">
            <button class="action-btn btn-skip" @click="skipPoem" v-if="poems.length > 1">
              <span class="btn-icon">↻</span>
              <span>换一首</span>
            </button>
            <button class="action-btn btn-fav" @click="toggleFav" :class="{ favorited: isFaved }">
              <span class="btn-icon">{{ isFaved ? '♥' : '♡' }}</span>
              <span>{{ isFaved ? '已收藏' : '收藏此诗' }}</span>
            </button>
          </div>

          <!-- 底部：再来一色 -->
          <button class="next-color-btn animate-item" data-step="6" @click="revealNext">
            <span>再来一色</span>
            <span class="next-arrow">→</span>
          </button>
        </template>

        <!-- 全部看完了 -->
        <div class="done-state" v-else-if="!loading && allShown">
          <div class="done-seal">終</div>
          <p class="done-text">今日色卡已览尽</p>
          <p class="done-sub">明日再来，与诗意重逢</p>
          <button class="action-btn" @click="$emit('close')">返回</button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { api } from '../api'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits(['close', 'fav'])

// ── 数据 ──────────────────────────────────────
const loading = ref(true)
const todayTheme = ref<any>(null)
const poems = ref<any[]>([])
const dailyColors = ref<any[]>([])   // 今日主打色列表
const colorIndex = ref(0)             // 当前色
const currentPoemIndex = ref(0)
const isFaved = ref(false)
const allShown = ref(false)

// ── 主色（从 dailyColors 取，或 fallback） ────
const mainColor = computed(() => {
  if (dailyColors.value.length > 0) {
    return dailyColors.value[colorIndex.value % dailyColors.value.length]
  }
  // Fallback：根据节气关键字猜颜色
  const kw = todayTheme.value?.keywords?.[0] || ''
  const colorMap: Record<string, any> = {
    '寒': { name: '玄青', pinyin: 'xuán qīng', hex: '#1a2a3a' },
    '雪': { name: '月白', pinyin: 'yuè bái', hex: '#d8e8f0' },
    '梅': { name: '胭脂', pinyin: 'yān zhī', hex: '#8B2942' },
    '风': { name: '艾绿', pinyin: 'ài lǜ', hex: '#7A9A6A' },
    '月': { name: '藕荷', pinyin: 'ǒu hé', hex: '#C4909A' },
    '花': { name: '桃夭', pinyin: 'táo yāo', hex: '#E8A0B0' },
    '雨': { name: '青黛', pinyin: 'qīng dài', hex: '#4A6B7C' },
    '春': { name: '鹅黄', pinyin: 'é huáng', hex: '#F5E090' },
    '秋': { name: '秋香', pinyin: 'qiū xiāng', hex: '#9B7A4A' },
    '夏': { name: '翠涛', pinyin: 'cuì tāo', hex: '#4A8B6A' },
    '冬': { name: '霜白', pinyin: 'shuāng bái', hex: '#E0E8EC' },
  }
  return colorMap[kw] || { name: '青梅', pinyin: 'qīng méi', hex: '#8BAF7A' }
})

// ── 当前诗 ──────────────────────────────────────
const currentPoem = computed(() => poems.value[currentPoemIndex.value] || {})

// ── 卡片背景 ──────────────────────────────────────
const cardStyle = computed(() => {
  const hex = mainColor.value.hex || '#F5F0E8'
  const isDark = isColorDark(hex)
  const textColor = isDark ? '#F5F0E8' : '#2C2420'
  return {
    '--card-bg': hex,
    '--text-color': textColor,
    '--text-muted': isDark ? 'rgba(245,240,232,0.65)' : 'rgba(44,36,32,0.55)',
    '--accent': isDark ? '#D4A86A' : '#8B2942',
  }
})

// 节气关键字 → 预设色列表
const FALLBACK_COLORS: Record<string, any[]> = {
  '寒': [
    { name: '玄青', pinyin: 'xuán qīng', hex: '#1a2a3a' },
    { name: '霜白', pinyin: 'shuāng bái', hex: '#E8EEF0' },
    { name: '月白', pinyin: 'yuè bái', hex: '#D0E8F0' },
  ],
  '雪': [
    { name: '月白', pinyin: 'yuè bái', hex: '#D0E8F0' },
    { name: '霜白', pinyin: 'shuāng bái', hex: '#E8EEF0' },
    { name: '玄青', pinyin: 'xuán qīng', hex: '#1a2a3a' },
  ],
  '梅': [
    { name: '胭脂', pinyin: 'yān zhī', hex: '#8B2942' },
    { name: '藕荷', pinyin: 'ǒu hé', hex: '#C4909A' },
    { name: '玄青', pinyin: 'xuán qīng', hex: '#1a2a3a' },
  ],
  '春': [
    { name: '鹅黄', pinyin: 'é huáng', hex: '#F5E090' },
    { name: '桃夭', pinyin: 'táo yāo', hex: '#E8A0B0' },
    { name: '青梅', pinyin: 'qīng méi', hex: '#8BAF7A' },
  ],
  '秋': [
    { name: '秋香', pinyin: 'qiū xiāng', hex: '#9B7A4A' },
    { name: '赭石', pinyin: 'zhě shí', hex: '#8B6A4A' },
    { name: '胭脂', pinyin: 'yān zhī', hex: '#8B2942' },
  ],
  '夏': [
    { name: '翠涛', pinyin: 'cuì tāo', hex: '#4A8B6A' },
    { name: '青梅', pinyin: 'qīng méi', hex: '#8BAF7A' },
    { name: '月白', pinyin: 'yuè bái', hex: '#D0E8F0' },
  ],
  '冬': [
    { name: '霜白', pinyin: 'shuāng bái', hex: '#E8EEF0' },
    { name: '玄青', pinyin: 'xuán qīng', hex: '#1a2a3a' },
    { name: '月白', pinyin: 'yuè bái', hex: '#D0E8F0' },
  ],
  '月': [
    { name: '月白', pinyin: 'yuè bái', hex: '#D0E8F0' },
    { name: '藕荷', pinyin: 'ǒu hé', hex: '#C4909A' },
    { name: '玄青', pinyin: 'xuán qīng', hex: '#1a2a3a' },
  ],
  '花': [
    { name: '桃夭', pinyin: 'táo yāo', hex: '#E8A0B0' },
    { name: '鹅黄', pinyin: 'é huáng', hex: '#F5E090' },
    { name: '胭脂', pinyin: 'yān zhī', hex: '#8B2942' },
  ],
  '雨': [
    { name: '青黛', pinyin: 'qīng dài', hex: '#4A6B7C' },
    { name: '玄青', pinyin: 'xuán qīng', hex: '#1a2a3a' },
    { name: '霜白', pinyin: 'shuāng bái', hex: '#E8EEF0' },
  ],
  '风': [
    { name: '艾绿', pinyin: 'ài lǜ', hex: '#7A9A6A' },
    { name: '青梅', pinyin: 'qīng méi', hex: '#8BAF7A' },
    { name: '月白', pinyin: 'yuè bái', hex: '#D0E8F0' },
  ],
  '年': [
    { name: '胭脂', pinyin: 'yān zhī', hex: '#8B2942' },
    { name: '赭石', pinyin: 'zhě shí', hex: '#8B6A4A' },
    { name: '秋香', pinyin: 'qiū xiāng', hex: '#9B7A4A' },
  ],
}

function buildFallbackColors(keywords: string[]): any[] {
  for (const kw of keywords) {
    if (FALLBACK_COLORS[kw]) return FALLBACK_COLORS[kw]
  }
  return [
    { name: '青梅', pinyin: 'qīng méi', hex: '#8BAF7A' },
    { name: '玄青', pinyin: 'xuán qīng', hex: '#1a2a3a' },
    { name: '胭脂', pinyin: 'yān zhī', hex: '#8B2942' },
    { name: '月白', pinyin: 'yuè bái', hex: '#D0E8F0' },
    { name: '鹅黄', pinyin: 'é huáng', hex: '#F5E090' },
  ]
}

function isColorDark(hex: string) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return (r * 299 + g * 587 + b * 114) / 1000 < 128
}

// ── 加载数据 ──────────────────────────────────────
async function loadToday() {
  loading.value = true
  allShown.value = false
  colorIndex.value = 0
  currentPoemIndex.value = 0
  poems.value = []
  isFaved.value = false

  try {
    // 1. 获取今日主题（节气+意象）
    const themeRes = await api.getDailyTheme()
    todayTheme.value = themeRes.data.data

    // 2. 获取今日主打色列表（用 daily-theme keywords 匹配）
    const kw = todayTheme.value?.keywords?.[0] || '寒'
    const colorRes = await api.getColorPoems(kw, 5)
    const colorData = colorRes.data.data

    // dailyColors 来自色·诗匹配 API（如果没有专门字段，从节气关键字派生）
    if (colorData?.colors?.length) {
      dailyColors.value = colorData.colors.slice(0, 5)
    } else if (Array.isArray(colorData) && colorData.length) {
      // 直接是 poems 数组，用诗来派生颜色
      dailyColors.value = colorData.map((p: any, i: number) => ({
        name: p.associated_color_name || ['青梅', '胭脂', '玄青', '月白', '鹅黄', '藕荷', '艾绿', '秋香'][i % 8],
        pinyin: p.associated_color_pinyin || '',
        hex: p.associated_color_hex || '#C8B89A',
      }))
    } else {
      // 完全 fallback：节气关键字 → 预设色
      dailyColors.value = buildFallbackColors(todayTheme.value?.keywords || [])
    }

    // 3. 获取匹配的诗
    if (colorData?.poems?.length) {
      poems.value = colorData.poems.slice(0, 5)
    } else if (colorData?.verses?.length) {
      poems.value = colorData.verses
    } else if (Array.isArray(colorData) && colorData.length) {
      // fallback: 直接是数组
      poems.value = colorData.slice(0, 5)
    }

    // 3. 获取匹配的诗（/poems 只返回摘要，需逐条取正文）
    const rawPoems = (colorData?.poems?.length ? colorData.poems
      : colorData?.verses?.length ? colorData.verses
      : Array.isArray(colorData) ? colorData : []) as any[]

    if (rawPoems.length) {
      // 取最多3首，逐条补全正文
      const top3 = rawPoems.slice(0, 3)
      const enriched = await Promise.all(
        top3.map(async (p: any) => {
          try {
            const detail = await api.getPoemDetail(p.id)
            const d = detail.data.data
            const lines: any[] = d.lines || []
            return {
              ...p,
              line: lines[0]?.content || p.title || '诗',
              title: d.title || p.title,
              dynasty: d.dynasty || p.dynasty,
              author: d.author || p.author,
            }
          } catch {
            return { ...p, line: p.title || '诗' }
          }
        })
      )
      poems.value = enriched
    }
  } catch (e) {
    console.error('加载今日色卡失败', e)
  } finally {
    loading.value = false
    await nextTick()
    playRevealAnimation()
  }
}

// ── 动画 ──────────────────────────────────────
function playRevealAnimation() {
  const items = document.querySelectorAll('.animate-item')
  items.forEach((el, i) => {
    const step = parseInt((el as HTMLElement).dataset.step || '0')
    ;(el as HTMLElement).style.animationDelay = `${(step - 1) * 0.25}s`
    ;(el as HTMLElement).classList.add('anim-in')
  })
}

// ── 换一首诗 ──────────────────────────────────────
function skipPoem() {
  if (poems.value.length <= 1) return
  const next = (currentPoemIndex.value + 1) % poems.value.length
  currentPoemIndex.value = next
  isFaved.value = false
}

// ── 收藏 ──────────────────────────────────────
async function toggleFav() {
  const poem = currentPoem.value
  if (!poem?.id) return
  try {
    if (isFaved.value) {
      await api.deleteFavorite('poem', poem.id)
      isFaved.value = false
    } else {
      await api.addFavorite('poem', poem.id)
      isFaved.value = true
    }
    emit('fav', { poem, favorited: isFaved.value })
  } catch (e) {
    console.error('收藏失败', e)
  }
}

// ── 再来一色 ──────────────────────────────────────
function revealNext() {
  if (dailyColors.value.length <= 1) {
    allShown.value = true
    return
  }
  colorIndex.value = (colorIndex.value + 1) % dailyColors.value.length
  currentPoemIndex.value = 0
  isFaved.value = false

  // 重触发动画
  const items = document.querySelectorAll('.animate-item')
  items.forEach(el => {
    ;(el as HTMLElement).classList.remove('anim-in')
    void (el as HTMLElement).offsetWidth // reflow
    ;(el as HTMLElement).classList.add('anim-in')
  })
}

onMounted(() => {
  if (props.open) loadToday()
})

watch(() => props.open, (val) => {
  if (val) loadToday()
})
</script>

<style scoped>
/* ── 全屏蒙层 ─────────────────────────── */
.color-card-overlay {
  position: fixed; inset: 0; z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(2px);
}

/* ── 色卡主体 ─────────────────────────── */
.color-card {
  position: relative;
  width: min(90vw, 380px);
  min-height: min(80vh, 580px);
  background: var(--card-bg, #F5F0E8);
  border-radius: 20px;
  display: flex; flex-direction: column;
  align-items: center;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* ── 宣纸纹理 ─────────────────────────── */
.paper-texture {
  position: absolute; inset: 0;
  background:
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  pointer-events: none;
  border-radius: 20px;
}

/* ── 关闭按钮 ─────────────────────────── */
.close-btn {
  position: absolute; top: 14px; right: 14px; z-index: 10;
  width: 36px; height: 36px; border-radius: 50%;
  background: rgba(0, 0, 0, 0.12); border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: var(--text-color, #2C2420);
  transition: background 0.2s;
}
.close-btn:hover { background: rgba(0, 0, 0, 0.22); }

/* ── 加载状态 ─────────────────────────── */
.loading-state {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 16px;
  color: var(--text-muted, rgba(44,36,32,0.55));
}
.loading-text {
  font-family: var(--font-serif); font-size: 16px; color: var(--text-muted);
}

/* ── 动画入场 ─────────────────────────── */
.animate-item {
  opacity: 0;
  transform: translateY(12px);
}
.animate-item.anim-in {
  animation: fadeSlideIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}
@keyframes fadeSlideIn {
  to { opacity: 1; transform: translateY(0); }
}

/* ── 节气头部 ─────────────────────────── */
.card-header {
  width: 100%; padding: 20px 20px 0;
  display: flex; flex-direction: column; align-items: center; gap: 8px;
}
.solar-term-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 12px; border-radius: 20px;
  background: rgba(0, 0, 0, 0.1);
  font-size: 12px; color: var(--text-color);
}
.st-icon { font-size: 14px; }
.st-name { font-weight: 600; }
.st-element { opacity: 0.7; }

.keyword-row {
  display: flex; gap: 6px; flex-wrap: wrap; justify-content: center;
}
.keyword {
  padding: 2px 10px; border-radius: 12px;
  background: rgba(0, 0, 0, 0.08);
  font-size: 11px; color: var(--text-muted);
}

/* ── 主色名 ─────────────────────────── */
.main-color {
  display: flex; flex-direction: column; align-items: center;
  margin: 20px 0 12px;
}
.color-reveal-ring {
  width: 120px; height: 120px; border-radius: 50%;
  border: 2px solid;
  display: flex; align-items: center; justify-content: center;
}
.color-name { text-align: center; margin-top: 10px; }
.color-char {
  display: block; font-family: var(--font-display);
  font-size: 32px; color: var(--text-color); letter-spacing: 0.1em;
}
.color-pinyin {
  display: block; font-size: 11px; color: var(--text-muted);
  font-family: var(--font-serif); margin-top: 2px;
}

/* ── 诗文区 ─────────────────────────── */
.poem-area {
  width: 100%; padding: 0 20px;
  display: flex; flex-direction: column; align-items: center; gap: 10px;
  flex: 1;
}
.poem-card {
  text-align: center; padding: 12px 8px;
  width: 100%;
  animation: poemFadeIn 0.5s ease;
}
@keyframes poemFadeIn { from { opacity: 0; } to { opacity: 1; } }
.poem-text {
  font-family: var(--font-serif); font-size: 18px;
  color: var(--text-color); line-height: 1.8; margin-bottom: 8px;
}
.poem-meta {
  display: flex; justify-content: center; gap: 6px;
  font-size: 13px; color: var(--text-muted);
}
.poem-sep { opacity: 0.5; }
.poem-title {
  font-size: 12px; color: var(--text-muted); margin-top: 2px;
}
.carousel-dots {
  display: flex; gap: 6px; justify-content: center; margin-top: 6px;
}
.dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: rgba(0, 0, 0, 0.15); cursor: pointer;
  transition: all 0.2s;
}
.dot.active { background: var(--accent); width: 18px; border-radius: 3px; }

/* ── 印章 ─────────────────────────── */
.seal-area {
  position: absolute; bottom: 90px; right: 18px;
}
.poem-seal {
  width: 40px; height: 40px; border-radius: 4px;
  border: 2px solid var(--accent, #8B2942);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display); font-size: 20px;
  color: var(--accent, #8B2942);
  transform: rotate(-8deg); opacity: 0.7;
}

/* ── 操作按钮 ─────────────────────────── */
.card-actions {
  display: flex; gap: 10px; margin-top: auto; padding: 12px 20px 4px;
}
.action-btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 10px; border-radius: 12px; border: none; cursor: pointer;
  font-size: 13px; transition: all 0.2s;
}
.btn-skip {
  background: rgba(0, 0, 0, 0.08); color: var(--text-muted);
}
.btn-skip:active { background: rgba(0, 0, 0, 0.14); }
.btn-fav {
  background: rgba(0, 0, 0, 0.08); color: var(--text-color);
}
.btn-fav:active { background: rgba(0, 0, 0, 0.14); }
.btn-fav.favorited {
  background: rgba(139, 41, 66, 0.12);
  color: #8B2942;
}
.btn-icon { font-size: 16px; }

/* ── 再来一色 ─────────────────────────── */
.next-color-btn {
  width: calc(100% - 40px); margin: 0 20px 20px;
  padding: 10px; border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  background: transparent; cursor: pointer;
  display: flex; align-items: center; justify-content: space-between;
  font-size: 13px; color: var(--text-muted);
  transition: all 0.2s;
}
.next-color-btn:active {
  background: rgba(0, 0, 0, 0.06);
}
.next-arrow { font-size: 16px; }

/* ── 全部看完 ─────────────────────────── */
.done-state {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 14px;
}
.done-seal {
  width: 60px; height: 60px; border-radius: 8px;
  border: 3px solid var(--accent);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display); font-size: 32px; color: var(--accent);
  transform: rotate(-8deg);
}
.done-text {
  font-family: var(--font-display); font-size: 18px; color: var(--text-color);
}
.done-sub { font-size: 13px; color: var(--text-muted); }
</style>
