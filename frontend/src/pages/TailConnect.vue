<template>
  <div class="tail-connect-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <van-loading type="spinner" size="48px">加载中...</van-loading>
    </div>

    <template v-else>
      <!-- 等待房间阶段 -->
      <div v-if="phase === 'waiting'" class="waiting-phase">
        <div class="waiting-card">
          <h2>接尾飞花令</h2>
          <p class="mode-desc">用上一句的尾字，接出新的诗句</p>
          
          <div class="room-info">
            <div class="info-row">
              <span class="label">房间号</span>
              <span class="value">{{ roomCode }}</span>
              <van-button size="small" @click="copyCode">复制</van-button>
            </div>
            <div class="info-row">
              <span class="label">玩家</span>
              <span class="value">{{ players.length }} / 8</span>
            </div>
            <div class="info-row">
              <span class="label">模式</span>
              <span class="value">接尾飞花令</span>
            </div>
          </div>

          <div class="players-list">
            <div 
              v-for="player in players" 
              :key="player.id"
              class="player-item"
            >
              <span class="host-badge" v-if="player.id === hostId">房主</span>
              <span class="player-name">{{ player.nickname }}</span>
            </div>
          </div>

          <van-button 
            v-if="isHost" 
            type="primary" 
            block
            :disabled="players.length < 2"
            @click="startGame"
          >
            {{ players.length < 2 ? '等待更多玩家...' : '开始游戏' }}
          </van-button>
          
          <van-button v-else type="default" disabled block>
            等待房主开始...
          </van-button>

          <van-button plain block @click="leaveRoom" class="leave-btn">
            离开房间
          </van-button>
        </div>
      </div>

      <!-- 游戏阶段 -->
      <TailConnectGame
        v-else-if="phase === 'playing'"
        ref="gameRef"
        :room-id="roomId"
        :players="players"
        :current-player-id="currentPlayerId"
        :current-char="currentChar"
        :current-round="currentRound"
        :time-limit="timeLimit"
        :used-chars="usedChars"
        :my-id="myId"
        @submit="handleSubmit"
        @play-again="handlePlayAgain"
        @back-home="handleBackHome"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { showToast, showSuccessToast, showFailToast } from 'vant'
import { useRoute, useRouter } from 'vue-router'
import TailConnectGame from '../components/game/TailConnectGame.vue'
import { socket } from '../socket'
import { api } from '../api'

interface Player {
  id: string
  nickname: string
  score: number
  correctCount: number
  streak: number
  isAlive: boolean
}

const route = useRoute()
const router = useRouter()

// 状态
const loading = ref(true)
const phase = ref<'waiting' | 'playing'>('waiting')
const roomId = ref('')
const roomCode = ref('')
const hostId = ref('')
const players = ref<Player[]>([])
const currentPlayerId = ref('')
const currentChar = ref('月')
const currentRound = ref(1)
const timeLimit = ref(8)
const usedChars = ref<string[]>([])
const myId = ref('')

const gameRef = ref<InstanceType<typeof TailConnectGame>>()

// 计算属性
const isHost = computed(() => myId.value === hostId.value)

// 初始化
onMounted(async () => {
  // 获取房间信息
  const room_id = route.params.roomId as string
  
  if (room_id) {
    roomId.value = room_id
    await joinRoom(room_id)
  } else {
    // 创建房间
    await createRoom()
  }

  // 连接 Socket
  initSocket()
  
  loading.value = false
})

// 创建房间
async function createRoom() {
  try {
    const res = await api.createRoom({
      mode: 'TAIL_CONNECT',
      keywords: ['月', '花', '春', '秋', '风', '雨'],
      time_limit_sec: 8,
      max_players: 8
    })
    
    const data = res.data
    roomId.value = data.room_id
    roomCode.value = data.code
    hostId.value = data.host_user_id
    myId.value = data.my_user_id
  } catch (e) {
    showFailToast('创建房间失败')
    router.replace('/')
  }
}

// 加入房间
async function joinRoom(room_id: string) {
  try {
    const res = await api.joinRoom(room_id)
    const data = res.data
    roomId.value = data.room_id
    roomCode.value = data.code
    hostId.value = data.host_user_id
    myId.value = data.my_user_id
    players.value = data.members || []
  } catch (e) {
    showFailToast('加入房间失败')
    router.replace('/')
  }
}

// Socket 初始化
function initSocket() {
  socket.connect()
  
  // 房间快照
  socket.on('room:snapshot', (data) => {
    players.value = data.members.map((m: any) => ({
      id: m.user_id,
      nickname: m.nickname,
      score: 0,
      correctCount: 0,
      streak: 0,
      isAlive: m.is_alive !== false
    }))
    
    if (data.room?.host_user_id) {
      hostId.value = data.room.host_user_id
    }
  })

  // 成员变化
  socket.on('room:member-changed', (data) => {
    socket.emit('room:subscribe', { room_id: roomId.value })
  })

  // 游戏开始
  socket.on('game:started', (data) => {
    phase.value = 'playing'
    currentChar.value = data.current_char || '月'
    currentRound.value = 1
    usedChars.value = []
    
    // 更新玩家存活状态
    players.value = data.members.map((m: any, i: number) => ({
      ...players.value.find(p => p.id === m.user_id) || {},
      id: m.user_id,
      isAlive: true,
      score: 0,
      streak: 0
    }))
    
    // 第一个玩家
    if (data.members?.length > 0) {
      currentPlayerId.value = data.members[0].user_id
    }
  })

  // 回合开始
  socket.on('turn:started', (data) => {
    currentPlayerId.value = data.player_id
    currentRound.value = data.round_no
    timeLimit.value = data.time_limit_sec || 8
    gameRef.value?.startTimer()
    gameRef.value?.loadSuggestions()
  })

  // 答案结果
  socket.on('answer:result', (data) => {
    const player = players.value.find(p => p.id === data.user_id)
    if (player && data.result === 'VALID') {
      player.score += data.score_delta
      player.correctCount++
      player.streak++
    }
    
    if (data.next_char) {
      currentChar.value = data.next_char
      usedChars.value.push(data.next_char)
    }
    
    if (data.result !== 'VALID' && data.eliminated) {
      player && (player.isAlive = false)
    }
  })

  // 玩家淘汰
  socket.on('player:eliminated', (data) => {
    const player = players.value.find(p => p.id === data.user_id)
    if (player) {
      player.isAlive = false
      gameRef.value?.showEliminate(data.reason, data.rare_poem)
    }
  })

  // 游戏结束
  socket.on('game:finished', (data) => {
    const ranking = data.results || []
    const winner = ranking.find((r: any) => r.is_winner)
    gameRef.value?.showResultPopup(ranking, winner)
  })

  // 错误
  socket.on('system:error', (data) => {
    showFailToast(data.message)
  })

  // 连接房间
  socket.connectRoom(roomId.value)
}

// 提交答案
function handleSubmit(answer: string) {
  socket.submitAnswer(roomId.value, '', answer)
}

// 开始游戏
function startGame() {
  socket.emit('room:start', { room_id: roomId.value })
}

// 离开房间
function leaveRoom() {
  socket.disconnectRoom()
  router.replace('/')
}

// 再来一局
function handlePlayAgain() {
  // 重置状态并重新开始
  phase.value = 'waiting'
  currentRound.value = 1
  usedChars.value = []
  players.value.forEach(p => {
    p.score = 0
    p.streak = 0
    p.correctCount = 0
    p.isAlive = true
  })
}

// 返回首页
function handleBackHome() {
  router.replace('/')
}

// 复制房间号
function copyCode() {
  navigator.clipboard.writeText(roomCode.value)
  showSuccessToast('已复制房间号')
}

// 清理
onUnmounted(() => {
  socket.disconnectRoom()
})
</script>

<style scoped>
.tail-connect-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8f4e8 0%, #f0ebe0 100%);
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.waiting-phase {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
}

.waiting-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.waiting-card h2 {
  text-align: center;
  font-size: 24px;
  color: #333;
  margin: 0 0 8px;
}

.mode-desc {
  text-align: center;
  color: #999;
  font-size: 14px;
  margin: 0 0 24px;
}

.room-info {
  background: #f8f8f8;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.info-row:not(:last-child) {
  border-bottom: 1px solid #eee;
}

.info-row .label {
  width: 80px;
  color: #666;
  font-size: 14px;
}

.info-row .value {
  flex: 1;
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.players-list {
  margin-bottom: 20px;
}

.player-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 8px;
}

.host-badge {
  font-size: 10px;
  padding: 2px 6px;
  background: #c9a227;
  color: white;
  border-radius: 4px;
}

.player-name {
  font-size: 14px;
  color: #333;
}

.leave-btn {
  margin-top: 12px;
}
</style>
