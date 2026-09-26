<template>
  <div class="solo-feihua-page">
    <!-- 顶部导航 -->
    <header class="page-header">
      <van-icon name="arrow-left" @click="$router.back()" />
      <span class="header-title">飞花令练习</span>
      <van-icon name="setting-o" @click="showSettings = true" />
    </header>

    <!-- 模式选择 -->
    <section class="mode-section" v-if="phase === 'select'">
      <h2 class="section-title">选择练习模式</h2>
      
      <div class="mode-grid">
        <!-- 自由练习 -->
        <div class="mode-card" @click="startPractice('free')">
          <div class="mode-icon">🎯</div>
          <div class="mode-name">自由练习</div>
          <div class="mode-desc">随意说出含关键字的诗句</div>
          <div class="mode-tag tag-easy">不计时</div>
        </div>

        <!-- 限时挑战 -->
        <div class="mode-card" @click="startPractice('timed')">
          <div class="mode-icon">⏱️</div>
          <div class="mode-name">限时挑战</div>
          <div class="mode-desc">计时答题，考验反应</div>
          <div class="mode-tag tag-medium">10-20秒</div>
        </div>

        <!-- 接尾练习 -->
        <div class="mode-card" @click="startPractice('tail')">
          <div class="mode-icon">🔗</div>
          <div class="mode-name">接尾练习</div>
          <div class="mode-desc">用上一句尾字接新诗句</div>
          <div class="mode-tag tag-hard">8秒</div>
        </div>

        <!-- 闯关模式 -->
        <div class="mode-card" @click="startPractice('challenge')">
          <div class="mode-icon">🏆</div>
          <div class="mode-name">闯关模式</div>
          <div class="mode-desc">逐步提升难度等级</div>
          <div class="mode-tag tag-vip">VIP</div>
        </div>
      </div>

      <!-- 关键词选择 -->
      <div class="keyword-section">
        <h3>选择关键字</h3>
        <div class="keyword-grid">
          <div 
            v-for="kw in commonKeywords" 
            :key="kw"
            class="keyword-chip"
            :class="{ active: selectedKeyword === kw }"
            @click="selectedKeyword = kw"
          >
            {{ kw }}
          </div>
        </div>
      </div>
    </section>

    <!-- 练习中 -->
    <section class="practice-section" v-else-if="phase === 'practice'">
      <!-- 顶部状态 -->
      <div class="practice-header">
        <div class="mode-badge">{{ modeName }}</div>
        <div class="stats-row">
          <span class="stat-item">
            <van-icon name="passed" />
            {{ correctCount }} / {{ totalCount }}
          </span>
          <span class="stat-item" v-if="practiceMode !== 'free'">
            <van-icon name="clock-o" />
            {{ timeRemaining }}s
          </span>
        </div>
      </div>

      <!-- 当前关键字 -->
      <div class="keyword-display">
        <span class="keyword-label">关键字</span>
        <span class="keyword-char">{{ currentKeyword }}</span>
      </div>

      <!-- 接尾模式显示 -->
      <div class="tail-hint" v-if="practiceMode === 'tail' && lastLine">
        <p>上一句：{{ lastLine }}</p>
        <p class="tail-char">尾字：<span>{{ lastTailChar }}</span></p>
      </div>

      <!-- 计时环 -->
      <div class="timer-ring" v-if="practiceMode !== 'free'" :class="{ warning: timeRemaining <= 3 }">
        <div class="timer-inner">
          <span class="timer-number">{{ timeRemaining }}</span>
        </div>
      </div>

      <!-- 提示区域 -->
      <div class="hint-area">
        <van-icon name="bulb-o" />
        <span>说出包含「{{ practiceMode === 'tail' ? lastTailChar : currentKeyword }}」字的诗句</span>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <van-field
          v-model="answerText"
          :placeholder="inputPlaceholder"
          :disabled="isProcessing"
          @keyup.enter="submitAnswer"
        />
        
        <!-- 快捷短语 -->
        <div class="quick-phrases">
          <van-tag 
            v-for="phrase in quickPhrases" 
            :key="phrase"
            plain 
            size="large"
            @click="answerText = phrase"
          >
            {{ phrase }}
          </van-tag>
        </div>

        <!-- 按钮 -->
        <div class="action-buttons">
          <van-button 
            v-if="practiceMode !== 'free'"
            type="default"
            plain
            @click="skipQuestion"
          >
            跳过
          </van-button>
          
          <van-button 
            type="primary"
            :loading="isProcessing"
            :disabled="!answerText.trim()"
            @click="submitAnswer"
          >
            提交
          </van-button>
        </div>
      </div>

      <!-- 历史记录 -->
      <div class="history-section" v-if="history.length > 0">
        <div class="history-header">
          <span>答题记录</span>
          <van-button size="small" @click="historyVisible = !historyVisible">
            {{ historyVisible ? '收起' : '展开' }}
          </van-button>
        </div>
        
        <div class="history-list" v-show="historyVisible">
          <div 
            v-for="(item, index) in history" 
            :key="index"
            class="history-item"
            :class="{ correct: item.isCorrect, wrong: !item.isCorrect }"
          >
            <van-icon :name="item.isCorrect ? 'passed' : 'cross'" />
            <span class="history-text">{{ item.answer }}</span>
            <span class="history-keyword">{{ item.keyword }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 结果页面 -->
    <section class="result-section" v-else-if="phase === 'result'">
      <div class="result-card">
        <!-- 成绩 -->
        <div class="score-display">
          <div class="score-circle">
            <span class="score-number">{{ correctCount }}</span>
            <span class="score-label">正确</span>
          </div>
          <div class="score-divider">/</div>
          <div class="total-number">{{ totalCount }}</div>
        </div>

        <!-- 正确率 -->
        <div class="accuracy-display">
          <van-circle 
            v-model="accuracyValue"
            :rate="accuracyRate"
            :speed="100"
            :stroke-width="60"
            color="#07c160"
          />
          <span class="accuracy-text">{{ accuracyRate }}%</span>
        </div>

        <!-- 评价 -->
        <div class="result-comment">
          <p class="comment-title">{{ resultComment.title }}</p>
          <p class="comment-text">{{ resultComment.text }}</p>
        </div>

        <!-- 详细统计 -->
        <div class="detail-stats">
          <div class="stat-card">
            <span class="stat-value correct">{{ correctCount }}</span>
            <span class="stat-label">答对</span>
          </div>
          <div class="stat-card">
            <span class="stat-value wrong">{{ totalCount - correctCount }}</span>
            <span class="stat-label">答错</span>
          </div>
          <div class="stat-card">
            <span class="stat-value time">{{ avgTime }}s</span>
            <span class="stat-label">平均用时</span>
          </div>
        </div>

        <!-- 错题回顾 -->
        <div class="wrong-review" v-if="wrongQuestions.length > 0">
          <h3>错题回顾</h3>
          <div 
            v-for="(item, index) in wrongQuestions" 
            :key="index"
            class="wrong-item"
          >
            <p class="wrong-question">关键字：{{ item.keyword }}</p>
            <p class="wrong-answer">你的答案：{{ item.answer }}</p>
            <p class="correct-answer">正确答案示例：{{ item.suggestion }}</p>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="result-actions">
          <van-button type="primary" block @click="restartPractice">
            再练一次
          </van-button>
          <van-button plain block @click="changeKeyword">
            换个关键字
          </van-button>
          <van-button plain block @click="$router.back()">
            返回首页
          </van-button>
        </div>
      </div>
    </section>

    <!-- 设置弹窗 -->
    <van-popup v-model:show="showSettings" position="bottom" round>
      <div class="settings-popup">
        <h3>练习设置</h3>
        
        <van-field label="关键字" :model-value="selectedKeyword" readonly />
        
        <van-field label="时间限制" label-width="80">
          <template #input>
            <van-radio-group v-model="timeLimit" direction="horizontal">
              <van-radio name="10">10秒</van-radio>
              <van-radio name="15">15秒</van-radio>
              <van-radio name="20">20秒</van-radio>
            </van-radio-group>
          </template>
        </van-field>

        <van-field label="题目数量" label-width="80">
          <template #input>
            <van-stepper v-model="questionCount" min="5" max="50" step="5" />
          </template>
        </van-field>

        <van-field label="语音输入" label-width="80">
          <template #input>
            <van-switch v-model="enableVoice" />
          </template>
        </van-field>

        <div class="popup-actions">
          <van-button @click="showSettings = false">取消</van-button>
          <van-button type="primary" @click="showSettings = false">确定</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 语音输入按钮 -->
    <div class="voice-fab" v-if="enableVoice && phase === 'practice'" @click="toggleVoice">
      <van-icon :name="isListening ? 'stop-circle' : 'volume'" />
    </div>

    <!-- 语音状态提示 -->
    <van-overlay :show="isListening" @click="stopVoice">
      <div class="voice-overlay">
        <div class="voice-animation">
          <div class="voice-wave"></div>
          <div class="voice-wave"></div>
          <div class="voice-wave"></div>
        </div>
        <p>正在聆听...</p>
        <p class="voice-hint">说出包含「{{ practiceMode === 'tail' ? lastTailChar : currentKeyword }}」字的诗句</p>
        <van-button type="primary" @click="stopVoice">停止</van-button>
      </div>
    </van-overlay>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showFailToast, showSuccessToast } from 'vant'
import { useSpeechRecognition } from '../composables/useSpeechRecognition'

const router = useRouter()

// 阶段
const phase = ref<'select' | 'practice' | 'result'>('select')
const practiceMode = ref<'free' | 'timed' | 'tail' | 'challenge'>('free')

// 状态
const selectedKeyword = ref('月')
const currentKeyword = ref('月')
const answerText = ref('')
const isProcessing = ref(false)
const historyVisible = ref(false)

// 练习统计
const correctCount = ref(0)
const totalCount = ref(0)
const timeRemaining = ref(15)
const history = ref<Array<{
  answer: string
  keyword: string
  isCorrect: boolean
  time: number
}>>([])

// 接尾模式
const lastLine = ref('')
const lastTailChar = ref('')

// 设置
const showSettings = ref(false)
const timeLimit = ref('15')
const questionCount = ref(10)
const enableVoice = ref(false)

// 语音识别
const {
  isListening,
  transcript,
  start: startVoice,
  stop: stopVoice
} = useSpeechRecognition()

// 常用关键字
const commonKeywords = [
  '月', '花', '春', '秋', '风', '雨', '雪', '云', '山', '水',
  '江', '河', '日', '夜', '星', '梦', '心', '情', '思', '酒',
  '人', '家', '乡', '柳', '梅', '鸟', '马', '帆', '灯', '烟'
]

// 快捷短语
const quickPhrases = [
  '海上生明月',
  '床前明月光',
  '举头望明月',
  '春江花月夜'
]

// 模式名称
const modeName = computed(() => {
  const names = {
    free: '自由练习',
    timed: '限时挑战',
    tail: '接尾练习',
    challenge: '闯关模式'
  }
  return names[practiceMode.value]
})

// 输入提示
const inputPlaceholder = computed(() => {
  const kw = practiceMode.value === 'tail' ? lastTailChar.value : currentKeyword.value
  return `输入包含「${kw}」字的诗句`
})

// 正确率
const accuracyRate = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((correctCount.value / totalCount.value) * 100)
})

// 正确率数值（用于 van-circle）
const accuracyValue = ref(0)

// 平均用时
const avgTime = computed(() => {
  if (history.value.length === 0) return 0
  const total = history.value.reduce((sum, h) => sum + h.time, 0)
  return (total / history.value.length).toFixed(1)
})

// 错题列表
const wrongQuestions = computed(() => {
  return history.value
    .filter(h => !h.isCorrect)
    .map(h => ({
      keyword: h.keyword,
      answer: h.answer,
      suggestion: getSuggestion(h.keyword)
    }))
})

// 结果评价
const resultComment = computed(() => {
  const rate = accuracyRate.value
  if (rate >= 90) return { title: '🌟 太厉害了！', text: '诗词储备惊人，继续保持！' }
  if (rate >= 70) return { title: '👍 很不错！', text: '继续练习，下一个诗人就是你！' }
  if (rate >= 50) return { title: '💪 还需努力', text: '多背诵古诗词，熟能生巧！' }
  return { title: '📚 加油！', text: '不要气馁，继续练习！' }
})

// 计时器
let timerInterval: number | null = null

function startTimer() {
  if (practiceMode.value === 'free') return
  
  timeRemaining.value = parseInt(timeLimit.value)
  
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

// 开始练习
function startPractice(mode: 'free' | 'timed' | 'tail' | 'challenge') {
  practiceMode.value = mode
  phase.value = 'practice'
  correctCount.value = 0
  totalCount.value = 0
  history.value = []
  currentKeyword.value = selectedKeyword.value
  lastLine.value = ''
  lastTailChar.value = ''
  answerText.value = ''
  
  startTimer()
}

// 提交答案
function submitAnswer() {
  if (!answerText.value.trim()) {
    showToast('请输入答案')
    return
  }
  
  isProcessing.value = true
  const startTime = Date.now()
  
  setTimeout(() => {
    const answer = answerText.value.trim()
    const requiredChar = practiceMode.value === 'tail' ? lastTailChar.value : currentKeyword.value
    
    // 验证答案
    const isCorrect = validateAnswer(answer, requiredChar)
    const timeSpent = (Date.now() - startTime) / 1000
    
    // 记录历史
    history.value.push({
      answer,
      keyword: requiredChar,
      isCorrect,
      time: timeSpent
    })
    
    if (isCorrect) {
      correctCount.value++
      showSuccessToast('✓ 正确')
    } else {
      showFailToast('✗ 错误')
    }
    
    // 接尾模式处理
    if (practiceMode.value === 'tail' && isCorrect) {
      lastLine.value = answer
      lastTailChar.value = getTailChar(answer)
    }
    
    totalCount.value++
    answerText.value = ''
    
    // 检查是否完成
    if (totalCount.value >= questionCount.value) {
      finishPractice()
    } else {
      startTimer()
    }
    
    isProcessing.value = false
  }, 300)
}

// 跳过
function skipQuestion() {
  history.value.push({
    answer: '（跳过）',
    keyword: practiceMode.value === 'tail' ? lastTailChar.value : currentKeyword.value,
    isCorrect: false,
    time: parseInt(timeLimit.value)
  })
  
  totalCount.value++
  answerText.value = ''
  
  if (practiceMode.value === 'tail') {
    // 跳过接尾，显示提示
    const suggestion = getSuggestion(lastTailChar.value || currentKeyword.value)
    showToast(`提示：${suggestion}`)
    lastTailChar.value = getTailChar(suggestion)
  }
  
  if (totalCount.value >= questionCount.value) {
    finishPractice()
  } else {
    startTimer()
  }
}

// 超时处理
function handleTimeout() {
  stopTimer()
  
  history.value.push({
    answer: '（超时）',
    keyword: practiceMode.value === 'tail' ? lastTailChar.value : currentKeyword.value,
    isCorrect: false,
    time: parseInt(timeLimit.value)
  })
  
  totalCount.value++
  
  if (practiceMode.value === 'tail') {
    const suggestion = getSuggestion(lastTailChar.value || currentKeyword.value)
    showToast(`超时！提示：${suggestion}`)
    lastTailChar.value = getTailChar(suggestion)
  }
  
  if (totalCount.value >= questionCount.value) {
    finishPractice()
  } else {
    startTimer()
  }
}

// 验证答案
function validateAnswer(answer: string, keyword: string): boolean {
  const clean = answer.replace(/[，。！？；：""''【】（）、…—]/g, '')
  
  // 必须包含关键字
  if (!clean.includes(keyword)) return false
  
  // 长度检查
  if (clean.length < 5) return false
  
  // 检查是否全为汉字
  if (!/[\u4e00-\u9fff]/.test(clean)) return false
  
  return true
}

// 获取尾字
function getTailChar(line: string): string {
  const clean = line.replace(/[，。！？；：""''【】（）、…—]/g, '')
  
  for (let i = clean.length - 1; i >= 0; i--) {
    const char = clean[i]
    if (/\u4e00-\u9fff/.test(char)) {
      return char
    }
  }
  
  return ''
}

// 获取建议答案
function getSuggestion(keyword: string): string {
  const suggestions: Record<string, string[]> = {
    '月': ['海上生明月', '床前明月光', '举头望明月', '春江花月夜'],
    '花': ['春眠不觉晓', '花开时节动京城', '感时花溅泪'],
    '春': ['春风又绿江南岸', '春城无处不飞花', '春眠不觉晓'],
    '秋': ['秋风吹不尽', '秋水共长天一色', '秋风吹落叶'],
    '风': ['风吹草低见牛羊', '春风不度玉门关', '风起云涌'],
    '雨': ['夜来风雨声', '清明时节雨纷纷', '斜风细雨'],
    '山': ['山色空蒙雨亦奇', '山重水复疑无路', '青山横北郭'],
    '水': ['水光潋滟晴方好', '桃花潭水深千尺', '一江春水'],
    '日': ['日出江花红胜火', '明日复明日', '红日初升'],
    '夜': ['夜来风雨声', '夜半钟声到客船', '夜泊牛渚'],
    '思': ['举头望明月', '低头思故乡', '思君如满月'],
    '酒': ['劝君更尽一杯酒', '酒逢知己千杯少', '酒入愁肠'],
    '乡': ['低头思故乡', '乡音无改鬓毛衰', '日暮乡关'],
  }
  
  const list = suggestions[keyword] || ['请说出包含此字的诗句']
  return list[Math.floor(Math.random() * list.length)]
}

// 完成练习
function finishPractice() {
  stopTimer()
  phase.value = 'result'
  
  // 动画效果
  setTimeout(() => {
    accuracyValue.value = accuracyRate.value
  }, 100)
}

// 重新开始
function restartPractice() {
  startPractice(practiceMode.value)
}

// 换个关键字
function changeKeyword() {
  phase.value = 'select'
}

// 语音控制
function toggleVoice() {
  if (isListening.value) {
    stopVoice()
  } else {
    startVoice()
  }
}

// 监听语音输入
watch(transcript, (val) => {
  if (val) {
    answerText.value = val
    submitAnswer()
  }
})

onMounted(() => {
  // 默认选中关键字
  selectedKeyword.value = '月'
})

onUnmounted(() => {
  stopTimer()
  stopVoice()
})
</script>

<style scoped>
.solo-feihua-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8f4e8 0%, #f0ebe0 100%);
  padding-bottom: 80px;
}

.page-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.header-title {
  font-size: 16px;
  font-weight: 600;
}

/* 模式选择 */
.mode-section {
  padding: 20px 16px;
}

.section-title {
  font-size: 20px;
  color: #333;
  margin: 0 0 16px;
}

.mode-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.mode-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.mode-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.mode-card:active {
  transform: translateY(0);
}

.mode-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.mode-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.mode-desc {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.mode-tag {
  display: inline-block;
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 10px;
}

.tag-easy { background: #e8f5e9; color: #4caf50; }
.tag-medium { background: var(--card)3e0; color: #ff9800; }
.tag-hard { background: #ffebee; color: #f44336; }
.tag-vip { background: linear-gradient(135deg, #ffd700, #ffb300); color: #fff; }

/* 关键字选择 */
.keyword-section {
  background: white;
  border-radius: 12px;
  padding: 16px;
}

.keyword-section h3 {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px;
}

.keyword-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-chip {
  padding: 6px 14px;
  background: #f5f5f5;
  border-radius: 18px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.keyword-chip:hover {
  background: #e8e4dc;
}

.keyword-chip.active {
  background: var(--card)3e0;
  color: #ff9800;
  border-color: #ff9800;
}

/* 练习中 */
.practice-section {
  padding: 16px;
}

.practice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.mode-badge {
  padding: 4px 12px;
  background: linear-gradient(135deg, #ff9800, #ffb74d);
  color: white;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.stats-row {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #666;
}

.keyword-display {
  text-align: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  margin-bottom: 16px;
}

.keyword-label {
  font-size: 14px;
  color: #999;
}

.keyword-char {
  display: block;
  font-size: 48px;
  font-weight: 700;
  color: #ff6b6b;
  font-family: 'STKaiti', serif;
  margin-top: 8px;
}

.tail-hint {
  background: var(--card)8e1;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  text-align: center;
}

.tail-hint p {
  margin: 4px 0;
  font-size: 14px;
  color: #666;
}

.tail-char {
  color: #ff6b6b !important;
  font-weight: 600;
}

.tail-char span {
  font-size: 18px;
}

.timer-ring {
  width: 100px;
  height: 100px;
  margin: 20px auto;
  border-radius: 50%;
  background: conic-gradient(
    #4a90d9 calc(var(--progress, 0) * 1%),
    #e8e4dc calc(var(--progress, 0) * 1%)
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

.timer-ring.warning {
  background: conic-gradient(
    #f44336 calc(var(--progress, 0) * 1%),
    #ffcdd2 calc(var(--progress, 0) * 1%)
  );
}

.timer-inner {
  position: relative;
  text-align: center;
}

.timer-number {
  font-size: 32px;
  font-weight: 700;
  color: #333;
}

.hint-area {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: #e3f2fd;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  color: #1976d2;
}

.hint-area span {
  color: #ff6b6b;
  font-weight: 600;
}

.input-area {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.quick-phrases {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 12px 0;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.action-buttons button {
  flex: 1;
}

/* 历史记录 */
.history-section {
  background: white;
  border-radius: 12px;
  padding: 16px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.history-header span {
  font-size: 14px;
  color: #666;
}

.history-list {
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.history-item:last-child {
  border-bottom: none;
}

.history-item.correct {
  color: #4caf50;
}

.history-item.wrong {
  color: #f44336;
}

.history-text {
  flex: 1;
  font-size: 14px;
}

.history-keyword {
  font-size: 12px;
  color: #999;
}

/* 结果页面 */
.result-section {
  padding: 20px 16px;
}

.result-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
}

.score-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 24px;
}

.score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4caf50, #81c784);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
}

.score-number {
  font-size: 32px;
  font-weight: 700;
}

.score-label {
  font-size: 12px;
}

.score-divider {
  font-size: 48px;
  color: #ccc;
}

.total-number {
  font-size: 48px;
  font-weight: 700;
  color: #333;
}

.accuracy-display {
  text-align: center;
  margin-bottom: 24px;
  position: relative;
}

.accuracy-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

.result-comment {
  text-align: center;
  margin-bottom: 24px;
}

.comment-title {
  font-size: 20px;
  margin: 0 0 8px;
}

.comment-text {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.detail-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.stat-card {
  background: #f8f8f8;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
}

.stat-value.correct { color: #4caf50; }
.stat-value.wrong { color: #f44336; }
.stat-value.time { color: #2196f3; }

.stat-label {
  font-size: 12px;
  color: #999;
}

.wrong-review h3 {
  font-size: 16px;
  margin: 0 0 12px;
}

.wrong-item {
  background: var(--card)3f3;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.wrong-item p {
  margin: 4px 0;
  font-size: 14px;
}

.wrong-question { color: #666; }
.wrong-answer { color: #f44336; }
.correct-answer { color: #4caf50; font-weight: 500; }

.result-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 设置弹窗 */
.settings-popup {
  padding: 20px;
}

.settings-popup h3 {
  text-align: center;
  margin: 0 0 20px;
}

.popup-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.popup-actions button {
  flex: 1;
}

/* 语音按钮 */
.voice-fab {
  position: fixed;
  bottom: 80px;
  right: 20px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4caf50, #81c784);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
  cursor: pointer;
  z-index: 100;
}

.voice-fab van-icon {
  font-size: 24px;
}

/* 语音遮罩 */
.voice-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: white;
  z-index: 1000;
}

.voice-overlay p {
  margin: 0;
}

.voice-hint {
  font-size: 14px;
  color: #aaa;
}

.voice-animation {
  display: flex;
  gap: 8px;
  align-items: flex-end;
  height: 40px;
}

.voice-wave {
  width: 8px;
  background: #4caf50;
  border-radius: 4px;
  animation: wave 1s ease-in-out infinite;
}

.voice-wave:nth-child(1) { animation-delay: 0s; }
.voice-wave:nth-child(2) { animation-delay: 0.2s; }
.voice-wave:nth-child(3) { animation-delay: 0.4s; }

@keyframes wave {
  0%, 100% { height: 10px; }
  50% { height: 40px; }
}
</style>
