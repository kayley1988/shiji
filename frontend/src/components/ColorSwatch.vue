<template>
  <div class="color-swatch-page bg-xuanzhi">

    <!-- 顶部导航 -->
    <header class="nav-header">
      <button class="nav-btn" @click="$router.back()">
        <van-icon name="arrow-left" />
      </button>
      <span class="nav-title">中国色</span>
      <span></span>
    </header>

    <!-- 分类 Tab -->
    <div class="category-tabs">
      <button
        v-for="(name, key) in CATEGORY_NAMES"
        :key="key"
        class="cat-tab"
        :class="{ active: activeCategory === key }"
        @click="activeCategory = key"
      >{{ name }}</button>
    </div>

    <!-- 色块网格 -->
    <div class="color-grid">
      <div
        v-for="color in currentColors"
        :key="color.hex"
        class="color-card animate-fadeUp"
        @click="showDetail(color)"
      >
        <!-- 色块 -->
        <div
          class="color-block"
          :style="{ background: `linear-gradient(135deg, ${color.hex} 0%, rgba(${color.rgb}, 0.7) 100%)` }"
        >
          <div class="color-overlay">
            <van-icon name="scan" />
            <span>查看详情</span>
          </div>
        </div>

        <!-- 颜色信息 -->
        <div class="color-info">
          <div class="color-name">{{ color.name }}</div>
          <div class="color-hex">{{ color.hex }}</div>
          <div class="color-rgb">rgb({{ color.rgb }})</div>
        </div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <van-popup
      v-model:show="showPopup"
      position="bottom"
      round
      class="detail-popup"
    >
      <div v-if="selectedColor" class="detail-sheet">
        <!-- 大色块 -->
        <div
          class="detail-block"
          :style="{
            background: `linear-gradient(135deg, ${selectedColor.hex} 0%, rgba(${selectedColor.rgb}, 0.65) 100%)`
          }"
        >
          <div class="detail-name">{{ selectedColor.name }}</div>
        </div>

        <!-- 颜色值 -->
        <div class="detail-values">
          <div class="val-row" @click="copy(selectedColor.hex)">
            <span class="val-label">HEX</span>
            <span class="val-code">{{ selectedColor.hex }}</span>
            <van-icon name="copy-o" />
          </div>
          <div class="val-row" @click="copy(`rgb(${selectedColor.rgb})`)">
            <span class="val-label">RGB</span>
            <span class="val-code">rgb({{ selectedColor.rgb }})</span>
            <van-icon name="copy-o" />
          </div>
          <div class="val-row" @click="copy(`rgba(${selectedColor.rgb}, 1)`)">
            <span class="val-label">RGBA</span>
            <span class="val-code">rgba({{ selectedColor.rgb }}, 1)</span>
            <van-icon name="copy-o" />
          </div>
        </div>

        <!-- 配套诗句 -->
        <div class="detail-poem">
          <div class="poem-label">配套诗句</div>
          <div class="poem-text">{{ selectedColor.poem }}</div>
          <div class="poem-source">{{ selectedColor.source }}</div>
        </div>

        <!-- 关闭 -->
        <van-button class="detail-close" block round @click="showPopup = false">
          关闭
        </van-button>
      </div>
    </van-popup>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { showToast } from 'vant'
import { CHINESE_COLORS, CATEGORY_NAMES, type ChineseColor } from '../styles/chinese-colors'

const activeCategory = ref<string>('red')
const showPopup = ref(false)
const selectedColor = ref<ChineseColor | null>(null)

const currentColors = computed(() =>
  CHINESE_COLORS.filter(c => c.category === activeCategory.value)
)

function showDetail(color: ChineseColor) {
  selectedColor.value = color
  showPopup.value = true
}

async function copy(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    showToast('已复制：' + text)
  } catch {
    showToast('复制失败')
  }
}
</script>

<style scoped>
.color-swatch-page {
  min-height: 100vh;
  padding-bottom: 40px;
}

/* ── 导航 ── */
.nav-header {
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
  background: rgba(248,252,248,0.94);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(90,143,117,0.12);
}
.nav-btn {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  background: none; border: none;
  color: var(--ink); font-size: 20px; cursor: pointer;
}
.nav-title {
  font-family: var(--font-display);
  font-size: 18px; color: var(--ink);
}

/* ── 分类 Tab ── */
.category-tabs {
  display: flex; gap: 8px; flex-wrap: wrap;
  padding: 16px 16px 8px;
}
.cat-tab {
  padding: 6px 16px;
  border-radius: 20px;
  border: 1.5px solid var(--parchment-dark);
  background: var(--parchment);
  color: var(--stone);
  font-family: var(--font-display);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.cat-tab.active {
  background: var(--ink);
  color: var(--parchment);
  border-color: var(--ink);
}

/* ── 色块网格 ── */
.color-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
  padding: 16px;
}

.color-card {
  background: #fff;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}
.color-card:active {
  transform: scale(0.97);
  box-shadow: var(--shadow-xs);
}

.color-block {
  height: 100px;
  position: relative;
  overflow: hidden;
}

.color-overlay {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 4px;
  background: rgba(0,0,0,0.3);
  color: #fff;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.2s;
}
.color-block:hover .color-overlay {
  opacity: 1;
}

.color-info {
  padding: 10px 12px;
}
.color-name {
  font-family: var(--font-display);
  font-size: 15px; font-weight: 600;
  color: var(--ink);
}
.color-hex {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: var(--stone);
  margin-top: 2px;
  letter-spacing: 1px;
}
.color-rgb {
  font-family: 'Courier New', monospace;
  font-size: 11px;
  color: var(--parchment-dark);
  margin-top: 1px;
}

/* ── 详情弹窗 ── */
.detail-popup {
  max-height: 80vh;
}
.detail-sheet {
  padding: 20px;
}

.detail-block {
  height: 140px;
  border-radius: var(--radius-md);
  display: flex; align-items: flex-end;
  padding: 16px;
  margin-bottom: 16px;
}
.detail-name {
  font-family: var(--font-display);
  font-size: 28px; font-weight: 700;
  color: #fff;
  text-shadow: 0 1px 4px rgba(0,0,0,0.3);
}

.detail-values {
  background: var(--parchment);
  border-radius: var(--radius-md);
  overflow: hidden;
  margin-bottom: 16px;
}
.val-row {
  display: flex; align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(70,110,88,0.05);
  cursor: pointer;
  transition: background 0.15s;
}
.val-row:last-child { border-bottom: none; }
.val-row:active { background: rgba(70,110,88,0.05); }
.val-label {
  font-family: var(--font-display);
  font-size: 13px; font-weight: 600;
  color: var(--stone);
  width: 50px;
}
.val-code {
  flex: 1;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: var(--ink);
}

.detail-poem {
  background: var(--parchment);
  border-radius: var(--radius-md);
  padding: 16px;
  margin-bottom: 16px;
  border-left: 3px solid var(--cinnabar);
}
.poem-label {
  font-family: var(--font-display);
  font-size: 12px; color: var(--stone);
  margin-bottom: 8px;
}
.poem-text {
  font-family: var(--font-display);
  font-size: 16px; line-height: 1.8;
  color: var(--ink);
  margin-bottom: 6px;
}
.poem-source {
  font-size: 12px; color: var(--stone);
}

.detail-close {
  background: var(--parchment-dark) !important;
  color: var(--ink) !important;
  border: none !important;
  font-family: var(--font-display) !important;
}

/* ── 动画 ── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fadeUp {
  animation: fadeUp 0.3s ease-out both;
}
.color-card:nth-child(1) { animation-delay: 0ms; }
.color-card:nth-child(2) { animation-delay: 60ms; }
.color-card:nth-child(3) { animation-delay: 120ms; }
.color-card:nth-child(4) { animation-delay: 180ms; }
</style>
