<template>
  <!-- 遮罩层 -->
  <Transition name="mask-fade">
    <div v-if="modelValue" class="drawer-mask" @click="$emit('update:modelValue', false)"></div>
  </Transition>

  <!-- 抽屉 -->
  <Transition name="drawer-slide">
    <div v-if="modelValue" class="drawer-panel">
      <!-- 头部用户信息 -->
      <div class="drawer-header" @click="goProfile">
        <div class="user-avatar" :style="avatarBg">{{ user?.nickname?.slice(-2) || '客' }}</div>
        <div class="user-info">
          <div class="user-name">{{ user?.nickname || '游客' }}</div>
          <div class="user-rank">
            <span class="rank-icon">{{ rankIcon(user?.rank) }}</span>
            {{ user?.rank || '萌新' }}
          </div>
        </div>
        <van-icon name="arrow" class="user-arrow" />
      </div>

      <!-- 统计数据 -->
      <div class="drawer-stats">
        <div class="stat-item">
          <span class="stat-num">{{ user?.total_games || 0 }}</span>
          <span class="stat-label">对局</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-num">{{ user?.total_wins || 0 }}</span>
          <span class="stat-label">胜场</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-num">{{ user?.exp || 0 }}</span>
          <span class="stat-label">经验</span>
        </div>
      </div>

      <!-- 导航列表 -->
      <nav class="drawer-nav">
        <div class="nav-item" @click="navigate('/zen')">
          <span class="nav-icon">🧘</span>
          <span class="nav-label">静心诗境</span>
          <van-icon name="arrow-left" class="nav-arrow" />
        </div>
        <div class="nav-item" @click="navigate('/notes')">
          <span class="nav-icon">📜</span>
          <span class="nav-label">私人诗摘</span>
          <van-icon name="arrow-left" class="nav-arrow" />
        </div>
        <div class="nav-item" @click="navigate('/solo')">
          <span class="nav-icon">🎼</span>
          <span class="nav-label">独酌自娱</span>
          <van-icon name="arrow-left" class="nav-arrow" />
        </div>
        <div class="nav-item" @click="navigate('/explore')">
          <span class="nav-icon">📖</span>
          <span class="nav-label">诗词品鉴</span>
          <van-icon name="arrow-left" class="nav-arrow" />
        </div>
        <div class="nav-item" @click="navigate('/poets')">
          <span class="nav-icon">🎭</span>
          <span class="nav-label">诗人雅集</span>
          <van-icon name="arrow-left" class="nav-arrow" />
        </div>
        <div class="nav-item" @click="navigate('/')">
          <span class="nav-icon">🏠</span>
          <span class="nav-label">首页</span>
          <van-icon name="arrow-left" class="nav-arrow" />
        </div>
        <div class="nav-item" @click="navigate('/colors')">
          <span class="nav-icon">🎨</span>
          <span class="nav-label">中国传统色</span>
          <van-icon name="arrow-left" class="nav-arrow" />
        </div>
        <div class="nav-item" @click="showThemePicker = true">
          <span class="nav-icon">🖌️</span>
          <span class="nav-label">国风皮肤</span>
          <van-icon name="arrow-left" class="nav-arrow" />
        </div>
        <div class="nav-item" @click="navigate('/badges')">
          <span class="nav-icon">🎖️</span>
          <span class="nav-label">徽章馆</span>
          <van-icon name="arrow-left" class="nav-arrow" />
        </div>
        <div class="nav-item" @click="navigate('/me/favorites')">
          <span class="nav-icon">⭐</span>
          <span class="nav-label">我的收藏</span>
          <van-icon name="arrow-left" class="nav-arrow" />
        </div>
        <div class="nav-item" @click="navigate('/me')">
          <span class="nav-icon">👤</span>
          <span class="nav-label">个人中心</span>
          <van-icon name="arrow-left" class="nav-arrow" />
        </div>
      </nav>

      <!-- 底部装饰 -->
      <div class="drawer-footer">
        <div class="footer-poem">「落霞与孤鹜齐飞，秋水共长天一色」</div>
        <div class="footer-version">诗语雅集 v1.0</div>
      </div>
    </div>
  </Transition>

  <!-- 国风皮肤选择器 -->
  <van-popup
    v-model:show="showThemePicker"
    position="bottom"
    round
    :style="{ padding: '20px 16px 28px' }"
  >
    <div class="theme-picker-title">🖌️ 选择国风皮肤</div>
    <div class="theme-grid">
      <div
        v-for="t in THEMES"
        :key="t.id"
        class="theme-card"
        :class="{ active: currentTheme === t.id }"
        @click="selectTheme(t.id)"
      >
        <span class="theme-icon">{{ t.icon }}</span>
        <span class="theme-name">{{ t.name }}</span>
        <span class="theme-desc">{{ t.desc }}</span>
        <van-icon v-if="currentTheme === t.id" name="success" class="theme-check" />
      </div>
    </div>
  </van-popup>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useTheme } from '../composables/useTheme'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [boolean] }>()
const router = useRouter()
const authStore = useAuthStore()
const user = computed(() => authStore.user)

const { THEMES, currentTheme, applyTheme } = useTheme()
const showThemePicker = ref(false)

function selectTheme(id: string) {
  applyTheme(id)
  showThemePicker.value = false
}

function navigate(path: string) {
  emit('update:modelValue', false)
  router.push(path)
}

function goProfile() {
  emit('update:modelValue', false)
  router.push('/me')
}

const avatarBg = computed(() => ({
  background: user.value ? avatarGradient(user.value.id) : 'var(--stone)'
}))

function avatarGradient(id: string): string {
  const colors = [
    ['#3D7A8A', '#5A9BAA'],
    ['#4A8B6A', '#6AAB8A'],
    ['#C4A882', '#D4B896'],
    ['#3D7A8A', '#7BB0C0'],
  ]
  const idx = id.charCodeAt(0) % colors.length
  const [c1, c2] = colors[idx]
  return `linear-gradient(135deg, ${c1}, ${c2})`
}

const rankIconMap: Record<string, string> = {
  '萌新': '🌱', '秀才': '🌿', '举人': '🌳',
  '进士': '🏆', '翰林': '🎖️', '雅客': '👑'
}
function rankIcon(rank?: string) { return rankIconMap[rank || '萌新'] || '🌱' }
</script>

<style scoped>
.drawer-mask {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(2px);
}

/* 抽屉主体 */
.drawer-panel {
  position: fixed; top: 0; left: 0; bottom: 0; z-index: 1001;
  width: 280px;
  background: var(--parchment);
  display: flex; flex-direction: column;
  box-shadow: 4px 0 32px rgba(0,0,0,0.15);
}

/* 头部 */
.drawer-header {
  display: flex; align-items: center; gap: 12px;
  padding: 48px 20px 20px;
  background: linear-gradient(135deg, var(--cinnabar), var(--cinnabar-light));
  cursor: pointer;
}
.user-avatar {
  width: 52px; height: 52px; border-radius: 50%;
  color: #fff; font-size: 20px; font-weight: 600;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.user-info { flex: 1; }
.user-name {
  font-family: var(--font-display);
  font-size: 18px; color: #fff; margin-bottom: 4px;
}
.user-rank {
  display: flex; align-items: center; gap: 4px;
  font-size: 12px; color: rgba(255,255,255,0.8);
}
.user-arrow { color: rgba(255,255,255,0.6); font-size: 14px; }

/* 统计 */
.drawer-stats {
  display: flex; align-items: center; justify-content: space-around;
  padding: 16px 20px;
  background: #fff;
  border-bottom: 1px solid var(--parchment-dark);
}
.stat-item { text-align: center; }
.stat-num {
  display: block; font-size: 18px; font-weight: 700;
  color: var(--ink); font-family: var(--font-sans);
}
.stat-label { font-size: 11px; color: var(--stone); }
.stat-divider { width: 1px; height: 28px; background: var(--parchment-dark); }

/* 导航 */
.drawer-nav { flex: 1; padding: 8px 0; }
.nav-item {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 20px;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid var(--parchment-dark);
}
.nav-item:hover { background: rgba(155,58,42,0.05); }
.nav-item:active { background: rgba(155,58,42,0.1); }
.nav-icon { font-size: 18px; }
.nav-label { flex: 1; font-size: 15px; color: var(--ink); font-family: var(--font-serif); }
.nav-arrow { color: var(--stone-light); font-size: 14px; }

/* 底部 */
.drawer-footer {
  padding: 20px;
  border-top: 1px solid var(--parchment-dark);
}
.footer-poem {
  font-family: var(--font-serif);
  font-size: 12px; color: var(--stone-light);
  text-align: center; margin-bottom: 8px; line-height: 1.8;
}
.footer-version {
  text-align: center; font-size: 11px; color: var(--stone-light);
}

/* 过渡动画 */
.mask-fade-enter-active, .mask-fade-leave-active { transition: opacity 0.25s; }
.mask-fade-enter-from, .mask-fade-leave-to { opacity: 0; }

.drawer-slide-enter-active { transition: transform 0.3s var(--ease-out); }
.drawer-slide-leave-active { transition: transform 0.25s ease-in; }
.drawer-slide-enter-from, .drawer-slide-leave-to { transform: translateX(-100%); }

/* ── 国风皮肤选择器 ── */
.theme-picker-title {
  font-family: var(--font-display);
  font-size: 17px; color: var(--ink);
  text-align: center; margin-bottom: 16px;
}
.theme-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.theme-card {
  position: relative;
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 18px 10px;
  background: #fff;
  border: 1.5px solid rgba(158,142,126,0.2);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s var(--ease-out);
}
.theme-card.active {
  border-color: var(--cinnabar);
  background: color-mix(in srgb, var(--cinnabar) 6%, transparent);
}
.theme-icon { font-size: 30px; }
.theme-name { font-family: var(--font-display); font-size: 15px; color: var(--ink); }
.theme-desc { font-size: 11px; color: var(--stone); text-align: center; line-height: 1.5; }
.theme-check {
  position: absolute; top: 8px; right: 8px;
  color: var(--cinnabar); font-size: 16px;
}
</style>
