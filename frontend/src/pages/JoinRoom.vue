<template>
  <div class="join-room bg-xuanzhi">

    <!-- 邀请码输入 -->
    <main class="join-content animate-fadeUp">
      <div class="join-card">
        <div class="card-eyebrow">输入邀请码</div>
        <h2 class="card-title">入席雅集</h2>

        <div class="code-input-wrap">
          <van-field
            v-model="code"
            placeholder="请输入6位邀请码"
            maxlength="6"
            class="code-field"
            @input="code = code.toUpperCase()"
          />
        </div>

        <div class="code-hint">邀请码格式：6位大写字母</div>

        <van-button
          class="btn-join"
          block
          round
          size="large"
          :loading="loading"
          :disabled="code.length !== 6"
          @click="joinRoom"
        >
          入席
        </van-button>
      </div>

      <!-- 装饰 -->
      <div class="decor-poem">
        <p>「飞流直下三千尺，疑是银河落九天」</p>
        <p>—— 李白《望庐山瀑布》</p>
      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, Toast } from 'vant'
import { useRoomStore } from '../stores/room'
import { api } from '../api'

const router = useRouter()
const roomStore = useRoomStore()
const code = ref('')
const loading = ref(false)

async function joinRoom() {
  if (code.value.length !== 6) {
    showToast('请输入6位邀请码')
    return
  }

  loading.value = true
  try {
    const lookup = await api.getRoomByCode(code.value)
    const roomId = lookup.data?.room_id
    if (!roomId) {
      showToast('房间不存在')
      loading.value = false
      return
    }
    await roomStore.joinRoom(roomId, code.value)
    router.replace(`/room/${roomId}`)
  } catch (e: any) {
    loading.value = false
    showToast(e?.response?.data?.error?.message || '加入失败')
  }
}
</script>

<style scoped>
.join-room {
  min-height: 100vh;
  padding-bottom: 40px;
}

.join-content {
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

.join-card {
  width: 100%;
  background: var(--card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: 28px 24px;
  position: relative;
  overflow: hidden;
}
.join-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--cinnabar), var(--gold));
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
  margin-bottom: 28px;
}

.code-input-wrap {
  margin-bottom: 8px;
}
.code-field {
  text-align: center;
  font-family: var(--font-sans);
  font-size: 28px !important;
  letter-spacing: 8px;
  font-weight: 700;
  background: var(--parchment-dark) !important;
  border: 1.5px solid var(--stone-light) !important;
  border-radius: var(--radius-md) !important;
  padding: 16px !important;
  --van-field-input-text-color: var(--ink);
}
.code-hint {
  text-align: center;
  font-size: 12px;
  color: var(--stone);
  margin-bottom: 24px;
}

.btn-join {
  height: 52px;
  background: linear-gradient(135deg, var(--cinnabar), var(--cinnabar-light)) !important;
  border: none !important;
  color: #fff !important;
  font-family: var(--font-display) !important;
  font-size: 18px !important;
  box-shadow: 0 4px 20px rgba(212,175,55,0.3) !important;
}
.btn-join:disabled {
  background: var(--stone-light) !important;
  box-shadow: none !important;
}

.decor-poem {
  text-align: center;
  padding: 16px 24px;
  background: linear-gradient(135deg, rgba(184,148,46,0.06), rgba(184,148,46,0.02));
  border: 1px solid rgba(184,148,46,0.12);
  border-radius: var(--radius-md);
  max-width: 320px;
}
.decor-poem p:first-child {
  font-family: var(--font-serif);
  font-size: 14px;
  color: var(--ink);
  line-height: 1.8;
  margin-bottom: 6px;
}
.decor-poem p:last-child {
  font-size: 12px;
  color: var(--stone);
}

/* ── 动画 ── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fadeUp { animation: fadeUp 0.5s var(--ease-out) both; }
</style>
