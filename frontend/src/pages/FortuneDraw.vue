<template>
  <van-popup
    v-model="show"
    position="bottom"
    round
    :style="{ maxHeight: '88vh', borderRadius: '20px 20px 0 0' }"
    closeable
    close-icon-position="top-right"
  >
    <div class="fortune-wrap">
      <div class="fortune-title">🎋 诗签筒</div>
      <p class="fortune-hint">选择你此刻的心情，让诗为你指引</p>

      <!-- 心情选择 -->
      <div class="mood-grid">
        <div
          v-for="m in moods"
          :key="m.value"
          class="mood-item"
          :class="{ active: selectedMood === m.value }"
          @click="selectedMood = m.value"
        >
          <span class="mood-emoji">{{ m.emoji }}</span>
          <span class="mood-label">{{ m.label }}</span>
        </div>
      </div>

      <!-- 签文 -->
      <Transition name="fortune-flip" mode="out-in">
        <div v-if="fortune" key="result" class="fortune-result">
          <div class="fortune-slip">
            <div class="slip-mood">{{ fortune.mood }}</div>
            <div class="slip-divider">❀</div>
            <div class="slip-line">「{{ fortune.line }}」</div>
            <div class="slip-meta">
              出自《{{ fortune.title }}》
              <span class="slip-author">{{ fortune.dynasty }} · {{ fortune.author }}</span>
            </div>
          </div>
          <div class="fortune-actions">
            <div class="fortune-btn" @click="doSpeak">
              <span>🔊</span><span>朗读</span>
            </div>
            <div class="fortune-btn" @click="doCopy">
              <span>📋</span><span>复制</span>
            </div>
            <div class="fortune-btn primary" @click="doRedraw">
              <span>🔄</span><span>再求一支</span>
            </div>
          </div>
        </div>

        <div v-else-if="loading" key="loading" class="fortune-prompt">
          <div class="shake-icon shaking">🎋</div>
          <p>诗签摇动中...</p>
        </div>

        <div v-else key="prompt" class="fortune-prompt">
          <div class="shake-icon" :class="{ shaking: !!selectedMood }">🎋</div>
          <p>选择心情，点按钮求签</p>
          <van-button
            :loading="loading"
            :disabled="!selectedMood"
            round
            block
            class="draw-btn"
            @click="doDraw"
          >{{ selectedMood ? '摇签求诗' : '先选心情' }}</van-button>
        </div>
      </Transition>

      <p v-if="fortune" class="fortune-tip">诗无言，吉凶在心。心诚则灵。</p>
    </div>
  </van-popup>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { showToast } from 'vant'
import { api } from '../api'
import { useSpeech } from '../composables/useSpeech'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [boolean] }>()

const show = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const { speak } = useSpeech()

const moods = [
  { value: '欢喜', label: '欢欣', emoji: '🌸' },
  { value: '忧愁', label: '忧愁', emoji: '🌧️' },
  { value: '平静', label: '平静', emoji: '🍃' },
  { value: '迷茫', label: '迷茫', emoji: '🌫️' },
  { value: '其他', label: '随缘', emoji: '✨' },
]

const selectedMood = ref('平静')
const fortune = ref<any>(null)
const loading = ref(false)

async function doDraw() {
  loading.value = true
  try {
    const res = await api.getFortune(selectedMood.value)
    fortune.value = res.data.data
  } catch {
    showToast('求签失败，请重试')
  } finally {
    loading.value = false
  }
}

function doRedraw() {
  fortune.value = null
  setTimeout(() => doDraw(), 100)
}

function doSpeak() {
  if (!fortune.value) return
  speak(`「${fortune.value.line}」——出自《${fortune.value.title}》，${fortune.value.author}。`)
}

function doCopy() {
  if (!fortune.value) return
  navigator.clipboard.writeText(
    `「${fortune.value.line}」—— ${fortune.value.author}《${fortune.value.title}》`
  ).then(() => showToast('已复制'))
}
</script>

<style scoped>
.fortune-wrap {
  padding: 20px 20px 36px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  background: var(--parchment);
}

.fortune-title {
  font-family: var(--font-display);
  font-size: 22px;
  color: var(--ink);
}
.fortune-hint {
  font-size: 13px;
  color: var(--ink-light);
  margin-top: -12px;
}

.mood-grid {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}
.mood-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 14px;
  border-radius: 12px;
  background: var(--card-bg);
  border: 1px solid var(--ink-faint);
  cursor: pointer;
  transition: all 0.2s;
}
.mood-item.active {
  border-color: var(--cinnabar);
  background: rgba(180, 60, 50, 0.08);
}
.mood-emoji { font-size: 24px; }
.mood-label { font-size: 12px; color: var(--ink-light); }

.fortune-result {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}
.fortune-slip {
  background: linear-gradient(135deg, var(--parchment-deep), var(--parchment));
  border: 1px solid var(--gold);
  border-radius: 12px;
  padding: 28px 24px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  box-shadow: 0 4px 20px rgba(139, 90, 43, 0.12);
}
.slip-mood { font-size: 13px; color: var(--cinnabar); letter-spacing: 2px; }
.slip-divider { color: var(--gold); font-size: 16px; }
.slip-line {
  font-family: var(--font-display);
  font-size: 20px;
  color: var(--ink);
  text-align: center;
  letter-spacing: 1px;
  line-height: 1.6;
}
.slip-meta {
  font-size: 12px;
  color: var(--ink-light);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.slip-author { font-size: 11px; }

.fortune-actions { display: flex; gap: 12px; width: 100%; }
.fortune-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px;
  border-radius: 10px;
  background: var(--card-bg);
  border: 1px solid var(--ink-faint);
  cursor: pointer;
  font-size: 12px;
  color: var(--ink-light);
  transition: transform 0.2s;
}
.fortune-btn span:first-child { font-size: 20px; }
.fortune-btn:hover { transform: translateY(-2px); }
.fortune-btn:active { transform: scale(0.95); }
.fortune-btn.primary {
  background: var(--cinnabar);
  border-color: var(--cinnabar);
  color: #fff;
}

.fortune-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 24px 0;
  color: var(--ink-light);
  font-size: 14px;
}
.shake-icon { font-size: 48px; }
.shake-icon.shaking { animation: shake 0.6s ease-in-out infinite; }
@keyframes shake {
  0%, 100% { transform: rotate(-8deg); }
  50% { transform: rotate(8deg); }
}

.draw-btn {
  background: var(--cinnabar) !important;
  color: #fff !important;
  border: none !important;
  font-family: var(--font-display);
}

.fortune-tip {
  font-size: 12px;
  color: var(--ink-faint);
  text-align: center;
}

.fortune-flip-enter-active, .fortune-flip-leave-active { transition: all 0.3s ease; }
.fortune-flip-enter-from { opacity: 0; transform: translateY(10px); }
.fortune-flip-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
