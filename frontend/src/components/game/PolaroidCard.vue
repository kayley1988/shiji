<template>
  <div 
    class="polaroid-card"
    :class="[style, { 'is-loading': loading, 'has-image': hasImage }]"
    :style="frameStyle"
    @click="$emit('click', poem)"
  >
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span>生成中...</span>
    </div>

    <!-- 图片区域 -->
    <div class="polaroid-image" :class="{ 'has-image': hasImage }">
      <img 
        v-if="imageUrl" 
        :src="imageUrl" 
        :alt="poem?.title"
        @load="onImageLoad"
        @error="onImageError"
      />
      <div v-else class="placeholder-art">
        <div class="placeholder-pattern"></div>
        <div class="placeholder-text">
          <span v-for="(char, i) in placeholderChars" :key="i">{{ char }}</span>
        </div>
      </div>
    </div>

    <!-- 诗句内容 -->
    <div class="polaroid-content">
      <div class="poem-text">
        <p 
          v-for="(line, i) in poemLines" 
          :key="i"
          class="poem-line"
        >{{ line }}</p>
      </div>
      <div class="poem-meta">
        <span class="poem-title">《{{ poem?.title }}》</span>
        <span class="poem-author">{{ poem?.author || '佚名' }}</span>
      </div>
    </div>

    <!-- 底部装饰 -->
    <div class="polaroid-footer">
      <span class="footer-tag" v-if="poem?.is_rare">冷门诗句</span>
      <span class="footer-tag difficulty" v-if="poem?.difficulty">{{ difficultyText }}</span>
    </div>

    <!-- 操作按钮 -->
    <div class="polaroid-actions" v-if="showActions">
      <button class="action-btn" @click.stop="$emit('generate')" :disabled="loading">
        <van-icon name="photo-o" /> 生图
      </button>
      <button class="action-btn" @click.stop="$emit('save')">
        <van-icon name="down" /> 保存
      </button>
      <button class="action-btn" @click.stop="$emit('share')">
        <van-icon name="share" /> 分享
      </button>
    </div>

    <!-- 水印 -->
    <div class="watermark" v-if="watermark">诗语雅集</div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

interface Poem {
  id: string
  title: string
  author: string
  dynasty?: string
  content: string
  full_text?: string
  tags?: string[]
  imagery?: string[]
  is_rare?: boolean
  difficulty?: 'easy' | 'medium' | 'hard'
}

interface Props {
  poem: Poem | null
  style?: 'classic' | 'vintage' | 'ink' | 'modern'
  imageUrl?: string
  loading?: boolean
  watermark?: boolean
  showActions?: boolean
  tilt?: number
}

const props = withDefaults(defineProps<Props>(), {
  style: 'classic',
  imageUrl: '',
  loading: false,
  watermark: true,
  showActions: true,
  tilt: 0
})

const emit = defineEmits<{
  click: [poem: Poem]
  generate: []
  save: []
  share: []
}>()

const hasImage = ref(false)

// 解析诗句行
const poemLines = computed(() => {
  if (!props.poem) return []
  const content = props.poem.full_text || props.poem.content
  // 按中文句号、换行分割
  return content.split(/[，；。\n]/).filter(l => l.trim())
})

// 占位符字符
const placeholderChars = computed(() => {
  const text = props.poem?.content || '诗'
  return text.slice(0, 4).split('')
})

// 难度文本
const difficultyText = computed(() => {
  const map: Record<string, string> = {
    easy: '入门',
    medium: '进阶',
    hard: '挑战'
  }
  return map[props.poem?.difficulty || 'easy'] || '入门'
})

// 边框样式
const frameStyle = computed(() => {
  const base = {}
  
  if (props.style === 'vintage') {
    return {
      '--frame-bg': '#e8dcc8',
      '--frame-shadow': '0 4px 20px rgba(0,0,0,0.2)',
      '--border-radius': '2px',
      transform: `rotate(${props.tilt || -2}deg)`
    }
  }
  
  if (props.style === 'ink') {
    return {
      '--frame-bg': '#f8f4e8',
      '--frame-shadow': 'none',
      '--border-radius': '0',
      '--border-width': '20px',
      '--border-style': 'double',
      transform: 'rotate(0deg)'
    }
  }
  
  if (props.style === 'modern') {
    return {
      '--frame-bg': '#ffffff',
      '--frame-shadow': '0 8px 30px rgba(0,0,0,0.12)',
      '--border-radius': '4px',
      transform: 'rotate(0deg)'
    }
  }
  
  // classic
  return {
    '--frame-bg': '#f5f5f5',
    '--frame-shadow': '0 4px 15px rgba(0,0,0,0.15)',
    '--border-radius': '1px',
    transform: `rotate(${props.tilt || 0}deg)`
  }
})

function onImageLoad() {
  hasImage.value = true
}

function onImageError() {
  hasImage.value = false
}
</script>

<style scoped>
.polaroid-card {
  position: relative;
  background: var(--frame-bg, #f5f5f5);
  border-radius: var(--border-radius, 2px);
  box-shadow: var(--frame-shadow, 0 4px 15px rgba(0,0,0,0.15));
  padding: var(--border-width, 12px);
  padding-bottom: 50px;
  max-width: 320px;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden;
}

.polaroid-card:hover {
  transform: scale(1.02) rotate(0deg) !important;
  box-shadow: 0 8px 30px rgba(0,0,0,0.2);
}

.polaroid-card.ink {
  border: var(--border-width, 20px) solid transparent;
  background-image: 
    linear-gradient(var(--frame-bg, #f8f4e8), var(--frame-bg, #f8f4e8)),
    linear-gradient(45deg, #8b7355 25%, transparent 25%, transparent 75%, #8b7355 75%);
  background-size: 100% 100%, 20px 20px;
  background-position: 0 0, 0 0;
  padding: 10px;
}

.polaroid-image {
  width: 100%;
  aspect-ratio: 1;
  background: #f0f0f0;
  overflow: hidden;
  position: relative;
}

.polaroid-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s ease;
}

.placeholder-art {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f5f0 0%, #e8e4dc 100%);
  position: relative;
  overflow: hidden;
}

.placeholder-pattern {
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(circle at 25% 25%, rgba(139,115,85,0.1) 2px, transparent 2px),
    radial-gradient(circle at 75% 75%, rgba(139,115,85,0.1) 2px, transparent 2px);
  background-size: 20px 20px;
}

.placeholder-text {
  position: relative;
  display: flex;
  gap: 8px;
  font-size: 24px;
  color: #8b7355;
  font-weight: 600;
  letter-spacing: 4px;
  opacity: 0.6;
}

.polaroid-content {
  padding: 16px 8px 8px;
  text-align: center;
}

.poem-text {
  margin-bottom: 12px;
}

.poem-line {
  margin: 0;
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  font-family: 'STKaiti', 'KaiTi', serif;
}

.poem-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.poem-title {
  font-size: 14px;
  color: #666;
}

.poem-author {
  font-size: 12px;
  color: #999;
}

.polaroid-footer {
  position: absolute;
  bottom: 12px;
  left: 12px;
  right: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.footer-tag {
  font-size: 10px;
  padding: 2px 8px;
  background: rgba(139, 115, 85, 0.1);
  color: #8b7355;
  border-radius: 10px;
}

.footer-tag.difficulty {
  background: rgba(200, 80, 80, 0.1);
  color: #c85050;
}

.polaroid-actions {
  position: absolute;
  bottom: 8px;
  right: 8px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.polaroid-card:hover .polaroid-actions {
  opacity: 1;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 4px 8px;
  font-size: 11px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #f5f5f5;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.watermark {
  position: absolute;
  bottom: 60px;
  right: 10px;
  font-size: 10px;
  color: rgba(0,0,0,0.15);
  transform: rotate(-5deg);
  pointer-events: none;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255,255,255,0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  z-index: 10;
}

.loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #e8e4dc;
  border-top-color: #8b7355;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-overlay span {
  font-size: 12px;
  color: #8b7355;
}
</style>
