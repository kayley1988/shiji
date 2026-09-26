<template>
  <div class="room-page bg-xuanzhi">

    <!-- ═══ 顶部导航 ═══════════════════════════════ -->
    <header class="nav-header">
      <div class="nav-left">
        <button class="nav-btn" @click="showSettings = true">
          <van-icon name="arrow-left" />
        </button>
      </div>
      <div class="nav-center">
        <span class="nav-code">{{ roomStore.room?.code }}</span>
        <span class="nav-mode-tag">{{ roomStore.room?.mode === 'SOLAR_TERM_ELEMENT' ? '节气五行' : '经典' }}</span>
      </div>
      <div class="nav-right">
        <button class="nav-btn" @click="copyCode">
          <van-icon name="description" />
        </button>
      </div>
    </header>

    <!-- ═══ 等待区 ═══════════════════════════════ -->
    <template v-if="roomStore.room?.status === 'WAITING'">

      <!-- 房间信息卡片 -->
      <section class="section-card animate-fadeUp">
        <div class="card-scroll-decor">
          <div class="scroll-rod top"></div>
          <div class="scroll-rod bottom"></div>
          <div class="card-body">
            <div class="card-eyebrow">房间配置</div>
            <h2 class="card-title">雅集待启</h2>

            <!-- 关键词 -->
            <div class="info-row">
              <span class="info-label">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                飞花关键字
              </span>
              <div class="kw-chips">
                <span class="kw-chip" v-for="kw in (roomStore.room?.keywords || [])" :key="kw">{{ kw }}</span>
              </div>
            </div>

            <!-- 配置 -->
            <div class="info-row">
              <span class="info-label">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><path d="M12 6v6l4 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                回合时限
              </span>
              <span class="info-value">{{ roomStore.room?.time_limit_sec }}秒</span>
            </div>

            <!-- 人数进度 -->
            <div class="info-row">
              <span class="info-label">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                房间人数
              </span>
              <span class="info-value">{{ roomStore.members.length }} / {{ roomStore.room?.max_players }}</span>
            </div>
            <div class="player-bar">
              <div class="player-bar-fill" :style="{ width: (roomStore.members.length / (roomStore.room?.max_players || 4)) * 100 + '%' }"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- 玩家卡片列表 -->
      <section class="section-players animate-fadeUp delay-1">
        <div class="section-header">
          <span class="header-line"></span>
          <span class="header-title">入席雅客</span>
          <span class="header-line"></span>
        </div>

        <div class="player-grid">
          <div
            v-for="(member, idx) in roomStore.members"
            :key="member.id"
            class="player-card"
            :class="{ 'is-host': member.role === 'host', 'is-self': member.user_id === authStore.user?.id }"
          >
            <!-- 座位号 -->
            <div class="seat-badge">{{ idx + 1 }}</div>
            <!-- 头像 -->
            <div class="player-avatar" :style="{ background: avatarGradient(member.user_id) }">
              {{ member.nickname.slice(-2) }}
            </div>
            <!-- 状态 -->
            <div class="online-dot" :class="{ offline: !member.is_online }"></div>
            <!-- 信息 -->
            <div class="player-name">{{ member.nickname }}</div>
            <div class="player-tag" v-if="member.role === 'host'">房主</div>
            <div class="player-tag tag-self" v-else-if="member.user_id === authStore.user?.id">我</div>
          </div>

          <!-- 空座位 -->
          <div
            v-for="n in Math.max(0, (roomStore.room?.max_players || 4) - roomStore.members.length)"
            :key="'empty-' + n"
            class="player-card empty-slot"
          >
            <div class="empty-icon">?</div>
            <div class="empty-label">等待入席</div>
          </div>
        </div>
      </section>

      <!-- 邀请卡片 -->
      <section class="section-invite animate-fadeUp delay-2">
        <div class="invite-card">
          <div class="invite-label">邀请好友加入</div>
          <div class="invite-code">{{ roomStore.room?.code }}</div>
          <van-button size="small" class="invite-btn" @click="copyCode">复制邀请码</van-button>
        </div>
      </section>

      <!-- 开始按钮 -->
      <div class="bottom-action" v-if="roomStore.isHost">
        <van-button
          class="btn-start"
          block
          round
          size="large"
          :disabled="roomStore.members.length < 2"
          @click="startGame"
        >
          <template v-if="roomStore.members.length < 2">
            <span class="btn-hint">等待至少2位玩家</span>
            <span class="btn-sub">{{ roomStore.members.length }}/2 人</span>
          </template>
          <template v-else>
            <span class="btn-text">开席</span>
          </template>
        </van-button>
      </div>
      <div class="bottom-hint" v-else>
        <span class="dot-pulse"></span>
        房主准备中，请稍候...
      </div>
    </template>

    <!-- ═══ 对战区 ═══════════════════════════════ -->
    <template v-else-if="roomStore.room?.status === 'PLAYING'">
      <section class="section-card battle-card animate-fadeUp">
        <!-- 当前出题者 -->
        <div class="current-player">
          <div class="cp-avatar" :style="{ background: avatarGradient(roomStore.room?.current_player_id) }">
            {{ currentPlayerName?.slice(-2) || '?' }}
          </div>
          <div class="cp-info">
            <div class="cp-label">当前出题</div>
            <div class="cp-name">{{ currentPlayerName || '—' }}</div>
          </div>
          <div class="timer-ring" :class="timerClass">
            <span class="timer-num">{{ timeLeft }}</span>
          </div>
        </div>

        <!-- 关键词高亮 -->
        <div class="keyword-display">
          <span class="kw-hint">请说出含</span>
          <span class="kw-highlight" v-for="kw in (roomStore.room?.keywords || [])" :key="kw">{{ kw }}</span>
          <span class="kw-hint">的诗句</span>
        </div>

        <!-- 答案输入 -->
        <div class="answer-area">
          <van-field
            v-model="answerText"
            placeholder="输入诗句，如：床前明月光"
            class="answer-input"
            :disabled="!canAnswer"
            @keyup.enter="submitAnswer"
          />
          <van-button
            class="submit-btn"
            type="primary"
            round
            :disabled="!canAnswer || !answerText.trim()"
            @click="submitAnswer"
          >
            <van-icon name="gem-o" />
            提交
          </van-button>
        </div>
      </section>

      <!-- 玩家积分板 -->
      <section class="section-scoreboard animate-fadeUp delay-1">
        <div class="section-header">
          <span class="header-line"></span>
          <span class="header-title">积分榜</span>
          <span class="header-line"></span>
        </div>
        <div class="score-list">
          <div
            v-for="(member, idx) in sortedMembers"
            :key="member.id"
            class="score-row"
            :class="{ 'self-row': member.user_id === authStore.user?.id }"
          >
            <div class="score-rank" :class="'rank-' + (idx + 1)">{{ idx + 1 }}</div>
            <div class="score-avatar" :style="{ background: avatarGradient(member.user_id) }">
              {{ member.nickname.slice(-2) }}
            </div>
            <div class="score-name">{{ member.nickname }}</div>
            <div class="score-val">{{ member.score }}分</div>
          </div>
        </div>
      </section>
    </template>

    <!-- ═══ 离开确认弹窗 ═════════════════════════ -->
    <van-popup v-model:show="showSettings" position="bottom" round class="sheet-popup">
      <div class="sheet-content">
        <div class="sheet-title">房间设置</div>
        <van-cell-group inset>
          <van-cell title="复制邀请码" is-link @click="copyCode" />
          <van-cell title="离开房间" is-link @click="leaveRoom" />
        </van-cell-group>
        <van-button block round class="sheet-cancel" @click="showSettings = false">取消</van-button>
      </div>
    </van-popup>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showConfirmDialog, Toast } from 'vant'
import { useRoomStore } from '../stores/room'
import { useAuthStore } from '../stores/auth'
import { socket } from '../socket'
import { api } from '../api'

const route = useRoute()
const router = useRouter()
const roomStore = useRoomStore()
const authStore = useAuthStore()

const roomId = route.params.id as string
const answerText = ref('')
const timeLeft = ref(0)
const showSettings = ref(false)
let timer: ReturnType<typeof setInterval> | null = null

const currentPlayerName = computed(() => {
  const pid = roomStore.room?.current_player_id
  return roomStore.members.find(m => m.user_id === pid)?.nickname
})

const canAnswer = computed(() => {
  return roomStore.currentTurn?.player_id === authStore.user?.id
})

const sortedMembers = computed(() => {
  return [...roomStore.members].sort((a, b) => (b.score ?? 0) - (a.score ?? 0))
})

const timerClass = computed(() => {
  if (timeLeft.value <= 5) return 'timer-danger'
  if (timeLeft.value <= 10) return 'timer-warn'
  return 'timer-safe'
})

function avatarGradient(uid?: string): string {
  if (!uid) return 'linear-gradient(135deg, #9e8e7e, #c4b8a8)'
  const h = uid.charCodeAt(0) * 7 + uid.charCodeAt(uid.length - 1) * 13
  const hue = h % 360
  return `linear-gradient(135deg, hsl(${hue},35%,55%), hsl(${(hue+40)%360},45%,45%))`
}

function startTimer() {
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    if (timeLeft.value > 0) timeLeft.value--
    else clearInterval(timer!)
  }, 1000)
}

const handleAnswerResult = (data: any) => {
  const member = roomStore.members.find(m => m.user_id === data.user_id)
  if (member) member.score += data.score_delta
}

onMounted(async () => {
  const turn = roomStore.currentTurn
  if (turn) {
    timeLeft.value = turn.time_limit_sec || 15
    startTimer()
  }

  socket.on('answer:result', handleAnswerResult)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  socket.off('answer:result', handleAnswerResult)
})

async function startGame() {
  try {
    Toast.loading({ message: '开席...', forbidClick: true })
    await roomStore.startGame()
    Toast.loading.hide()
  } catch (e: any) {
    Toast.loading.hide()
    showToast(e?.response?.data?.error?.message || '开席失败')
  }
}

function submitAnswer() {
  if (!answerText.value.trim() || !roomStore.currentTurn) return
  socket.submitAnswer(roomId, roomStore.currentTurn.turn_id, answerText.value)
  answerText.value = ''
}

async function copyCode() {
  const code = roomStore.room?.code
  if (code) {
    await navigator.clipboard.writeText(code)
    showToast('邀请码已复制')
    showSettings.value = false
  }
}

async function leaveRoom() {
  showSettings.value = false
  await showConfirmDialog({ title: '离开房间', message: '确定要离开房间吗？' })
  roomStore.reset()
  router.replace('/')
}
</script>

<style scoped>
.room-page {
  min-height: 100vh;
  padding-bottom: 100px;
}

/* ── 顶部导航 ── */
.nav-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(250,246,240,0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(158,142,126,0.15);
}

.nav-btn {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  background: none; border: none;
  color: var(--ink);
  font-size: 20px;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: background 0.2s;
}
.nav-btn:hover { background: rgba(158,142,126,0.1); }

.nav-center {
  display: flex;
  align-items: center;
  gap: 8px;
}
.nav-code {
  font-family: var(--font-sans);
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 3px;
  color: var(--ink);
}
.nav-mode-tag {
  font-size: 11px;
  padding: 2px 8px;
  background: var(--parchment-dark);
  color: var(--stone);
  border-radius: var(--radius-full);
  border: 1px solid var(--stone-light);
}

/* ── 卷轴卡片通用 ── */
.section-card {
  margin: 16px;
}
.card-scroll-decor {
  position: relative;
  background: var(--parchment);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}
.scroll-rod {
  position: absolute;
  left: 0; right: 0;
  height: 12px;
  background: linear-gradient(90deg, var(--gold) 0%, var(--gold-light) 50%, var(--gold) 100%);
  border-radius: 4px;
  z-index: 1;
}
.scroll-rod.top { top: 0; }
.scroll-rod.bottom { bottom: 0; }

.card-body {
  padding: 28px 20px 24px;
}
.card-eyebrow {
  font-family: var(--font-sans);
  font-size: 11px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--stone);
  margin-bottom: 6px;
}
.card-title {
  font-family: var(--font-display);
  font-size: 28px;
  color: var(--ink);
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px dashed rgba(158,142,126,0.2);
}
.info-row:last-of-type { border-bottom: none; }

.info-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--stone);
}
.info-label svg { color: var(--stone-light); }

.info-value {
  font-family: var(--font-sans);
  font-size: 15px;
  font-weight: 500;
  color: var(--ink);
}

.kw-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.kw-chip {
  padding: 3px 12px;
  background: linear-gradient(135deg, var(--cinnabar), var(--cinnabar-light));
  color: #fff;
  font-size: 13px;
  border-radius: var(--radius-full);
  font-family: var(--font-serif);
}

.player-bar {
  height: 4px;
  background: var(--parchment-dark);
  border-radius: 2px;
  margin-top: 10px;
  overflow: hidden;
}
.player-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--jade), var(--celadon));
  border-radius: 2px;
  transition: width 0.5s var(--ease-out);
}

/* ── 玩家网格 ── */
.section-players {
  padding: 0 16px;
  margin-bottom: 16px;
}
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.header-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--stone-light), transparent);
}
.header-title {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--stone);
  white-space: nowrap;
}

.player-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.player-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 8px;
  background: #fff;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s, box-shadow 0.2s;
}
.player-card.is-host {
  border: 1.5px solid var(--gold);
  box-shadow: 0 0 0 3px rgba(184,148,46,0.12);
}
.player-card.is-self {
  border: 1.5px solid var(--jade);
}

.seat-badge {
  position: absolute;
  top: 6px;
  left: 6px;
  width: 18px; height: 18px;
  background: var(--parchment-dark);
  color: var(--stone);
  font-size: 10px;
  font-family: var(--font-sans);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}
.player-card.is-host .seat-badge { background: var(--gold); color: #fff; }

.player-avatar {
  width: 48px; height: 48px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;
  color: #fff;
  font-family: var(--font-display);
  margin-bottom: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.online-dot {
  position: absolute;
  top: 10px; right: 10px;
  width: 8px; height: 8px;
  background: var(--jade);
  border-radius: 50%;
  border: 2px solid #fff;
}
.online-dot.offline { background: var(--stone-light); }

.player-name {
  font-size: 13px;
  color: var(--ink);
  text-align: center;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.player-tag {
  font-size: 10px;
  padding: 1px 6px;
  background: var(--gold);
  color: #fff;
  border-radius: var(--radius-full);
  margin-top: 4px;
}
.player-tag.tag-self {
  background: var(--jade);
}

.empty-slot {
  background: rgba(250,246,240,0.6);
  border: 1.5px dashed var(--stone-light);
  box-shadow: none;
}
.empty-icon {
  font-size: 24px;
  color: var(--stone-light);
  margin-bottom: 4px;
}
.empty-label {
  font-size: 11px;
  color: var(--stone-light);
}

/* ── 邀请卡片 ── */
.section-invite {
  padding: 0 16px;
  margin-bottom: 16px;
}
.invite-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 18px;
  background: linear-gradient(135deg, rgba(184,148,46,0.08), rgba(184,148,46,0.04));
  border: 1px solid rgba(184,148,46,0.2);
  border-radius: var(--radius-md);
}
.invite-label {
  font-size: 13px;
  color: var(--stone);
  white-space: nowrap;
}
.invite-code {
  flex: 1;
  font-family: var(--font-sans);
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 5px;
  color: var(--gold);
  text-align: center;
}
.invite-btn {
  background: var(--gold) !important;
  border-color: var(--gold) !important;
  color: #fff !important;
  font-size: 12px !important;
  height: 28px !important;
}

/* ── 底部按钮 ── */
.bottom-action {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  padding: 12px 20px 20px;
  background: linear-gradient(transparent, var(--parchment) 30%);
}
.btn-start {
  height: 52px;
  background: linear-gradient(135deg, var(--cinnabar), var(--cinnabar-light)) !important;
  border: none !important;
  color: #fff !important;
  font-family: var(--font-display) !important;
  font-size: 18px !important;
  box-shadow: 0 4px 20px rgba(155,58,42,0.35) !important;
}
.btn-start:disabled {
  background: var(--stone-light) !important;
  box-shadow: none !important;
}
.btn-text { display: block; }
.btn-hint { display: block; font-size: 13px; opacity: 0.8; }
.btn-sub { display: block; font-size: 11px; opacity: 0.7; margin-top: 2px; }

.bottom-hint {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  padding: 16px 20px 28px;
  background: linear-gradient(transparent, var(--parchment) 30%);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  color: var(--stone);
}
.dot-pulse {
  width: 8px; height: 8px;
  background: var(--celadon);
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.8); }
}

/* ── 对战区 ── */
.battle-card { margin-bottom: 16px; }
.current-player {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 4px;
  border-bottom: 1px dashed rgba(158,142,126,0.2);
  margin-bottom: 16px;
}
.cp-avatar {
  width: 52px; height: 52px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  font-size: 20px;
  font-family: var(--font-display);
  box-shadow: var(--shadow-sm);
  flex-shrink: 0;
}
.cp-info { flex: 1; }
.cp-label { font-size: 12px; color: var(--stone); }
.cp-name { font-size: 18px; font-weight: 600; color: var(--ink); }

.timer-ring {
  width: 52px; height: 52px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  border: 3px solid var(--celadon);
  transition: border-color 0.3s;
}
.timer-ring.timer-danger { border-color: var(--danger); }
.timer-ring.timer-warn { border-color: var(--warning); }
.timer-num {
  font-family: var(--font-sans);
  font-size: 18px;
  font-weight: 700;
  color: var(--ink);
}

.keyword-display {
  text-align: center;
  padding: 12px 0 20px;
}
.kw-hint { font-size: 15px; color: var(--stone); }
.kw-highlight {
  display: inline-block;
  margin: 0 6px;
  padding: 4px 16px;
  background: linear-gradient(135deg, var(--cinnabar), var(--cinnabar-light));
  color: #fff;
  font-size: 20px;
  font-family: var(--font-display);
  border-radius: var(--radius-sm);
}

.answer-area {
  display: flex;
  gap: 10px;
  align-items: center;
}
.answer-input {
  flex: 1;
  background: var(--parchment-dark) !important;
  border: 1px solid var(--stone-light) !important;
  border-radius: var(--radius-full) !important;
  padding: 0 16px !important;
  --van-field-input-text-color: var(--ink);
}
.submit-btn {
  background: linear-gradient(135deg, var(--jade), var(--jade-light)) !important;
  border: none !important;
  color: #fff !important;
  height: 44px !important;
  padding: 0 20px !important;
}
.submit-btn .van-icon { margin-right: 4px; }

/* ── 积分榜 ── */
.section-scoreboard {
  padding: 0 16px;
}
.score-list {
  background: #fff;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
.score-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(158,142,126,0.1);
}
.score-row:last-child { border-bottom: none; }
.score-row.self-row { background: rgba(61,107,74,0.05); }
.score-rank {
  width: 24px; height: 24px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px;
  font-family: var(--font-sans);
  font-weight: 700;
  background: var(--parchment-dark);
  color: var(--stone);
  flex-shrink: 0;
}
.score-rank.rank-1 { background: linear-gradient(135deg, #D4A017, #F4CF47); color: #fff; }
.score-rank.rank-2 { background: linear-gradient(135deg, #8B7355, #A08060); color: #fff; }
.score-rank.rank-3 { background: linear-gradient(135deg, #7A5C3A, #9A7A58); color: #fff; }
.score-avatar {
  width: 36px; height: 36px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  font-size: 14px;
  font-family: var(--font-display);
  flex-shrink: 0;
}
.score-name {
  flex: 1;
  font-size: 14px;
  color: var(--ink);
}
.score-val {
  font-family: var(--font-sans);
  font-size: 15px;
  font-weight: 600;
  color: var(--cinnabar);
}

/* ── 底部弹窗 ── */
.sheet-popup {
  background: var(--parchment) !important;
}
.sheet-content {
  padding: 24px 16px 32px;
}
.sheet-title {
  font-family: var(--font-display);
  font-size: 20px;
  text-align: center;
  color: var(--ink);
  margin-bottom: 20px;
}
.sheet-cancel {
  margin-top: 16px;
  background: var(--parchment-dark) !important;
  border: none !important;
  color: var(--stone) !important;
}

/* ── 动画 ── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fadeUp { animation: fadeUp 0.5s var(--ease-out) both; }
.delay-1 { animation-delay: 0.1s; }
.delay-2 { animation-delay: 0.2s; }
</style>
