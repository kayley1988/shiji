<template>
  <div class="dash-page bg-xuanzhi">

    <!-- 顶部导航 -->
    <header class="app-nav">
      <button class="nav-back" @click="$router.back()">
        <van-icon name="arrow-left" />
      </button>
      <span class="nav-title">学习仪表盘</span>
      <span class="nav-right"></span>
    </header>

    <div v-if="!summary" class="page-loading"><p>墨香徐来…</p></div>

    <template v-else>
      <div class="dash-body animate-fadeUp">

        <!-- ══ 统计卡 ═══════════════════════════════ -->
        <div class="stat-grid">
          <div class="stat-card">
            <b>{{ summary.rounds }}</b>
            <span>累计闯关</span>
          </div>
          <div class="stat-card">
            <b>{{ summary.total_questions }}</b>
            <span>刷题总数</span>
          </div>
          <div class="stat-card">
            <b>{{ summary.accuracy }}<i class="unit">%</i></b>
            <span>总正确率</span>
          </div>
          <div class="stat-card" :class="{ alert: summary.mistakes_open > 0 }">
            <b>{{ summary.mistakes_open }}</b>
            <span>错题待清</span>
          </div>
        </div>

        <!-- ══ 打卡日历（最近 12 周）═══════════════════════════════ -->
        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">📅 打卡日历</span>
            <span class="panel-sub">近 {{ calendar.length }} 天 · 答题越多颜色越深</span>
          </div>
          <div class="heatmap" v-if="calendar.length">
            <div class="hm-grid">
              <div v-for="(week, wi) in heatmapWeeks" :key="week[0]?.date || wi" class="hm-col">
                <div
                  v-for="cell in week" :key="cell.date"
                  class="hm-cell"
                  :class="cell.level >= 0 ? 'lv' + cell.level : ''"
                  :title="cell.date + (cell.total ? `：答 ${cell.total} 题 · 对 ${cell.correct}` : '')"
                ></div>
              </div>
            </div>
            <div class="hm-legend">
              <span>少</span>
              <i class="hm-cell lv0"></i><i class="hm-cell lv1"></i>
              <i class="hm-cell lv2"></i><i class="hm-cell lv3"></i><i class="hm-cell lv4"></i>
              <span>多</span>
            </div>
          </div>
          <p v-else class="empty-tip">还没有闯关记录，先去开一局吧</p>
        </div>

        <!-- ══ 错题集 ═══════════════════════════════ -->
        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">📕 错题集</span>
            <span class="panel-sub" v-if="mistakes.length">{{ mistakes.length }} 题待清</span>
            <button v-if="mistakes.length" class="redo-btn" @click="redoMistakes">
              ⚔️ 错题重练
            </button>
          </div>
          <div v-if="mistakes.length" class="mistake-list">
            <div v-for="m in mistakes" :key="m.line_id" class="mistake-item">
              <div class="mi-top">
                <span class="mi-title">{{ m.title }} · {{ m.author }}</span>
                <span class="mi-count">错 {{ m.wrong_count }} 次</span>
              </div>
              <div class="mi-question">{{ m.question }}</div>
              <div class="mi-ans">
                <span class="mi-wrong">你的答案：{{ m.user_answer || '（未作答）' }}</span>
                <span class="mi-correct">正确：{{ m.correct_answer }}</span>
              </div>
              <div class="mi-date">最近答错：{{ m.last_wrong_at }}</div>
            </div>
          </div>
          <p v-else class="empty-tip">错题集空空如也，正是刷题的好状态 ✨</p>
        </div>

        <!-- ══ 最近闯关 ═══════════════════════════════ -->
        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">🏆 最近闯关</span>
          </div>
          <div v-if="recent.length" class="recent-list">
            <div v-for="(r, i) in recent" :key="i" class="recent-item"
              :class="{ good: r.correct === r.total }">
              <div class="ri-left">
                <span class="ri-mode">{{ modeName(r.mode) }}</span>
                <span class="ri-dynasty" v-if="r.dynasty">{{ r.dynasty }}</span>
              </div>
              <span class="ri-result">✓ {{ r.correct }} / {{ r.total }}</span>
              <span class="ri-score">{{ r.score }}分</span>
              <span class="ri-date">{{ r.created_at }}</span>
            </div>
          </div>
          <p v-else class="empty-tip">暂无闯关记录</p>
        </div>

        <!-- 底部操作 -->
        <div class="dash-actions">
          <van-button type="primary" block round @click="$router.push('/challenge')">再闯一局</van-button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { api } from '../api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const summary = ref<any>(null)
const calendar = ref<any[]>([])
const recent = ref<any[]>([])
const mistakes = ref<any[]>([])

const MODE_NAMES: Record<string, string> = {
  classic: '经典', endless: '无尽', mistake_quiz: '错题重练',
}
function modeName(m: string) { return MODE_NAMES[m] || m }

// 热力图：7 行（周一~周日）× N 列（周），补齐开头空位
const heatmapWeeks = computed(() => {
  if (!calendar.value.length) return []
  const cells = calendar.value.map(c => ({
    ...c,
    level: c.total === 0 ? 0 : c.total <= 5 ? 1 : c.total <= 12 ? 2 : c.total <= 25 ? 3 : 4,
  }))
  // 第一天对齐到周一；空位用 pad 占位对象（不渲染颜色）
  const first = new Date(cells[0].date + 'T00:00:00')
  const pad = (first.getDay() + 6) % 7   // 周日=0 → 6
  const padCells = Array.from({ length: pad }, (_, i) => ({
    date: `pad-${i}`, rounds: 0, total: 0, correct: 0, level: -1,
  }))
  const all = [...padCells, ...cells]
  const cols: any[][] = []
  for (let i = 0; i < all.length; i += 7) cols.push(all.slice(i, i + 7))
  return cols
})

function redoMistakes() {
  router.push('/challenge?mistake=1')
}

onMounted(async () => {
  const uid = (authStore.user as any)?.id
  if (!uid) {
    // 身份未就绪，稍候一次
    await new Promise(r => setTimeout(r, 1200))
  }
  const finalUid = (authStore.user as any)?.id
  if (!finalUid) {
    showToast('用户身份未就绪，请刷新重试')
    summary.value = { rounds: 0, total_questions: 0, accuracy: 0, mistakes_open: 0, best_score: 0 }
    return
  }
  try {
    const [dashRes, misRes] = await Promise.all([
      api.challengeDashboard(finalUid),
      api.challengeMistakes(finalUid),
    ])
    summary.value = dashRes.data.summary
    calendar.value = dashRes.data.calendar || []
    recent.value = dashRes.data.recent || []
    mistakes.value = misRes.data.mistakes || []
  } catch (e) {
    showToast('加载失败，请重试')
  }
})
</script>

<style scoped>
.dash-page { min-height: 100vh; padding-bottom: 40px; }

/* 统计卡 */
.dash-body { padding: 16px; }
.stat-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;
  margin-bottom: 16px;
}
.stat-card {
  background: var(--card, rgba(255,255,255,0.04));
  border: 1px solid var(--line, rgba(255,255,255,0.08));
  border-radius: 14px;
  padding: 14px 6px 12px;
  text-align: center;
}
.stat-card b {
  display: block; font-size: 22px; line-height: 1.2;
  color: var(--gold, #D4AF37);
  font-family: var(--font-display, serif);
}
.stat-card b .unit { font-style: normal; font-size: 13px; }
.stat-card span { font-size: 11px; color: var(--stone, #8a8f98); letter-spacing: 1px; }
.stat-card.alert b { color: var(--cinnabar, #e05a4e); }

/* 面板 */
.panel {
  background: var(--card, rgba(255,255,255,0.04));
  border: 1px solid var(--line, rgba(255,255,255,0.08));
  border-radius: 16px;
  padding: 14px 16px;
  margin-bottom: 14px;
}
.panel-head { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.panel-title { font-size: 15px; font-weight: 600; color: var(--ink, #eae4d5); }
.panel-sub { font-size: 11px; color: var(--stone, #8a8f98); margin-right: auto; }
.empty-tip { font-size: 12.5px; color: var(--stone, #8a8f98); text-align: center; padding: 18px 0; }

/* 热力图 */
.heatmap { overflow-x: auto; }
.hm-grid { display: flex; gap: 3px; min-width: max-content; }
.hm-col { display: flex; flex-direction: column; gap: 3px; }
.hm-cell {
  width: 12px; height: 12px; border-radius: 3px;
  background: rgba(255,255,255,0.05);
}
.hm-cell.lv1 { background: rgba(212,175,55,0.25); }
.hm-cell.lv2 { background: rgba(212,175,55,0.5); }
.hm-cell.lv3 { background: rgba(212,175,55,0.75); }
.hm-cell.lv4 { background: var(--gold, #D4AF37); }
.hm-legend {
  display: flex; align-items: center; gap: 4px;
  margin-top: 10px; font-size: 10px; color: var(--stone, #8a8f98);
  justify-content: flex-end;
}
.hm-legend .hm-cell { width: 10px; height: 10px; }

/* 错题重练按钮 */
.redo-btn {
  margin-left: auto;
  padding: 6px 14px;
  font-size: 12.5px; letter-spacing: 1px;
  color: var(--ink, #eae4d5);
  background: var(--cinnabar, #e05a4e);
  border: none; border-radius: 999px; cursor: pointer;
  transition: opacity 0.2s;
}
.redo-btn:active { opacity: 0.8; }

/* 错题列表 */
.mistake-list { display: flex; flex-direction: column; gap: 10px; }
.mistake-item {
  border: 1px solid var(--line, rgba(255,255,255,0.08));
  border-radius: 12px; padding: 10px 12px;
  background: rgba(255,255,255,0.02);
}
.mi-top { display: flex; justify-content: space-between; align-items: center; }
.mi-title { font-size: 12px; color: var(--stone, #8a8f98); }
.mi-count { font-size: 11px; color: var(--cinnabar, #e05a4e); }
.mi-question { font-size: 14.5px; color: var(--ink, #eae4d5); margin: 6px 0; line-height: 1.6; }
.mi-ans { display: flex; flex-wrap: wrap; gap: 10px; font-size: 12px; }
.mi-wrong { color: var(--cinnabar, #e05a4e); }
.mi-correct { color: var(--jade, #6fa287); }
.mi-date { margin-top: 6px; font-size: 10.5px; color: var(--stone, #8a8f98); }

/* 最近闯关 */
.recent-list { display: flex; flex-direction: column; gap: 6px; }
.recent-item {
  display: grid; grid-template-columns: 110px 1fr auto auto;
  align-items: center; gap: 10px;
  padding: 8px 12px;
  border-radius: 10px;
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--line, rgba(255,255,255,0.08));
  font-size: 12px;
}
.recent-item.good { border-color: rgba(212,175,55,0.4); }
.ri-left { display: flex; gap: 6px; align-items: center; }
.ri-mode {
  font-size: 11px; color: var(--gold, #D4AF37);
  border: 1px solid rgba(212,175,55,0.35);
  border-radius: 4px; padding: 1px 6px;
}
.ri-dynasty { color: var(--stone, #8a8f98); }
.ri-result { color: var(--ink, #eae4d5); }
.ri-score { color: var(--gold, #D4AF37); font-weight: 600; }
.ri-date { color: var(--stone, #8a8f98); font-size: 11px; }

.dash-actions { margin-top: 20px; }

/* 复用 Challenge 页的导航样式 */
.app-nav {
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
  background: rgba(20,22,27,0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(212,175,55,0.16);
}
.nav-back {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  background: none; border: none;
  color: var(--ink); font-size: 20px; cursor: pointer;
}
.nav-title { font-size: 16px; color: var(--ink); letter-spacing: 2px; }
.nav-right { width: 36px; }
.page-loading { text-align: center; padding: 80px 0; color: var(--stone); font-size: 14px; }
</style>
