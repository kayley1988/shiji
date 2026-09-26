<template>
  <div class="favorites-page bg-xuanzhi">

    <!-- 顶部导航 -->
    <header class="app-nav">
      <button class="nav-back" @click="$router.back()">
        <van-icon name="arrow-left" />
      </button>
      <span class="nav-title">我的收藏</span>
      <span class="nav-right"></span>
    </header>

    <!-- Tab 切换 -->
    <van-tabs v-model:active="activeTab" class="fav-tabs" line-height="2px">
      <van-tab title="诗词" name="poem">
        <div class="tab-content" v-if="poemFavorites.length">
          <div
            v-for="item in poemFavorites"
            :key="item.id"
            class="poem-card"
          >
            <div class="poem-body" @click="goPoem(item)">
              <div class="poem-title">{{ item.title }}</div>
              <div class="poem-author">{{ item.author }}</div>
            </div>
            <button class="remove-btn" @click.stop="removePoem(item)">
              <van-icon name="cross" />
            </button>
          </div>
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">📖</div>
          <div class="empty-text">暂无收藏诗词</div>
        </div>
      </van-tab>

      <van-tab title="节气" name="solar_term">
        <div class="tab-content" v-if="termFavorites.length">
          <div
            v-for="item in termFavorites"
            :key="item.id"
            class="term-card"
          >
            <div class="term-body" @click="goTerm(item)">
              <div class="term-seal-mini"><span>{{ item.name?.slice(0,1) }}</span></div>
              <div>
                <div class="term-name">{{ item.name }}</div>
                <div class="term-meta">{{ item.season }} · {{ item.element }}行</div>
              </div>
            </div>
            <button class="remove-btn" @click.stop="removeTerm(item)">
              <van-icon name="cross" />
            </button>
          </div>
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">🌿</div>
          <div class="empty-text">暂无收藏节气</div>
        </div>
      </van-tab>

      <van-tab title="颜色" name="color">
        <div class="tab-content" v-if="colorFavorites.length">
          <div class="color-grid">
            <div
              v-for="item in colorFavorites"
              :key="item.id"
              class="color-item"
            >
              <div
                class="color-swatch"
                :style="{ background: getColorHex(item.color_name) }"
              ></div>
              <span class="color-name">{{ item.color_name }}</span>
              <button class="color-remove" @click.stop="removeColor(item)">
                <van-icon name="cross" />
              </button>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">🎨</div>
          <div class="empty-text">暂无收藏颜色</div>
        </div>
      </van-tab>
    </van-tabs>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { api } from '../api'
import { CHINESE_COLORS } from '../styles/chinese-colors'

const router = useRouter()
const activeTab = ref('poem')
const poemFavorites = ref<any[]>([])
const termFavorites = ref<any[]>([])
const colorFavorites = ref<any[]>([])

// 颜色名 → hex 映射（静态数据，无需请求）
const colorMap = new Map(CHINESE_COLORS.map(c => [c.name, c.hex]))
function getColorHex(name: string) {
  return colorMap.get(name) || '#888'
}

onMounted(async () => {
  await fetchFavorites()
})

async function fetchFavorites() {
  try {
    const res = await api.get('/me/favorites')
    const favorites = res.data?.favorites || []
    poemFavorites.value = favorites.filter((f: any) => f.type === 'poem')
    termFavorites.value = favorites.filter((f: any) => f.type === 'solar_term')
    colorFavorites.value = favorites.filter((f: any) => f.type === 'color')
  } catch (e) {
    console.error('获取收藏失败', e)
  }
}

function goPoem(item: any) {
  router.push(`/explore?poem_id=${item.poem_id}`)
}

function goTerm(item: any) {
  router.push(`/solar-term/${item.solar_term_id}`)
}

async function removeColor(item: any) {
  try {
    await api.delete(`/me/favorites/color/${encodeURIComponent(item.color_name)}`)
    colorFavorites.value = colorFavorites.value.filter(f => f.id !== item.id)
    showToast('已取消收藏')
  } catch {
    showToast('操作失败')
  }
}

async function removePoem(item: any) {
  try {
    await api.delete(`/me/favorites/poem/${item.poem_id}`)
    poemFavorites.value = poemFavorites.value.filter(f => f.id !== item.id)
    showToast('已取消收藏')
  } catch {
    showToast('操作失败')
  }
}

async function removeTerm(item: any) {
  try {
    await api.delete(`/me/favorites/solar_term/${item.solar_term_id}`)
    termFavorites.value = termFavorites.value.filter(f => f.id !== item.id)
    showToast('已取消收藏')
  } catch {
    showToast('操作失败')
  }
}
</script>

<style scoped>
.favorites-page { min-height: 100vh; padding-bottom: 40px; }

/* Tab 样式覆盖 */
.fav-tabs :deep(.van-tabs__nav) {
  background: var(--parchment);
}
.fav-tabs :deep(.van-tab) {
  font-family: var(--font-serif);
  color: var(--stone);
}
.fav-tabs :deep(.van-tab--active) {
  color: var(--cinnabar);
  font-weight: 600;
}
.fav-tabs :deep(.van-tabs__line) {
  background: var(--cinnabar);
}

.tab-content { padding: 16px; }

/* 诗词卡片 */
.poem-card {
  display: flex; align-items: center; gap: 8px;
  padding: 14px 16px;
  background: #fff;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  margin-bottom: 10px;
  border-left: 3px solid var(--gold);
  transition: all 0.2s;
}
.poem-card:hover { box-shadow: var(--shadow-md); }
.poem-body { flex: 1; cursor: pointer; }
.poem-title { font-family: var(--font-display); font-size: 16px; color: var(--ink); margin-bottom: 4px; }
.poem-author { font-size: 12px; color: var(--stone); }

/* 节气卡片 */
.term-card {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 16px;
  background: #fff;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  margin-bottom: 10px;
  border-left: 3px solid var(--jade);
  transition: all 0.2s;
}
.term-card:hover { box-shadow: var(--shadow-md); }
.term-body { flex: 1; display: flex; align-items: center; gap: 12px; cursor: pointer; }
.term-seal-mini {
  width: 40px; height: 40px; flex-shrink: 0;
  background: var(--jade); color: #fff;
  border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center;
}
.term-seal-mini span { font-size: 18px; font-family: var(--font-display); }
.term-name { font-family: var(--font-display); font-size: 16px; color: var(--ink); margin-bottom: 2px; }
.term-meta { font-size: 12px; color: var(--stone); }

/* 删除按钮 */
.remove-btn {
  width: 28px; height: 28px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: transparent;
  border: none; cursor: pointer;
  color: var(--stone-light); font-size: 16px;
  border-radius: 50%; transition: all 0.15s;
}
.remove-btn:hover { background: rgba(155,58,42,0.1); color: var(--cinnabar); }

/* 颜色网格 */
.color-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.color-item {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  position: relative;
}
.color-swatch {
  width: 100%; aspect-ratio: 1;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
}
.color-name { font-size: 11px; color: var(--stone); text-align: center; line-height: 1.3; }
.color-remove {
  position: absolute; top: -4px; right: -4px;
  width: 18px; height: 18px;
  background: rgba(0,0,0,0.5); color: #fff;
  border: none; border-radius: 50%; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px;
}

/* 空状态 */
.empty-state { display: flex; flex-direction: column; align-items: center; padding: 80px 0; gap: 12px; }
.empty-icon { font-size: 48px; }
.empty-text { font-size: 14px; color: var(--stone); }
</style>
