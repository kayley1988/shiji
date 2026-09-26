<template>
  <div class="ambient-page" :class="themeClass">
    <!-- 顶部导航 -->
    <div class="zen-header">
      <van-icon name="arrow-left" class="back-btn" @click="$router.back()" />
      <span class="zen-title">静心诗境</span>
      <span class="zen-sub">{{ solarTerm }}</span>
    </div>

    <!-- 加载态 -->
    <div v-if="loading" class="zen-loading">
      <div class="breathing-circle"></div>
      <p class="breathing-text">静下来，诗在等你</p>
    </div>

    <!-- 诗境主体 -->
    <div v-else-if="poem" class="zen-body">
      <!-- 诗意引导语 -->
      <div class="zen-intro">
        <p>{{ poem.intro }}</p>
      </div>

      <!-- 诗句展示 -->
      <div class="zen-lines">
        <div
          v-for="(line, idx) in poem.lines"
          :key="idx"
          class="zen-line"
          :class="{ dim: idx >= visibleCount }"
          @click="toggleLine(idx)"
        >
          {{ line }}
        </div>
      </div>

      <!-- 显示更多按钮 -->
      <div v-if="poem.lines.length > 4 && visibleCount < poem.lines.length" class="zen-more" @click="showAll">
        <van-icon name="expand" />
        <span>展开全文</span>
      </div>
      <div v-else-if="visibleCount >= 4" class="zen-more" @click="collapse">
        <van-icon name="shrink" />
        <span>收起</span>
      </div>

      <!-- 诗作信息 -->
      <div class="zen-meta">
        <span class="zen-author">《{{ poem.title }}》</span>
        <span class="zen-dynasty">{{ poem.dynasty }} · {{ poem.author }}</span>
      </div>

      <!-- 操作区 -->
      <div class="zen-actions">
        <div class="zen-btn" @click="speakLines">
          <span class="zen-btn-icon">🔊</span>
          <span>静听</span>
        </div>
        <div class="zen-btn" @click="refresh">
          <span class="zen-btn-icon">🔄</span>
          <span>换一首</span>
        </div>
        <div class="zen-btn" @click="showFortune = true">
          <span class="zen-btn-icon">🎋</span>
          <span>求签</span>
        </div>
      </div>
    </div>

    <!-- 诗签筒弹窗 -->
    <FortuneDraw v-if="showFortune" v-model="showFortune" />

    <!-- 朗读组件（隐藏） -->
    <div ref="speechTarget" style="display:none"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useTheme } from '../composables/useTheme'
import { useSpeech } from '../composables/useSpeech'
import FortuneDraw from './FortuneDraw.vue'

const { currentTheme } = useTheme()
const { speak } = useSpeech()

const themeClass = computed(() => `theme-${currentTheme.value}`)

const loading = ref(true)
const poem = ref<any>(null)
const solarTerm = ref('')
const visibleCount = ref(4)
const showFortune = ref(false)

async function fetchPoem() {
  loading.value = true
  try {
    const res = await api.getAmbientPoem()
    poem.value = res.data
    solarTerm.value = poem.value.solar_term ? `· ${poem.value.solar_term}` : ''
    visibleCount.value = 4
  } catch (e) {
    console.error('静心诗境加载失败', e)
  } finally {
    loading.value = false
  }
}

function toggleLine(idx: number) {
  if (idx < visibleCount.value) return
  visibleCount.value = idx + 1
}

function showAll() {
  visibleCount.value = poem.value.lines.length
}

function collapse() {
  visibleCount.value = 4
}

async function speakLines() {
  if (!poem.value) return
  const text = poem.value.lines.join('，')
  speak(text)
}

function refresh() {
  fetchPoem()
}

onMounted(fetchPoem)
</script>

<style scoped>
.ambient-page {
  min-height: 100vh;
  padding: 0 0 40px;
  background: linear-gradient(180deg, var(--parchment) 0%, var(--parchment-deep) 100%);
}

.zen-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px 12px;
  border-bottom: 1px solid var(--ink-light);
}
.back-btn {
  font-size: 22px;
  cursor: pointer;
  color: var(--ink);
}
.zen-title {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--ink);
}
.zen-sub {
  font-size: 13px;
  color: var(--ink-light);
  margin-left: auto;
}

/* 呼吸加载 */
.zen-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  gap: 24px;
}
.breathing-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: radial-gradient(circle, var(--jade-light), transparent);
  animation: breathe 3s ease-in-out infinite;
}
@keyframes breathe {
  0%, 100% { transform: scale(0.8); opacity: 0.4; }
  50% { transform: scale(1.2); opacity: 0.9; }
}
.breathing-text {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--ink-light);
  animation: breathe 3s ease-in-out infinite;
}

/* 诗境主体 */
.zen-body {
  padding: 32px 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 28px;
}

.zen-intro {
  background: rgba(196,168,130,0.08);
  border-left: 3px solid var(--gold);
  border-radius: 0 8px 8px 0;
  padding: 14px 18px;
  width: 100%;
  font-size: 15px;
  color: var(--ink-light);
  line-height: 1.8;
  font-family: var(--font-display);
}

.zen-lines {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
}

.zen-line {
  font-family: var(--font-display);
  font-size: 22px;
  color: var(--ink);
  letter-spacing: 2px;
  cursor: pointer;
  transition: opacity 0.3s, color 0.3s;
  padding: 4px 0;
  text-align: center;
}
.zen-line.dim {
  color: var(--ink-faint);
  font-size: 18px;
}
.zen-line:hover {
  color: var(--cinnabar);
}

.zen-more {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--ink-light);
  cursor: pointer;
  padding: 8px;
}

.zen-meta {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
}
.zen-author {
  font-family: var(--font-display);
  font-size: 15px;
  color: var(--ink);
}
.zen-dynasty {
  font-size: 13px;
  color: var(--ink-light);
}

/* 操作区 */
.zen-actions {
  display: flex;
  gap: 20px;
  margin-top: 12px;
}
.zen-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 12px 16px;
  border-radius: 12px;
  background: var(--card-bg);
  border: 1px solid var(--ink-faint);
  min-width: 72px;
  transition: transform 0.2s;
}
.zen-btn:hover { transform: translateY(-2px); }
.zen-btn:active { transform: scale(0.95); }
.zen-btn-icon { font-size: 22px; }
.zen-btn span:last-child {
  font-size: 12px;
  color: var(--ink-light);
}
</style>
