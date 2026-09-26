<template>
  <div class="badges-page bg-xuanzhi">

    <!-- 顶部 -->
    <header class="page-header">
      <div class="header-left" @click="$router.back()">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M12 4l-6 6 6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h1 class="header-title">徽章馆</h1>
      <div class="header-right"></div>
    </header>

    <!-- 进度概览 -->
    <div class="progress-card animate-fadeUp">
      <div class="progress-info">
        <div class="progress-num">
          <span class="num-big">{{ earnedCount }}</span>
          <span class="num-sep">/</span>
          <span class="num-total">{{ totalCount }}</span>
        </div>
        <div class="progress-label">已收集</div>
      </div>
      <div class="progress-bar-wrap">
        <div class="progress-track">
          <div
            class="progress-fill"
            :style="{ width: progressPercent + '%' }"
          ></div>
        </div>
        <span class="progress-pct">{{ progressPercent }}%</span>
      </div>
      <div class="rarity-row">
        <div v-for="r in rarityOrder" :key="r.key" class="rarity-stat">
          <div class="rarity-dot" :class="`rarity-${r.key}`"></div>
          <span class="rarity-name">{{ r.label }}</span>
          <span class="rarity-count">{{ rarityCount(r.key) }}</span>
        </div>
      </div>
    </div>

    <!-- 加载 -->
    <div v-if="loading" class="loading-state">
      <span>品鉴中...</span>
    </div>

    <!-- 徽章分类 -->
    <template v-else>
      <div v-for="cat in categories" :key="cat.key" class="category-section animate-fadeUp">
        <div class="category-header">
          <span class="cat-icon">{{ cat.icon }}</span>
          <h2 class="cat-title">{{ cat.label }}</h2>
          <span class="cat-count">{{ categoryCount(cat.key) }} / {{ catTotal(cat.key) }}</span>
        </div>

        <div class="badge-grid">
          <div
            v-for="badge in getByCategory(cat.key)"
            :key="badge.id"
            class="badge-card"
            :class="[
              `badge-card--${badge.rarity}`,
              { 'badge-card--locked': !badge.earned }
            ]"
            @click="showBadgeDetail(badge)"
          >
            <!-- 背景光效 -->
            <div class="badge-glow" :class="`glow-${badge.rarity}`"></div>

            <!-- 主内容 -->
            <div class="badge-icon-wrap">
              <div class="badge-icon-emoji">{{ badge.earned ? badge.icon : '🔒' }}</div>
              <div v-if="badge.earned" class="badge-earned-ring"></div>
            </div>

            <div class="badge-name">{{ badge.earned ? badge.name : '???' }}</div>

            <!-- 稀有度标签 -->
            <div class="badge-rarity-tag" :class="`rarity-tag-${badge.rarity}`">
              {{ rarityLabel(badge.rarity) }}
            </div>

            <!-- 已获得标记 -->
            <div v-if="badge.earned" class="badge-earned-mark">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 徽章详情弹层 -->
    <div class="badge-overlay" v-if="showDetail" @click.self="showDetail = false">
      <div class="badge-modal" v-if="selectedBadge">
        <div class="detail-icon" :class="`badge-detail--${selectedBadge.rarity}`">
          {{ selectedBadge.earned ? selectedBadge.icon : '🔒' }}
        </div>
        <h2 class="detail-name">{{ selectedBadge.earned ? selectedBadge.name : '未解锁' }}</h2>
        <div class="detail-rarity" :class="`rarity-tag-${selectedBadge.rarity}`">
          {{ rarityLabel(selectedBadge.rarity) }}
        </div>
        <p class="detail-desc">{{ selectedBadge.description }}</p>
        <div class="detail-meta" v-if="selectedBadge.earned">
          获得于 {{ formatDate(selectedBadge.earned_at) }}
        </div>
        <div class="detail-meta locked" v-else>
          完成对应条件即可解锁
        </div>
        <button class="btn-outline detail-close" @click="showDetail = false">
          我知道了
        </button>
      </div>
    </div>

    <div class="safe-bottom"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const badges = ref<any[]>([])
const showDetail = ref(false)
const selectedBadge = ref<any>(null)

const rarityOrder = [
  { key: 'legend', label: '传说' },
  { key: 'epic',   label: '史诗' },
  { key: 'rare',   label: '稀有' },
  { key: 'common', label: '普通' },
]

const categories = [
  { key: 'feihua',     label: '飞花令',     icon: '🌸' },
  { key: 'social',     label: '雅集成就',   icon: '🏅' },
  { key: 'special',    label: '特殊徽章',   icon: '⭐' },
]

const totalCount    = computed(() => badges.value.length)
const earnedCount   = computed(() => badges.value.filter(b => b.earned).length)
const progressPercent = computed(() =>
  totalCount.value ? Math.round(earnedCount.value / totalCount.value * 100) : 0
)

function rarityCount(key: string) {
  return badges.value.filter(b => b.rarity === key && b.earned).length
}

function categoryCount(key: string) {
  return badges.value.filter(b => b.category === key && b.earned).length
}

function catTotal(key: string) {
  return badges.value.filter(b => b.category === key).length
}

function getByCategory(cat: string) {
  return badges.value.filter(b => b.category === cat)
}

function rarityLabel(rarity: string) {
  const map: Record<string, string> = {
    common: '普通', rare: '稀有', epic: '史诗', legend: '传说'
  }
  return map[rarity] || rarity
}

function formatDate(iso: string | null) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日`
}

function showBadgeDetail(badge: any) {
  selectedBadge.value = badge
  showDetail.value = true
}

onMounted(async () => {
  try {
    const userId = authStore.user?.id
    if (userId) {
      const res = await api.getUserBadges(userId)
      // 拦截器 unwrap → res = Flask { data: { badges: [...] } }
      badges.value = res.data?.badges || []
    } else {
      // 未登录时只显示徽章列表
      const res = await api.getBadgeList()
      // 同上：res.data = { badges: [...] }
      badges.value = (res.data?.badges || []).map((b: any) => ({ ...b, earned: false }))
    }
  } catch (e) {
    console.error('加载徽章失败', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* ── 页面布局 ─────────────────────────── */
.badges-page { min-height: 100vh; }

/* ── 顶部导航 ─────────────────────────── */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
}

.header-left, .header-right { width: 40px; }
.header-left { cursor: pointer; color: var(--ink); }
.header-title {
  font-family: var(--font-display);
  font-size: 1.1rem;
  color: var(--ink);
}

/* ── 进度卡片 ─────────────────────────── */
.progress-card {
  margin: 0 20px 20px;
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
}

.progress-info {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 12px;
}

.num-big {
  font-family: var(--font-sans);
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--cinnabar);
  line-height: 1;
}
.num-sep {
  font-family: var(--font-sans);
  font-size: 1.5rem;
  color: var(--stone-light);
}
.num-total {
  font-family: var(--font-sans);
  font-size: 1.5rem;
  color: var(--stone);
}

.progress-label {
  font-family: var(--font-serif);
  font-size: 0.85rem;
  color: var(--stone);
}

.progress-bar-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.progress-track {
  flex: 1;
  height: 6px;
  background: var(--parchment-dark);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--cinnabar), var(--gold));
  border-radius: 3px;
  transition: width 0.8s var(--ease-out);
}

.progress-pct {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  color: var(--gold);
  font-weight: 600;
  min-width: 36px;
}

.rarity-row {
  display: flex;
  justify-content: space-between;
}

.rarity-stat {
  display: flex;
  align-items: center;
  gap: 4px;
}

.rarity-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
}
.rarity-legend { background: var(--gold); }
.rarity-epic   { background: #3D7A8A; }
.rarity-rare   { background: var(--jade); }
.rarity-common { background: var(--stone-light); }

.rarity-name {
  font-family: var(--font-sans);
  font-size: 0.65rem;
  color: var(--stone);
}

.rarity-count {
  font-family: var(--font-sans);
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--ink);
}

/* ── 加载 ─────────────────────────────── */
.loading-state {
  text-align: center;
  padding: 60px 20px;
  font-family: var(--font-serif);
  color: var(--stone);
}

/* ── 分类 ─────────────────────────────── */
.category-section { padding: 0 20px 24px; }

.category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}

.cat-icon { font-size: 1.1rem; }

.cat-title {
  font-family: var(--font-display);
  font-size: 1rem;
  color: var(--ink);
}

.cat-count {
  margin-left: auto;
  font-family: var(--font-sans);
  font-size: 0.75rem;
  color: var(--stone);
}

/* ── 徽章网格 ─────────────────────────── */
.badge-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.badge-card {
  background: #fff;
  border-radius: var(--radius-md);
  padding: 14px 8px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all 0.2s var(--ease-out);
  position: relative;
  overflow: hidden;
}
.badge-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }
.badge-card:active { transform: translateY(-1px); }

/* 稀有度边框 */
.badge-card--legend { border: 1.5px solid rgba(196,168,130,0.4); }
.badge-card--epic   { border: 1.5px solid rgba(61,122,138,0.3); }
.badge-card--rare   { border: 1.5px solid rgba(74,139,106,0.3); }
.badge-card--common { border: 1px solid var(--stone-light); }

/* 未解锁 */
.badge-card--locked {
  background: var(--parchment);
  filter: grayscale(0.6);
  opacity: 0.75;
}

/* 光效 */
.badge-glow {
  position: absolute;
  top: -20px; right: -20px;
  width: 60px; height: 60px;
  border-radius: 50%;
}
.glow-legend { background: radial-gradient(circle, rgba(196,168,130,0.2) 0%, transparent 70%); }
.glow-epic   { background: radial-gradient(circle, rgba(155,58,42,0.15) 0%, transparent 70%); }
.glow-rare   { background: radial-gradient(circle, rgba(61,107,74,0.15) 0%, transparent 70%); }
.glow-common { background: radial-gradient(circle, rgba(158,142,126,0.1) 0%, transparent 70%); }

/* 图标 */
.badge-icon-wrap {
  position: relative;
  width: 52px; height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge-icon-emoji {
  font-size: 1.8rem;
  line-height: 1;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.badge-earned-ring {
  position: absolute;
  inset: -3px;
  border: 2px solid var(--gold);
  border-radius: 50%;
  animation: pulseGold 2s ease infinite;
}

.badge-name {
  font-family: var(--font-serif);
  font-size: 0.75rem;
  color: var(--ink);
  text-align: center;
  line-height: 1.3;
}

.badge-card--locked .badge-name { color: var(--stone-light); }

/* 稀有度小标签 */
.badge-rarity-tag {
  font-family: var(--font-sans);
  font-size: 0.55rem;
  padding: 1px 5px;
  border-radius: 3px;
}
.rarity-tag-legend { background: rgba(184,148,46,0.1); color: var(--gold); }
.rarity-tag-epic   { background: rgba(155,58,42,0.1); color: var(--cinnabar); }
.rarity-tag-rare   { background: rgba(61,107,74,0.1); color: var(--jade); }
.rarity-tag-common { background: rgba(158,142,126,0.1); color: var(--stone); }

/* 已获得标记 */
.badge-earned-mark {
  position: absolute;
  top: 6px; right: 6px;
  width: 16px; height: 16px;
  background: var(--jade);
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── 详情弹层 ─────────────────────────── */
.badge-detail {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
}

.detail-icon {
  width: 80px; height: 80px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
}
.badge-detail--legend { background: rgba(184,148,46,0.1); }
.badge-detail--epic   { background: rgba(155,58,42,0.1); }
.badge-detail--rare   { background: rgba(61,107,74,0.1); }
.badge-detail--common { background: rgba(158,142,126,0.1); }

.detail-name {
  font-family: var(--font-display);
  font-size: 1.3rem;
  color: var(--ink);
}

.detail-rarity {
  font-family: var(--font-sans);
  font-size: 0.7rem;
  padding: 2px 10px;
  border-radius: 20px;
}

.detail-desc {
  font-family: var(--font-serif);
  font-size: 0.9rem;
  color: var(--stone);
  line-height: 1.6;
}

.detail-meta {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  color: var(--stone);
}
.detail-meta.locked { color: var(--cinnabar); }

.detail-close { margin-top: 8px; }

/* ── 徽章详情弹层 ─────────────────────── */
.badge-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: fadeIn 0.2s ease;
}

.badge-modal {
  width: 100%;
  max-width: 340px;
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 28px 24px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  animation: slideUp 0.25s var(--ease-out);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}

/* ── 底部 ─────────────────────────────── */
.safe-bottom { height: 32px; }
</style>
