<template>
  <div class="admin-page bg-xuanzhi">
    <!-- 顶部 -->
    <header class="page-header">
      <div class="header-left" @click="$router.back()">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M12 4l-6 6 6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h1 class="header-title">管理后台</h1>
      <div class="header-right"></div>
    </header>

    <!-- 加载状态 -->
    <div class="loading-wrap" v-if="loading">
      <div class="loading-spinner"></div>
      <p>加载中…</p>
    </div>

    <!-- 错误提示 -->
    <div class="error-tip" v-else-if="error">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="loadStats">重试</button>
    </div>

    <template v-else-if="data">
      <!-- 概览卡片 -->
      <div class="stats-row animate-fadeUp">
        <div class="stat-card stat-primary">
          <div class="stat-icon">👥</div>
          <div class="stat-body">
            <div class="stat-value">{{ data.users?.total ?? 0 }}</div>
            <div class="stat-label">用户总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📜</div>
          <div class="stat-body">
            <div class="stat-value">{{ (data.poems?.total ?? 0).toLocaleString() }}</div>
            <div class="stat-label">诗句总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🎮</div>
          <div class="stat-body">
            <div class="stat-value">{{ data.games?.total ?? 0 }}</div>
            <div class="stat-label">游戏场次</div>
          </div>
        </div>
      </div>

      <!-- 用户活跃 -->
      <div class="stats-row2 animate-fadeUp delay-1">
        <div class="stat-mini">
          <div class="stat-mini-val">+{{ data.users?.today_new ?? 0 }}</div>
          <div class="stat-mini-label">今日新增</div>
        </div>
        <div class="stat-mini">
          <div class="stat-mini-val">+{{ data.users?.week_new ?? 0 }}</div>
          <div class="stat-mini-label">本周新增</div>
        </div>
        <div class="stat-mini">
          <div class="stat-mini-val">{{ data.users?.active_7d ?? 0 }}</div>
          <div class="stat-mini-label">活跃用户</div>
        </div>
        <div class="stat-mini">
          <div class="stat-mini-val">{{ data.poems?.approved ?? 0 }}</div>
          <div class="stat-mini-label">已审诗句</div>
        </div>
      </div>

      <!-- 用户增长曲线 -->
      <div class="chart-card animate-fadeUp delay-1" v-if="userGrowth.length > 1">
        <h2 class="card-title">每日新增用户</h2>
        <div class="chart-wrap">
          <svg :viewBox="`0 0 ${chartW} ${chartH}`" preserveAspectRatio="none">
            <defs>
              <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#9B3A2A"/>
                <stop offset="100%" stop-color="#D4724A"/>
              </linearGradient>
            </defs>
            <rect
              v-for="(d, i) in userGrowth" :key="i"
              :x="barX(i)" :y="barY(d.count)" :width="barW" :height="barH(d.count)"
              rx="2" fill="url(#barGrad)"
            />
          </svg>
        </div>
        <div class="chart-meta">
          <span>共 {{ totalNewUsers }} 人 (近30日)</span>
          <span>日均 {{ avgNewUsers }} 人</span>
        </div>
      </div>

      <!-- 热门诗句 Top -->
      <div class="top-card animate-fadeUp delay-2" v-if="topVerses.length">
        <h2 class="card-title">热门诗句 TOP5</h2>
        <div class="top-list">
          <div class="top-item" v-for="(v, i) in topVerses" :key="i">
            <span class="top-num">{{ i + 1 }}</span>
            <div class="top-info">
              <p class="top-text">{{ v.text }}</p>
              <p class="top-meta">{{ v.dynasty }} · {{ v.author }}</p>
            </div>
            <span class="top-count">{{ v.game_count }}</span>
          </div>
        </div>
      </div>

      <!-- 热门诗人 Top -->
      <div class="top-card animate-fadeUp delay-3" v-if="topAuthors.length">
        <h2 class="card-title">热门诗人 TOP5</h2>
        <div class="top-list">
          <div class="top-item" v-for="(a, i) in topAuthors" :key="i">
            <span class="top-num">{{ i + 1 }}</span>
            <div class="top-info">
              <p class="top-text">{{ a.author }}</p>
              <p class="top-meta">{{ a.verse_count }} 首诗句</p>
            </div>
            <span class="top-count">{{ a.game_count }}</span>
          </div>
        </div>
      </div>

      <!-- 每日对局趋势 -->
      <div class="chart-card animate-fadeUp delay-4" v-if="dailyGames.length > 1">
        <h2 class="card-title">每日对局趋势</h2>
        <div class="chart-wrap">
          <svg :viewBox="`0 0 ${chartW} ${chartH}`" preserveAspectRatio="none">
            <defs>
              <linearGradient id="gameGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#4A7A5A"/>
                <stop offset="100%" stop-color="#4A7A5A44"/>
              </linearGradient>
            </defs>
            <path :d="gameAreaPath" fill="url(#gameGrad)"/>
            <path :d="gameLinePath" fill="none" stroke="#4A7A5A" stroke-width="1.5" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="chart-meta">
          <span>今日: {{ todayGames }}</span>
          <span>峰值: {{ maxDailyGames }}</span>
        </div>
      </div>
    </template>

    <div class="safe-bottom"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'

const loading = ref(true)
const error = ref('')
const data = ref<any>(null)

const chartW = 320
const chartH = 80

// 用户增长柱状图
const userGrowth = computed(() => data.value?.daily_new_users ?? [])
const totalNewUsers = computed(() => userGrowth.value.reduce((s: number, d: any) => s + d.count, 0))
const avgNewUsers = computed(() => userGrowth.value.length ? Math.round(totalNewUsers.value / userGrowth.value.length) : 0)

function barX(i: number) {
  return ((i + 0.5) / userGrowth.value.length) * chartW
}
function barW() {
  return Math.max((chartW / userGrowth.value.length) * 0.6, 2)
}
function barY(count: number) {
  const max = Math.max(...userGrowth.value.map((d: any) => d.count), 1)
  return chartH - (count / max) * (chartH - 4) - 2
}
function barH(count: number) {
  const max = Math.max(...userGrowth.value.map((d: any) => d.count), 1)
  return Math.max((count / max) * (chartH - 4), 2)
}

// 每日对局曲线
const dailyGames = computed(() => data.value?.daily_games ?? [])
const topVerses = computed<any[]>(() => data.value?.top_verses ?? [])
const topAuthors = computed<any[]>(() => data.value?.top_authors ?? [])
const todayGames = computed(() => {
  const today = dailyGames.value.find((d: any) => d.day === new Date().toISOString().slice(0, 10))
  return today?.count ?? 0
})
const maxDailyGames = computed(() =>
  dailyGames.value.length ? Math.max(...dailyGames.value.map((d: any) => d.count)) : 0
)

const gameLinePath = computed(() => {
  const arr = dailyGames.value
  if (!arr.length) return ''
  const max = Math.max(...arr.map((d: any) => d.count), 1)
  return arr.map((d: any, i: number) => {
    const x = (i / Math.max(arr.length - 1, 1)) * chartW
    const y = chartH - (d.count / max) * (chartH - 4) - 2
    return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
})

const gameAreaPath = computed(() => {
  const arr = dailyGames.value
  if (!arr.length) return ''
  const max = Math.max(...arr.map((d: any) => d.count), 1)
  const pts = arr.map((d: any, i: number) => {
    const x = (i / Math.max(arr.length - 1, 1)) * chartW
    const y = chartH - (d.count / max) * (chartH - 4) - 2
    return `${x.toFixed(1)},${y.toFixed(1)}`
  })
  return `M0,${chartH} ${pts.join(' ')} L${chartW},${chartH} Z`
})

async function loadStats() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.getAdminStats()
    data.value = res.data.data
  } catch (e: any) {
    if (e?.status === 403 || e?.message?.includes('403')) {
      error.value = '⚠️ 需要管理员权限'
    } else {
      error.value = '加载失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadStats() })
</script>

<style scoped>
.admin-page { min-height: 100vh; }

.page-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; background: #fff;
}
.header-left { width: 40px; cursor: pointer; }
.header-title { font-size: 16px; font-weight: 600; color: var(--yanhong); }
.header-right { width: 40px; }

.loading-wrap {
  display: flex; flex-direction: column; align-items: center;
  padding: 60px; gap: 12px; color: #999;
}
.loading-spinner {
  width: 32px; height: 32px; border: 3px solid rgba(155,58,42,0.2);
  border-top-color: var(--yanhong); border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.error-tip {
  text-align: center; padding: 40px; color: #999;
}
.btn-retry {
  margin-top: 12px; padding: 8px 24px; border: none;
  border-radius: 8px; background: var(--yanhong); color: #fff;
  cursor: pointer; font-size: 14px;
}

/* ── 统计卡片 ─────────────────────────── */
.stats-row {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;
  margin: 16px 16px 8px;
}
.stats-row2 {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;
  margin: 0 16px 12px;
}
.stat-mini {
  background: #fff; border-radius: 8px; padding: 10px 6px;
  text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.stat-mini-val { font-size: 16px; font-weight: 700; color: #333; }
.stat-mini-label { font-size: 10px; color: #999; margin-top: 2px; }
.stat-card {
  background: #fff; border-radius: 12px; padding: 14px 12px;
  display: flex; align-items: center; gap: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.stat-primary { background: linear-gradient(135deg, #9B3A2A, #C4503A); color: #fff; }
.stat-icon { font-size: 24px; }
.stat-value { font-size: 22px; font-weight: 700; }
.stat-primary .stat-value, .stat-primary .stat-label { color: #fff; }
.stat-label { font-size: 11px; color: #999; margin-top: 2px; }

/* ── 图表卡片 ─────────────────────────── */
.chart-card {
  margin: 0 16px 12px; padding: 14px; border-radius: 12px;
  background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.card-title {
  font-size: 13px; color: #666; margin: 0 0 10px;
  font-weight: 500; border-left: 3px solid var(--yanhong); padding-left: 8px;
}
.chart-wrap { height: 80px; }
.chart-wrap svg { width: 100%; height: 100%; }
.chart-meta {
  display: flex; justify-content: space-between;
  font-size: 11px; color: #999; margin-top: 6px;
}

/* ── Top 列表 ─────────────────────────── */
.top-card {
  margin: 0 16px 12px; padding: 14px; border-radius: 12px;
  background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.top-list { display: flex; flex-direction: column; gap: 10px; }
.top-item {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 0; border-bottom: 1px solid #f5f5f5;
}
.top-item:last-child { border-bottom: none; }
.top-num {
  width: 20px; height: 20px; border-radius: 50%;
  background: rgba(155,58,42,0.1); color: var(--yanhong);
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; flex-shrink: 0;
}
.top-info { flex: 1; min-width: 0; }
.top-text {
  font-size: 13px; color: #333; margin: 0;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.top-meta { font-size: 11px; color: #999; margin: 2px 0 0; }
.top-count {
  font-size: 14px; font-weight: 600; color: var(--yanhong);
  flex-shrink: 0;
}

.safe-bottom { height: 40px; }
</style>
