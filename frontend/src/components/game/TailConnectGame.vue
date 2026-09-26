<template>
  <div class="tail-connect-game">
    <!-- 顶部状态栏 -->
    <header class="game-header">
      <div class="round-info">
        <span class="round-label">第 {{ currentRound }} 轮</span>
        <span class="player-count">{{ alivePlayers.length }}人存活</span>
      </div>
      
      <div class="keyword-display">
        <span class="keyword-label">当前接字</span>
        <span class="keyword-char">{{ currentChar }}</span>
      </div>
    </header>

    <!-- 玩家列表 -->
    <div class="players-row">
      <div 
        v-for="player in players" 
        :key="player.id"
        class="player-item"
        :class="{ 
          'is-active': player.id === currentPlayerId,
          'is-eliminated': !player.isAlive,
          'is-self': player.id === myId
        }"
      >
        <div class="player-avatar">{{ player.nickname?.slice(-2) || '?' }}</div>
        <div class="player-name">{{ player.nickname || '玩家' }}</div>
        <div class="player-score">{{ player.score }}分</div>
        <div v-if="player.id === currentPlayerId" class="active-indicator">轮到你了</div>
      </div>
    </div>

    <!-- 回合计时器 -->
    <div class="turn-timer" v-if="isMyTurn && timeRemaining > 0">
      <div 
        class="timer-ring"
        :class="{ 'is-warning': timeRemaining <= 3 }"
        :style="{ '--progress': timerProgress }"
      >
        <span class="timer-number">{{ timeRemaining }}</span>
      </div>
      <p class="timer-hint">剩余时间</p>
    </div>

    <!-- 等待提示 -->
    <div class="waiting-hint" v-else-if="!isMyTurn">
      <p class="hint-text">等待 <strong>{{ currentPlayerName }}</strong> 作答...</p>
      <p class="hint-char">请用包含「<span class="highlight">{{ currentChar }}</span>」字的诗句接龙</p>
    </div>

    <!-- 答案输入区 -->
    <div class="answer-section" v-if="isMyTurn">
      <div class="input-hint">
        <van-icon name="info-o" />
        请输入包含「<span class="highlight">{{ currentChar }}</span>」字的诗句
      </div>
      
      <van-field
        v-model="answerText"
        placeholder="例如：海上生明月"
        :disabled="isSubmitting"
        maxlength="30"
        show-word-limit
        @keyup.enter="submitAnswer"
      >
        <template #left-icon>
          <van-icon name="edit" />
        </template>
      </van-field>

      <!-- 快捷输入 -->
      <div class="quick-inputs">
        <van-button 
          v-for="suggestion in suggestions" 
          :key="suggestion"
          size="small" 
          plain
          @click="answerText = suggestion"
        >
          {{ suggestion }}
        </van-button>
      </div>

      <!-- 语音输入按钮 -->
      <div class="voice-input">
        <van-button 
          :icon="isListening ? 'stop-circle-o' : 'volume-o'"
          type="primary"
          :loading="isListening"
          :disabled="isSubmitting"
          @click="toggleVoice"
        >
          {{ isListening ? '停止' : '语音输入' }}
        </van-button>
      </div>

      <!-- 提交按钮 -->
      <van-button 
        type="primary" 
        block
        :loading="isSubmitting"
        :disabled="!answerText.trim() || isSubmitting"
        @click="submitAnswer"
      >
        提交答案
      </van-button>
    </div>

    <!-- 已用诗句列表 -->
    <div class="used-lines">
      <div class="section-title">已用接字</div>
      <div class="char-tags">
        <span 
          v-for="char in usedChars" 
          :key="char"
          class="char-tag"
        >{{ char }}</span>
      </div>
    </div>

    <!-- 结算弹窗 -->
    <van-popup v-model:show="showResult" position="bottom" round>
      <div class="result-popup">
        <div class="result-header">
          <h2>游戏结束</h2>
        </div>
        
        <div class="winner-section" v-if="winner">
          <div class="winner-badge">🏆</div>
          <div class="winner-name">{{ winner.nickname }}</div>
          <div class="winner-score">{{ winner.score }}分</div>
        </div>

        <div class="ranking-list">
          <div 
            v-for="(item, index) in ranking"
            :key="item.id"
            class="rank-item"
            :class="{ 'is-self': item.id === myId }"
          >
            <span class="rank-number">{{ index + 1 }}</span>
            <span class="rank-name">{{ item.nickname }}</span>
            <span class="rank-score">{{ item.score }}分</span>
          </div>
        </div>

        <div class="result-actions">
          <van-button type="primary" block @click="$emit('play-again')">
            再来一局
          </van-button>
          <van-button plain block @click="$emit('back-home')">
            返回首页
          </van-button>
        </div>
      </div>
    </van-popup>

    <!-- 淘汰提示 -->
    <van-dialog
      v-model:show="showEliminateHint"
      title="很遗憾"
      show-cancel-button
      @confirm="$emit('continue-watch')"
    >
      <div class="eliminate-content">
        <p>你被淘汰了！</p>
        <p class="eliminate-reason">{{ eliminateReason }}</p>
        <p class="eliminate-poem" v-if="eliminatedPoem">
          这句诗不错：{{ eliminatedPoem }}
        </p>
      </div>
    </van-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { showToast, showFailToast } from 'vant'
import { useSpeechRecognition } from '../../composables/useSpeechRecognition'

interface Player {
  id: string
  nickname: string
  score: number
  correctCount: number
  streak: number
  isAlive: boolean
}

interface Props {
  roomId: string
  players: Player[]
  currentPlayerId: string
  currentChar: string
  currentRound: number
  timeLimit: number
  usedChars: string[]
  myId: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  submit: [answer: string]
  'play-again': []
  'back-home': []
  'continue-watch': []
}>()

// 状态
const answerText = ref('')
const isSubmitting = ref(false)
const timeRemaining = ref(0)
const showResult = ref(false)
const showEliminateHint = ref(false)
const eliminateReason = ref('')
const eliminatedPoem = ref('')
const ranking = ref<Player[]>([])
const winner = ref<Player | null>(null)
const suggestions = ref<string[]>([])

// 计算属性
const alivePlayers = computed(() => props.players.filter(p => p.isAlive))
const isMyTurn = computed(() => props.currentPlayerId === props.myId)
const currentPlayerName = computed(() => {
  const p = props.players.find(p => p.id === props.currentPlayerId)
  return p?.nickname || '未知'
})
const timerProgress = computed(() => {
  return ((props.timeLimit - timeRemaining.value) / props.timeLimit) * 100
})

// 语音识别
const {
  isListening,
  transcript,
  error: voiceError,
  start: startListening,
  stop: stopListening
} = useSpeechRecognition()

// 监听语音输入
watch(transcript, (newVal) => {
  if (newVal) {
    answerText.value = newVal
  }
})

watch(voiceError, (err) => {
  if (err) {
    showFailToast('语音识别失败，请手动输入')
  }
})

function toggleVoice() {
  if (isListening.value) {
    stopListening()
  } else {
    startListening()
  }
}

// 提交答案
async function submitAnswer() {
  if (!answerText.value.trim()) {
    showToast('请输入诗句')
    return
  }
  
  if (isSubmitting.value) return
  
  isSubmitting.value = true
  
  try {
    emit('submit', answerText.value.trim())
    answerText.value = ''
  } finally {
    isSubmitting.value = false
  }
}

// 计时器
let timerInterval: number | null = null

function startTimer() {
  timeRemaining.value = props.timeLimit
  
  if (timerInterval) {
    clearInterval(timerInterval)
  }
  
  timerInterval = window.setInterval(() => {
    if (timeRemaining.value > 0) {
      timeRemaining.value--
      
      if (timeRemaining.value === 0) {
        handleTimeout()
      }
    }
  }, 1000)
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

function handleTimeout() {
  showToast('超时了！')
  // 超时处理由父组件控制
}

// 加载建议
function loadSuggestions() {
  // 根据当前字加载建议诗句
  const suggestionsMap: Record<string, string[]> = {
    '月': ['海上生明月', '床前明月光', '举头望明月', '春江花月夜'],
    '明': ['明日复明日', '清明时节雨纷纷'],
    '花': ['春眠不觉晓', '花开时节动京城'],
    '春': ['春风又绿江南岸', '春城无处不飞花'],
    '风': ['风吹草低见牛羊', '春风不度玉门关'],
    '雨': ['夜来风雨声', '清明时节雨纷纷'],
    '秋': ['秋风吹不尽', '秋水共长天一色'],
    '山': ['山色空蒙雨亦奇', '山重水复疑无路'],
    '水': ['水光潋滟晴方好', '桃花潭水深千尺'],
  }
  
  suggestions.value = suggestionsMap[props.currentChar] || []
}

// 暴露方法给父组件
defineExpose({
  startTimer,
  stopTimer,
  showResultPopup: (r: Player[], w: Player | null) => {
    ranking.value = r
    winner.value = w
    showResult.value = true
  },
  showEliminate: (reason: string, poem?: string) => {
    eliminateReason.value = reason
    eliminatedPoem.value = poem || ''
    showEliminateHint.value = true
  },
  loadSuggestions
})

// 监听回合变化
watch(() => props.currentPlayerId, () => {
  if (isMyTurn.value) {
    startTimer()
    loadSuggestions()
  }
})

watch(() => props.currentChar, () => {
  loadSuggestions()
})

onMounted(() => {
  loadSuggestions()
  if (isMyTurn.value) {
    startTimer()
  }
})

onUnmounted(() => {
  stopTimer()
  stopListening()
})
</script>

<style scoped>
.tail-connect-game {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8f4e8 0%, #f0ebe0 100%);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.round-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.round-label {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.player-count {
  font-size: 12px;
  color: #666;
}

.keyword-display {
  text-align: center;
}

.keyword-label {
  font-size: 12px;
  color: #999;
}

.keyword-char {
  display: block;
  font-size: 32px;
  font-weight: 700;
  color: #c85050;
  font-family: 'STKaiti', serif;
}

.players-row {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 8px 0;
}

.player-item {
  flex-shrink: 0;
  width: 70px;
  text-align: center;
  padding: 8px;
  background: white;
  border-radius: 8px;
  opacity: 0.6;
  transition: all 0.3s ease;
}

.player-item.is-active {
  opacity: 1;
  background: linear-gradient(135deg, #fff9e6 0%, #fff3cc 100%);
  border: 2px solid #c9a227;
}

.player-item.is-eliminated {
  opacity: 0.3;
  text-decoration: line-through;
}

.player-item.is-self .player-avatar {
  border-color: #4a90d9;
}

.player-avatar {
  width: 40px;
  height: 40px;
  margin: 0 auto 4px;
  border-radius: 50%;
  background: linear-gradient(135deg, #e8dcc8 0%, #d4c4a8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  border: 2px solid transparent;
}

.player-name {
  font-size: 12px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.player-score {
  font-size: 10px;
  color: #999;
}

.active-indicator {
  font-size: 10px;
  color: #c9a227;
  margin-top: 4px;
}

.turn-timer {
  text-align: center;
  padding: 20px;
}

.timer-ring {
  width: 100px;
  height: 100px;
  margin: 0 auto;
  border-radius: 50%;
  background: conic-gradient(
    #4a90d9 calc(var(--progress) * 1%),
    #e8e4dc calc(var(--progress) * 1%)
  );
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.timer-ring::before {
  content: '';
  position: absolute;
  width: 80px;
  height: 80px;
  background: white;
  border-radius: 50%;
}

.timer-ring.is-warning {
  background: conic-gradient(
    #c85050 calc(var(--progress) * 1%),
    #e8e4dc calc(var(--progress) * 1%)
  );
}

.timer-number {
  position: relative;
  font-size: 32px;
  font-weight: 700;
  color: #333;
}

.timer-hint {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.waiting-hint {
  text-align: center;
  padding: 40px 20px;
}

.hint-text {
  font-size: 16px;
  color: #666;
  margin-bottom: 12px;
}

.hint-char {
  font-size: 18px;
  color: #333;
}

.highlight {
  color: #c85050;
  font-weight: 600;
}

.answer-section {
  background: white;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #666;
}

.quick-inputs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.voice-input {
  display: flex;
  justify-content: center;
}

.used-lines {
  background: white;
  border-radius: 12px;
  padding: 12px 16px;
}

.section-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.char-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.char-tag {
  padding: 4px 12px;
  background: linear-gradient(135deg, #f5f5f0 0%, #e8e4dc 100%);
  border-radius: 16px;
  font-size: 14px;
  color: #666;
}

.result-popup {
  padding: 24px;
}

.result-header {
  text-align: center;
  margin-bottom: 20px;
}

.result-header h2 {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.winner-section {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #fff9e6 0%, #fff3cc 100%);
  border-radius: 12px;
  margin-bottom: 20px;
}

.winner-badge {
  font-size: 48px;
}

.winner-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 8px 0;
}

.winner-score {
  font-size: 24px;
  color: #c9a227;
  font-weight: 700;
}

.ranking-list {
  margin-bottom: 20px;
}

.rank-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.rank-item.is-self {
  background: #f5f5f0;
  border-radius: 8px;
}

.rank-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e8e4dc;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #666;
  margin-right: 12px;
}

.rank-item:nth-child(1) .rank-number {
  background: #ffd700;
  color: #fff;
}

.rank-item:nth-child(2) .rank-number {
  background: #c0c0c0;
  color: #fff;
}

.rank-item:nth-child(3) .rank-number {
  background: #cd7f32;
  color: #fff;
}

.rank-name {
  flex: 1;
  font-size: 14px;
  color: #333;
}

.rank-score {
  font-size: 14px;
  color: #666;
}

.result-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.eliminate-content {
  padding: 20px;
  text-align: center;
}

.eliminate-content p {
  margin: 8px 0;
  color: #666;
}

.eliminate-reason {
  color: #c85050;
  font-size: 14px;
}

.eliminate-poem {
  font-style: italic;
  color: #999;
}
</style>
