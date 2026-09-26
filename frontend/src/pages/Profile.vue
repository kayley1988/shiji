<template>
  <div class="profile-page bg-xuanzhi">
    <!-- 顶部 -->
    <header class="page-header">
      <div class="header-left" @click="$router.back()">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M12 4l-6 6 6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h1 class="header-title">我的</h1>
      <div class="header-right"></div>
    </header>

    <!-- 用户卡片 + 段位进度 -->
    <div class="profile-card animate-fadeUp" v-if="user">
      <div class="avatar" :style="avatarGradient(user.id)">{{ user.nickname.slice(-2) }}</div>
      <div class="user-info">
        <div class="nickname-row">
          <span class="nickname">{{ user.nickname }}</span>
          <span class="role-badge" v-if="user.role === 'admin'">管理员</span>
        </div>
        <div class="rank-badge">
          <span class="rank-icon">{{ rankIcon(stats?.user?.rank || user.rank) }}</span>
          {{ stats?.user?.rank || user.rank || '萌新' }}
        </div>
        <!-- 段位进度条 -->
        <div class="rank-progress" v-if="stats?.user">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: stats.user.rank_progress + '%' }"></div>
          </div>
          <span class="progress-label">{{ stats.user.rank_progress }}%</span>
        </div>
      </div>
      <div class="exp-info">
        <span class="exp-label">经验</span>
        <span class="exp-value">{{ stats?.user?.exp ?? user.exp }}</span>
      </div>
    </div>

    <!-- 统计网格 -->
    <div class="stats-grid animate-fadeUp">
      <div class="stat-item">
        <div class="stat-value">{{ stats?.user?.total_games ?? user?.total_games ?? 0 }}</div>
        <div class="stat-label">总对局</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ stats?.user?.total_wins ?? user?.total_wins ?? 0 }}</div>
        <div class="stat-label">胜场</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ stats?.user?.badge_count ?? 0 }}</div>
        <div class="stat-label">徽章</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ stats?.user?.fav_count ?? 0 }}</div>
        <div class="stat-label">收藏</div>
      </div>
    </div>

    <!-- 活跃曲线 -->
    <div class="curve-card animate-fadeUp delay-1" v-if="dailyLogins.length > 1">
      <h2 class="card-title">近30日活跃</h2>
      <div class="curve-wrap">
        <svg :viewBox="`0 0 ${curveW} ${curveH}`" class="curve-svg" preserveAspectRatio="none">
          <defs>
            <linearGradient id="curveGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="rgba(155,58,42,0.3)"/>
              <stop offset="100%" stop-color="rgba(155,58,42,0)"/>
            </linearGradient>
          </defs>
          <path :d="areaPath" fill="url(#curveGrad)"/>
          <path :d="linePath" fill="none" stroke="#9B3A2A" stroke-width="1.5" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="curve-labels">
        <span>今日: {{ todayLogin }}</span>
        <span>峰值: {{ maxLogin }}</span>
        <span>活跃日: {{ activeDays }}</span>
      </div>
    </div>

    <!-- 雷达图 -->
    <div class="radar-card animate-fadeUp delay-2" v-if="(stats?.user?.total_games ?? user?.total_games) > 0">
      <h2 class="card-title">能力分析</h2>
      <div class="radar-wrap">
        <svg viewBox="0 0 200 200" class="radar-svg">
          <g class="radar-bg" opacity="0.12">
            <polygon v-for="n in 5" :key="n"
              :points="hexPoints(100, 100, n * 16, 5, -Math.PI/2)" />
          </g>
          <g opacity="0.15">
            <line v-for="(_, i) in radarLabels" :key="i"
              x1="100" y1="100"
              :x2="100 + 80 * Math.cos(-Math.PI/2 + i * 2*Math.PI/5)"
              :y2="100 + 80 * Math.sin(-Math.PI/2 + i * 2*Math.PI/5)"
              stroke="#9E8E7E" stroke-width="1"/>
          </g>
          <text v-for="(label, i) in radarLabels" :key="'l'+i"
            :x="100 + 92 * Math.cos(-Math.PI/2 + i * 2*Math.PI/5)"
            :y="100 + 92 * Math.sin(-Math.PI/2 + i * 2*Math.PI/5)"
            text-anchor="middle" dominant-baseline="middle"
            font-size="9" fill="#9E8E7E" font-family="Noto Sans SC">
            {{ label }}
          </text>
          <polygon :points="radarPoints" fill="rgba(155,58,42,0.25)"
            stroke="rgb(155,58,42)" stroke-width="2" stroke-linejoin="round"/>
          <circle v-for="(p, i) in radarCoords" :key="i"
            :cx="p.x" :cy="p.y" r="3.5" fill="rgba(155,58,42,0.9)"/>
        </svg>
      </div>
      <div class="radar-legend">
        <div v-for="(label, i) in radarLabels" :key="i" class="legend-item">
          <span class="legend-dot"></span>
          <span class="legend-label">{{ label }}</span>
          <span class="legend-val">{{ Math.round(myRadar[i]) }}</span>
        </div>
      </div>
    </div>

    <!-- 链接 -->
    <div class="link-list animate-fadeUp delay-3">
      <div class="link-item" @click="$router.push('/badges')">
        <span class="link-icon">🏅</span>
        <span class="link-text">我的徽章</span>
        <span class="link-arrow">→</span>
      </div>
      <div class="link-item" @click="$router.push('/me/favorites')">
        <span class="link-icon">❤️</span>
        <span class="link-text">我的收藏</span>
        <span class="link-arrow">→</span>
      </div>
      <div class="link-item" @click="$router.push('/my-colors')">
        <span class="link-icon">🎨</span>
        <span class="link-text">我的中国色</span>
        <span class="link-arrow">→</span>
      </div>
      <div class="link-item link-item-admin" v-if="user?.role === 'admin'" @click="$router.push('/admin')">
        <span class="link-icon">⚙️</span>
        <span class="link-text">管理后台</span>
        <span class="link-arrow">→</span>
      </div>
    </div>

    <div class="safe-bottom"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { api } from '../api'

const authStore = useAuthStore()
const user = ref<any>(null)
const stats = ref<any>(null)

const radarLabels = ['速度', '准确', '广度', '连击', '节气']

// ── 雷达图 ─────────────────────────────
const myRadar = computed(() => {
  const u = stats.value?.user ?? user.value
  if (!u) return [0, 0, 0, 0, 0]
  const g = u.total_games || 1
  const w = u.total_wins || 0
  const c = u.total_correct || 0
  return [
    Math.min(100, Math.round(c / g * 8)),
    Math.min(100, Math.round(w / g * 100)),
    Math.min(100, Math.round(c / g * 10)),
    Math.min(100, Math.round(c / g * 6)),
    Math.min(100, Math.round(w / g * 80 + 20)),
  ]
})

const radarCoords = computed(() =>
  myRadar.value.map((v, i) => {
    const angle = -Math.PI / 2 + i * (2 * Math.PI / 5)
    const r = (v / 100) * 80
    return { x: 100 + r * Math.cos(angle), y: 100 + r * Math.sin(angle) }
  })
)

const radarPoints = computed(() =>
  radarCoords.value.map(p => `${p.x},${p.y}`).join(' ')
)

// ── 活跃曲线 ───────────────────────────
const curveW = 320
const curveH = 60

const dailyLogins = computed(() => stats.value?.daily_logins ?? [])

const maxLogin = computed(() =>
  dailyLogins.value.length ? Math.max(...dailyLogins.value.map((d: any) => d.count)) : 0
)
const todayLogin = computed(() => {
  const today = dailyLogins.value.find((d: any) =>
    d.day === new Date().toISOString().slice(0, 10)
  )
  return today?.count ?? 0
})
const activeDays = computed(() => dailyLogins.value.length)

const linePath = computed(() => {
  const arr = dailyLogins.value
  if (!arr.length) return ''
  const max = Math.max(...arr.map((d: any) => d.count), 1)
  const pts = arr.map((d: any, i: number) => {
    const x = (i / Math.max(arr.length - 1, 1)) * curveW
    const y = curveH - (d.count / max) * (curveH - 4) - 2
    return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`
  })
  return pts.join(' ')
})

const areaPath = computed(() => {
  const arr = dailyLogins.value
  if (!arr.length) return ''
  const max = Math.max(...arr.map((d: any) => d.count), 1)
  const pts = arr.map((d: any, i: number) => {
    const x = (i / Math.max(arr.length - 1, 1)) * curveW
    const y = curveH - (d.count / max) * (curveH - 4) - 2
    return `${x.toFixed(1)},${y.toFixed(1)}`
  })
  const last = arr.length - 1
  const lastX = (last / Math.max(last, 1)) * curveW
  return `M${pts[0]} ${pts.slice(1).map(p => 'L' + p).join(' ')} L${lastX},${curveH} L0,${curveH} Z`
})

// ── 工具 ──────────────────────────────
function hexPoints(cx: number, cy: number, r: number, sides: number, startAngle: number) {
  return Array.from({ length: sides }, (_, i) => {
    const angle = startAngle + (i * 2 * Math.PI / sides)
    return `${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`
  }).join(' ')
}

function avatarGradient(id: string) {
  const hues = [350, 160, 200, 30, 280]
  const h = hues[id?.charCodeAt(0) % hues.length] || 350
  return `background: linear-gradient(135deg, hsl(${h}, 50%, 40%) 0%, hsl(${h}, 60%, 55%) 100%)`
}

function rankIcon(rank: string) {
  const map: Record<string, string> = {
    '萌新': '🌱', '初窥': '🌿', '入门': '🌾', '小成': '🌵',
    '大成': '🌳', '高手': '🏆', '宗师': '🎖️', '诗仙': '👑'
  }
  return map[rank] || '🌱'
}

onMounted(async () => {
  try {
    // 获取基本信息（拦截器不 unwrap，res.data = Flask {code, data: {user}}
    const res = await api.getProfile()
    user.value = res.data.data
    authStore.user = res.data.data
    authStore.isLoggedIn = true
    // 获取详细统计
    try {
      const s = await api.getMyStats()
      stats.value = s.data.data
    } catch (e) {
      console.warn('获取统计失败', e)
    }
  } catch (e) {
    console.error('获取用户信息失败', e)
  }
})
</script>

<style scoped>
.profile-page { min-height: 100vh; }

.page-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; background: #fff;
}
.header-left, .header-right { width: 40px; }
.header-left { cursor: pointer; }
.header-title { font-size: 16px; font-weight: 600; color: var(--yanhong); }

/* ── 用户卡片 ─────────────────────────── */
.profile-card {
  margin: 16px; padding: 16px; border-radius: 12px;
  background: #fff; display: flex; align-items: center; gap: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.avatar {
  width: 52px; height: 52px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 18px; font-weight: 600; flex-shrink: 0;
}
.user-info { flex: 1; min-width: 0; }
.nickname-row { display: flex; align-items: center; gap: 6px; }
.nickname { font-size: 16px; font-weight: 600; color: #333; }
.role-badge {
  font-size: 10px; padding: 1px 6px; border-radius: 10px;
  background: var(--yanhong); color: #fff;
}
.rank-badge {
  display: flex; align-items: center; gap: 4px;
  font-size: 13px; color: #888; margin-top: 4px;
}
.exp-info {
  text-align: center; flex-shrink: 0;
}
.exp-label { display: block; font-size: 11px; color: #aaa; }
.exp-value { font-size: 18px; font-weight: 700; color: var(--yanhong); }

/* ── 进度条 ─────────────────────────── */
.rank-progress { margin-top: 6px; display: flex; align-items: center; gap: 8px; }
.progress-bar {
  flex: 1; height: 5px; border-radius: 3px;
  background: rgba(155,58,42,0.12); overflow: hidden;
}
.progress-fill {
  height: 100%; border-radius: 3px;
  background: linear-gradient(90deg, #9B3A2A, #D4724A);
  transition: width 0.6s ease;
}
.progress-label { font-size: 11px; color: #9B3A2A; flex-shrink: 0; }

/* ── 统计网格 ─────────────────────────── */
.stats-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;
  margin: 0 16px 12px;
}
.stat-item {
  background: #fff; border-radius: 10px; padding: 12px 8px;
  text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.stat-value { font-size: 20px; font-weight: 700; color: #333; }
.stat-label { font-size: 11px; color: #999; margin-top: 2px; }

/* ── 活跃曲线 ─────────────────────────── */
.curve-card {
  margin: 0 16px 12px; padding: 14px; border-radius: 12px;
  background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.card-title {
  font-size: 13px; color: #666; margin: 0 0 10px;
  font-weight: 500; border-left: 3px solid var(--yanhong);
  padding-left: 8px;
}
.curve-wrap { height: 60px; }
.curve-svg { width: 100%; height: 100%; }
.curve-labels {
  display: flex; justify-content: space-around;
  font-size: 11px; color: #999; margin-top: 6px;
}

/* ── 雷达图 ─────────────────────────── */
.radar-card {
  margin: 0 16px 12px; padding: 14px; border-radius: 12px;
  background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.radar-wrap { display: flex; justify-content: center; }
.radar-svg { width: 160px; height: 160px; }
.radar-legend { display: flex; flex-wrap: wrap; gap: 4px 12px; margin-top: 8px; justify-content: center; }
.legend-item { display: flex; align-items: center; gap: 4px; font-size: 11px; color: #666; }
.legend-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--yanhong); }
.legend-val { font-weight: 600; color: #333; }

/* ── 链接 ─────────────────────────── */
.link-list {
  margin: 8px 16px; background: #fff; border-radius: 12px;
  overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.link-item {
  display: flex; align-items: center; padding: 14px 16px;
  cursor: pointer; transition: background 0.2s;
}
.link-item:active { background: rgba(0,0,0,0.04); }
.link-item + .link-item { border-top: 1px solid #f5f5f5; }
.link-item-admin { border-top: 1px solid #f5f5f5 !important; }
.link-icon { font-size: 18px; margin-right: 10px; }
.link-text { flex: 1; font-size: 14px; color: #333; }
.link-arrow { color: #ccc; font-size: 14px; }

.safe-bottom { height: 40px; }
</style>
