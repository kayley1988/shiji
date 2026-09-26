<template>
  <div class="my-colors-page bg-xuanzhi">
    <!-- 顶部 -->
    <header class="page-header">
      <div class="header-left" @click="$router.back()">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M12 4l-6 6 6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h1 class="header-title">我的中国色</h1>
      <div class="header-right"></div>
    </header>

    <!-- 统计 -->
    <div class="stats-bar animate-fadeUp">
      <div class="stat-chip">
        <span class="sc-num">{{ colors.length }}</span>
        <span class="sc-label">已收藏</span>
      </div>
      <div class="stat-chip">
        <span class="sc-num">{{ uniqueDynasties }}</span>
        <span class="sc-label">涉及诗人</span>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state animate-fadeUp" v-if="!loading && colors.length === 0">
      <div class="empty-icon">🎨</div>
      <p class="empty-title">尚未收藏任何颜色</p>
      <p class="empty-sub">去首页「今日色卡」答题，解锁你的第一色</p>
      <button class="go-btn" @click="$router.push('/')">去探索</button>
    </div>

    <!-- 加载 -->
    <div class="loading-state" v-if="loading">
      <div class="spinner"></div>
      <p>加载中…</p>
    </div>

    <!-- 颜色画廊 -->
    <div class="color-gallery" v-else>
      <div
        v-for="(c, i) in colors"
        :key="c.id || i"
        class="color-card"
        :style="cardStyle(c)"
        :class="'animate-fadeUp delay-' + Math.min(i, 4)"
        @click="showDetail(c)"
      >
        <!-- 背景色 -->
        <div class="cc-bg" :style="{ background: c.hex }"></div>

        <!-- 内容 -->
        <div class="cc-content">
          <div class="cc-header">
            <span class="cc-name">{{ c.name }}</span>
            <span class="cc-pinyin">{{ c.pinyin }}</span>
          </div>

          <!-- 诗卡 -->
          <div class="cc-poem" v-if="c.poem">
            <p class="cc-verse">「{{ c.verse }}」</p>
            <p class="cc-meta">{{ c.dynasty }} · {{ c.author }}</p>
          </div>

          <!-- 底部 -->
          <div class="cc-footer">
            <span class="cc-date">{{ c.date }}</span>
            <button class="cc-remove" @click.stop="removeColor(c)">✕</button>
          </div>
        </div>

        <!-- 印章 -->
        <div class="cc-seal" v-if="c.poem">詩</div>
      </div>
    </div>

    <div class="safe-bottom"></div>

    <!-- 颜色详情弹窗 -->
    <Teleport to="body">
      <div class="detail-overlay" v-if="detailColor" @click.self="detailColor = null">
        <div class="detail-card" :style="{ background: detailColor.hex }">
          <button class="detail-close" @click="detailColor = null">
            <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
              <path d="M4 4l12 12M16 4L4 16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
          <div class="detail-content">
            <p class="detail-name">{{ detailColor.name }}</p>
            <p class="detail-pinyin">{{ detailColor.pinyin }}</p>
            <div class="detail-hex">{{ detailColor.hex }}</div>
            <div class="detail-poem" v-if="detailColor.poem">
              <p class="detail-verse">「{{ detailColor.verse }}」</p>
              <p class="detail-meta">{{ detailColor.dynasty }} · {{ detailColor.author }}</p>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'

// ── 数据 ──────────────────────────────────────
const loading = ref(true)
const colors = ref<any[]>([])
const detailColor = ref<any>(null)

// ── 统计 ──────────────────────────────────────
const uniqueDynasties = computed(() => {
  const set = new Set(colors.value.map(c => c.dynasty).filter(Boolean))
  return set.size
})

// ── 卡片样式 ──────────────────────────────────────
function cardStyle(c: any) {
  const hex = c.hex || '#C8B89A'
  const dark = isColorDark(hex)
  return {
    '--cc-bg': hex,
    '--cc-text': dark ? '#F5F0E8' : '#2C2420',
    '--cc-muted': dark ? 'rgba(245,240,232,0.6)' : 'rgba(44,36,32,0.55)',
    '--cc-accent': dark ? '#D4A86A' : '#8B2942',
  }
}

function isColorDark(hex: string) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return (r * 299 + g * 587 + b * 114) / 1000 < 128
}

// ── 加载收藏的诗 ──────────────────────────────────────
async function loadMyColors() {
  loading.value = true
  try {
    const res = await api.getFavorites('poem')
    const favs = res.data?.favorites || res.data || []

    // 过滤出有颜色信息的收藏
    const colored = favs
      .filter((f: any) => f.associated_color_name || f.color_name)
      .map((f: any) => ({
        id: f.id,
        name: f.associated_color_name || f.color_name || '未名',
        pinyin: f.associated_color_pinyin || f.color_pinyin || '',
        hex: f.associated_color_hex || f.color_hex || '#C8B89A',
        poem: f.target || {},
        verse: f.target?.lines?.[0]?.content || f.target?.content?.[0] || f.target?.title || '',
        author: f.target?.author || '',
        dynasty: f.target?.dynasty || '',
        date: f.created_at?.slice(0, 10) || new Date().toISOString().slice(0, 10),
      }))

    colors.value = colored
  } catch (e) {
    console.error('加载我的颜色失败', e)
    colors.value = []
  } finally {
    loading.value = false
  }
}

// ── 删除 ──────────────────────────────────────
async function removeColor(c: any) {
  try {
    await api.removeFavorite('poem', c.id)
    colors.value = colors.value.filter(x => x.id !== c.id)
  } catch (e) {
    console.error('删除失败', e)
  }
}

// ── 详情 ──────────────────────────────────────
function showDetail(c: any) {
  detailColor.value = c
}

onMounted(loadMyColors)
</script>

<style scoped>
.my-colors-page { min-height: 100vh; }

/* ── 顶部 ─────────────────────────────── */
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; background: var(--card);
}
.header-left { width: 40px; cursor: pointer; }
.header-title { font-size: 16px; font-weight: 600; color: var(--yanhong); }
.header-right { width: 40px; }

/* ── 统计条 ─────────────────────────────── */
.stats-bar {
  display: flex; gap: 12px; padding: 12px 16px 8px;
}
.stat-chip {
  display: flex; align-items: baseline; gap: 4px;
  background: var(--card); border-radius: 8px; padding: 6px 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.sc-num { font-size: 20px; font-weight: 700; color: #333; }
.sc-label { font-size: 12px; color: #999; }

/* ── 加载 ─────────────────────────────── */
.loading-state {
  display: flex; flex-direction: column; align-items: center;
  padding: 60px; gap: 12px; color: #999;
}
.spinner {
  width: 32px; height: 32px; border-radius: 50%;
  border: 2px solid rgba(212,175,55,0.15);
  border-top-color: var(--yanhong);
  animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── 空状态 ─────────────────────────────── */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  padding: 80px 40px; text-align: center; gap: 10px;
}
.empty-icon { font-size: 48px; margin-bottom: 10px; }
.empty-title { font-size: 16px; color: #333; font-weight: 600; }
.empty-sub { font-size: 13px; color: #999; }
.go-btn {
  margin-top: 10px; padding: 10px 28px; border-radius: 20px;
  border: none; background: var(--yanhong); color: #fff;
  font-size: 14px; cursor: pointer;
}

/* ── 画廊 ─────────────────────────────── */
.color-gallery {
  display: flex; flex-direction: column; gap: 12px;
  padding: 8px 16px 20px;
}

.color-card {
  position: relative; border-radius: 14px; overflow: hidden;
  min-height: 120px; cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: transform 0.2s, box-shadow 0.2s;
}
.color-card:active { transform: scale(0.98); }

.cc-bg {
  position: absolute; inset: 0;
  background: var(--cc-bg);
  transition: transform 0.3s;
}
.color-card:hover .cc-bg { transform: scale(1.03); }

.cc-content {
  position: relative; z-index: 1;
  padding: 14px 16px;
  display: flex; flex-direction: column; gap: 8px;
  min-height: 120px;
}

.cc-header { display: flex; align-items: baseline; gap: 8px; }
.cc-name {
  font-family: var(--font-display); font-size: 26px;
  color: var(--cc-text); letter-spacing: 0.05em;
}
.cc-pinyin { font-size: 11px; color: var(--cc-muted); }

.cc-poem { flex: 1; }
.cc-verse {
  font-family: var(--font-serif); font-size: 14px;
  color: var(--cc-text); line-height: 1.7;
  opacity: 0.85;
}
.cc-meta { font-size: 12px; color: var(--cc-muted); margin-top: 4px; }

.cc-footer {
  display: flex; justify-content: space-between; align-items: center;
}
.cc-date { font-size: 11px; color: var(--cc-muted); }
.cc-remove {
  width: 24px; height: 24px; border-radius: 50%;
  background: rgba(0,0,0,0.1); border: none; cursor: pointer;
  font-size: 12px; color: var(--cc-text); opacity: 0.6;
  transition: opacity 0.2s;
}
.cc-remove:hover { opacity: 1; }

.cc-seal {
  position: absolute; bottom: 12px; right: 12px;
  width: 36px; height: 36px; border-radius: 4px;
  border: 2px solid var(--cc-accent);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display); font-size: 18px;
  color: var(--cc-accent); opacity: 0.7; transform: rotate(-6deg);
}

/* ── 详情弹窗 ─────────────────────────────── */
.detail-overlay {
  position: fixed; inset: 0; z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,0.5); backdrop-filter: blur(2px);
}
.detail-card {
  width: min(90vw, 340px); border-radius: 20px;
  padding: 30px 24px; position: relative;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  color: #fff;
}
.detail-close {
  position: absolute; top: 12px; right: 12px;
  width: 32px; height: 32px; border-radius: 50%;
  background: rgba(0,0,0,0.2); border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
}
.detail-content { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.detail-name { font-family: var(--font-display); font-size: 36px; letter-spacing: 0.1em; }
.detail-pinyin { font-size: 12px; opacity: 0.7; }
.detail-hex {
  font-size: 12px; padding: 4px 14px; border-radius: 12px;
  background: rgba(255,255,255,0.15); margin-top: 4px;
  font-family: monospace; letter-spacing: 0.05em;
}
.detail-poem { margin-top: 12px; text-align: center; }
.detail-verse { font-family: var(--font-serif); font-size: 17px; line-height: 1.8; }
.detail-meta { font-size: 12px; opacity: 0.7; margin-top: 6px; }

.safe-bottom { height: 40px; }
</style>
