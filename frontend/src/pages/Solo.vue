<template>
  <div class="solo-page bg-xuanzhi">

    <!-- 顶部导航 -->
    <header class="app-nav">
      <button class="nav-back" @click="$router.back()">
        <van-icon name="arrow-left" />
      </button>
      <span class="nav-title">独酌自娱</span>
      <span class="nav-right"></span>
    </header>

    <!-- ══ 规则介绍页 ═══════════════════════════════ -->
    <div v-if="phase === 'intro'" class="phase-intro animate-fadeUp">
      <div class="intro-card">
        <div class="intro-seal">令</div>
        <h2 class="intro-title">飞花令</h2>
        <p class="intro-desc">
          古人雅集，以字为令。<br/>
          我出关键字，你写含此字的千古名句。
        </p>
        <div class="intro-rules">
          <div class="rule-item">
            <van-icon name="flower-o" size="20" />
            <span>每轮随机抽取关键字</span>
          </div>
          <div class="rule-item">
            <van-icon name="edit" size="20" />
            <span>输入含此字的完整诗句</span>
          </div>
          <div class="rule-item">
            <van-icon name="passed" size="20" />
            <span>答对计入佳句，答错也有提示</span>
          </div>
          <div class="rule-item">
            <van-icon name="clock-o" size="20" />
            <span>不限时间，不限次数，随心自娱</span>
          </div>
        </div>
      </div>

      <!-- 关键字预览 -->
      <div class="keyword-preview" v-if="keywords.length">
        <p class="preview-label">今日关键字</p>
        <div class="preview-chips">
          <span class="kw-chip" v-for="kw in keywords" :key="kw">{{ kw }}</span>
        </div>
      </div>

      <van-button type="primary" block class="start-btn" @click="startGame">
        <van-icon name="play-circle-o" size="18" />
        开始飞花
      </van-button>
    </div>

    <!-- ══ 游戏页 ══════════════════════════════════ -->
    <div v-else-if="phase === 'playing'" class="phase-game">

      <!-- 进度条 -->
      <div class="game-progress">
        <span class="gp-index">{{ currentRound + 1 }} / {{ totalRounds }}</span>
        <div class="gp-bar">
          <div class="gp-fill" :style="{ width: ((currentRound) / totalRounds * 100) + '%' }"></div>
        </div>
        <span class="gp-score">✦ {{ correctCount }} 佳句</span>
      </div>

      <!-- 关键字展示 -->
      <div class="keyword-display animate-fadeUp" :key="currentRound">
        <div class="kw-seal-wrap">
          <div class="kw-seal">
            <span>{{ currentKeyword }}</span>
          </div>
        </div>
        <p class="kw-hint">请输入含「<strong>{{ currentKeyword }}</strong>」字的完整诗句</p>
      </div>

      <!-- 答题输入 -->
      <div class="answer-card animate-fadeUp delay-1" :key="'answer-' + currentRound">
        <van-field
          v-model="userAnswer"
          :placeholder="`如：春江花月夜……`"
          class="answer-field"
          @keyup.enter="submitAnswer"
        />
        <van-button
          type="primary"
          block
          class="answer-submit"
          :disabled="!userAnswer.trim() || submitting"
          :loading="submitting"
          @click="submitAnswer"
        >
          <van-icon name="checked" v-if="!submitting" />
          确认作答
        </van-button>
        <button class="peek-toggle" @click="openPeek">
          <van-icon name="eye-o" />
          想不起来？查看含「{{ currentKeyword }}」字的诗句
        </button>
      </div>

      <!-- 结果展示 -->
      <transition name="result-slide">
        <div v-if="showResult" class="result-card animate-fadeUp" :class="resultCorrect ? 'result-correct' : 'result-wrong'">
          <!-- 正确 -->
          <template v-if="resultCorrect">
            <div class="result-header">
              <van-icon name="star" size="24" color="var(--gold)" />
              <span class="result-tag tag-correct">✦ 佳句</span>
            </div>
            <p class="result-line">「{{ validatedAnswer.line }}」</p>
            <p class="result-poem">
              {{ validatedAnswer.poem_title }} · {{ validatedAnswer.poem_author }}
              <span class="result-dynasty">{{ validatedAnswer.poem_dynasty }}</span>
            </p>
            <!-- 全诗展示 -->
            <div v-if="validatedAnswer.full_poem?.length" class="full-poem">
              <div class="fp-sep"></div>
              <p class="fp-label">全诗</p>
              <p class="fp-lines" v-for="(l, i) in validatedAnswer.full_poem" :key="i"
                 :class="{ 'fp-cur': i + 1 === validatedAnswer.line_order }">
                {{ l }}
              </p>
            </div>
          </template>

          <!-- 错误 -->
          <template v-else>
            <div class="result-header">
              <van-icon name="revoked" size="24" color="var(--stone)" />
              <span class="result-tag tag-wrong">未收录</span>
            </div>
            <p class="wrong-user">「{{ userAnswer }}」</p>
            <p class="wrong-msg">{{ validatedAnswer.message }}</p>
            <!-- 提示 -->
            <div v-if="validatedAnswer.hint_lines?.length" class="hints">
              <p class="hints-label">含「{{ currentKeyword }}」的诗句：</p>
              <div class="hint-item" v-for="(h, i) in validatedAnswer.hint_lines" :key="i">
                <span class="hint-line">「{{ h.line }}」</span>
                <span class="hint-meta">{{ h.title }} · {{ h.author }}</span>
              </div>
            </div>
          </template>

          <!-- 下一题 / 完成 -->
          <van-button
            type="default"
            block
            class="next-btn"
            @click="nextRound"
          >
            {{ currentRound + 1 >= totalRounds ? '查看成绩' : '下一题' }}
            <van-icon name="arrow" />
          </van-button>
        </div>
      </transition>
    </div>

    <!-- ══ 完成页 ══════════════════════════════════ -->
    <div v-else-if="phase === 'finish'" class="phase-finish animate-fadeUp">
      <div class="finish-card">
        <div class="finish-seal">
          <span>{{ winRate }}%</span>
        </div>
        <h3 class="finish-title">{{ finishTitle }}</h3>
        <p class="finish-sub">{{ correctCount }} / {{ totalRounds }} 佳句</p>
        <div class="finish-stats">
          <div class="fs-item">
            <span class="fs-num">{{ correctCount }}</span>
            <span class="fs-label">佳句</span>
          </div>
          <div class="fs-div"></div>
          <div class="fs-item">
            <span class="fs-num">{{ totalRounds - correctCount }}</span>
            <span class="fs-label">未中</span>
          </div>
          <div class="fs-div"></div>
          <div class="fs-item">
            <span class="fs-num">{{ winRate }}%</span>
            <span class="fs-label">正确率</span>
          </div>
        </div>
      </div>

      <van-button type="primary" block class="restart-btn" @click="restartGame">
        <van-icon name="replay" />
        再来一轮
      </van-button>

      <van-button plain block class="back-btn" @click="$router.back()">
        返回首页
      </van-button>
    </div>

    <!-- 查看含关键字的诗句（弹窗） -->
    <van-popup
      v-model:show="peekVisible"
      position="bottom"
      round
      :style="{ maxHeight: '72vh' }"
    >
      <div class="peek-panel">
        <div class="peek-header">
          <span class="peek-title">含「{{ currentKeyword }}」的诗句</span>
          <van-icon name="cross" @click="peekVisible = false" />
        </div>
        <div class="peek-list">
          <van-loading v-if="peekLoading" class="peek-loading" />
          <van-empty v-else-if="!peekLines.length" description="暂无诗句" />
          <div v-for="(l, i) in peekLines" :key="i" class="peek-item">
            <span class="peek-line">「{{ l.line }}」</span>
            <span class="peek-meta">{{ l.poem_title }} · {{ l.poem_author }}</span>
          </div>
          <div v-if="peekHasMore && !peekLoading" class="peek-more" @click="loadMorePeek">
            加载更多 ↓
          </div>
        </div>
      </div>
    </van-popup>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'

// ── 阶段控制 ──────────────────────────────────
type Phase = 'intro' | 'playing' | 'finish'
const phase = ref<Phase>('intro')

// ── 游戏参数 ──────────────────────────────────
const keywords = ref<string[]>([])
const roundKeywords = ref<string[]>([])
const totalRounds = 8
const currentRound = ref(0)
const correctCount = ref(0)

// ── 当前题目 ──────────────────────────────────
const currentKeyword = ref('')
const userAnswer = ref('')
const submitting = ref(false)
const showResult = ref(false)
const resultCorrect = ref(false)
const validatedAnswer = ref<any>({})

// ── 查看佳句（peek） ──────────────────────────
const peekVisible = ref(false)
const peekLoading = ref(false)
const peekLines = ref<any[]>([])
const peekPage = ref(1)
const peekHasMore = ref(false)

async function openPeek() {
  peekVisible.value = true
  peekPage.value = 1
  peekLines.value = []
  await loadPeek()
}

async function loadPeek() {
  if (peekLoading.value) return
  peekLoading.value = true
  try {
    const res = await api.practicePeek({
      keyword: currentKeyword.value,
      page: peekPage.value,
      page_size: 20,
    })
    const d = res.data
    if (d) {
      if (peekPage.value === 1) {
        peekLines.value = d.lines || []
      } else {
        peekLines.value.push(...(d.lines || []))
      }
      peekHasMore.value = d.has_more === true
    }
  } catch {
    peekHasMore.value = false
  } finally {
    peekLoading.value = false
  }
}

async function loadMorePeek() {
  peekPage.value++
  await loadPeek()
}

// ── 统计数据 ──────────────────────────────────
const winRate = computed(() =>
  Math.round(correctCount.value / totalRounds * 100)
)
const finishTitle = computed(() => {
  const r = winRate.value
  if (r >= 90) return '才高八斗'
  if (r >= 70) return '腹有诗书'
  if (r >= 50) return '渐入佳境'
  if (r >= 30) return '初窥门径'
  return '勤学苦练'
})

// ── 初始化：获取关键字池 ───────────────────────
onMounted(async () => {
  try {
    const res = await api.getPracticeKeywords()
    const kws = res.data?.keywords
    if (kws?.length) {
      keywords.value = kws
    } else {
      keywords.value = ['月', '花', '春', '酒', '风', '雨', '雪', '秋', '云', '山', '水', '柳']
    }
  } catch {
    keywords.value = ['月', '花', '春', '酒', '风', '雨', '雪', '秋']
  }
})

function startGame() {
  // 从关键字池随机选 totalRounds 个
  const pool = [...keywords.value]
  const shuffled = pool.sort(() => Math.random() - 0.5)
  roundKeywords.value = [...new Set(shuffled)].slice(0, totalRounds)

  currentKeyword.value = roundKeywords.value[0]
  phase.value = 'playing'
  currentRound.value = 0
  correctCount.value = 0
  userAnswer.value = ''
  showResult.value = false
}

async function submitAnswer() {
  const line = userAnswer.value.trim()
  if (!line || submitting.value) return

  submitting.value = true
  showResult.value = false

  try {
    const res = await api.practiceValidate({
      line,
      keyword: currentKeyword.value,
    })
    const d = res.data
    validatedAnswer.value = d || {}
    resultCorrect.value = d?.correct === true
    if (resultCorrect.value) correctCount.value++
  } catch (err: any) {
    console.error('validate error:', err?.response?.data || err?.message || err)
    validatedAnswer.value = { correct: false, message: err?.response?.data?.message || err?.message || '网络异常，请重试' }
    resultCorrect.value = false
  } finally {
    submitting.value = false
    showResult.value = true
  }
}

function nextRound() {
  userAnswer.value = ''
  showResult.value = false

  if (currentRound.value + 1 >= totalRounds) {
    phase.value = 'finish'
    return
  }

  currentRound.value++
  currentKeyword.value = roundKeywords.value[currentRound.value] || keywords.value[0]
}

function restartGame() {
  phase.value = 'intro'
}
</script>

<style scoped>
.solo-page { min-height: 100vh; padding-bottom: 30px; }

/* ── 导航栏 ── */
.app-nav {
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
  background: rgba(250,246,240,0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(158,142,126,0.15);
}
.nav-back {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  background: none; border: none; color: var(--ink);
  font-size: 20px; cursor: pointer; border-radius: var(--radius-sm);
}
.nav-title { font-family: var(--font-display); font-size: 18px; color: var(--ink); }
.nav-right { width: 36px; }

/* ── 规则介绍页 ── */
.phase-intro { padding: 20px 16px; display: flex; flex-direction: column; gap: 16px; }
.intro-card {
  background: linear-gradient(135deg, rgba(212,175,55,0.07), rgba(184,148,46,0.04));
  border: 1px solid rgba(184,148,46,0.15);
  border-radius: var(--radius-md); padding: 28px 20px; text-align: center;
}
.intro-seal {
  display: inline-flex; align-items: center; justify-content: center;
  width: 56px; height: 56px; border-radius: 50%;
  background: rgba(212,175,55,0.1); color: var(--cinnabar);
  font-family: var(--font-display); font-size: 22px; font-weight: 700;
  border: 2px solid rgba(212,175,55,0.2);
  margin-bottom: 12px;
}
.intro-title {
  font-family: var(--font-display); font-size: 24px; color: var(--ink);
  margin-bottom: 8px;
}
.intro-desc {
  font-size: 14px; color: var(--stone); line-height: 1.8; margin-bottom: 20px;
}
.intro-rules { display: flex; flex-direction: column; gap: 10px; text-align: left; }
.rule-item {
  display: flex; align-items: center; gap: 10px;
  font-size: 14px; color: var(--ink);
}
.rule-item .van-icon { color: var(--gold); flex-shrink: 0; }

.keyword-preview { padding: 0 4px; }
.preview-label { font-size: 12px; color: var(--stone); margin-bottom: 8px; text-align: center; }
.preview-chips { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.kw-chip {
  padding: 4px 14px; border-radius: var(--radius-full);
  background: rgba(184,148,46,0.1); color: var(--gold);
  font-size: 14px; font-family: var(--font-serif);
  border: 1px solid rgba(184,148,46,0.2);
}

.start-btn { border-radius: var(--radius-md); height: 48px; font-size: 16px; }

/* ── 游戏页 ── */
.phase-game { padding: 0 16px; display: flex; flex-direction: column; gap: 14px; }

.game-progress {
  display: flex; align-items: center; gap: 10px; padding: 8px 0;
}
.gp-index { font-size: 13px; color: var(--stone); width: 30px; }
.gp-bar { flex: 1; height: 6px; background: var(--line); border-radius: 3px; }
.gp-fill { height: 100%; background: linear-gradient(90deg, var(--cinnabar), var(--gold)); border-radius: 3px; transition: width 0.4s; }
.gp-score { font-size: 13px; color: var(--gold); width: 48px; text-align: right; }

/* 关键字展示 */
.keyword-display { text-align: center; padding: 8px 0 2px; }
.kw-seal-wrap { display: flex; justify-content: center; margin-bottom: 8px; }
.kw-seal {
  width: 60px; height: 60px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: var(--cinnabar); color: #fff;
  font-family: var(--font-display); font-size: 28px; font-weight: 700;
  box-shadow: 0 4px 14px rgba(212,175,55,0.32);
  border: 2px solid rgba(255,255,255,0.3);
}
.kw-hint { font-size: 13px; color: var(--stone); line-height: 1.6; text-align: center; }
.kw-hint strong { color: var(--cinnabar); }

/* 答题卡 */
.answer-card {
  background: var(--card); border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm); padding: 16px; display: flex; flex-direction: column; gap: 12px;
}
.answer-field :deep(.van-field__control) {
  font-family: var(--font-serif); font-size: 16px; color: var(--ink);
  text-align: center;
}
.answer-field :deep(.van-field__body) { justify-content: center; }
.answer-submit {
  border-radius: var(--radius-md); height: 44px;
  background: var(--cinnabar) !important;
  border-color: var(--cinnabar) !important;
  color: #fff !important;
  font-weight: 600;
  transition: all 0.2s;
}
.answer-submit:disabled {
  background: rgba(158,142,126,0.35) !important;
  border-color: rgba(158,142,126,0.35) !important;
  color: rgba(255,255,255,0.6) !important;
}

/* 结果卡 */
.result-card {
  background: var(--card); border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm); padding: 20px;
}
.result-correct { border-left: 3px solid var(--gold); }
.result-wrong   { border-left: 3px solid var(--stone-light); }

.result-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.result-tag {
  font-size: 13px; padding: 2px 10px; border-radius: var(--radius-full);
}
.tag-correct { background: rgba(184,148,46,0.1); color: var(--gold); }
.tag-wrong   { background: rgba(158,142,126,0.1); color: var(--stone); }

.result-line {
  font-family: var(--font-serif); font-size: 17px; line-height: 1.8; color: var(--ink);
  margin-bottom: 8px;
}
.result-poem { font-size: 13px; color: var(--stone); margin-bottom: 14px; }
.result-dynasty { margin-left: 6px; color: var(--stone-light); }

/* 全诗 */
.full-poem { margin: 14px 0; }
.fp-sep { height: 1px; background: rgba(158,142,126,0.15); margin-bottom: 12px; }
.fp-label { font-size: 11px; color: var(--stone-light); margin-bottom: 8px; }
.fp-lines {
  font-family: var(--font-serif); font-size: 14px; line-height: 2; color: var(--stone);
  text-align: center;
}
.fp-cur { color: var(--cinnabar); font-weight: 600; }

.wrong-user { font-family: var(--font-serif); font-size: 16px; color: var(--stone); margin-bottom: 6px; }
.wrong-msg  { font-size: 13px; color: var(--stone); margin-bottom: 12px; }

.hints { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
.hints-label { font-size: 12px; color: var(--stone); }
.hints {
  background: var(--paper-warm);
  border-radius: 10px; padding: 12px 14px;
  margin-top: 6px;
}
.hints-label { font-size: 12px; color: var(--stone); margin-bottom: 8px; }
.hint-item {
  display: flex; flex-direction: column; gap: 2px;
  padding: 6px 0; border-bottom: 1px solid rgba(158,142,126,0.12);
}
.hint-item:last-child { border-bottom: none; padding-bottom: 0; }
.hint-line { font-family: var(--font-serif); font-size: 14px; color: var(--ink); }
.hint-meta { font-size: 11px; color: var(--stone-light); }

.next-btn { margin-top: 14px; border-radius: var(--radius-md); }

/* 查看佳句 */
.peek-toggle {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  width: 100%; background: none; border: none; cursor: pointer;
  font-size: 13px; color: var(--gold); padding: 4px 0;
}
.peek-toggle .van-icon { font-size: 15px; }
.peek-toggle:active { opacity: 0.7; }

.peek-panel {
  display: flex; flex-direction: column;
  height: 72vh; background: var(--paper);
}
.peek-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px; border-bottom: 1px solid rgba(158,142,126,0.15);
  font-family: var(--font-display); font-size: 16px; color: var(--ink);
}
.peek-header .van-icon { font-size: 20px; color: var(--stone); cursor: pointer; }
.peek-list { flex: 1; overflow-y: auto; padding: 12px 16px; }
.peek-loading { display: flex; justify-content: center; padding: 40px 0; }
.peek-item {
  display: flex; flex-direction: column; gap: 4px;
  padding: 12px 0; border-bottom: 1px dashed rgba(158,142,126,0.15);
}
.peek-line { font-family: var(--font-serif); font-size: 15px; color: var(--ink); line-height: 1.7; }
.peek-line .kw { color: var(--cinnabar); font-weight: 600; }
.peek-meta { font-size: 11px; color: var(--stone-light); }
.peek-more {
  text-align: center; padding: 14px 0; font-size: 13px; color: var(--gold); cursor: pointer;
}

/* ── 完成页 ── */
.phase-finish { padding: 20px 16px; display: flex; flex-direction: column; gap: 14px; }
.finish-card {
  background: linear-gradient(135deg, rgba(212,175,55,0.08), rgba(184,148,46,0.05));
  border: 1px solid rgba(184,148,46,0.15); border-radius: var(--radius-md);
  padding: 32px 20px; text-align: center;
}
.finish-seal {
  display: inline-flex; align-items: center; justify-content: center;
  width: 80px; height: 80px; border-radius: 50%;
  background: linear-gradient(135deg, var(--gold), #d4a83a);
  color: #fff; font-family: var(--font-display);
  font-size: 20px; font-weight: 700;
  box-shadow: 0 4px 16px rgba(184,148,46,0.4);
  margin-bottom: 14px;
}
.finish-title { font-family: var(--font-display); font-size: 22px; color: var(--ink); margin-bottom: 4px; }
.finish-sub { font-size: 14px; color: var(--stone); margin-bottom: 20px; }
.finish-stats { display: flex; align-items: center; justify-content: center; gap: 0; }
.fs-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; }
.fs-num { font-size: 26px; font-weight: 700; color: var(--ink); }
.fs-label { font-size: 11px; color: var(--stone); }
.fs-div { width: 1px; height: 32px; background: var(--line); }

.restart-btn { border-radius: var(--radius-md); height: 48px; font-size: 16px; }
.back-btn { border-radius: var(--radius-md); height: 44px; }

/* ── 动画 ── */
.animate-fadeUp { animation: fadeUp 0.4s ease both; }
.delay-1 { animation-delay: 0.1s; }
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

.result-slide-enter-active { animation: fadeUp 0.3s ease; }
.result-slide-leave-active { display: none; }
</style>
