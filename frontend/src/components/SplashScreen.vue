<template>
  <Transition name="splash-fade" @after-leave="$emit('done')">
    <div v-if="visible" class="splash bg-xuanzhi">
      <!-- 背景水墨晕染 -->
      <div class="ink-bg">
        <div class="ink-blob b1"></div>
        <div class="ink-blob b2"></div>
        <div class="ink-blob b3"></div>
      </div>

      <!-- 主标题 -->
      <div class="splash-main">
        <div class="splash-emblem">诗</div>
        <h1 class="splash-title">诗语雅集</h1>
        <p class="splash-subtitle">以诗会友 · 飞花行令</p>
      </div>

      <!-- 加载步骤（纯前端动画，不等后端） -->
      <div class="splash-loading">
        <div class="loading-track">
          <div class="loading-fill" :style="{ width: fillPercent + '%' }"></div>
        </div>
        <div class="loading-step">{{ loadingStore.step }}</div>
        <div class="loading-dots">
          <span v-for="n in 3" :key="n" class="dot" :class="{ active: dotIndex >= n }"></span>
        </div>
      </div>

      <!-- 底部诗词 -->
      <div class="splash-quote">
        <p>「人生得意须尽欢，莫使金樽空对月」</p>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useLoadingStore } from '../stores/loading'

const emit = defineEmits<{ done: [] }>()
const loadingStore = useLoadingStore()
const visible = ref(true)

// dotIndex: 0→1→2→3 跟随 step 变化
const STEPS = ['载入诗词库', '连接雅集', '准备就绪']
const dotIndex = computed(() => {
  const idx = STEPS.indexOf(loadingStore.step)
  return idx >= 0 ? idx + 1 : 0
})
const fillPercent = computed(() => dotIndex.value / 3 * 100)
</script>

<style scoped>
.splash {
  position: fixed; inset: 0; z-index: 9999;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  overflow: hidden;
}

/* 水墨晕染背景 */
.ink-bg { position: absolute; inset: 0; overflow: hidden; }
.ink-blob {
  position: absolute; border-radius: 50%;
  filter: blur(60px); opacity: 0.08;
  animation: drift 8s ease-in-out infinite;
}
.b1 { width: 400px; height: 400px; background: var(--cinnabar); top: -100px; right: -80px; animation-delay: 0s; }
.b2 { width: 300px; height: 300px; background: var(--jade); bottom: -60px; left: -60px; animation-delay: 3s; }
.b3 { width: 250px; height: 250px; background: var(--gold); top: 50%; left: 50%; transform: translate(-50%,-50%); animation-delay: 6s; }
@keyframes drift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(20px, -20px) scale(1.05); }
  66% { transform: translate(-15px, 15px) scale(0.95); }
}

/* 主标题 */
.splash-main { text-align: center; z-index: 1; }
.splash-emblem {
  width: 72px; height: 72px;
  margin: 0 auto 16px;
  background: var(--cinnabar);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display);
  font-size: 36px; color: #fff;
  box-shadow: 0 8px 32px rgba(61,122,138,0.35);
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 8px 32px rgba(61,122,138,0.35); }
  50% { box-shadow: 0 8px 48px rgba(61,122,138,0.55); }
}
.splash-title {
  font-family: var(--font-display);
  font-size: 40px; color: var(--ink);
  margin-bottom: 8px; letter-spacing: 6px;
}
.splash-subtitle {
  font-family: var(--font-serif);
  font-size: 14px; color: var(--stone); letter-spacing: 4px;
}

/* 加载 */
.splash-loading {
  position: absolute; bottom: 120px;
  width: 200px; text-align: center; z-index: 1;
}
.loading-track {
  height: 3px; background: var(--stone-light);
  border-radius: 2px; overflow: hidden; margin-bottom: 10px;
}
.loading-fill {
  height: 100%; background: var(--cinnabar);
  border-radius: 2px;
  transition: width 0.6s var(--ease-out);
}
.loading-step {
  font-size: 12px; color: var(--stone);
  letter-spacing: 2px; margin-bottom: 12px;
}
.loading-dots { display: flex; justify-content: center; gap: 6px; }
.dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--stone-light);
  transition: background 0.3s;
}
.dot.active { background: var(--cinnabar); }

/* 底部诗词 */
.splash-quote {
  position: absolute; bottom: 40px;
  font-family: var(--font-serif); font-size: 13px;
  color: var(--stone-light); letter-spacing: 1px;
}

/* 过渡 */
.splash-fade-leave-active { transition: opacity 0.8s ease; }
.splash-fade-leave-to { opacity: 0; }
</style>
