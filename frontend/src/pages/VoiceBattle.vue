<template>
  <div class="voice-battle-container">
    <VoiceBattle :initial-mode="initialMode" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import VoiceBattle from '../components/game/VoiceBattle.vue'

const route = useRoute()

// 支持三种模式: keyword(飞花令), quote(接句), tail(接尾)
const initialMode = computed(() => {
  const mode = route.query.mode as string
  if (mode === 'keyword' || mode === 'quote' || mode === 'tail') {
    return mode
  }
  return 'keyword'
})
</script>

<style scoped>
.voice-battle-container {
  min-height: 100vh;
  background: #1a1a2e;
}
</style>
