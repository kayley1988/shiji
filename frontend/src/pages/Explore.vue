<template>
  <div class="explore-page bg-xuanzhi">

    <!-- 顶部导航 -->
    <header class="app-nav">
      <button class="nav-back" @click="$router.back()">
        <van-icon name="arrow-left" />
      </button>
      <span class="nav-title">诗词品鉴</span>
      <span class="nav-right"></span>
    </header>

    <!-- 搜索作者 -->
    <div class="search-bar">
      <van-search
        v-model="authorQuery"
        placeholder="按作者搜索，如：杜甫、李白"
        shape="round"
        background="transparent"
        :show-action="authorQuery.length > 0"
        @search="onAuthorSearch"
        @clear="onAuthorSearch"
      >
        <template #action>
          <div @click="onAuthorSearch">搜索</div>
        </template>
      </van-search>
    </div>

    <!-- 筛选区 -->
    <div class="filter-section">

      <!-- 朝代 -->
      <div class="filter-row">
        <span class="filter-label">朝代</span>
        <div class="filter-chips">
          <span
            class="chip"
            :class="{ active: !activeDynasty }"
            @click="selectDynasty('')"
          >全部</span>
          <span
            v-for="d in filters.dynasties"
            :key="d"
            class="chip"
            :class="{ active: activeDynasty === d }"
            @click="selectDynasty(d)"
          >{{ d }}</span>
        </div>
      </div>

      <!-- 意象（按类别分组） -->
      <div class="filter-block" v-if="filters.imagery_groups.length">
        <div class="filter-label">意象</div>
        <div class="filter-chips">
          <span
            class="chip chip-jade"
            :class="{ active: !activeImagery }"
            @click="selectImagery('')"
          >全部</span>
        </div>
        <div
          v-for="group in filters.imagery_groups"
          :key="group.name"
          class="imagery-group"
        >
          <span class="imagery-group-name">{{ group.name }}</span>
          <div class="filter-chips">
            <span
              v-for="img in group.items"
              :key="img"
              class="chip chip-jade"
              :class="{ active: activeImagery === img }"
              @click="selectImagery(img)"
            >{{ img }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 诗词列表 -->
    <div class="poem-list">
      <div
        v-for="poem in poems"
        :key="poem.id"
        class="poem-card animate-fadeUp"
        @click="openDetail(poem)"
      >
        <div class="poem-head">
          <div class="poem-meta">
            <span class="poem-title">{{ poem.title }}</span>
            <span class="poem-sep">·</span>
            <span class="poem-author">{{ poem.author }}</span>
            <span v-if="poem.dynasty" class="poem-dynasty">{{ poem.dynasty }}</span>
          </div>
        </div>
        <p class="poem-preview">「{{ poem.preview }}」</p>
      </div>

      <!-- 加载状态 -->
      <van-loading v-if="loading" class="list-loading" type="spinner" />
      <van-empty v-else-if="!poems.length" description="暂无诗词，换个条件试试" />

      <!-- 加载更多 -->
      <div v-if="hasMore && !loading" class="load-more" @click="loadMore">
        加载更多 ↓
      </div>
    </div>

    <!-- 诗词详情弹窗（左侧滑出） -->
    <van-popup
      v-model:show="detailVisible"
      position="left"
      :style="{ width: '100%', height: '100%' }"
      class="poem-detail-popup"
      closeable
      close-icon-position="top-left"
    >
      <div v-if="currentPoem" class="poem-detail">
        <div class="detail-content">
          <!-- 标题 -->
          <h2 class="detail-title">{{ currentPoem.title }}</h2>
          <p class="detail-meta">
            {{ currentPoem.author }}
            <span v-if="currentPoem.dynasty"> · {{ currentPoem.dynasty }}</span>
          </p>

          <van-divider />

          <!-- 诗句双栏 -->
          <div class="detail-lines">
            <div
              v-for="(line, i) in currentPoem.lines"
              :key="i"
              class="line-row"
            >
              <p class="line-trad">{{ line.content }}</p>
              <span class="line-sep">｜</span>
              <p class="line-simp">{{ simplifiedLines[i] || '…' }}</p>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="detail-actions">
            <van-button
              size="small"
              :icon="currentPoemSpeaking ? 'stop-circle-o' : 'volume-o'"
              @click="speakPoem"
            >
              {{ currentPoemSpeaking ? '停止' : '朗读全诗' }}
            </van-button>
            <van-button
              size="small"
              icon="chat-o"
              @click="aiExplainPoem"
              :loading="aiLoading"
            >
              AI 解读
            </van-button>
          </div>

          <!-- AI 解读内容 -->
          <transition name="slide-down">
            <div v-if="aiReady" class="ai-explain">
              <h4 class="ai-explain-title">✦ AI 深度解读</h4>

              <!-- 5 板块（时间轴板块单独渲染） -->
              <div
                v-for="(sec, i) in aiSections"
                :key="i"
                class="ai-section"
              >
                <div class="ai-section-label">
                  <span class="ai-section-icon">{{ sectionIcons[i % sectionIcons.length] }}</span>
                  <span>{{ sec.title }}</span>
                </div>
                <p class="ai-section-text">{{ sec.body }}</p>
              </div>

              <!-- 作者生平时间轴 -->
              <div v-if="timeline.length" class="ai-section">
                <div class="ai-section-label">
                  <span class="ai-section-icon">📜</span>
                  <span>作者生平时间轴</span>
                </div>
                <div class="timeline">
                  <div
                    v-for="(ev, i) in timeline"
                    :key="i"
                    class="timeline-item"
                    :class="[i % 2 === 0 ? 'left' : 'right', { highlight: ev.highlight }]"
                  >
                    <div class="timeline-dot" :class="{ highlight: ev.highlight }"></div>
                    <div class="timeline-card" :class="{ highlight: ev.highlight }">
                      <span class="timeline-year">{{ ev.year }}</span>
                      <span class="timeline-event">{{ ev.event }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 作者作品集 -->
              <div v-if="authorWorks.length" class="author-works">
                <div class="ai-section-label">
                  <span class="ai-section-icon">📚</span>
                  <span>{{ authorName }} · 作品集</span>
                </div>
                <div class="works-grid">
                  <div
                    v-for="w in authorWorks"
                    :key="w.id"
                    class="work-card"
                    @click="openWork(w)"
                  >
                    <span class="work-title">{{ w.title }}</span>
                    <span class="work-dynasty">{{ w.dynasty }}</span>
                  </div>
                </div>
                <button class="view-author-all" @click="viewAllByAuthor">
                  查看 {{ authorName }} 全部诗作 →
                </button>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </van-popup>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { api } from '../api'
import { speak, stop, speaking } from '../composables/useSpeech'
import { useOpenCC } from '../composables/useOpenCC'

// ── 列表数据 ─────────────────────────────────────────
const poems = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)

// ── 筛选条件 ─────────────────────────────────────────
const filters = reactive({
  dynasties: [] as string[],
  imagery: [] as string[],
  imagery_groups: [] as { name: string; items: string[] }[],
})
const activeDynasty = ref('')
const activeImagery = ref('')
const authorQuery = ref('')

// ── 详情弹窗 ─────────────────────────────────────────
const detailVisible = ref(false)
const currentPoem = ref<any>(null)
const currentPoemSpeaking = ref(false)
const simplifiedLines = ref<string[]>([])
const aiSections = ref<{ title: string; body: string }[]>([])
const aiLoading = ref(false)
const timeline = ref<{ year: string; event: string; highlight: boolean }[]>([])
const authorWorks = ref<{ id: string; title: string; author: string; dynasty: string }[]>([])
const authorName = ref('')
const aiReady = ref(false)

// ── OpenCC 繁→简 ────────────────────────────────────
const { toSimplified } = useOpenCC()

// ── AI 解读图标（5 板块，时间轴单独渲染）──────────
const sectionIcons = ['🌿', '🏛', '✒️', '🌟']

// ── 加载筛选条件 ─────────────────────────────────────
onMounted(async () => {
  try {
    const res = await api.getExploreFilters()
    const d = res.data
    if (d) {
      filters.dynasties = d.dynasties || []
      filters.imagery = d.imagery || []
      filters.imagery_groups = d.imagery_groups || []
      // 默认选唐诗（最经典）
      if (d.dynasties.includes('唐')) {
        activeDynasty.value = '唐'
      }
    }
  } catch (e) {
    console.error('load filters error:', e)
  }
  await fetchPoems(true)
})

// ── 加载诗词列表 ─────────────────────────────────────
async function fetchPoems(reset = false) {
  if (loading.value) return
  if (reset) { page.value = 1; poems.value = [] }
  loading.value = true

  try {
    const res = await api.getExplorePoems({
      dynasty: activeDynasty.value || undefined,
      author: authorQuery.value || undefined,
      tag_type: activeImagery.value ? 'scene' : undefined,
      tag_name: activeImagery.value || undefined,
      page: page.value,
      page_size: 20,
    })
    const d = res.data
    if (d) {
      if (reset) {
        poems.value = d.poems || []
      } else {
        poems.value.push(...(d.poems || []))
      }
      hasMore.value = d.poems?.length === 20
    }
  } catch (e) {
    console.error('load poems error:', e)
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  page.value++
  await fetchPoems(false)
}

function selectDynasty(d: string) {
  activeDynasty.value = d
  fetchPoems(true)
}

function selectImagery(img: string) {
  activeImagery.value = img
  fetchPoems(true)
}

function onAuthorSearch() {
  fetchPoems(true)
}

// ── 详情 ─────────────────────────────────────────────
async function openDetail(poem: any) {
  currentPoem.value = poem
  aiSections.value = []
  timeline.value = []
  authorWorks.value = []
  authorName.value = poem.author || ''
  aiReady.value = false
  detailVisible.value = true
  currentPoemSpeaking.value = false

  // 拉取完整内容
  try {
    const res = await api.getPoemDetail(poem.id)
    const d = res.data
    if (d) {
      currentPoem.value = {
        ...poem,
        lines: d.lines || [],
      }
    }
  } catch {}

  // 同步转简体（显示在右侧）
  simplifiedLines.value = []
  const rawLines = (currentPoem.value?.lines || []).map((l: any) => l.content || l)
  if (rawLines.length) {
    const fullText = rawLines.join('\n')
    simplifiedLines.value = toSimplified(fullText).split('\n')
  }
}

function speakPoem() {
  if (currentPoemSpeaking.value) {
    stop()
    currentPoemSpeaking.value = false
    return
  }
  const lines = (currentPoem.value?.lines || []).map((l: any) => l.content || l)
  if (!lines.length) return
  // 朗读时用简体（语音识别效果更好）
  speak(toSimplified(lines.join('，')))
  currentPoemSpeaking.value = true
}

async function aiExplainPoem() {
  if (!currentPoem.value) return
  aiLoading.value = true
  aiSections.value = []
  timeline.value = []
  authorWorks.value = []
  aiReady.value = false
  try {
    const poem = currentPoem.value
    const res = await api.aiPoemExplain({
      poem: (poem.lines || []).map((l: any) => l.content || l).join('，'),
      source: `${poem.title} · ${poem.author}`,
      title: poem.title || '',
      author: poem.author || '',
      dynasty: poem.dynasty || '',
      poem_id: poem.id || '',
      colorName: '',
      note: '',
    })
    const d = res.data || {}
    const raw = d.content || ''
    authorName.value = d.author || poem.author || ''
    authorWorks.value = d.works || []

    parseAiContent(raw)
    aiReady.value = true
  } catch {
    aiSections.value = [{ title: '提示', body: 'AI 解读暂时不可用' }]
    aiReady.value = true
  } finally {
    aiLoading.value = false
  }
}

// 解析 AI 返回的 5 板块；「时间轴/生平」板块单独解析为时间轴数据
function parseAiContent(raw: string) {
  aiSections.value = []
  timeline.value = []
  const parts = raw.split(/\n(?=##\s+)/)
  for (const p of parts) {
    const m = p.match(/^##\s+(.+?)\n([\s\S]*)$/)
    if (!m) continue
    const title = m[1].trim()
    const body = m[2].trim()
    if (/时间轴|生平/.test(title)) {
      parseTimeline(body)
    } else {
      aiSections.value.push({ title, body })
    }
  }
  if (!aiSections.value.length && !timeline.value.length) {
    aiSections.value = [{ title: '', body: raw.trim() }]
  }
}

function parseTimeline(body: string) {
  timeline.value = []
  const lines = body.split('\n')
  for (const line of lines) {
    const t = line.replace(/^[-•*·\s]+/, '').trim()
    const m = t.match(/^(\d{3,4})\s*年?\s*[·｜|、:\-—]\s*([\s\S]+)$/)
    if (m) {
      const highlight = /【重点】|（重点）|重点/.test(m[2])
      const event = m[2].replace(/【重点】/g, '').replace(/（重点）/g, '').trim()
      timeline.value.push({ year: `${m[1]}年`, event, highlight })
    }
  }
}

// 点击作品集里的诗，跳转到该诗详情
function openWork(w: any) {
  openDetail(w)
}

// 查看该作者全部诗作：关闭详情，回到列表并自动筛选作者
function viewAllByAuthor() {
  const a = authorName.value || currentPoem.value?.author
  if (!a) return
  detailVisible.value = false
  authorQuery.value = a
  activeDynasty.value = ''
  fetchPoems(true)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
.explore-page { min-height: 100vh; padding-bottom: 30px; }

.app-nav {
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
  background: rgba(250,246,240,0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(158,142,126,0.15);
}
.nav-back {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  background: none; border: none; color: var(--ink);
  font-size: 20px; cursor: pointer; border-radius: var(--radius-sm);
}
.nav-title { font-family: var(--font-display); font-size: 18px; color: var(--ink); }
.nav-right { width: 36px; }

.search-bar { padding: 0 12px; }

.filter-section { padding: 8px 16px 12px; }
.filter-row { margin-bottom: 10px; }
.filter-block { margin-bottom: 12px; }
.filter-label {
  font-size: 11px; color: var(--stone); margin-bottom: 6px;
  display: block;
}
.filter-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.imagery-group {
  margin-top: 10px;
  padding-left: 10px;
  border-left: 2px solid rgba(61,107,74,0.16);
}
.imagery-group-name {
  display: block;
  font-size: 11px; color: var(--jade);
  margin-bottom: 5px;
  font-family: var(--font-display);
}
.chip {
  padding: 3px 12px; border-radius: var(--radius-full);
  font-size: 12px; color: var(--stone);
  background: rgba(158,142,126,0.1);
  cursor: pointer; transition: all 0.2s;
  border: 1px solid transparent;
}
.chip:hover { color: var(--cinnabar); border-color: var(--cinnabar); }
.chip.active { background: var(--cinnabar); color: #fff; border-color: var(--cinnabar); }
.chip-jade.active { background: var(--jade); border-color: var(--jade); }

/* 列表 */
.poem-list { padding: 8px 16px; display: flex; flex-direction: column; gap: 12px; }
.poem-card {
  background: var(--card); border-radius: var(--radius-md);
  padding: 14px 16px; cursor: pointer;
  box-shadow: var(--shadow-sm); transition: all 0.2s;
}
.poem-card:hover { transform: translateY(-1px); box-shadow: var(--shadow-md); }
.poem-head { margin-bottom: 8px; }
.poem-meta { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; }
.poem-title { font-family: var(--font-display); font-size: 16px; color: var(--ink); }
.poem-sep { color: var(--stone-light); }
.poem-author { font-size: 13px; color: var(--stone); }
.poem-dynasty {
  font-size: 10px; padding: 1px 6px; border-radius: var(--radius-full);
  background: rgba(184,148,46,0.1); color: var(--gold);
}
.poem-preview {
  font-family: var(--font-serif); font-size: 13px; color: var(--stone);
  line-height: 1.7;
}

.list-loading { display: flex; justify-content: center; padding: 20px; }
.load-more {
  text-align: center; padding: 14px;
  font-size: 13px; color: var(--stone); cursor: pointer;
}

/* 详情弹窗：左滑全屏 */
.poem-detail-popup { height: 100% !important; max-height: 100% !important; }
.poem-detail { height: 100%; overflow-y: auto; background: var(--parchment); }
.detail-content { padding: 60px 24px 40px; max-width: 640px; margin: 0 auto; }
.detail-title { font-family: var(--font-display); font-size: 24px; color: var(--ink); margin-bottom: 8px; }
.detail-meta { font-size: 14px; color: var(--stone); margin-bottom: 8px; }
.detail-lines { padding: 16px 0; display: flex; flex-direction: column; gap: 4px; }
.line-row { display: flex; align-items: baseline; gap: 10px; }
.line-trad { font-family: var(--font-serif); font-size: 17px; color: var(--ink); line-height: 2.2; flex: 1; letter-spacing: 0.04em; }
.line-sep { color: var(--stone-light); font-size: 14px; flex-shrink: 0; padding-top: 2px; }
.line-simp { font-family: var(--font-serif); font-size: 15px; color: var(--stone); line-height: 2.2; flex: 1; letter-spacing: 0.04em; }
.detail-actions { display: flex; gap: 10px; margin-top: 8px; }

/* AI 解读（国风宣纸排版） */
.ai-explain { margin-top: 16px; }
.ai-explain-title {
  font-family: var(--font-display); font-size: 16px; color: var(--cinnabar);
  margin-bottom: 12px; letter-spacing: 0.06em;
}
.ai-section {
  background: var(--parchment);
  border-bottom: 1px solid rgba(158,142,126,0.22);
  padding: 14px 4px; margin-bottom: 4px;
}
.ai-section-label {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; color: var(--ink); font-family: var(--font-display);
  margin-bottom: 10px; letter-spacing: 0.04em;
}
.ai-section-icon { font-size: 15px; }
.ai-section-text {
  font-family: var(--font-serif); font-size: 14px; color: var(--ink);
  line-height: 2.1; white-space: pre-wrap;
}

/* 时间轴：中间竖线，左右交替 */
.timeline {
  position: relative;
  padding: 8px 0;
  margin-top: 4px;
}
.timeline::before {
  content: '';
  position: absolute;
  left: 50%; top: 0; bottom: 0;
  width: 1px; background: rgba(158,142,126,0.42);
  transform: translateX(-50%);
}
.timeline-item {
  position: relative;
  width: 50%;
  box-sizing: border-box;
  padding-bottom: 18px;
}
.timeline-item.left { padding-right: 22px; text-align: right; }
.timeline-item.right { margin-left: 50%; padding-left: 22px; text-align: left; }
.timeline-dot {
  position: absolute;
  top: 4px;
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--stone-light);
  border: 2px solid var(--parchment);
  box-shadow: 0 0 0 1px rgba(158,142,126,0.5);
  z-index: 1;
}
.timeline-item.left .timeline-dot { right: -6px; }
.timeline-item.right .timeline-dot { left: -6px; }
.timeline-dot.highlight {
  background: var(--cinnabar);
  box-shadow: 0 0 0 1px var(--cinnabar);
}
.timeline-card {
  display: inline-block;
  background: var(--card);
  border: 1px solid rgba(158,142,126,0.16);
  border-radius: 8px;
  padding: 8px 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  max-width: 100%;
}
.timeline-card.highlight {
  border-color: var(--cinnabar);
  background: rgba(168,79,54,0.06);
}
.timeline-year {
  display: block;
  font-family: var(--font-display);
  font-size: 12px; color: var(--cinnabar);
  margin-bottom: 3px;
}
.timeline-event {
  font-family: var(--font-serif);
  font-size: 13px; color: var(--ink);
  line-height: 1.6;
}

/* 作者作品集 */
.author-works { margin-top: 12px; }
.works-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-top: 6px;
}
.work-card {
  background: var(--card);
  border: 1px solid rgba(158,142,126,0.16);
  border-radius: 8px;
  padding: 10px 12px;
  cursor: pointer;
  display: flex; flex-direction: column; gap: 4px;
  transition: all 0.2s;
}
.work-card:hover { border-color: var(--cinnabar); box-shadow: 0 2px 10px rgba(168,79,54,0.08); }
.work-title { font-family: var(--font-display); font-size: 13px; color: var(--ink); }
.work-dynasty { font-size: 11px; color: var(--stone); }
.view-author-all {
  display: block;
  margin: 12px auto 0;
  padding: 6px 18px;
  background: none;
  border: 1px solid var(--cinnabar);
  color: var(--cinnabar);
  border-radius: var(--radius-full);
  font-size: 13px; font-family: var(--font-display);
  cursor: pointer;
  transition: all 0.2s;
}
.view-author-all:hover { background: var(--cinnabar); color: #fff; }

.slide-down-enter-active { animation: fadeUp 0.3s ease; }
.slide-down-leave-active { display: none; }
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.animate-fadeUp { animation: fadeUp 0.3s ease both; }
</style>
