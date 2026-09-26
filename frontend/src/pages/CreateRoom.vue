<template>
  <div class="create-room bg-xuanzhi">

    <main class="form-content">

      <!-- 模式选择 -->
      <section class="section-card animate-fadeUp">
        <div class="card-section-label">
          <span class="section-dot"></span>
          游戏模式
        </div>
        <div class="mode-selector">
          <div
            class="mode-option"
            :class="{ active: form.mode === 'CLASSIC' }"
            @click="form.mode = 'CLASSIC'"
          >
            <div class="mode-opt-icon" style="color: var(--cinnabar)">
              <svg width="24" height="24" viewBox="0 0 48 48" fill="none">
                <circle cx="24" cy="24" r="20" stroke="currentColor" stroke-width="2" stroke-dasharray="4 3"/>
                <text x="50%" y="55%" text-anchor="middle" dominant-baseline="middle" font-size="14" font-family="serif">月</text>
              </svg>
            </div>
            <div class="mode-opt-info">
              <div class="mode-opt-name">经典飞花令</div>
              <div class="mode-opt-desc">自选关键字</div>
            </div>
            <div class="mode-opt-check" v-if="form.mode === 'CLASSIC'">
              <van-icon name="checked" />
            </div>
          </div>

          <div
            class="mode-option"
            :class="{ active: form.mode === 'SOLAR_TERM_ELEMENT' }"
            @click="form.mode = 'SOLAR_TERM_ELEMENT'"
          >
            <div class="mode-opt-icon" style="color: var(--jade)">
              <svg width="24" height="24" viewBox="0 0 48 48" fill="none">
                <circle cx="24" cy="24" r="20" stroke="currentColor" stroke-width="2"/>
                <path d="M24 10L24 38M10 24L38 24M14 14L34 34M34 14L14 34" stroke="currentColor" stroke-width="1.5"/>
                <circle cx="24" cy="24" r="4" fill="currentColor"/>
              </svg>
            </div>
            <div class="mode-opt-info">
              <div class="mode-opt-name">节气五行</div>
              <div class="mode-opt-desc">五行加成翻倍</div>
            </div>
            <div class="mode-opt-check" v-if="form.mode === 'SOLAR_TERM_ELEMENT'">
              <van-icon name="checked" />
            </div>
          </div>
        </div>
      </section>

      <!-- 关键词选择 -->
      <section class="section-card animate-fadeUp delay-1">
        <div class="card-section-label">
          <span class="section-dot"></span>
          飞花关键字
          <span class="label-hint">（选1-3个）</span>
        </div>
        <div class="keyword-grid">
          <div
            v-for="kw in availableKeywords"
            :key="kw"
            class="kw-option"
            :class="{ selected: form.keywords.includes(kw) }"
            @click="toggleKeyword(kw)"
          >
            {{ kw }}
          </div>
        </div>
        <div class="tip" v-if="form.mode === 'SOLAR_TERM_ELEMENT'">
          节气五行模式中，命中五行对应关键字得双倍积分
        </div>
      </section>

      <!-- 时间与人数 -->
      <section class="section-card animate-fadeUp delay-2">
        <div class="card-section-label">
          <span class="section-dot"></span>
          房间配置
        </div>

        <div class="config-row">
          <div class="config-label">回合时限</div>
          <div class="config-options">
            <div
              v-for="t in [10, 15, 20]"
              :key="t"
              class="config-opt"
              :class="{ active: form.timeLimit === String(t) }"
              @click="form.timeLimit = String(t)"
            >
              {{ t }}秒
            </div>
          </div>
        </div>

        <div class="config-row">
          <div class="config-label">房间人数</div>
          <div class="stepper-wrap">
            <button class="stepper-btn" @click="form.maxPlayers = Math.max(2, form.maxPlayers - 1)">
              <van-icon name="minus" />
            </button>
            <span class="stepper-val">{{ form.maxPlayers }}</span>
            <button class="stepper-btn" @click="form.maxPlayers = Math.min(8, form.maxPlayers + 1)">
              <van-icon name="plus" />
            </button>
          </div>
        </div>
      </section>

    </main>

    <!-- 底部按钮 -->
    <div class="bottom-action">
      <van-button
        class="btn-create"
        block
        round
        size="large"
        :loading="loading"
        @click="createRoom"
      >
        开席雅集
      </van-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, Toast } from 'vant'
import { useRoomStore } from '../stores/room'
import { api } from '../api'

const router = useRouter()
const roomStore = useRoomStore()
const loading = ref(false)
const availableKeywords = ref<string[]>([])

const form = reactive({
  mode: 'SOLAR_TERM_ELEMENT',
  keywords: ['春'],
  timeLimit: '15',
  maxPlayers: 4
})

onMounted(async () => {
  try {
    const res = await api.getDailyTheme()
    availableKeywords.value = res.data?.data?.keywords || ['春', '风', '月', '花', '雨']
    form.keywords = [availableKeywords.value[0]]
  } catch {
    availableKeywords.value = ['春', '风', '月', '花', '雨', '雪', '秋', '冬']
  }
})

function toggleKeyword(kw: string) {
  const idx = form.keywords.indexOf(kw)
  if (idx >= 0) {
    if (form.keywords.length > 1) form.keywords.splice(idx, 1)
  } else {
    if (form.keywords.length < 3) form.keywords.push(kw)
    else showToast('最多选3个关键字')
  }
}

async function createRoom() {
  if (form.keywords.length === 0) {
    showToast('请选择关键字')
    return
  }
  loading.value = true
  try {
    const room = await roomStore.createRoom({
      mode: form.mode,
      keywords: form.keywords,
      time_limit_sec: parseInt(form.timeLimit),
      max_players: form.maxPlayers
    })
    Toast.loading.hide()
    router.replace(`/room/${room.room_id}`)
  } catch (e: any) {
    loading.value = false
    showToast(e?.response?.data?.error?.message || '创建失败')
  }
}
</script>

<style scoped>
.create-room {
  min-height: 100vh;
  padding-bottom: 100px;
}

/* ── 导航 ── */
.nav-header {
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
  background: rgba(250,246,240,0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(158,142,126,0.15);
}
.nav-btn {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  background: none; border: none;
  color: var(--ink); font-size: 20px; cursor: pointer;
  border-radius: var(--radius-sm);
}
.nav-title {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--ink);
}

/* ── 表单 ── */
.form-content { padding: 16px; }
.section-card {
  background: var(--card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  padding: 20px;
  margin-bottom: 14px;
}

.card-section-label {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 500;
  color: var(--ink);
  margin-bottom: 16px;
}
.section-dot {
  width: 6px; height: 6px;
  background: var(--cinnabar);
  border-radius: 50%;
  flex-shrink: 0;
}
.label-hint { font-size: 12px; color: var(--stone); font-weight: 400; }

/* ── 模式选择 ── */
.mode-selector { display: flex; flex-direction: column; gap: 10px; }
.mode-option {
  display: flex; align-items: center; gap: 14px;
  padding: 14px;
  border: 1.5px solid var(--parchment-dark);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}
.mode-option.active {
  border-color: var(--cinnabar);
  background: rgba(212,175,55,0.04);
}
.mode-opt-icon { flex-shrink: 0; }
.mode-opt-info { flex: 1; }
.mode-opt-name { font-size: 15px; font-weight: 500; color: var(--ink); }
.mode-opt-desc { font-size: 12px; color: var(--stone); margin-top: 2px; }
.mode-opt-check { color: var(--cinnabar); font-size: 18px; }

/* ── 关键词 ── */
.keyword-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}
.kw-option {
  aspect-ratio: 1;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display);
  font-size: 20px;
  color: var(--stone);
  background: var(--parchment-dark);
  border-radius: var(--radius-md);
  border: 1.5px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}
.kw-option.selected {
  background: linear-gradient(135deg, var(--cinnabar), var(--cinnabar-light));
  color: #fff;
  border-color: var(--cinnabar);
  box-shadow: 0 2px 10px rgba(212,175,55,0.3);
}

.tip {
  font-size: 12px;
  color: var(--stone);
  margin-top: 12px;
  padding: 8px 12px;
  background: rgba(61,107,74,0.06);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--jade);
}

/* ── 配置 ── */
.config-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid rgba(158,142,126,0.1);
}
.config-row:last-child { border-bottom: none; }
.config-label { font-size: 14px; color: var(--ink); }
.config-options { display: flex; gap: 8px; }
.config-opt {
  padding: 6px 14px;
  background: var(--parchment-dark);
  color: var(--stone);
  border-radius: var(--radius-full);
  font-size: 13px;
  cursor: pointer;
  border: 1.5px solid transparent;
  transition: all 0.2s;
}
.config-opt.active {
  background: rgba(212,175,55,0.1);
  color: var(--cinnabar);
  border-color: var(--cinnabar);
}

.stepper-wrap { display: flex; align-items: center; gap: 12px; }
.stepper-btn {
  width: 32px; height: 32px;
  background: var(--parchment-dark);
  border: none;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: var(--ink); cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}
.stepper-btn:hover { background: var(--stone-light); }
.stepper-val {
  font-family: var(--font-sans);
  font-size: 20px;
  font-weight: 700;
  color: var(--ink);
  min-width: 24px;
  text-align: center;
}

/* ── 底部按钮 ── */
.bottom-action {
  position: fixed; bottom: 0; left: 0; right: 0;
  padding: 12px 20px 24px;
  background: linear-gradient(transparent, var(--parchment) 30%);
}
.btn-create {
  height: 52px;
  background: linear-gradient(135deg, var(--cinnabar), var(--cinnabar-light)) !important;
  border: none !important;
  color: #fff !important;
  font-family: var(--font-display) !important;
  font-size: 18px !important;
  box-shadow: 0 4px 20px rgba(212,175,55,0.35) !important;
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
