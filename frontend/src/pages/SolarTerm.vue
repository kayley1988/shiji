<template>
  <div class="solar-term-page bg-xuanzhi">

    <!-- 节气卷轴 -->
    <section class="section-hero animate-fadeUp" v-if="termInfo">
      <div class="term-scroll">
        <div class="scroll-rod top"></div>
        <div class="scroll-rod bottom"></div>
        <div class="term-body">
          <div class="term-meta-row">
            <span class="term-season">{{ termInfo.season }}</span>
            <span class="term-divider">·</span>
            <span class="term-element">{{ termInfo.element }}行</span>
            <div class="term-seal"><span>{{ termInfo.name?.slice(0,1) || '节' }}</span></div>
          </div>
          <h1 class="term-title">{{ termInfo.name }}</h1>
          <p class="term-desc" v-if="termInfo.description">{{ termInfo.description }}</p>
        </div>
      </div>
    </section>

    <!-- 主题意象 -->
    <section class="section-card animate-fadeUp delay-1" v-if="termInfo">
      <div class="card-section-label">
        <span class="section-dot"></span>
        主题意象
      </div>
      <div class="kw-chips">
        <span class="kw-chip" v-for="kw in (termInfo.keywords || [])" :key="kw">{{ kw }}</span>
      </div>
      <div class="imagery-text" v-if="termInfo.imagery">
        <p v-for="(img, i) in termInfo.imagery" :key="i">「{{ img }}」</p>
      </div>
    </section>

    <!-- 相关诗词 -->
    <section class="section-poems animate-fadeUp delay-2" v-if="relatedPoems.length">
      <div class="section-header">
        <span class="header-line"></span>
        <span class="header-title">相关诗词</span>
        <span class="header-line"></span>
      </div>

      <div class="poem-list">
        <div
          v-for="poem in relatedPoems"
          :key="poem.poem_id"
          class="poem-card"
          @click="goToPoem(poem.poem_id)"
        >
          <div class="poem-top">
            <div class="poem-title">{{ poem.title }}</div>
            <div class="poem-author">{{ poem.author }}</div>
          </div>
          <div class="poem-line">「{{ poem.line_content }}」</div>
          <div class="poem-arrow">
            <van-icon name="arrow" />
          </div>
        </div>
      </div>
    </section>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <span class="loading-text">品鉴中...</span>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'

const route = useRoute()
const router = useRouter()
const termId = route.params.id as string

const termInfo = ref<any>(null)
const relatedPoems = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await api.getSolarTermDetail(termId)
    termInfo.value = res.data
    relatedPoems.value = res.data?.related_poems || []
  } finally {
    loading.value = false
  }
})

function goToPoem(poemId: string) {
  // TODO: 跳转到诗词详情
  console.log('goToPoem', poemId)
}
</script>

<style scoped>
.solar-term-page { min-height: 100vh; padding-bottom: 40px; }

/* ── 卷轴 ── */
.term-scroll {
  position: relative;
  margin: 16px;
  background: var(--parchment);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}
.scroll-rod {
  position: absolute; left: 0; right: 0; height: 12px;
  background: linear-gradient(90deg, var(--gold) 0%, var(--gold-light) 50%, var(--gold) 100%);
  border-radius: 4px; z-index: 1;
}
.scroll-rod.top { top: 0; }
.scroll-rod.bottom { bottom: 0; }

.term-body { padding: 32px 24px 28px; }
.term-meta-row {
  display: flex; align-items: center; gap: 8px; margin-bottom: 10px;
}
.term-season { font-size: 12px; color: var(--stone); }
.term-divider { color: var(--stone-light); }
.term-element {
  font-size: 12px; padding: 2px 8px;
  background: var(--parchment-dark); color: var(--stone);
  border-radius: var(--radius-full);
}
.term-seal {
  margin-left: auto;
  width: 36px; height: 36px;
  background: var(--jade);
  border-radius: 4px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 2px 2px 6px rgba(61,107,74,0.3);
}
.term-seal span { color: #fff; font-size: 18px; font-family: var(--font-display); }
.term-title {
  font-family: var(--font-display);
  font-size: 36px;
  color: var(--ink);
  margin-bottom: 12px;
}
.term-desc {
  font-size: 14px; color: var(--stone); line-height: 1.8;
}

/* ── 意象卡片 ── */
.section-card {
  margin: 0 16px 16px;
  background: var(--card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  padding: 20px;
}
.card-section-label {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 500; color: var(--ink);
  margin-bottom: 14px;
}
.section-dot {
  width: 6px; height: 6px;
  background: var(--jade); border-radius: 50%; flex-shrink: 0;
}
.kw-chips { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
.kw-chip {
  padding: 4px 14px;
  background: linear-gradient(135deg, var(--jade), var(--jade-light));
  color: #fff; font-size: 14px;
  border-radius: var(--radius-full);
}
.imagery-text p {
  font-family: var(--font-serif);
  font-size: 14px; color: var(--stone);
  line-height: 2; text-align: center;
  margin: 4px 0;
}

/* ── 诗词列表 ── */
.section-poems { padding: 0 16px; }
.section-header {
  display: flex; align-items: center; gap: 12px; margin-bottom: 14px;
}
.header-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--stone-light), transparent);
}
.header-title {
  font-family: var(--font-display); font-size: 16px;
  color: var(--stone); white-space: nowrap;
}

.poem-list { display: flex; flex-direction: column; gap: 10px; }
.poem-card {
  display: flex; align-items: center; gap: 12px;
  padding: 16px;
  background: var(--card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid var(--gold);
}
.poem-card:hover { box-shadow: var(--shadow-md); transform: translateX(4px); }
.poem-top { flex: 1; }
.poem-title {
  font-family: var(--font-display);
  font-size: 16px; color: var(--ink);
  margin-bottom: 2px;
}
.poem-author { font-size: 12px; color: var(--stone); }
.poem-line {
  font-family: var(--font-serif);
  font-size: 13px; color: var(--ink-light);
  flex: 1;
}
.poem-arrow { color: var(--stone-light); font-size: 16px; }

/* ── 加载 ── */
.loading-state {
  display: flex; justify-content: center;
  padding: 60px 0;
}
.loading-text { font-size: 14px; color: var(--stone); letter-spacing: 2px; }

/* ── 动画 ── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fadeUp { animation: fadeUp 0.5s var(--ease-out) both; }
.delay-1 { animation-delay: 0.1s; }
.delay-2 { animation-delay: 0.2s; }
</style>
