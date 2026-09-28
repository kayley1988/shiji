<template>
  <div class="challenge-page bg-xuanzhi">

    <!-- 顶部导航 -->
    <header class="app-nav">
      <button class="nav-back" @click="$router.back()">
        <van-icon name="arrow-left" />
      </button>
      <span class="nav-title">题库闯关</span>
      <span class="nav-right"></span>
    </header>

    <!-- ══ 维度选择页 ═══════════════════════════════ -->
    <div v-if="phase === 'select'" class="phase-select animate-fadeUp">
      <div class="select-intro">
        <p class="intro-text">选择维度，开启你的诗词闯关之旅</p>
      </div>

      <!-- 朝代 -->
      <div class="dim-section">
        <div class="dim-label">
          <van-icon name="clock-o" size="14" />
          <span>朝代</span>
          <span class="dim-hint">（必选）</span>
        </div>
        <div class="dim-chips">
          <button
            v-for="d in dimensions?.dynasties" :key="d.id"
            class="dim-chip"
            :class="{ active: selected.dynasty === d.id }"
            @click="selected.dynasty = d.id"
          >
            <span class="chip-name">{{ d.name }}</span>
            <span class="chip-desc">{{ d.desc }}</span>
            <span class="chip-count">{{ d.count }}</span>
          </button>
        </div>
      </div>

      <!-- 派系 -->
      <div class="dim-section" v-if="dimensions?.factions">
        <div class="dim-label">
          <van-icon name="friends-o" size="14" />
          <span>诗人派系</span>
          <span class="dim-hint">（可选）</span>
        </div>
        <div class="dim-chips grid-2">
          <button
            v-for="f in dimensions.factions" :key="f.id"
            class="dim-chip small"
            :class="{ active: selected.faction === f.id }"
            @click="toggleChip('faction', f.id)"
          >
            <span class="chip-name">{{ f.name }}</span>
            <span class="chip-poets">{{ f.poets?.join(' · ') }}</span>
          </button>
        </div>
      </div>

      <!-- 主题 -->
      <div class="dim-section" v-if="dimensions?.themes">
        <div class="dim-label">
          <van-icon name="flag-o" size="14" />
          <span>主题意象</span>
          <span class="dim-hint">（可选）</span>
        </div>
        <div class="dim-chips wrap">
          <button
            v-for="t in dimensions.themes" :key="t.id"
            class="dim-tag"
            :class="{ active: selected.theme === t.id }"
            @click="toggleChip('theme', t.id)"
          >{{ t.name }}</button>
        </div>
      </div>

      <!-- 形式 -->
      <div class="dim-section" v-if="dimensions?.forms">
        <div class="dim-label">
          <van-icon name="orders-o" size="14" />
          <span>诗歌形式</span>
          <span class="dim-hint">（可选）</span>
        </div>
        <div class="dim-chips wrap">
          <button
            v-for="f in dimensions.forms" :key="f.id"
            class="dim-tag"
            :class="{ active: selected.form === f.id }"
            @click="toggleChip('form', f.id)"
          >{{ f.name }}</button>
        </div>
      </div>

      <!-- 模式 -->
      <div class="dim-section">
        <div class="dim-label">
          <van-icon name="fire-o" size="14" />
          <span>模式</span>
        </div>
        <div class="mode-chips">
          <button class="mode-chip" :class="{ active: mode === 'classic' }" @click="mode = 'classic'">
            <span class="mc-name">经典闯关</span>
            <span class="mc-desc">10 题一局，看成绩</span>
          </button>
          <button class="mode-chip" :class="{ active: mode === 'endless' }" @click="mode = 'endless'">
            <span class="mc-name">无尽刷题 ∞</span>
            <span class="mc-desc">连刷不停，随时结算</span>
          </button>
        </div>
        <p class="lifetime-line" v-if="lifetime.answered">
          历史累计：刷过 {{ lifetime.answered }} 题 · 答对 {{ lifePct }}% · 最高连对 {{ lifetime.bestStreak }}
        </p>
      </div>

      <!-- 开始按钮 -->
      <div class="start-area">
        <van-button
          type="primary"
          block
          round
          :disabled="!selected.dynasty || starting"
          :loading="starting"
          class="start-btn"
          @click="handleStart"
        >
          {{ starting ? '题库抽取中…' : (selected.dynasty ? (mode === 'endless' ? '开始连刷 ∞' : '开始闯关') : '请先选择朝代') }}
        </van-button>
        <p class="start-tip" v-if="startError">{{ startError }}</p>
      </div>
    </div>

    <!-- ══ 答题页 ═══════════════════════════════ -->
    <div v-else-if="phase === 'playing'" class="phase-play animate-fadeUp">

      <!-- 进度条 -->
      <div class="play-progress">
        <span class="pp-index">{{ isEndless ? `第${cum.rounds + 1}组 ` : '' }}{{ currentIdx + 1 }}/{{ questions.length }}</span>
        <div class="pp-bar">
          <div class="pp-fill" :style="{ width: ((currentIdx + 1) / questions.length * 100) + '%' }"></div>
        </div>
        <span class="pp-score" :class="{ fire: isEndless && cum.streak >= 3 }">
          {{ isEndless ? `✓${cum.correct} · 连${cum.streak}` : `✓ ${answeredCount}` }}
        </span>
        <span v-if="isEndless" class="pp-cashout" @click="settleEndless(true)">结算</span>
      </div>

      <!-- 当前题目 -->
      <div class="q-card" v-if="currentQ">
        <div class="q-meta">{{ currentQ.title }} · {{ currentQ.author }}</div>
        <div class="q-verse">{{ currentQ.question }}</div>
        <div class="q-hint">请填入□中的字</div>

        <!-- 选项 -->
        <div class="q-options">
          <button
            v-for="opt in currentQ.options" :key="opt"
            class="q-opt"
            :class="{
              selected: selectedOpt === opt,
              correct: showResult && opt === currentQ.answer,
              wrong: showResult && selectedOpt === opt && opt !== currentQ.answer
            }"
            @click="selectOpt(opt)"
            :disabled="showResult"
          >{{ opt }}</button>
        </div>

        <!-- 结果反馈 -->
        <div class="q-feedback" v-if="showResult">
          <div class="feedback-correct" v-if="selectedOpt === currentQ.answer">
            <van-icon name="passed" size="20" color="var(--jade)" />
            <span>答对了！+5 经验</span>
          </div>
          <template v-else>
            <div class="feedback-wrong">
              <van-icon name="cross" size="20" color="var(--cinnabar)" />
              <span>正确答案是「{{ currentQ.answer }}」</span>
            </div>
            <button class="ai-explain-btn" :disabled="explainLoading" @click="askExplain">
              {{ explainLoading ? 'AI 品读中…' : '✨ AI 讲解这句诗' }}
            </button>
          </template>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="play-actions">
        <van-button
          v-if="!showResult"
          type="primary"
          block
          round
          :disabled="!selectedOpt"
          class="confirm-btn"
          @click="confirmAnswer"
        >确认作答</van-button>
        <van-button
          v-else
          type="default"
          block
          round
          class="next-btn"
          @click="nextQuestion"
        >{{ currentIdx + 1 >= questions.length ? '查看成绩' : '下一题' }}</van-button>
      </div>

      <!-- 已答进度点 -->
      <div class="q-dots">
        <span
          v-for="(q, i) in answers" :key="i"
          class="q-dot"
          :class="{
            done: q.answer !== null,
            correct: q.isCorrect === true,
            wrong: q.isCorrect === false
          }"
        ></span>
      </div>
    </div>

    <!-- ══ 结果页 ═══════════════════════════════ -->
    <div v-else-if="phase === 'result'" class="phase-result animate-fadeUp">
      <div class="result-card">
        <div class="result-stars">
          <span v-for="i in 3" :key="i" class="result-star" :class="{ filled: starCount >= i }">★</span>
        </div>
        <div class="result-score">{{ resultData.score }}分</div>
        <div class="result-sub">答对 {{ resultData.correct }} / {{ resultData.total }} 题</div>
        <div class="result-exp">+{{ resultData.exp_gain }} 经验值</div>
      </div>

      <!-- 无尽模式：本次连刷累计 -->
      <div v-if="resultData?.cumulative" class="cum-card">
        <div class="cum-title">∞ 本次连刷战绩</div>
        <div class="cum-grid">
          <div class="cum-cell"><b>{{ resultData.cumulative.answered }}</b><span>已刷题数</span></div>
          <div class="cum-cell"><b>{{ resultData.cumulative.correct }}</b><span>答对</span></div>
          <div class="cum-cell"><b>{{ accPct }}%</b><span>正确率</span></div>
          <div class="cum-cell"><b>{{ resultData.cumulative.bestStreak }}</b><span>最高连对</span></div>
        </div>
      </div>

      <!-- 答题回顾 -->
      <div class="review-list">
        <div
          v-for="(r, i) in resultData.results" :key="i"
          class="review-item"
          :class="{ correct: r.correct, wrong: !r.correct }"
        >
          <div class="review-header">
            <van-icon :name="r.correct ? 'passed' : 'cross'" size="16"
              :color="r.correct ? 'var(--jade)' : 'var(--cinnabar)'" />
            <span class="review-title">{{ r.title }} · {{ r.author }}</span>
          </div>
          <div class="review-q">{{ r.question }}</div>
          <div class="review-ans">
            <span v-if="!r.correct" class="review-wrong">你的答案：{{ r.user_answer || '（未作答）' }}</span>
            <span class="review-correct">正确答案：{{ r.correct_answer }}</span>
          </div>
        </div>
      </div>

      <div class="result-actions">
        <van-button v-if="resultData?.cumulative" type="primary" block round class="retry-btn" @click="continueEndless">继续刷 ∞</van-button>
        <van-button v-else type="primary" block round class="retry-btn" @click="handleRetry">再来一局</van-button>
        <van-button v-if="resultData?.cumulative" plain block round class="back-btn" @click="handleRetry">换个维度</van-button>
        <van-button plain block round class="back-btn" @click="$router.back()">返回首页</van-button>
      </div>
    </div>

    <!-- AI 讲解弹层 -->
    <div class="explain-mask" v-if="explainOpen" @click.self="explainOpen = false">
      <div class="explain-card">
        <div class="explain-head">
          <span class="eh-title">✨ AI 诗词讲解</span>
          <span class="eh-close" @click="explainOpen = false">✕</span>
        </div>
        <div class="explain-meta" v-if="currentQ">
          {{ currentQ.title }} · {{ currentQ.author }}（{{ currentQ.dynasty }}）
        </div>
        <div class="explain-body">
          <p v-if="explainLoading" class="explain-tip">墨香徐来，AI 正在品读这首诗…</p>
          <template v-else>
            <template v-for="(b, i) in explainBlocks" :key="i">
              <h4 v-if="b.h" class="ex-h">{{ b.t }}</h4>
              <p v-else class="ex-p">{{ b.t }}</p>
            </template>
          </template>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="page-loading">
      <p>墨香徐来…</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { showToast } from 'vant'
import { api } from '../api'


// ── 类型 ──────────────────────────────────────
interface Dynasty { id: string; name: string; desc: string; count: number }
interface Faction  { id: string; name: string; poets: string[]; count: number }
interface Theme   { id: string; name: string }
interface Form    { id: string; name: string; desc?: string }

interface Dimensions {
  dynasties: Dynasty[]
  factions: Faction[]
  themes: Theme[]
  forms: Form[]
}

interface Question {
  poem_id: string
  line_id: string
  question: string
  title: string
  author: string
  dynasty: string
  options: string[]
  answer: string
}

interface Answer {
  line_id: string
  answer: string | null
  isCorrect: boolean | null
}

const phase = ref<'select' | 'playing' | 'result'>('select')
const loading = ref(false)
const starting = ref(false)
const startError = ref('')
const dimensions = ref<Dimensions | null>(null)

// 模式：classic 经典 10 题 / endless 无尽连刷
const mode = ref<'classic' | 'endless'>('classic')
const isEndless = computed(() => mode.value === 'endless')

// 无尽模式：本次连刷累计（组数/题数/答对/总分/经验/连对）
const cum = ref({ rounds: 0, answered: 0, correct: 0, score: 0, exp: 0, streak: 0, bestStreak: 0 })
// 历史累计（跨会话持久化）
const LKEY = 'shiji_endless_lifetime'
const lifetime = ref({ answered: 0, correct: 0, bestStreak: 0 })
const accPct = computed(() => cum.value.answered ? Math.round(cum.value.correct / cum.value.answered * 100) : 0)
const lifePct = computed(() => lifetime.value.answered ? Math.round(lifetime.value.correct / lifetime.value.answered * 100) : 0)

function loadLifetime() {
  try {
    const v = JSON.parse(localStorage.getItem(LKEY) || '{}')
    if (v && typeof v.answered === 'number') lifetime.value = v
  } catch { lifetime.value = { answered: 0, correct: 0, bestStreak: 0 } }
}
function saveLifetime() {
  try { localStorage.setItem(LKEY, JSON.stringify(lifetime.value)) } catch { /* 忽略 */ }
}

// 选择状态
const selected = ref({ dynasty: '', faction: '', theme: '', form: '' })

// 闯关数据
const sessionId = ref('')
const questions = ref<Question[]>([])
const currentIdx = ref(0)
const currentQ = computed<Question | null>(() => questions.value[currentIdx.value] ?? null)
const selectedOpt = ref('')
const showResult = ref(false)
const answers = ref<Answer[]>([])
const resultData = ref<any>(null)

// ── 计算 ──────────────────────────────────────
const answeredCount = computed(() => answers.value.filter(a => a.answer !== null).length)
const starCount = computed(() => {
  if (!resultData.value) return 0
  const pct = resultData.value.score
  if (pct >= 90) return 3
  if (pct >= 60) return 2
  if (pct >= 30) return 1
  return 0
})

// ── 加载维度 ──────────────────────────────────────
onMounted(async () => {
  loadLifetime()
  loading.value = true
  try {
    const res = await api.getChallengeDimensions()
    dimensions.value = res.data
  } catch (e) {
    showToast('加载失败，请重试')
  } finally {
    loading.value = false
  }
})

// ── 切换 chip ──────────────────────────────────────
function toggleChip(type: 'faction' | 'theme' | 'form', id: string) {
  if (selected.value[type] === id) {
    selected.value[type] = ''
  } else {
    selected.value[type] = id
  }
}

// ── 开始闯关（无尽模式重置本次累计） ──────────────────────────────────────
async function handleStart() {
  if (!selected.value.dynasty) {
    startError.value = '请先选择一个朝代'
    return
  }
  cum.value = { rounds: 0, answered: 0, correct: 0, score: 0, exp: 0, streak: 0, bestStreak: 0 }
  await startBatch()
}

// 抽一组新题进入答题（保持 cum 不动，供无尽续组复用）
async function startBatch() {
  starting.value = true
  startError.value = ''
  try {
    const res = await api.startChallenge({
      dynasty: selected.value.dynasty || undefined,
      faction: selected.value.faction || undefined,
      theme: selected.value.theme || undefined,
      form: selected.value.form || undefined,
      count: 10,
    })
    sessionId.value = res.data.session_id
    questions.value = res.data.questions
    answers.value = questions.value.map(q => ({ line_id: q.line_id, answer: null, isCorrect: null }))
    currentIdx.value = 0
    selectedOpt.value = ''
    showResult.value = false
    explainOpen.value = false
    phase.value = 'playing'
  } catch (e: any) {
    startError.value = e?.response?.data?.error?.message || '启动失败，请换个维度试试'
  } finally {
    starting.value = false
  }
}

// ── 选选项 ──────────────────────────────────────
function selectOpt(opt: string) {
  if (showResult.value) return
  selectedOpt.value = opt
}

// ── 确认答案 ──────────────────────────────────────
function confirmAnswer() {
  if (!selectedOpt.value) return
  const q = currentQ.value
  if (!q) return
  showResult.value = true
  const isCorrect = selectedOpt.value === q.answer
  answers.value[currentIdx.value] = {
    line_id: q.line_id,
    answer: selectedOpt.value,
    isCorrect,
  }
  // 无尽模式：实时连对统计
  if (isEndless.value) {
    if (isCorrect) {
      cum.value.streak++
      cum.value.bestStreak = Math.max(cum.value.bestStreak, cum.value.streak)
    } else {
      cum.value.streak = 0
    }
  }
}

// ── 下一题 ──────────────────────────────────────
function nextQuestion() {
  if (currentIdx.value + 1 >= questions.value.length) {
    if (isEndless.value) settleEndless()
    else submitChallenge()
  } else {
    currentIdx.value++
    selectedOpt.value = ''
    showResult.value = false
    explainOpen.value = false
  }
}

// ── 无尽模式：结算本组 → 落账 → 无缝续组或收摊 ──────────────────────────────────────
async function settleEndless(cashOut = false) {
  loading.value = true
  try {
    const res = await api.submitChallenge({
      session_id: sessionId.value,
      answers: answers.value
        .filter(a => a.answer !== null)
        .map(a => ({ line_id: a.line_id, answer: a.answer as string })),
    })
    const d = res.data
    const answeredN = answers.value.filter(a => a.answer !== null).length
    cum.value.rounds++
    cum.value.answered += answeredN
    cum.value.correct += d.correct
    cum.value.score += d.score
    cum.value.exp += d.exp_gain
    // 历史累计落账
    lifetime.value.answered += answeredN
    lifetime.value.correct += d.correct
    lifetime.value.bestStreak = Math.max(lifetime.value.bestStreak, cum.value.bestStreak)
    saveLifetime()

    if (cashOut) {
      resultData.value = { ...d, cumulative: { ...cum.value } }
      cum.value.streak = 0
      phase.value = 'result'
    } else {
      showToast(`第 ${cum.value.rounds} 组完成 · 累计 ✓${cum.value.correct}/${cum.value.answered}`)
      await startBatch()
    }
  } catch (e) {
    showToast('结算失败，请重试')
  } finally {
    loading.value = false
  }
}

// 结果页「继续刷 ∞」：保持本次累计，续一组
async function continueEndless() {
  await startBatch()
}

// ── 提交闯关 ──────────────────────────────────────
async function submitChallenge() {
  loading.value = true
  try {
    const res = await api.submitChallenge({
      session_id: sessionId.value,
      answers: answers.value
        .filter(a => a.answer !== null)
        .map(a => ({ line_id: a.line_id, answer: a.answer as string })),
    })
    resultData.value = res.data
    phase.value = 'result'
  } catch (e) {
    showToast('提交失败')
  } finally {
    loading.value = false
  }
}

// ── AI 讲解（答错时）──────────────────────────────────
const explainOpen = ref(false)
const explainLoading = ref(false)
const explainText = ref('')
const explainCache = new Map<string, string>()

// 「## 标题 / 正文段落」轻量分段，渲染讲解内容
const explainBlocks = computed(() =>
  explainText.value
    .split('\n')
    .map(l => l.trim())
    .filter(Boolean)
    .map(l => ({ h: l.startsWith('##'), t: l.replace(/^#+\s*/, '') }))
)

async function askExplain() {
  const q = currentQ.value
  if (!q || explainLoading.value) return
  const cacheKey = q.line_id
  if (explainCache.has(cacheKey)) {
    explainText.value = explainCache.get(cacheKey)!
    explainOpen.value = true
    return
  }
  explainLoading.value = true
  explainOpen.value = true
  try {
    // 题干「」内为已知句，拼上正确答案构成完整上下文
    const known = (q.question.match(/「(.+?)」/) || [])[1] || ''
    const poemText = [known, q.answer].filter(Boolean).join('\n')
    const res: any = await api.aiPoemExplain({
      poem: poemText,
      source: `${q.title} - ${q.author}`,
      title: q.title,
      author: q.author,
      dynasty: q.dynasty,
      poem_id: q.poem_id,
    })
    explainText.value = res.data?.content || '讲解生成失败，请稍后再试。'
    explainCache.set(cacheKey, explainText.value)
  } catch (e: any) {
    const r = e?.response?.data
    explainText.value = r?.data?.content || r?.message || '讲解请求失败，请稍后再试。'
  } finally {
    explainLoading.value = false
  }
}

// ── 重玩 ──────────────────────────────────────
function handleRetry() {
  selected.value = { dynasty: '', faction: '', theme: '', form: '' }
  questions.value = []
  answers.value = []
  currentIdx.value = 0
  selectedOpt.value = ''
  showResult.value = false
  phase.value = 'select'
}
</script>

<style scoped>
.challenge-page { min-height: 100vh; padding-bottom: 40px; }

/* ── 维度选择 ── */
.phase-select { padding: 16px; }
.select-intro { text-align: center; margin-bottom: 20px; }
.intro-text { font-size: 14px; color: var(--stone); }

.dim-section { margin-bottom: 24px; }
.dim-label {
  display: flex; align-items: center; gap: 6px;
  font-size: 14px; font-weight: 600; color: var(--ink);
  margin-bottom: 12px;
}
.dim-hint { font-size: 12px; color: var(--stone); font-weight: 400; }

/* 朝代 chips */
.dim-chips { display: flex; flex-direction: column; gap: 10px; }
.dim-chips.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.dim-chips.wrap { display: flex; flex-wrap: wrap; gap: 8px; }

.dim-chip {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 16px; border-radius: 12px;
  background: var(--card); border: 1.5px solid var(--line);
  text-align: left; cursor: pointer; transition: all 0.2s;
  box-shadow: 0 1px 6px rgba(0,0,0,0.07);
}
.dim-chip:hover { border-color: var(--cinnabar); }
.dim-chip.active {
  border-color: var(--cinnabar);
  background: rgba(212,175,55,0.07);
  box-shadow: 0 2px 10px rgba(212,175,55,0.15);
}
.dim-chip.small { flex-direction: column; align-items: flex-start; padding: 10px 14px; }
.chip-name { font-family: var(--font-display); font-size: 15px; font-weight: 600; color: var(--ink); }
.chip-desc { font-size: 12px; color: var(--stone); }
.chip-count { margin-left: auto; font-size: 12px; color: var(--stone-light); }
.chip-poets { font-size: 11px; color: var(--stone); }

/* 主题/形式 tag */
.dim-tag {
  padding: 6px 14px; border-radius: 20px;
  background: var(--card); border: 1px solid var(--line);
  font-size: 13px; color: var(--ink); cursor: pointer; transition: all 0.2s;
}
.dim-tag:hover { border-color: var(--gold); color: var(--gold); }
.dim-tag.active {
  background: rgba(184,148,46,0.1);
  border-color: var(--gold);
  color: var(--gold);
}

/* 开始按钮 */
.start-area { margin-top: 28px; }
.start-btn { height: 48px; font-size: 16px; }
.start-tip { text-align: center; font-size: 13px; color: var(--cinnabar); margin-top: 8px; }

/* 模式选择 */
.mode-chips { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.mode-chip {
  display: flex; flex-direction: column; align-items: flex-start; gap: 3px;
  padding: 12px 14px; border-radius: 12px;
  background: var(--card); border: 1.5px solid var(--line);
  cursor: pointer; transition: all 0.2s; text-align: left;
}
.mode-chip.active {
  border-color: var(--cinnabar);
  background: rgba(212,175,55,0.07);
  box-shadow: 0 2px 10px rgba(212,175,55,0.15);
}
.mc-name { font-family: var(--font-display); font-size: 15px; font-weight: 600; color: var(--ink); }
.mode-chip.active .mc-name { color: var(--cinnabar); }
.mc-desc { font-size: 12px; color: var(--stone); }
.lifetime-line { margin-top: 10px; font-size: 12px; color: var(--stone-light); text-align: center; }

/* 无尽模式答题页 */
.pp-cashout {
  font-size: 12px; font-weight: 600; cursor: pointer; user-select: none;
  color: var(--gold); padding: 4px 10px; border-radius: 12px;
  border: 1px solid rgba(212,175,55,0.4); white-space: nowrap;
}
.pp-cashout:hover { background: rgba(212,175,55,0.12); }
.pp-score.fire { color: var(--cinnabar); font-weight: 700; }

/* 无尽战绩卡 */
.cum-card {
  background: var(--card); border-radius: 14px; padding: 16px;
  border: 1px solid rgba(212,175,55,0.2);
}
.cum-title { font-size: 14px; font-weight: 700; color: var(--gold); margin-bottom: 12px; text-align: center; letter-spacing: 1px; }
.cum-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center; }
.cum-cell { display: flex; flex-direction: column; gap: 2px; }
.cum-cell b { font-family: var(--font-display); font-size: 22px; color: var(--cinnabar); }
.cum-cell span { font-size: 11px; color: var(--stone); }

/* ── 答题页 ── */
.phase-play { padding: 16px; display: flex; flex-direction: column; gap: 16px; }

.play-progress { display: flex; align-items: center; gap: 10px; }
.pp-index { font-size: 13px; color: var(--stone); width: 36px; }
.pp-bar { flex: 1; height: 6px; background: var(--line); border-radius: 3px; }
.pp-fill { height: 100%; background: linear-gradient(90deg, var(--cinnabar), var(--gold)); border-radius: 3px; transition: width 0.4s; }
.pp-score { font-size: 13px; color: var(--jade); width: 28px; text-align: right; }

/* 题目卡 */
.q-card {
  background: var(--card); border-radius: 16px; padding: 20px;
  box-shadow: 0 2px 14px rgba(0,0,0,0.10);
  display: flex; flex-direction: column; gap: 12px;
}
.q-meta { font-size: 12px; color: var(--stone); }
.q-verse {
  font-family: var(--font-serif); font-size: 22px; line-height: 1.8;
  color: var(--ink); text-align: center; letter-spacing: 0.1em;
}
.q-hint { text-align: center; font-size: 13px; color: var(--stone); }

.q-options { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.q-opt {
  padding: 12px; border-radius: 10px;
  background: var(--paper-warm); border: 1.5px solid var(--line);
  font-family: var(--font-serif); font-size: 18px; color: var(--ink);
  cursor: pointer; transition: all 0.2s; text-align: center;
}
.q-opt:hover { border-color: var(--cinnabar); background: rgba(212,175,55,0.05); }
.q-opt.selected { border-color: var(--cinnabar); background: rgba(212,175,55,0.1); color: var(--cinnabar); }
.q-opt.correct { border-color: var(--jade); background: rgba(61,107,74,0.12); color: var(--jade); }
.q-opt.wrong { border-color: var(--cinnabar); background: rgba(212,175,55,0.08); color: var(--cinnabar); opacity: 0.7; }

.q-feedback { text-align: center; padding: 8px 0; }
.feedback-correct { display: flex; align-items: center; justify-content: center; gap: 6px; font-size: 14px; color: var(--jade); }
.feedback-wrong { display: flex; align-items: center; justify-content: center; gap: 6px; font-size: 14px; color: var(--cinnabar); }

/* AI 讲解入口 + 弹层 */
.ai-explain-btn {
  margin-top: 10px; padding: 8px 18px; border-radius: 18px;
  background: rgba(212,175,55,0.10); border: 1px solid rgba(212,175,55,0.45);
  color: var(--gold); font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.ai-explain-btn:hover:not(:disabled) { background: rgba(212,175,55,0.2); }
.ai-explain-btn:disabled { opacity: 0.55; cursor: wait; }

.explain-mask {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(10, 11, 14, 0.72);
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
.explain-card {
  width: 100%; max-width: 560px; max-height: 82vh;
  display: flex; flex-direction: column;
  background: var(--card, #1E222B); border-radius: 16px;
  border: 1px solid rgba(212,175,55,0.35);
  box-shadow: 0 12px 48px rgba(0,0,0,0.5);
  overflow: hidden;
}
.explain-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px 10px;
}
.eh-title { font-size: 15px; font-weight: 700; color: var(--gold); letter-spacing: 1px; }
.eh-close { font-size: 16px; color: var(--stone); cursor: pointer; padding: 4px 8px; }
.eh-close:hover { color: var(--ink); }
.explain-meta { padding: 0 16px 10px; font-size: 12px; color: var(--stone); border-bottom: 1px solid var(--line); }
.explain-body { padding: 14px 16px 20px; overflow-y: auto; line-height: 1.9; }
.ex-h { font-size: 14px; font-weight: 700; color: var(--cinnabar-light, #E9CB6B); margin: 14px 0 6px; }
.ex-h:first-child { margin-top: 0; }
.ex-p { font-size: 13px; color: var(--ink); margin: 0 0 10px; white-space: pre-wrap; }
.explain-tip { text-align: center; color: var(--stone); font-size: 14px; padding: 30px 0; }

/* 操作按钮 */
.play-actions { margin-top: 4px; }
.confirm-btn, .next-btn { height: 44px; font-size: 15px; }
.confirm-btn:disabled { opacity: 0.5; }

/* 答题点 */
.q-dots { display: flex; justify-content: center; gap: 6px; margin-top: 8px; }
.q-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--line); transition: all 0.2s; }
.q-dot.done { background: var(--stone); }
.q-dot.correct { background: var(--jade); }
.q-dot.wrong { background: var(--cinnabar); }

/* ── 结果页 ── */
.phase-result { padding: 16px; display: flex; flex-direction: column; gap: 16px; }

.result-card {
  background: linear-gradient(135deg, rgba(212,175,55,0.1), rgba(184,148,46,0.06));
  border-radius: 20px; padding: 28px 20px;
  text-align: center; border: 1px solid rgba(212,175,55,0.15);
  box-shadow: 0 4px 20px rgba(212,175,55,0.10);
}
.result-stars { display: flex; justify-content: center; gap: 6px; margin-bottom: 12px; }
.result-star { font-size: 32px; color: var(--line); transition: color 0.3s; }
.result-star.filled { color: var(--gold); }
.result-score { font-family: var(--font-display); font-size: 48px; color: var(--cinnabar); margin-bottom: 4px; }
.result-sub { font-size: 14px; color: var(--stone); margin-bottom: 6px; }
.result-exp { font-size: 14px; color: var(--gold); font-weight: 600; }

/* 答题回顾 */
.review-list { display: flex; flex-direction: column; gap: 10px; }
.review-item {
  background: var(--card); border-radius: 12px; padding: 14px;
  border-left: 3px solid; box-shadow: 0 1px 6px rgba(0,0,0,0.07);
}
.review-item.correct { border-color: var(--jade); }
.review-item.wrong { border-color: var(--cinnabar); }
.review-header { display: flex; align-items: center; gap: 6px; margin-bottom: 6px; }
.review-title { font-size: 12px; color: var(--stone); }
.review-q { font-family: var(--font-serif); font-size: 16px; color: var(--ink); margin-bottom: 6px; }
.review-ans { font-size: 12px; display: flex; flex-direction: column; gap: 2px; }
.review-wrong { color: var(--cinnabar); }
.review-correct { color: var(--jade); }

.result-actions { display: flex; flex-direction: column; gap: 10px; margin-top: 8px; }
.retry-btn { height: 44px; font-size: 15px; }
.back-btn { height: 44px; font-size: 15px; }

/* 加载 */
.page-loading { display: flex; align-items: center; justify-content: center; min-height: 60vh; font-family: var(--font-serif); font-size: 16px; color: var(--stone); }

/* 动画 */
.animate-fadeUp { animation: fadeSlideUp 0.3s ease-out; }
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
