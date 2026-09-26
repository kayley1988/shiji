<template>
  <div class="voice-battle-page">
    <!-- 顶部状态 -->
    <header class="battle-header">
      <div class="score-board">
        <div class="score-item player">
          <span class="score-label">你</span>
          <span class="score-value">{{ playerScore }}</span>
        </div>
        <div class="vs-divider">⚔️</div>
        <div class="score-item ai">
          <span class="score-label">AI</span>
          <span class="score-value">{{ aiScore }}</span>
        </div>
      </div>
      <div class="round-info">第 {{ currentRound }} / {{ totalRounds }} 轮</div>
    </header>

    <!-- 对战区域 -->
    <div class="battle-arena">
      <!-- AI 头像 -->
      <div class="avatar ai-avatar" :class="{ speaking: aiSpeaking }">
        <div class="avatar-ring"></div>
        <div class="avatar-face">
          <span v-if="aiSpeaking">🤖</span>
          <span v-else>🤖</span>
        </div>
        <div class="speaking-waves" v-if="aiSpeaking">
          <div class="wave-line"></div>
          <div class="wave-line"></div>
          <div class="wave-line"></div>
        </div>
        <div class="ai-status" v-if="aiSpeaking">
          <span class="pulse"></span>
        </div>
      </div>

      <!-- 对话区域 -->
      <div class="dialogue-area">
        <!-- AI 消息 -->
        <Transition name="slide-up">
          <div v-if="currentQuestion" class="bubble ai-bubble">
            <div class="bubble-header">
              <span class="bubble-avatar">🤖</span>
              <span class="bubble-name">AI 出题</span>
            </div>
            <div class="bubble-body">
              <div class="question-type-badge" :class="selectedMode">
                {{ modeLabel }}
              </div>
              <p class="question-text">
                <template v-if="selectedMode === 'quote'">
                  请接下句：<br>
                  <span class="quote-line">「{{ currentQuestion.quote }}」</span>
                </template>
                <template v-else-if="selectedMode === 'tail'">
                  请用「<span class="keyword">{{ currentQuestion.start_char || currentQuestion.keyword }}</span>」字开头的诗句回答
                </template>
                <template v-else>
                  请说出包含「<span class="keyword">{{ currentQuestion.keyword }}</span>」字的诗句
                </template>
              </p>
              <p class="ai-note" v-if="currentQuestion.type === 'ai_generated'">
                <van-icon name="info-o" /> AI 拓展生成
              </p>
            </div>
          </div>
        </Transition>

        <!-- 玩家回复 -->
        <Transition name="slide-up">
          <div v-if="playerAnswer" class="bubble player-bubble">
            <div class="bubble-body">
              <p class="answer-text">「{{ playerAnswer }}」</p>
            </div>
            <div class="bubble-footer">
              <span class="answer-time">{{ answerTime }}</span>
            </div>
          </div>
        </Transition>
      </div>

      <!-- 玩家头像 -->
      <div class="avatar player-avatar" :class="{ listening: isListening }">
        <div class="avatar-ring"></div>
        <div class="avatar-face">😀</div>
        <div class="speaking-waves" v-if="isListening">
          <div class="wave-line"></div>
          <div class="wave-line"></div>
          <div class="wave-line"></div>
        </div>
      </div>
    </div>

    <!-- 计时区域 -->
    <div class="timer-section" v-if="phase === 'playing'">
      <div class="timer-track">
        <div 
          class="timer-fill" 
          :class="{ 
            'warning': timeRemaining <= 3, 
            'danger': timeRemaining <= 1 
          }"
          :style="{ width: timerPercent + '%' }"
        ></div>
      </div>
      <div class="timer-label">
        <span v-if="timeRemaining > 0">{{ timeRemaining }}s</span>
        <span v-else class="timeout-text">时间到！</span>
      </div>
    </div>

    <!-- 操作区域 -->
    <div class="action-section">
      <!-- 麦克风按钮 -->
      <div 
        class="mic-wrapper"
        @touchstart.prevent="handleMicDown"
        @touchend.prevent="handleMicUp"
        @mousedown="handleMicDown"
        @mouseup="handleMicUp"
      >
        <div 
          class="mic-btn"
          :class="{
            'recording': isRecording,
            'listening': isListening,
            'success': lastResult === 'correct',
            'error': lastResult === 'wrong'
          }"
        >
          <van-icon :name="isRecording ? 'cross' : (isListening ? 'music-o' : 'volume')" />
          <div class="mic-ripple" v-if="isRecording"></div>
        </div>
        <span class="mic-label">
          {{ micLabel }}
        </span>
      </div>

      <!-- 结果反馈 -->
      <Transition name="fade">
        <div v-if="showFeedback" class="feedback-card" :class="lastResult">
          <van-icon :name="lastResult === 'correct' ? 'checked' : 'close'" />
          <span>{{ feedbackText }}</span>
        </div>
      </Transition>

      <!-- 跳过按钮 -->
      <van-button 
        plain 
        size="small" 
        class="skip-btn"
        @click="skipQuestion"
        v-if="canSkip"
      >
        跳过此题
      </van-button>
    </div>

    <!-- 进度条 -->
    <div class="progress-section">
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
      <div class="progress-label">
        <span>正确 {{ correctCount }}</span>
        <span>错误 {{ wrongCount }}</span>
        <span>连胜 {{ currentStreak }}</span>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 开始页面 -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <div class="overlay-page start-page" v-if="phase === 'start'">
      <div class="page-content">
        <div class="hero-section">
          <div class="hero-emoji">🤖</div>
          <h1>诗词对战</h1>
          <p class="hero-desc">与 AI 来一场精彩的诗词对决！</p>
        </div>

        <!-- 模式选择 -->
        <div class="mode-selector">
          <div class="selector-title">选择模式</div>
          <div class="mode-options">
            <div 
              v-for="mode in modes"
              :key="mode.id"
              class="mode-option"
              :class="{ active: selectedMode === mode.id }"
              @click="selectedMode = mode.id"
            >
              <span class="mode-icon">{{ mode.icon }}</span>
              <span class="mode-name">{{ mode.name }}</span>
              <span class="mode-desc">{{ mode.desc }}</span>
            </div>
          </div>
        </div>

        <!-- 关键字选择（仅飞花令模式） -->
        <div class="keyword-selector" v-if="selectedMode === 'keyword'">
          <div class="selector-title">选择关键字</div>
          <div class="keyword-grid">
            <div 
              v-for="kw in availableKeywords"
              :key="kw"
              class="keyword-chip"
              :class="{ active: selectedKeyword === kw }"
              @click="selectedKeyword = kw"
            >
              {{ kw }}
            </div>
          </div>
        </div>

        <!-- 难度选择 -->
        <div class="difficulty-selector">
          <div class="selector-title">选择难度</div>
          <van-radio-group v-model="difficulty" direction="horizontal">
            <van-radio name="easy">简单</van-radio>
            <van-radio name="medium">中等</van-radio>
            <van-radio name="hard">困难</van-radio>
          </van-radio-group>
        </div>

        <!-- 开始按钮 -->
        <van-button 
          type="primary" 
          size="large" 
          block
          class="start-btn"
          @click="startBattle"
        >
          <van-icon name="play-circle-o" size="20" />
          开始对战
        </van-button>

        <!-- TTS 语音设置 -->
        <div class="tts-settings">
          <div class="tts-header" @click="showVoicePanel = !showVoicePanel">
            <van-icon name="setting-o" />
            <span>语音设置</span>
            <van-icon :name="showVoicePanel ? 'arrow-up' : 'arrow-down'" />
          </div>
          <div class="tts-panel" v-if="showVoicePanel">
            <div class="voice-info">
              当前语音：<span class="voice-name">{{ currentVoiceName }}</span>
            </div>
            <div class="voice-list">
              <div 
                v-for="voice in chineseVoices"
                :key="voice.name"
                class="voice-item"
                :class="{ active: selectedVoiceName === voice.name }"
                @click="selectVoice(voice)"
              >
                {{ voice.name }}
                <van-icon name="success" v-if="selectedVoiceName === voice.name" />
              </div>
            </div>
            <van-button size="small" @click="previewVoice">
              <van-icon name="volume-o" /> 试听
            </van-button>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 结果页面 -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <div class="overlay-page result-page" v-if="phase === 'result'">
      <div class="page-content">
        <div class="result-hero">
          <div class="result-emoji">{{ resultEmoji }}</div>
          <h1>{{ resultTitle }}</h1>
          <p class="result-desc">{{ resultDesc }}</p>
        </div>

        <!-- 分数对比 -->
        <div class="score-comparison">
          <div class="score-bar-wrapper">
            <div 
              class="score-bar-fill player" 
              :style="{ width: playerScorePercent + '%' }"
            ></div>
            <div 
              class="score-bar-fill ai" 
              :style="{ width: aiScorePercent + '%' }"
            ></div>
          </div>
          <div class="score-labels">
            <span class="player-label">你 {{ playerScore }}</span>
            <span class="ai-label">AI {{ aiScore }}</span>
          </div>
        </div>

        <!-- 统计数据 -->
        <div class="stats-grid">
          <div class="stat-card correct">
            <span class="stat-value">{{ correctCount }}</span>
            <span class="stat-label">答对</span>
          </div>
          <div class="stat-card wrong">
            <span class="stat-value">{{ wrongCount }}</span>
            <span class="stat-label">答错</span>
          </div>
          <div class="stat-card streak">
            <span class="stat-value">{{ maxStreak }}</span>
            <span class="stat-label">最高连胜</span>
          </div>
          <div class="stat-card accuracy">
            <span class="stat-value">{{ accuracy }}%</span>
            <span class="stat-label">正确率</span>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="result-actions">
          <van-button type="primary" size="large" block @click="restartBattle">
            再来一局
          </van-button>
          <van-button plain size="large" block @click="$router.back()">
            返回
          </van-button>
        </div>
      </div>
    </div>

    <!-- AI 评论弹窗 -->
    <van-overlay :show="showAiComment" @click="showAiComment = false">
      <div class="ai-comment-popup" @click.stop>
        <div class="comment-avatar">{{ aiCommentEmoji }}</div>
        <div class="comment-content">
          <p>{{ aiCommentText }}</p>
        </div>
        <van-button type="primary" size="small" block @click="closeAiComment">
          继续
        </van-button>
      </div>
    </van-overlay>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { showToast, showSuccessToast, showFailToast } from 'vant'
import { useSpeechRecognition } from '../../composables/useSpeechRecognition'
import { useSpeechSynthesis } from '../../composables/useSpeechSynthesis'
import { api } from '../../api'

// Props
interface Props {
  initialMode?: 'keyword' | 'quote' | 'tail'
}

const props = withDefaults(defineProps<Props>(), {
  initialMode: 'keyword'
})

// 阶段
const phase = ref<'start' | 'playing' | 'result'>('start')

// 模式选择
const modes: { id: 'keyword' | 'quote' | 'tail'; icon: string; name: string; desc: string }[] = [
  { id: 'keyword', icon: '🔥', name: '飞花令', desc: '说出含关键字的诗句' },
  { id: 'quote', icon: '💬', name: '接句', desc: 'AI出上句，你接下句' },
  { id: 'tail', icon: '🔗', name: '接尾', desc: '用指定字开头' }
]
const selectedMode = ref<'keyword' | 'quote' | 'tail'>(props.initialMode)
const selectedKeyword = ref('月')
const difficulty = ref('medium')

// 游戏状态
const playerScore = ref(0)
const aiScore = ref(0)
const currentRound = ref(1)
const totalRounds = ref(10)
const correctCount = ref(0)
const wrongCount = ref(0)
const currentStreak = ref(0)
const maxStreak = ref(0)

// 当前状态
const currentQuestion = ref<any>(null)
const playerAnswer = ref('')
const answerTime = ref('')

// 语音状态
const isRecording = ref(false)
const isListening = ref(false)
const aiSpeaking = ref(false)

// 计时
const timeRemaining = ref(15)
const timerTimeLimit = ref(15)
let timerInterval: number | null = null

// 反馈
const showFeedback = ref(false)
const lastResult = ref<'correct' | 'wrong' | null>(null)
const feedbackText = ref('')

// AI 评论
const showAiComment = ref(false)
const aiCommentText = ref('')
const aiCommentEmoji = ref('')

// TTS 设置
const showVoicePanel = ref(false)
const chineseVoices = ref<SpeechSynthesisVoice[]>([])

// 语音识别
const { transcript, isSupported: asrSupported, start: startASR, stop: stopASR, interimTranscript } = useSpeechRecognition()

// 语音合成
const {
  speak,
  stop: stopSpeak,
  isSpeaking,
  currentVoice,
  getChineseVoices,
  selectVoice: selectTtsVoice
} = useSpeechSynthesis()

// 计算属性
const availableKeywords = ['月', '花', '春', '秋', '风', '雨', '山', '水', '鸟', '夜', '酒', '思']
const canSkip = computed(() => phase.value === 'playing' && currentQuestion.value !== null)
const timerPercent = computed(() => (timeRemaining.value / timerTimeLimit.value) * 100)
const progressPercent = computed(() => (currentRound.value / totalRounds.value) * 100)
const playerScorePercent = computed(() => {
  const total = playerScore.value + aiScore.value
  return total > 0 ? (playerScore.value / total) * 100 : 50
})
const aiScorePercent = computed(() => 100 - playerScorePercent.value)
const accuracy = computed(() => {
  const total = correctCount.value + wrongCount.value
  return total > 0 ? Math.round((correctCount.value / total) * 100) : 0
})
const modeLabel = computed(() => {
  const labels: Record<string, string> = { keyword: '飞花令', quote: '接句', tail: '接尾' }
  return labels[selectedMode.value]
})
const micLabel = computed(() => {
  if (isRecording.value || isListening.value) return '聆听中...'
  if (phase.value === 'start') return '准备开始'
  return '按住说话'
})
const currentVoiceName = computed(() => currentVoice.value?.name || '未选择')
const selectedVoiceName = computed(() => currentVoice.value?.name)

// 结果
const resultEmoji = computed(() => {
  if (playerScore.value > aiScore.value) return '🏆'
  if (playerScore.value < aiScore.value) return '😅'
  return '🤝'
})
const resultTitle = computed(() => {
  if (playerScore.value > aiScore.value) return '你赢了！'
  if (playerScore.value < aiScore.value) return 'AI 获胜'
  return '平局'
})
const resultDesc = computed(() => {
  if (playerScore.value > aiScore.value) return '太厉害了！诗词功底深厚！'
  if (playerScore.value < aiScore.value) return '别灰心，多练习一定能进步！'
  return '势均力敌！再来一局？'
})

// AI 评论语录
const aiEncouragements = ['不错不错，继续加油！🤖', '好的，下一题！', '这题有点意思~']
const aiTaunts = ['哈哈，这道题你答错啦~', '看来这题有点难哦！', 'AI 再得一分！']
const aiPraises = ['太棒了！答对了！👏', '厉害！继续保持！', '哇，这道都能答出来！']

// 开始对战
async function startBattle() {
  phase.value = 'playing'
  playerScore.value = 0
  aiScore.value = 0
  currentRound.value = 1
  currentStreak.value = 0
  maxStreak.value = 0
  correctCount.value = 0
  wrongCount.value = 0
  
  await nextTick()
  await loadQuestion()
}

// 加载题目
async function loadQuestion() {
  // 重置状态
  currentQuestion.value = null
  playerAnswer.value = ''
  showFeedback.value = false
  lastResult.value = null
  
  // 获取题目（优先后端 API）
  try {
    const res = await api.poetryGenerate({
      mode: selectedMode.value,
      keyword: selectedMode.value === 'keyword' ? selectedKeyword.value : '',
      difficulty: difficulty.value
    })
    
    if (res.success) {
      currentQuestion.value = res
    }
  } catch (err) {
    // 后端不可用时使用前端题库
    currentQuestion.value = generateLocalQuestion()
  }
  
  // 设置计时
  timerTimeLimit.value = difficulty.value === 'easy' ? 20 : difficulty.value === 'hard' ? 10 : 15
  timeRemaining.value = timerTimeLimit.value
  startTimer()
  
  // AI 朗读题目
  await nextTick()
  await aiSpeakQuestion()
}

// 本地题目生成
function generateLocalQuestion() {
  const q = {
    type: 'keyword' as 'keyword' | 'quote' | 'tail',
    keyword: selectedKeyword.value,
    prompt: `请说出包含「${selectedKeyword.value}」字的诗句`,
    quote: '',
    answer: ''
  }
  
  if (selectedMode.value === 'quote') {
    const pairs: [string, string][] = [
      ['床前明月光', '疑是地上霜'],
      ['春眠不觉晓', '处处闻啼鸟'],
      ['白日依山尽', '黄河入海流'],
    ]
    const [quote, answer] = pairs[Math.floor(Math.random() * pairs.length)]
    q.type = 'quote'
    q.quote = quote
    q.answer = answer
  }
  
  return q
}

// AI 朗读题目
async function aiSpeakQuestion() {
  aiSpeaking.value = true
  
  let text = ''
  if (selectedMode.value === 'quote') {
    text = `请接下句：${currentQuestion.value.quote}`
  } else if (selectedMode.value === 'tail') {
    const char = currentQuestion.value.start_char || currentQuestion.value.keyword
    text = `请用${char}字开头的诗句回答！准备，开始！`
  } else {
    const kw = currentQuestion.value.keyword
    text = `请说出包含${kw}字的诗句。准备，开始！`
  }
  
  await speak(text)
  aiSpeaking.value = false
}

// 麦克风按下
function handleMicDown() {
  if (phase.value !== 'playing' || isListening.value) return
  isRecording.value = true
  isListening.value = true
  startASR()
}

// 麦克风释放
function handleMicUp() {
  if (!isRecording.value) return
  isRecording.value = false
  isListening.value = false
  stopASR()
}

// 监听识别结果
watch(transcript, (text) => {
  if (text && phase.value === 'playing') {
    playerAnswer.value = text
    answerTime.value = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    checkAnswer(text)
  }
}, { immediate: true })

// 检查答案
async function checkAnswer(answer: string) {
  stopTimer()
  
  // 验证答案
  let isCorrect = false
  const q = currentQuestion.value
  
  if (selectedMode.value === 'keyword') {
    const clean = answer.replace(/[，。！？；：""''【】（）、…—]/g, '')
    isCorrect = clean.includes(q.keyword) && clean.length >= 4
  } else if (selectedMode.value === 'quote') {
    const clean = answer.replace(/[，。！？；：""''【】（）、…—]/g, '')
    const expected = q.answer.replace(/[，。！？；：""''【】（）、…—]/g, '')
    isCorrect = clean.includes(expected) || clean === expected
  } else if (selectedMode.value === 'tail') {
    const startChar = q.start_char || q.keyword
    const clean = answer.replace(/[，。！？；：""''【】（）、…—]/g, '')
    isCorrect = clean.startsWith(startChar) && clean.length >= 4
  }
  
  // 显示结果
  if (isCorrect) {
    correctCount.value++
    currentStreak.value++
    maxStreak.value = Math.max(maxStreak.value, currentStreak.value)
    const baseScore = 10 + currentStreak.value * 2
    playerScore.value += baseScore
    feedbackText.value = `✓ 正确！+${baseScore}分`
    lastResult.value = 'correct'
    showSuccessToast(feedbackText.value)
  } else {
    wrongCount.value++
    currentStreak.value = 0
    aiScore.value += 5
    feedbackText.value = `✗ 错误`
    lastResult.value = 'wrong'
    showFailToast(feedbackText.value)
  }
  
  showFeedback.value = true
  setTimeout(() => { showFeedback.value = false }, 2000)
  
  // AI 评论
  await delay(800)
  showAiComment.value = true
  
  if (isCorrect) {
    aiCommentText.value = aiPraises[Math.floor(Math.random() * aiPraises.length)]
    aiCommentEmoji.value = '🤖'
  } else {
    aiCommentText.value = aiTaunts[Math.floor(Math.random() * aiTaunts.length)]
    if (selectedMode.value === 'quote' && currentQuestion.value.answer) {
      aiCommentText.value += `\n\n正确答案：「${currentQuestion.value.answer}」`
    }
    aiCommentEmoji.value = '😏'
  }
  
  await delay(2000)
  closeAiComment()
}

// 关闭 AI 评论
function closeAiComment() {
  showAiComment.value = false
  
  if (currentRound.value >= totalRounds.value) {
    endBattle()
  } else {
    currentRound.value++
    loadQuestion()
  }
}

// 跳过
async function skipQuestion() {
  wrongCount.value++
  currentStreak.value = 0
  aiScore.value += 5
  
  showFailToast('跳过 -5分')
  lastResult.value = 'wrong'
  feedbackText.value = '跳过'
  showFeedback.value = true
  setTimeout(() => { showFeedback.value = false }, 1500)
  
  aiCommentText.value = aiEncouragements[Math.floor(Math.random() * aiEncouragements.length)]
  aiCommentEmoji.value = '🤖'
  showAiComment.value = true
  
  await delay(2000)
  closeAiComment()
}

// 计时
function startTimer() {
  timeRemaining.value = timerTimeLimit.value
  if (timerInterval) clearInterval(timerInterval)
  
  timerInterval = window.setInterval(() => {
    timeRemaining.value--
    if (timeRemaining.value <= 0) {
      handleTimeout()
    }
  }, 1000)
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

// 超时
async function handleTimeout() {
  stopTimer()
  
  wrongCount.value++
  currentStreak.value = 0
  aiScore.value += 5
  
  lastResult.value = 'wrong'
  feedbackText.value = '⏰ 超时'
  showFeedback.value = true
  
  aiCommentText.value = '时间到！看来这道有点难哦~'
  if (selectedMode.value === 'quote' && currentQuestion.value.answer) {
    aiCommentText.value += `\n\n正确答案：「${currentQuestion.value.answer}」`
  }
  aiCommentEmoji.value = '⏰'
  showAiComment.value = true
  
  await delay(2000)
  closeAiComment()
}

// 结束
function endBattle() {
  stopTimer()
  stopSpeak()
  phase.value = 'result'
}

// 重新开始
function restartBattle() {
  phase.value = 'start'
}

// 语音设置
function selectVoice(voice: SpeechSynthesisVoice) {
  selectTtsVoice(voice)
}

function previewVoice() {
  const text = '床前明月光，疑是地上霜。举头望明月，低头思故乡。'
  speak(text, { rate: 0.85 })
}

// 延迟
function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// 监听语音状态
watch(isSpeaking, (speaking) => {
  aiSpeaking.value = speaking
})

onMounted(() => {
  // 加载中文语音
  setTimeout(() => {
    chineseVoices.value = getChineseVoices()
  }, 500)
  
  if (!asrSupported.value) {
    showToast('您的浏览器不支持语音识别，将使用手动输入模式')
  }
})

onUnmounted(() => {
  stopTimer()
  stopSpeak()
})
</script>

<style scoped>
.voice-battle-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 50%, #2d1b4e 100%);
  color: white;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* 顶部状态 */
.battle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(0,0,0,0.2);
  backdrop-filter: blur(10px);
}

.score-board {
  display: flex;
  align-items: center;
  gap: 20px;
}

.score-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-label {
  font-size: 12px;
  opacity: 0.7;
}

.score-value {
  font-size: 28px;
  font-weight: 700;
}

.player .score-value { color: #f472b6; }
.ai .score-value { color: #60a5fa; }

.vs-divider {
  font-size: 18px;
  opacity: 0.5;
}

.round-info {
  font-size: 14px;
  opacity: 0.7;
  background: rgba(255,255,255,0.1);
  padding: 6px 12px;
  border-radius: 20px;
}

/* 对战区域 */
.battle-arena {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 20px;
  min-height: 280px;
}

/* 头像 */
.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-avatar {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
}

.player-avatar {
  background: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%);
}

.avatar-ring {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.2);
  animation: pulse-ring 2s ease-in-out infinite;
}

.ai-avatar.speaking .avatar-ring,
.player-avatar.listening .avatar-ring {
  border-color: rgba(255,255,255,0.6);
  animation: pulse-ring-fast 0.8s ease-in-out infinite;
}

@keyframes pulse-ring {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.05); opacity: 0.7; }
}

@keyframes pulse-ring-fast {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

.avatar-face {
  font-size: 36px;
  z-index: 1;
}

/* 语音波形 */
.speaking-waves {
  position: absolute;
  bottom: -15px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 3px;
  align-items: flex-end;
  height: 15px;
}

.wave-line {
  width: 3px;
  background: linear-gradient(to top, #4ade80, #22c55e);
  border-radius: 2px;
  animation: wave-anim 0.6s ease-in-out infinite;
}

.wave-line:nth-child(1) { animation-delay: 0s; height: 6px; }
.wave-line:nth-child(2) { animation-delay: 0.1s; height: 12px; }
.wave-line:nth-child(3) { animation-delay: 0.2s; height: 8px; }

@keyframes wave-anim {
  0%, 100% { transform: scaleY(0.5); }
  50% { transform: scaleY(1.5); }
}

/* 对话区域 */
.dialogue-area {
  flex: 1;
  max-width: 55%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 0 16px;
}

.bubble {
  padding: 16px;
  border-radius: 20px;
  max-width: 100%;
}

.ai-bubble {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-bottom-left-radius: 4px;
}

.bubble-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.bubble-avatar {
  font-size: 20px;
}

.bubble-name {
  font-size: 12px;
  opacity: 0.7;
}

.bubble-body {
  line-height: 1.6;
}

.question-type-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  margin-bottom: 8px;
}

.question-type-badge.keyword {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
}

.question-type-badge.quote {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.question-type-badge.tail {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
}

.question-text {
  margin: 0;
  font-size: 16px;
}

.quote-line {
  font-style: italic;
  font-size: 18px;
}

.keyword {
  color: #fbbf24;
  font-weight: 700;
}

.ai-note {
  margin: 8px 0 0;
  font-size: 11px;
  opacity: 0.5;
  display: flex;
  align-items: center;
  gap: 4px;
}

.player-bubble {
  background: linear-gradient(135deg, rgba(236, 72, 153, 0.3) 0%, rgba(244, 63, 94, 0.3) 100%);
  border: 1px solid rgba(244, 63, 94, 0.3);
  border-bottom-right-radius: 4px;
  align-self: flex-end;
}

.answer-text {
  margin: 0;
  font-size: 16px;
}

.bubble-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 6px;
}

.answer-time {
  font-size: 11px;
  opacity: 0.5;
}

/* 计时区域 */
.timer-section {
  padding: 0 20px;
  margin-bottom: 10px;
}

.timer-track {
  height: 6px;
  background: rgba(255,255,255,0.1);
  border-radius: 3px;
  overflow: hidden;
}

.timer-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #4ade80);
  border-radius: 3px;
  transition: width 1s linear;
}

.timer-fill.warning {
  background: linear-gradient(90deg, #f97316, #fb923c);
}

.timer-fill.danger {
  background: linear-gradient(90deg, #ef4444, #f87171);
  animation: pulse-danger 0.5s infinite;
}

@keyframes pulse-danger {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.timer-label {
  text-align: center;
  margin-top: 6px;
  font-size: 14px;
  opacity: 0.7;
}

.timeout-text {
  color: #ef4444;
  font-weight: 600;
}

/* 操作区域 */
.action-section {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.mic-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.mic-btn {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  color: white;
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.2s ease;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
}

.mic-btn:active {
  transform: scale(0.95);
}

.mic-btn.recording {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);
}

.mic-btn.success {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  box-shadow: 0 4px 20px rgba(34, 197, 94, 0.4);
}

.mic-btn.error {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.mic-ripple {
  position: absolute;
  inset: -10px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.3);
  animation: ripple 1.5s ease-out infinite;
}

@keyframes ripple {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

.mic-label {
  font-size: 13px;
  opacity: 0.7;
}

/* 反馈卡片 */
.feedback-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 24px;
  font-size: 15px;
  font-weight: 600;
}

.feedback-card.correct {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
}

.feedback-card.wrong {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
}

.skip-btn {
  opacity: 0.7;
}

/* 进度条 */
.progress-section {
  padding: 0 20px 20px;
}

.progress-track {
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
  transition: width 0.3s ease;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  opacity: 0.6;
}

/* 覆盖页面 */
.overlay-page {
  position: fixed;
  inset: 0;
  background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 50%, #2d1b4e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}

.page-content {
  width: 100%;
  max-width: 420px;
  max-height: 100vh;
  overflow-y: auto;
}

/* 开始页面 */
.hero-section {
  text-align: center;
  margin-bottom: 32px;
}

.hero-emoji {
  font-size: 64px;
  margin-bottom: 16px;
}

.hero-section h1 {
  font-size: 32px;
  margin: 0 0 8px;
  background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-desc {
  color: rgba(255,255,255,0.7);
  margin: 0;
}

/* 模式选择 */
.mode-selector {
  margin-bottom: 24px;
}

.selector-title {
  font-size: 14px;
  opacity: 0.7;
  margin-bottom: 12px;
}

.mode-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mode-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(255,255,255,0.05);
  border: 2px solid transparent;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-option.active {
  background: rgba(99, 102, 241, 0.15);
  border-color: #6366f1;
}

.mode-icon {
  font-size: 24px;
}

.mode-name {
  flex: 1;
  font-weight: 600;
}

.mode-desc {
  font-size: 12px;
  opacity: 0.6;
}

/* 关键字选择 */
.keyword-selector {
  margin-bottom: 24px;
}

.keyword-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-chip {
  padding: 8px 16px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.keyword-chip.active {
  background: rgba(251, 191, 36, 0.2);
  border-color: #fbbf24;
  color: #fbbf24;
}

/* 难度选择 */
.difficulty-selector {
  margin-bottom: 24px;
}

/* 开始按钮 */
.start-btn {
  margin-bottom: 20px;
  height: 50px;
  font-size: 16px;
}

/* TTS 设置 */
.tts-settings {
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  overflow: hidden;
}

.tts-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px;
  cursor: pointer;
  font-size: 14px;
}

.tts-header span {
  flex: 1;
}

.tts-panel {
  padding: 0 16px 16px;
}

.voice-info {
  font-size: 13px;
  margin-bottom: 12px;
  opacity: 0.8;
}

.voice-name {
  color: #a78bfa;
}

.voice-list {
  max-height: 120px;
  overflow-y: auto;
  margin-bottom: 12px;
}

.voice-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255,255,255,0.05);
  border-radius: 8px;
  margin-bottom: 6px;
  font-size: 12px;
  cursor: pointer;
}

.voice-item.active {
  background: rgba(99, 102, 241, 0.2);
}

/* 结果页面 */
.result-hero {
  text-align: center;
  margin-bottom: 32px;
}

.result-emoji {
  font-size: 72px;
  margin-bottom: 16px;
}

.result-hero h1 {
  font-size: 32px;
  margin: 0 0 8px;
}

.result-desc {
  color: rgba(255,255,255,0.7);
  margin: 0;
}

/* 分数对比 */
.score-comparison {
  margin-bottom: 24px;
}

.score-bar-wrapper {
  height: 12px;
  background: rgba(59, 130, 246, 0.3);
  border-radius: 6px;
  overflow: hidden;
  position: relative;
}

.score-bar-fill {
  position: absolute;
  top: 0;
  height: 100%;
  transition: width 1s ease;
}

.score-bar-fill.player {
  left: 0;
  background: linear-gradient(90deg, #ec4899 0%, #f43f5e 100%);
  border-radius: 6px 0 0 6px;
}

.score-bar-fill.ai {
  right: 0;
  background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
  border-radius: 0 6px 6px 0;
}

.score-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 13px;
}

.player-label { color: #f472b6; }
.ai-label { color: #60a5fa; }

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 32px;
}

.stat-card {
  text-align: center;
  padding: 16px 8px;
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  display: block;
}

.stat-label {
  font-size: 11px;
  opacity: 0.6;
  margin-top: 4px;
}

.stat-card.correct .stat-value { color: #4ade80; }
.stat-card.wrong .stat-value { color: #f87171; }
.stat-card.streak .stat-value { color: #fbbf24; }
.stat-card.accuracy .stat-value { color: #60a5fa; }

/* 结果操作 */
.result-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* AI 评论弹窗 */
.ai-comment-popup {
  position: absolute;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(20, 20, 40, 0.95);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 20px;
  padding: 24px;
  width: 300px;
  text-align: center;
  backdrop-filter: blur(20px);
}

.comment-avatar {
  font-size: 48px;
  margin-bottom: 12px;
}

.comment-content p {
  margin: 0 0 20px;
  font-size: 15px;
  line-height: 1.6;
  white-space: pre-line;
}

/* 过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active {
  transition: all 0.3s ease;
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

/* 响应式 */
@media (max-width: 380px) {
  .avatar {
    width: 60px;
    height: 60px;
  }
  
  .avatar-face {
    font-size: 28px;
  }
  
  .dialogue-area {
    max-width: 50%;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

</style>
