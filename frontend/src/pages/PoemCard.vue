<template>
  <div class="poem-card-page">
    <!-- 顶部导航 -->
    <header class="page-header">
      <van-icon name="arrow-left" @click="$router.back()" />
      <span class="header-title">诗句详情</span>
      <van-icon name="ellipsis" @click="showMore = true" />
    </header>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <van-loading type="spinner" size="48px">加载中...</van-loading>
    </div>

    <template v-else-if="poem">
      <!-- 拍立得卡片展示 -->
      <div class="card-container">
        <PolaroidCard
          :poem="poem"
          :style="selectedStyle"
          :image-url="generatedImage"
          :loading="isGenerating"
          watermark
          show-actions
          @generate="showGenerateModal = true"
          @save="saveCard"
          @share="shareCard"
        />
      </div>

      <!-- 诗句信息 -->
      <section class="poem-info">
        <h2 class="poem-title">{{ poem.title }}</h2>
        <p class="poem-author">{{ poem.author }} · {{ poem.dynasty }}</p>
        
        <div class="poem-content">
          <p v-for="(line, i) in poemLines" :key="i">{{ line }}</p>
        </div>

        <!-- 标签 -->
        <div class="tags-row">
          <van-tag v-for="tag in poem.tags" :key="tag" type="primary" plain>
            {{ tag }}
          </van-tag>
        </div>

        <!-- 意象 -->
        <div class="imagery-section" v-if="poem.imagery?.length">
          <h3>诗词意象</h3>
          <div class="imagery-list">
            <span 
              v-for="img in poem.imagery" 
              :key="img"
              class="imagery-item"
            >{{ img }}</span>
          </div>
        </div>
      </section>

      <!-- 赏析 -->
      <section class="appreciation-section" v-if="explanation">
        <h3>诗词赏析</h3>
        <div class="appreciation-content">
          <p>{{ explanation }}</p>
        </div>
      </section>

      <!-- 模板选择 -->
      <section class="style-section">
        <h3>选择边框样式</h3>
        <div class="style-grid">
          <div 
            v-for="style in styles"
            :key="style.id"
            class="style-item"
            :class="{ active: selectedStyle === style.id }"
            @click="selectedStyle = style.id as any"
          >
            <div class="style-preview" :class="style.id">
              <span class="preview-char">{{ poem.title?.charAt(0) || '诗' }}</span>
            </div>
            <span class="style-name">{{ style.name }}</span>
          </div>
        </div>
      </section>

      <!-- AI 生图 -->
      <section class="generate-section">
        <h3>AI 诗词成画</h3>
        <p class="section-desc">选择风格，生成意境图片</p>
        
        <div class="style-grid">
          <div 
            v-for="artStyle in artStyles"
            :key="artStyle.id"
            class="art-style-item"
            :class="{ active: selectedArtStyle === artStyle.id }"
            @click="selectedArtStyle = artStyle.id"
          >
            <div class="art-preview">
              <img :src="artStyle.preview" :alt="artStyle.name" />
            </div>
            <span class="art-name">{{ artStyle.name }}</span>
            <van-tag v-if="artStyle.isVip" type="warning">会员</van-tag>
          </div>
        </div>

        <van-button 
          type="primary" 
          block
          :loading="isGenerating"
          @click="generateArt"
        >
          {{ isGenerating ? '生成中...' : '生成意境图' }}
        </van-button>

        <p class="quota-info">
          今日剩余次数：{{ quota.remaining }} / {{ quota.daily_limit }}
        </p>
      </section>

      <!-- 操作按钮 -->
      <section class="actions-section">
        <van-button type="primary" plain block @click="addToFavorites">
          <van-icon name="star-o" /> 收藏诗句
        </van-button>
        
        <van-button type="default" plain block @click="shareCard">
          <van-icon name="share" /> 分享
        </van-button>
      </section>
    </template>

    <!-- 生图弹窗 -->
    <van-popup v-model:show="showGenerateModal" position="bottom" round>
      <div class="generate-modal">
        <h3>生成诗词意境图</h3>
        
        <van-field label="选择风格">
          <template #input>
            <van-radio-group v-model="selectedArtStyle" direction="horizontal">
              <van-radio name="shuimo">水墨</van-radio>
              <van-radio name="gongbi">工笔</van-radio>
              <van-radio name="modern">现代</van-radio>
            </van-radio-group>
          </template>
        </van-field>

        <van-field label="边框样式">
          <template #input>
            <van-radio-group v-model="selectedStyle" direction="horizontal">
              <van-radio name="classic">经典</van-radio>
              <van-radio name="vintage">复古</van-radio>
              <van-radio name="ink">水墨</van-radio>
            </van-radio-group>
          </template>
        </van-field>

        <van-field
          v-model="customPrompt"
          label="自定义提示词"
          placeholder="可选，描述你想要的画面"
          type="textarea"
          rows="2"
        />

        <div class="modal-actions">
          <van-button @click="showGenerateModal = false">取消</van-button>
          <van-button type="primary" :loading="isGenerating" @click="generateArt">
            生成
          </van-button>
        </div>
      </div>
    </van-popup>

    <!-- 更多操作 -->
    <van-action-sheet
      v-model:show="showMore"
      :actions="moreActions"
      @select="handleMoreAction"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showSuccessToast, showFailToast } from 'vant'
import PolaroidCard from '../components/game/PolaroidCard.vue'
import { api } from '../api'

const route = useRoute()
const router = useRouter()

// 状态
const loading = ref(true)
const poem = ref<any>(null)
const explanation = ref('')
const generatedImage = ref('')
const isGenerating = ref(false)
const showGenerateModal = ref(false)
const showMore = ref(false)
const selectedStyle = ref<'classic' | 'vintage' | 'ink' | 'modern'>('classic')
const selectedArtStyle = ref('shuimo')
const customPrompt = ref('')
const quota = ref({ remaining: 3, daily_limit: 3 })

// 边框样式
const styles = [
  { id: 'classic', name: '经典拍立得' },
  { id: 'vintage', name: '复古胶片' },
  { id: 'ink', name: '水墨古卷' },
  { id: 'modern', name: '现代简约' }
]

// AI 风格
const artStyles = [
  { id: 'shuimo', name: '水墨画', preview: '/assets/styles/shuimo.jpg', isVip: false },
  { id: 'gongbi', name: '工笔画', preview: '/assets/styles/gongbi.jpg', isVip: false },
  { id: 'dunhuang', name: '敦煌风', preview: '/assets/styles/dunhuang.jpg', isVip: true },
  { id: 'modern', name: '现代风', preview: '/assets/styles/modern.jpg', isVip: false }
]

// 更多操作
const moreActions = [
  { name: '复制诗句', action: () => copyPoem() },
  { name: '添加到收藏', action: () => addToFavorites() },
  { name: '举报', action: () => reportPoem() }
]

// 诗句行
const poemLines = computed(() => {
  if (!poem.value) return []
  const content = poem.value.full_text || poem.value.content
  return content.split(/[，；。\n]/).filter((l: string) => l.trim())
})

// 初始化
onMounted(async () => {
  const poemId = route.params.id as string
  
  try {
    // 获取诗句详情
    const res = await api.get(`/v1/poems/${poemId}`)
    poem.value = res.data.data
    
    // 获取赏析
    if (poem.value) {
      const expRes = await api.get(`/v1/poems/${poemId}/explanation`)
      explanation.value = expRes.data.data?.explanation || ''
    }
    
    // 获取配额
    const quotaRes = await api.get('/v1/art/quota')
    quota.value = quotaRes.data.data
  } catch (e) {
    showFailToast('加载失败')
  } finally {
    loading.value = false
  }
})

// 生成 AI 图片
async function generateArt() {
  if (!poem.value) return
  
  if (quota.value.remaining <= 0) {
    showToast('今日生成次数已用完')
    return
  }
  
  isGenerating.value = true
  
  try {
    const res = await api.post('/v1/art/generate', {
      poem_id: poem.value.id,
      poem_text: poem.value.full_text || poem.value.content,
      style: selectedArtStyle.value,
      custom_prompt: customPrompt.value || undefined
    })
    
    const data = res.data.data
    
    if (data.task_id) {
      // 轮询任务状态
      await pollTaskStatus(data.task_id)
    } else if (data.result_url) {
      generatedImage.value = data.result_url
      showSuccessToast('生成成功')
    }
    
    // 更新配额
    quota.value.remaining--
  } catch (e: any) {
    showFailToast(e.response?.data?.error?.message || '生成失败')
  } finally {
    isGenerating.value = false
    showGenerateModal.value = false
  }
}

// 轮询任务状态
async function pollTaskStatus(taskId: string, maxAttempts = 30) {
  for (let i = 0; i < maxAttempts; i++) {
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    try {
      const res = await api.get(`/v1/art/tasks/${taskId}`)
      const task = res.data.data
      
      if (task.status === 'succeeded') {
        generatedImage.value = task.result_url
        showSuccessToast('生成成功')
        return
      }
      
      if (task.status === 'failed') {
        showFailToast('生成失败：' + (task.error_message || '未知错误'))
        return
      }
    } catch (e) {
      // 继续等待
    }
  }
  
  showToast('生成超时，请稍后查看')
}

// 保存卡片
function saveCard() {
  if (!generatedImage.value) {
    showToast('先生成图片后再保存')
    return
  }
  
  // 下载图片
  const link = document.createElement('a')
  link.href = generatedImage.value
  link.download = `${poem.value?.title || 'poem'}.png`
  link.click()
  
  showSuccessToast('已保存')
}

// 分享
function shareCard() {
  const text = `${poem.value?.title}\n${poem.value?.content}\n—— ${poem.value?.author}`
  
  if (navigator.share) {
    navigator.share({
      title: poem.value?.title,
      text: text,
      url: window.location.href
    })
  } else {
    navigator.clipboard.writeText(text + '\n' + window.location.href)
    showSuccessToast('已复制到剪贴板')
  }
}

// 收藏
async function addToFavorites() {
  try {
    await api.put(`/v1/me/favorites/poem/${poem.value.id}`)
    showSuccessToast('已收藏')
  } catch (e: any) {
    if (e.response?.status === 409) {
      showToast('已在收藏中')
    } else {
      showFailToast('收藏失败')
    }
  }
}

// 复制诗句
function copyPoem() {
  const text = `${poem.value?.title}\n${poem.value?.content}\n—— ${poem.value?.author}`
  navigator.clipboard.writeText(text)
  showSuccessToast('已复制')
}

// 举报
function reportPoem() {
  showToast('感谢反馈，我们会尽快处理')
}

// 处理更多操作
function handleMoreAction(action: any) {
  if (action.action) {
    action.action()
  }
  showMore.value = false
}
</script>

<style scoped>
.poem-card-page {
  min-height: 100vh;
  background: #f8f8f8;
  padding-bottom: 80px;
}

.page-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.page-header span {
  font-size: 16px;
  font-weight: 500;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.card-container {
  display: flex;
  justify-content: center;
  padding: 24px 16px;
  background: white;
}

.poem-info {
  background: white;
  padding: 20px;
  margin: 12px;
  border-radius: 12px;
}

.poem-title {
  font-size: 22px;
  color: #333;
  margin: 0 0 4px;
  text-align: center;
}

.poem-author {
  text-align: center;
  color: #999;
  font-size: 14px;
  margin: 0 0 16px;
}

.poem-content {
  font-size: 18px;
  line-height: 2;
  text-align: center;
  font-family: 'STKaiti', 'KaiTi', serif;
  color: #333;
  margin-bottom: 16px;
}

.poem-content p {
  margin: 0;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.imagery-section,
.appreciation-section,
.style-section,
.generate-section,
.actions-section {
  background: white;
  padding: 20px;
  margin: 12px;
  border-radius: 12px;
}

.imagery-section h3,
.appreciation-section h3,
.style-section h3,
.generate-section h3 {
  font-size: 16px;
  color: #333;
  margin: 0 0 12px;
}

.imagery-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.imagery-item {
  padding: 4px 12px;
  background: #f0f0f0;
  border-radius: 16px;
  font-size: 14px;
  color: #666;
}

.appreciation-content {
  font-size: 14px;
  line-height: 1.8;
  color: #666;
}

.style-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.style-item {
  text-align: center;
  cursor: pointer;
}

.style-item.active .style-preview {
  border-color: #c9a227;
  box-shadow: 0 2px 8px rgba(201, 162, 39, 0.3);
}

.style-preview {
  width: 60px;
  height: 60px;
  margin: 0 auto 8px;
  border-radius: 4px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid transparent;
  transition: all 0.2s ease;
}

.style-preview.vintage {
  background: #e8dcc8;
}

.style-preview.ink {
  background: #f8f4e8;
  border-radius: 0;
}

.style-preview.modern {
  background: #fff;
  border-radius: 2px;
}

.preview-char {
  font-size: 20px;
  color: #8b7355;
}

.style-name {
  font-size: 12px;
  color: #666;
}

.art-style-item {
  position: relative;
  text-align: center;
  cursor: pointer;
}

.art-style-item.active .art-preview {
  border-color: #c9a227;
}

.art-preview {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 8px;
  border: 2px solid transparent;
  transition: all 0.2s ease;
}

.art-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.art-name {
  font-size: 12px;
  color: #666;
}

.section-desc {
  font-size: 13px;
  color: #999;
  margin: -8px 0 12px;
}

.quota-info {
  text-align: center;
  font-size: 12px;
  color: #999;
  margin-top: 12px;
}

.generate-modal {
  padding: 20px;
}

.generate-modal h3 {
  text-align: center;
  margin: 0 0 20px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.modal-actions button {
  flex: 1;
}

.actions-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
