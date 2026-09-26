import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLoadingStore = defineStore('loading', () => {
  const phase = ref<'idle' | 'init' | 'done'>('idle')
  const step = ref('')
  const ALL_STEPS = ['载入诗词库', '连接雅集', '准备就绪']

  async function start() {
    if (phase.value !== 'idle') return
    phase.value = 'init'

    // 每个步骤走一遍动画，总共约 2.1s（纯前端，无需等待后端）
    for (let i = 0; i < ALL_STEPS.length; i++) {
      step.value = ALL_STEPS[i]
      await sleep(700)
    }
    phase.value = 'done'
  }

  function sleep(ms: number) {
    return new Promise<void>(resolve => setTimeout(resolve, ms))
  }

  return { phase, step, start }
})
