<template>
  <div class="result-page bg-xuanzhi">

    <!-- 顶部装饰 -->
    <div class="top-decor">
      <div class="decor-line left"></div>
      <div class="decor-diamond"></div>
      <div class="decor-line right"></div>
    </div>

    <!-- 加载 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-text">品鉴中...</div>
    </div>

    <template v-else>
      <!-- ═══ 结果标题 ═══════════════════════════ -->
      <header class="result-header animate-fadeUp">
        <div class="result-seal" :class="isWinner ? 'seal-gold' : 'seal-cinnabar'">
          <span>{{ isWinner ? '胜' : '局' }}</span>
        </div>
        <div class="result-titles">
          <h1 class="result-title">{{ isWinner ? '恭喜夺魁' : '惜败一局' }}</h1>
          <p class="result-sub" v-if="resultList[0]">
            <span class="winner-name">{{ resultList[0].nickname }}</span> 拔得头筹
          </p>
          <p class="result-sub" v-else>暂无记录</p>
        </div>
      </header>

      <!-- ═══ 排名列表 ═══════════════════════════ -->
      <section class="section-ranks animate-fadeUp delay-1">
        <div
          v-for="(item, idx) in resultList"
          :key="item.user_id"
          class="rank-card"
          :class="{
            'rank-1': idx === 0,
            'rank-2': idx === 1,
            'rank-3': idx === 2,
            'self': item.user_id === myId
          }"
        >
          <!-- 名次 -->
          <div class="rank-badge" :class="`rank-badge-${idx + 1}`">
            <template v-if="idx === 0">🥇</template>
            <template v-else-if="idx === 1">🥈</template>
            <template v-else-if="idx === 2">🥉</template>
            <template v-else>{{ idx + 1 }}</template>
          </div>

          <!-- 玩家信息 -->
          <div class="rank-player">
            <div class="player-avatar" :style="{ background: avatarGradient(item.user_id) }">
              {{ item.nickname.slice(-2) }}
            </div>
            <div class="player-info">
              <span class="player-name">
                {{ item.nickname }}
                <span class="self-tag" v-if="item.user_id === myId">我</span>
              </span>
              <span class="player-tags">
                <span class="tag-round tag-gold" v-if="item.is_winner">魁首</span>
                <span class="tag-round tag-stone">{{ placementText(item.placement) }}</span>
              </span>
            </div>
          </div>

          <!-- 数据 -->
          <div class="rank-stats">
            <div class="stat-pair">
              <span class="stat-val">{{ item.score }}</span>
              <span class="stat-key">分</span>
            </div>
            <div class="stat-sep"></div>
            <div class="stat-pair">
              <span class="stat-val">{{ item.correct_count }}</span>
              <span class="stat-key">句</span>
            </div>
          </div>

          <!-- 排名印章 -->
          <div class="rank-seal" v-if="idx === 0">壹</div>
        </div>
      </section>

      <!-- ═══ 数据图表 ═══════════════════════════ -->
      <section class="section-chart animate-fadeUp delay-2">
        <h2 class="section-title">
          <span class="title-line"></span>
          战绩分析
          <span class="title-line"></span>
        </h2>

        <!-- 柱状图：各玩家正确数 -->
        <div class="chart-card">
          <div class="chart-label">本局正确数</div>
          <div class="bar-chart">
            <div
              v-for="item in resultList"
              :key="item.user_id"
              class="bar-item"
            >
              <div class="bar-track">
                <div
                  class="bar-fill"
                  :style="{
                    height: barHeight(item.correct_count) + '%',
                    background: item.user_id === myId ? 'var(--cinnabar)' : 'var(--jade)'
                  }"
                ></div>
              </div>
              <div class="bar-name">{{ item.nickname.slice(-2) }}</div>
              <div class="bar-val">{{ item.correct_count }}</div>
            </div>
          </div>
        </div>

        <!-- 个人雷达图（仅自己） -->
        <div class="chart-card" v-if="myResult">
          <div class="chart-label">个人能力</div>
          <div class="radar-chart">
            <svg viewBox="0 0 200 200" class="radar-svg">
              <!-- 背景网格 -->
              <g class="radar-grid" opacity="0.2">
                <polygon v-for="n in 5" :key="n"
                  :points="hexPoints(100, 100, n * 15, 5, -Math.PI/2)" />
              </g>
              <!-- 坐标轴 -->
              <g class="radar-axes" opacity="0.15">
                <line v-for="(label, i) in radarLabels" :key="i"
                  x1="100" y1="100"
                  :x2="100 + 75 * Math.cos(-Math.PI/2 + i * 2*Math.PI/5)"
                  :y2="100 + 75 * Math.sin(-Math.PI/2 + i * 2*Math.PI/5)"
                  stroke="#9E8E7E" stroke-width="1" />
              </g>
              <!-- 数据 -->
              <polygon
                :points="radarPoints"
                fill="rgba(212,175,55,0.15)"
                stroke="var(--cinnabar)"
                stroke-width="1.5"
              />
              <!-- 标签 -->
              <text v-for="(label, i) in radarLabels" :key="'l'+i"
                :x="100 + 88 * Math.cos(-Math.PI/2 + i * 2*Math.PI/5)"
                :y="100 + 88 * Math.sin(-Math.PI/2 + i * 2*Math.PI/5)"
                text-anchor="middle" dominant-baseline="middle"
                font-size="10" fill="var(--stone)" font-family="Noto Sans SC, sans-serif">
                {{ label }}
              </text>
              <!-- 数值点 -->
              <circle v-for="(pt, i) in radarCoords" :key="'c'+i"
                :cx="pt.x" :cy="pt.y" r="3"
                fill="var(--cinnabar)" />
            </svg>
          </div>
          <div class="radar-legend">
            <div v-for="(label, i) in radarLabels" :key="i" class="legend-item">
              <span class="legend-val">{{ myRadarValues[i] }}</span>
              <span class="legend-key">{{ label }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- ═══ 徽章展示 ════════════════════════════ -->
      <section class="section-badges animate-fadeUp delay-3" v-if="earnedBadges.length">
        <h2 class="section-title">
          <span class="title-line"></span>
          我的徽章
          <span class="title-line"></span>
        </h2>
        <div class="badges-scroll">
          <div
            v-for="badge in newBadges"
            :key="badge.id"
            class="result-badge"
            :class="`result-badge--${badge.rarity}`"
            @click="$router.push('/badges')"
          >
            <div class="result-badge-icon">{{ badge.icon }}</div>
            <div class="result-badge-name">{{ badge.name }}</div>
            <div class="result-badge-rarity" :class="`rarity-tag-${badge.rarity}`">
              {{ rarityLabel(badge.rarity) }}
            </div>
          </div>
        </div>
        <div class="badges-more" @click="$router.push('/badges')">
          查看全部 {{ earnedBadges.length }} 枚徽章 →
        </div>
      </section>

      <!-- ═══ 底部操作 ═══════════════════════════ -->
      <section class="section-actions animate-fadeUp delay-3">
        <button class="btn-primary btn-lg" @click="$router.push('/')">
          再来一局
        </button>
        <button class="btn-outline" @click="$router.push('/me')">
          查看战绩
        </button>
      </section>

    </template>

    <div class="safe-bottom"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const roomId = route.params.id as string
const loading = ref(true)
const resultList = ref<any[]>([])
const earnedBadges = ref<any[]>([])
const newBadges = ref<any[]>([])

const myId = computed(() => authStore.user?.id)
const isWinner = computed(() => resultList.value[0]?.user_id === myId.value)
const myResult = computed(() => resultList.value.find(r => r.user_id === myId.value))

// 雷达图数据（基于本局 + 历史数据推算）
const radarLabels = ['速度', '准确', '广度', '连击', '节气']
const myRadarValues = computed(() => {
  const r = myResult.value
  if (!r) return [0, 0, 0, 0, 0]
  return [
    Math.min(100, r.correct_count * 25),   // 速度
    Math.min(100, 80 + r.correct_count * 5),  // 准确
    Math.min(100, 60),  // 广度（估算）
    Math.min(100, r.element_bonus_count * 30), // 连击
    Math.min(100, 70),  // 节气（估算）
  ]
})

const radarCoords = computed(() => {
  return myRadarValues.value.map((v, i) => {
    const angle = -Math.PI / 2 + i * (2 * Math.PI / 5)
    const r = (v / 100) * 75
    return { x: 100 + r * Math.cos(angle), y: 100 + r * Math.sin(angle) }
  })
})

const radarPoints = computed(() =>
  radarCoords.value.map(p => `${p.x},${p.y}`).join(' ')
)

function hexPoints(cx: number, cy: number, r: number, sides: number, startAngle: number) {
  return Array.from({ length: sides }, (_, i) => {
    const angle = startAngle + (i * 2 * Math.PI / sides)
    return `${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`
  }).join(' ')
}

const maxCorrect = computed(() =>
  Math.max(...resultList.value.map(r => r.correct_count || 1), 1)
)

function barHeight(correct: number) {
  return (correct / maxCorrect.value) * 100
}

function avatarGradient(userId: string) {
  const hues = [350, 160, 200, 30, 280]
  const h = hues[userId.charCodeAt(0) % hues.length]
  return `linear-gradient(135deg, hsl(${h}, 50%, 45%) 0%, hsl(${h}, 60%, 60%) 100%)`
}

function placementText(p: number) {
  const map: Record<number, string> = { 1: '魁首', 2: '榜眼', 3: '探花' }
  return map[p] || `第${p}名`
}

function rarityLabel(rarity: string) {
  const map: Record<string, string> = { common: '普通', rare: '稀有', epic: '史诗', legend: '传说' }
  return map[rarity] || rarity
}

onMounted(async () => {
  try {
    const [resultRes, badgeRes] = await Promise.all([
      api.getRoomResult(roomId),
      authStore.user?.id
        ? api.getUserBadges(authStore.user.id).catch(() => null)
        : Promise.resolve(null)
    ])
    // 拦截器 unwrap → res = Flask { data: { results/badges: [...] } }
    resultList.value = resultRes?.data?.results || []
    const allBadges = badgeRes?.data?.badges || []
    earnedBadges.value = allBadges.filter((b: any) => b.earned)
    newBadges.value = earnedBadges.value.slice(0, 6)
  } catch (e) {
    console.error('获取结果失败', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.result-page { min-height: 100vh; }

/* ── 顶部装饰线 ───────────────────────── */
.top-decor {
  display: flex;
  align-items: center;
  padding: 24px 32px 0;
  gap: 12px;
}
.decor-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--stone-light));
}
.decor-line.right { background: linear-gradient(90deg, var(--stone-light), transparent); }
.decor-diamond {
  width: 8px; height: 8px;
  background: var(--cinnabar);
  transform: rotate(45deg);
}

/* ── 加载 ─────────────────────────────── */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60vh;
}
.loading-text {
  font-family: var(--font-serif);
  font-size: 1rem;
  color: var(--stone);
  letter-spacing: 0.2em;
}

/* ── 结果标题 ─────────────────────────── */
.result-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 20px 20px;
  gap: 16px;
  text-align: center;
}

.result-seal {
  width: 72px; height: 72px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 1.8rem;
  color: #fff;
  box-shadow: var(--shadow-md);
}
.seal-gold { background: linear-gradient(135deg, var(--gold), var(--gold-light)); }
.seal-cinnabar { background: linear-gradient(135deg, var(--cinnabar), var(--cinnabar-light)); }

.result-titles { }

.result-title {
  font-family: var(--font-display);
  font-size: 2rem;
  color: var(--ink);
  letter-spacing: 0.1em;
  margin-bottom: 6px;
}

.result-sub {
  font-family: var(--font-serif);
  font-size: 0.9rem;
  color: var(--stone);
}

.winner-name { color: var(--gold); }

/* ── 排名卡片 ─────────────────────────── */
.section-ranks { padding: 0 20px 20px; }

.rank-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--card);
  border-radius: var(--radius-lg);
  padding: 16px;
  margin-bottom: 10px;
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.2s;
}
.rank-card:hover { box-shadow: var(--shadow-md); }

.rank-card::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
}
.rank-1::before { background: linear-gradient(to bottom, #FFD700, #FFA500); }
.rank-2::before { background: linear-gradient(to bottom, #C0C0C0, #A0A0A0); }
.rank-3::before { background: linear-gradient(to bottom, #CD7F32, #A0522D); }
.rank-card:not(.rank-1):not(.rank-2):not(.rank-3)::before { background: var(--stone-light); }

.rank-card.self { background: rgba(212,175,55,0.03); }

.rank-badge {
  width: 36px; height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-sans);
  font-size: 0.8rem;
  font-weight: 600;
  flex-shrink: 0;
}
.rank-badge-1 { background: rgba(255,215,0,0.15); color: #B8860B; }
.rank-badge-2 { background: rgba(192,192,192,0.15); color: #808080; }
.rank-badge-3 { background: rgba(205,127,50,0.15); color: #8B4513; }
.rank-badge-4, .rank-badge-5 { background: var(--parchment-dark); color: var(--stone); }

.rank-player { display: flex; align-items: center; gap: 10px; flex: 1; }

.player-avatar {
  width: 40px; height: 40px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 0.8rem;
  flex-shrink: 0;
}

.player-info { display: flex; flex-direction: column; gap: 3px; }

.player-name {
  font-family: var(--font-serif);
  font-size: 0.95rem;
  color: var(--ink);
  display: flex;
  align-items: center;
  gap: 6px;
}

.self-tag {
  font-size: 0.6rem;
  padding: 1px 5px;
  background: rgba(212,175,55,0.1);
  color: var(--cinnabar);
  border-radius: 3px;
  font-family: var(--font-sans);
}

.player-tags { display: flex; gap: 4px; }

.rank-stats {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-pair {
  display: flex;
  align-items: baseline;
  gap: 2px;
}
.stat-val {
  font-family: var(--font-sans);
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--ink);
}
.stat-key {
  font-family: var(--font-sans);
  font-size: 0.65rem;
  color: var(--stone);
}
.stat-sep {
  width: 1px; height: 24px;
  background: var(--parchment-dark);
}

.rank-seal {
  position: absolute;
  right: 16px; top: 50%;
  transform: translateY(-50%);
  width: 32px; height: 32px;
  border: 1.5px solid var(--gold);
  border-radius: 4px;
  color: var(--gold);
  font-family: var(--font-display);
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.6;
}

/* ── 图表区 ───────────────────────────── */
.section-chart { padding: 0 20px 20px; }

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: var(--font-display);
  font-size: 1rem;
  color: var(--ink-light);
  letter-spacing: 0.15em;
  margin-bottom: 14px;
}

.title-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--stone-light), transparent);
}

.chart-card {
  background: var(--card);
  border-radius: var(--radius-lg);
  padding: 20px;
  margin-bottom: 12px;
  box-shadow: var(--shadow-sm);
}

.chart-label {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  color: var(--stone);
  letter-spacing: 0.1em;
  margin-bottom: 14px;
}

/* 柱状图 */
.bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 100px;
  gap: 8px;
}

.bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.bar-track {
  width: 100%;
  height: 80px;
  display: flex;
  align-items: flex-end;
  background: var(--parchment);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  width: 100%;
  border-radius: 4px 4px 0 0;
  min-height: 4px;
  transition: height 0.8s var(--ease-out);
}

.bar-name {
  font-family: var(--font-sans);
  font-size: 0.65rem;
  color: var(--stone);
}

.bar-val {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--ink);
}

/* 雷达图 */
.radar-chart {
  width: 200px;
  height: 200px;
  margin: 0 auto 12px;
}

.radar-svg { width: 100%; height: 100%; }

.radar-legend {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 8px;
}

.legend-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.legend-val {
  font-family: var(--font-sans);
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
}

.legend-key {
  font-family: var(--font-sans);
  font-size: 0.6rem;
  color: var(--stone);
}

/* ── 底部操作 ─────────────────────────── */
.section-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
}

.btn-lg { width: 100%; max-width: 320px; padding: 14px; font-size: 1rem; }

.safe-bottom { height: 32px; }

/* ── 徽章展示 ─────────────────────────── */
.section-badges { padding: 0 20px 20px; }

.badges-scroll {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: none;
}
.badges-scroll::-webkit-scrollbar { display: none; }

.result-badge {
  flex-shrink: 0;
  width: 80px;
  background: var(--card);
  border-radius: var(--radius-md);
  padding: 14px 8px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all 0.2s var(--ease-out);
  position: relative;
  overflow: hidden;
}
.result-badge:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }

.result-badge--legend { border: 1.5px solid rgba(184,148,46,0.4); }
.result-badge--epic   { border: 1.5px solid rgba(212,175,55,0.3); }
.result-badge--rare   { border: 1.5px solid rgba(61,107,74,0.3); }
.result-badge--common { border: 1px solid var(--stone-light); }

.result-badge-icon {
  font-size: 1.8rem;
  line-height: 1;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.result-badge-name {
  font-family: var(--font-serif);
  font-size: 0.65rem;
  color: var(--ink);
  text-align: center;
  line-height: 1.3;
}

.result-badge-rarity {
  font-family: var(--font-sans);
  font-size: 0.5rem;
  padding: 1px 4px;
  border-radius: 3px;
}

.rarity-tag-legend { background: rgba(184,148,46,0.1); color: var(--gold); }
.rarity-tag-epic   { background: rgba(212,175,55,0.1); color: var(--cinnabar); }
.rarity-tag-rare   { background: rgba(61,107,74,0.1); color: var(--jade); }
.rarity-tag-common { background: rgba(158,142,126,0.1); color: var(--stone); }

.badges-more {
  text-align: center;
  padding: 10px;
  font-family: var(--font-sans);
  font-size: 0.75rem;
  color: var(--cinnabar);
  cursor: pointer;
}
</style>
