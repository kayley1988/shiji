<template>
  <Teleport to="body">
    <div class="quiz-overlay" @click.self="$emit('close')">
      <div class="quiz-card" :style="cardStyle">

        <!-- 关闭 -->
        <button class="close-btn" @click="handleClose">
          <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
            <path d="M4 4l12 12M16 4L4 16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </button>

        <!-- 顶部：颜色信息 -->
        <div class="quiz-header" v-if="currentColor">
          <div class="color-chip" :style="{ background: currentColor.hex }"></div>
          <div class="color-info">
            <span class="color-name-lg">{{ currentColor.name }}</span>
            <span class="color-pinyin">{{ currentColor.pinyin }}</span>
          </div>
        </div>

        <!-- 加载 -->
        <div class="quiz-loading" v-if="loading">
          <p class="loading-text">墨香徐来…</p>
        </div>

        <!-- 答题区 -->
        <template v-else-if="question">
          <div class="quiz-prompt">
            <p class="prompt-label">请填入所缺之字</p>
            <div class="quiz-verse-wrap">
              <p class="quiz-verse" v-html="highlightedVerse"></p>
            </div>
          </div>

          <!-- 选项 -->
          <div class="quiz-options">
            <button
              v-for="opt in question.options"
              :key="opt"
              class="quiz-option"
              :class="{
                'selected': selected === opt,
                'correct': showResult && opt === question.answer,
                'wrong': showResult && selected === opt && opt !== question.answer
              }"
              @click="select(opt)"
              :disabled="showResult"
            >{{ opt }}</button>
          </div>

          <!-- 结果反馈 -->
          <div class="quiz-result" v-if="showResult">
            <p v-if="isCorrect" class="result-correct">✓ 答对了</p>
            <p v-else class="result-wrong">✗ 答案是「{{ question.answer }}」</p>
            <button class="result-btn" @click="handleNext">
              {{ isCorrect ? (allDone ? '完成' : '再来一色') : '继续' }}
            </button>
          </div>

          <!-- 进度 -->
          <div class="quiz-progress">
            <div class="progress-dots">
              <span v-for="i in totalColors" :key="i"
                class="pdot"
                :class="{ done: i <= solvedCount, current: i === solvedCount + 1 }"
              ></span>
            </div>
            <span class="progress-text">{{ solvedCount }} / {{ totalColors }}</span>
          </div>
        </template>

        <!-- 全部完成 -->
        <div class="quiz-done" v-else-if="!loading">
          <div class="done-seal">終</div>
          <p class="done-main">今日色卡已览尽</p>
          <p class="done-sub">明日再来，与诗意重逢</p>
          <div class="done-colors">
            <div
              v-for="c in solvedColors"
              :key="c.name"
              class="done-color-chip"
              :style="{ background: c.hex }"
              :title="c.name"
            ></div>
          </div>
          <button class="result-btn" @click="$emit('close')">返回</button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '../api'

const props = defineProps<{ open: boolean }>()
function handleClose() {
  console.log('ColorQuiz: 关闭按钮点击')
  emit('close')
}

const emit = defineEmits(['close', 'solved'])

// ── 数据 ──────────────────────────────────────
const loading = ref(true)
const colors = ref<any[]>([])       // 今日颜色列表
const currentIndex = ref(0)
const question = ref<any>(null)     // 当前题目
const selected = ref('')
const showResult = ref(false)
const solvedColors = ref<any[]>([])
const allDone = ref(false)

// ── 当前色 ──────────────────────────────────────
const currentColor = computed(() => colors.value[currentIndex.value])

const totalColors = computed(() => colors.value.length)
const solvedCount = computed(() => solvedColors.value.length)

// ── 着色诗句 ──────────────────────────────────────
const highlightedVerse = computed(() => {
  if (!question.value || !currentColor.value) return ''
  const verse = question.value.verse
  const answer = question.value.answer
  const idx = verse.indexOf(answer)
  if (idx === -1) return verse
  return (
    verse.slice(0, idx) +
    `<span class="fill-blank">${answer}</span>` +
    verse.slice(idx + answer.length)
  )
})

// ── 卡片配色 ──────────────────────────────────────
const cardStyle = computed(() => {
  const hex = currentColor.value?.hex || '#F5F0E8'
  const dark = isColorDark(hex)
  return {
    '--c-bg': hex,
    '--c-text': dark ? '#F5F0E8' : '#2C2420',
    '--c-muted': dark ? 'rgba(245,240,232,0.6)' : 'rgba(44,36,32,0.55)',
    '--c-accent': dark ? '#D4A86A' : '#8B2942',
  }
})

function isColorDark(hex: string) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return (r * 299 + g * 587 + b * 114) / 1000 < 128
}

// ── 静态色卡题目库 ──────────────────────────────────────
const FALLBACK_COLORS = [
  {
    name: '玄青', pinyin: 'xuán qīng', hex: '#1a2a3a',
    poem: { title: '春晓', author: '孟浩然' },
    question: { verse: '春眠不觉晓', question: '春眠不___晓', answer: '觉', options: ['觉', '知', '闻', '听'] },
    answer: '觉', options: ['觉', '知', '闻', '听']
  },
  {
    name: '月白', pinyin: 'yuè bái', hex: '#D0E8F0',
    poem: { title: '春晓', author: '孟浩然' },
    question: { verse: '处处闻啼鸟', question: '处处___啼鸟', answer: '闻', options: ['闻', '听', '见', '知'] },
    answer: '闻', options: ['闻', '听', '见', '知']
  },
  {
    name: '胭脂', pinyin: 'yān zhī', hex: '#8B2942',
    poem: { title: '春晓', author: '孟浩然' },
    question: { verse: '夜来风雨声', question: '夜来___雨声', answer: '风', options: ['风', '雨', '雪', '霜'] },
    answer: '风', options: ['风', '雨', '雪', '霜']
  },
  {
    name: '鹅黄', pinyin: 'é huáng', hex: '#F5E090',
    poem: { title: '咏鹅', author: '骆宾王' },
    question: { verse: '白毛浮绿水', question: '白毛___绿水', answer: '浮', options: ['浮', '游', '漂', '荡'] },
    answer: '浮', options: ['浮', '游', '漂', '荡']
  },
]

// ── 加载 ──────────────────────────────────────
function loadQuiz() {
  loading.value = true
  solvedColors.value = []
  currentIndex.value = 0
  allDone.value = false

  // 纯静态，秒开
  colors.value = FALLBACK_COLORS
  question.value = FALLBACK_COLORS[0].question

  // loading 持续 600ms 保留仪式感，然后自动消失
  setTimeout(() => { loading.value = false }, 600)
}

// ── 构造题目（从诗句中挖空一个字）──────────────
function makeQuestion(verse: string, author: string): any {
  // 找一个常见汉字作为答案
  const candidates = verse.split('').filter(c =>
    !'，。！？、；：「」『』（）' .includes(c) && c.charCodeAt(0) > 0x3000
  )
  if (candidates.length === 0) {
    return { question: verse, answer: '风', options: ['风', '雨', '云', '月'] }
  }
  const answer = candidates[Math.floor(Math.random() * candidates.length)]
  const question = verse.replace(answer, '___')
  // 生成干扰项：随机替换答案
  const distractors = generateDistractors(answer)
  const options = [...distractors, answer].sort(() => Math.random() - 0.5)
  return { verse, question, answer, options }
}

const COMMON_CHARS = '风雨云月花雪梅山川水火天地上下前后东西南北春秋冬夏白青红绿黄黑白明暗高低远近'
  + '君臣父子天地山河草木鸟兽鱼虫天地古今长短多少有无'

function generateDistractors(answer: string): string[] {
  const set = new Set<string>()
  for (const c of COMMON_CHARS) {
    if (c !== answer && !set.has(c)) set.add(c)
    if (set.size >= 3) break
  }
  return Array.from(set).slice(0, 3)
}

// ── 选择答案 ──────────────────────────────────────
const isCorrect = computed(() => selected.value === question.value?.answer)

function select(opt: string) {
  if (showResult.value) return
  selected.value = opt
  showResult.value = true
  if (isCorrect.value) {
    // 收藏
    const c = currentColor.value
    if (c && !solvedColors.value.find(sc => sc.name === c.name)) {
      solvedColors.value.push(c)
    }
    emit('solved', c)
  }
}

// ── 下一步 ──────────────────────────────────────
function handleNext() {
  if (isCorrect.value) {
    // 答对了 → 下一色
    if (currentIndex.value < colors.value.length - 1) {
      currentIndex.value++
      question.value = colors.value[currentIndex.value]?.question || null
    } else {
      allDone.value = true
    }
  }
  selected.value = ''
  showResult.value = false
}

onMounted(() => { if (props.open) loadQuiz() })
watch(() => props.open, (v) => {
  if (v) loadQuiz()
  else {
    loading.value = false
    question.value = null
  }
})
</script>

<style scoped>
.quiz-overlay {
  position: fixed; inset: 0; z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,0.55); backdrop-filter: blur(3px);
}
.quiz-card {
  position: relative;
  width: min(92vw, 400px);
  min-height: min(75vh, 520px);
  background: var(--c-bg, #F5F0E8);
  border-radius: 20px;
  display: flex; flex-direction: column; align-items: center; padding: 20px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.25);
}

/* ── 关闭 ───────────────────────────────── */
.close-btn {
  position: absolute; top: 14px; right: 14px;
  width: 34px; height: 34px; border-radius: 50%;
  background: rgba(0,0,0,0.1); border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: var(--c-text); transition: background 0.2s;
}
.close-btn:hover { background: rgba(0,0,0,0.18); }

/* ── 颜色头部 ───────────────────────────────── */
.quiz-header {
  display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
}
.color-chip {
  width: 44px; height: 44px; border-radius: 50%;
  border: 2px solid rgba(0,0,0,0.12);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.color-info { display: flex; flex-direction: column; }
.color-name-lg {
  font-family: var(--font-display); font-size: 24px;
  color: var(--c-text); letter-spacing: 0.05em;
}
.color-pinyin { font-size: 11px; color: var(--c-muted); margin-top: 2px; }

/* ── 加载 ───────────────────────────────── */
.quiz-loading {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 14px; color: var(--c-muted);
  pointer-events: none; user-select: none;
}
.loading-text {
  font-family: var(--font-serif); font-size: 16px;
  color: var(--c-muted);
}

/* ── 题目 ───────────────────────────────── */
.quiz-prompt { text-align: center; margin-bottom: 16px; }
.prompt-label {
  font-size: 12px; color: var(--c-muted); margin-bottom: 12px;
}
.quiz-verse-wrap {
  background: rgba(0,0,0,0.06); border-radius: 12px; padding: 16px 20px;
}
.quiz-verse {
  font-family: var(--font-serif); font-size: 22px;
  color: var(--c-text); line-height: 1.8; margin: 0;
  letter-spacing: 0.08em;
}
.quiz-verse :deep(.fill-blank) {
  color: var(--c-accent); border-bottom: 2px solid var(--c-accent);
  font-weight: 700; min-width: 1.2em; display: inline-block;
  text-align: center;
}

/* ── 选项 ───────────────────────────────── */
.quiz-options {
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
  width: 100%; margin-top: 16px;
}
.quiz-option {
  padding: 12px; border-radius: 12px;
  border: 1.5px solid rgba(0,0,0,0.12);
  background: rgba(0,0,0,0.04);
  font-size: 20px; font-family: var(--font-serif);
  color: var(--c-text); cursor: pointer; transition: all 0.2s;
  letter-spacing: 0.1em;
}
.quiz-option:active:not(:disabled) { transform: scale(0.97); }
.quiz-option.correct {
  background: rgba(74, 139, 106, 0.2);
  border-color: #4A8B6A; color: #4A8B6A;
}
.quiz-option.wrong {
  background: rgba(155, 58, 42, 0.15);
  border-color: #9B3A2A; color: #9B3A2A;
}
.quiz-option.selected:not(.correct):not(.wrong) {
  border-color: var(--c-accent);
}

/* ── 结果 ───────────────────────────────── */
.quiz-result {
  margin-top: 16px; text-align: center; width: 100%;
}
.result-correct { color: #4A8B6A; font-size: 15px; font-weight: 600; }
.result-wrong { color: #9B3A2A; font-size: 15px; }
.result-btn {
  margin-top: 10px; padding: 10px 36px; border-radius: 24px;
  border: none; background: var(--c-accent); color: #fff;
  font-size: 14px; cursor: pointer; transition: opacity 0.2s;
}
.result-btn:active { opacity: 0.8; }

/* ── 进度 ───────────────────────────────── */
.quiz-progress {
  margin-top: auto; display: flex; align-items: center; gap: 10px;
}
.progress-dots { display: flex; gap: 5px; }
.pdot {
  width: 8px; height: 8px; border-radius: 50%;
  background: rgba(0,0,0,0.12); transition: all 0.3s;
}
.pdot.done { background: var(--c-accent); }
.pdot.current { background: rgba(0,0,0,0.25); }
.progress-text { font-size: 11px; color: var(--c-muted); }

/* ── 完成 ───────────────────────────────── */
.quiz-done {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 14px;
}
.done-seal {
  width: 56px; height: 56px; border-radius: 8px;
  border: 3px solid var(--c-accent);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display); font-size: 28px; color: var(--c-accent);
  transform: rotate(-8deg);
}
.done-main {
  font-family: var(--font-display); font-size: 18px; color: var(--c-text);
}
.done-sub { font-size: 13px; color: var(--c-muted); }
.done-colors { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; }
.done-color-chip {
  width: 32px; height: 32px; border-radius: 50%;
  border: 2px solid rgba(0,0,0,0.1);
}
</style>
