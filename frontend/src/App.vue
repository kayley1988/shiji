<template>
  <div class="app bg-xuanzhi">
    <!-- 全局启动页 -->
    <SplashScreen
      v-if="loadingStore.phase !== 'done'"
      @done="onSplashDone"
    />

    <!-- 左侧抽屉 -->
    <SideDrawer v-model="drawerOpen" />

    <!-- 页面内容 -->
    <div class="app-body">
      <!-- 顶部导航栏（带汉堡菜单） -->
      <header class="app-nav" v-if="showNav">
        <button class="nav-hamburger" @click="drawerOpen = true">
          <van-icon name="wap-nav" />
        </button>
        <span class="nav-title">{{ pageTitle }}</span>
        <span class="nav-right"></span>
      </header>

      <!-- 路由页面 -->
      <router-view v-slot="{ Component }">
        <Transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import SplashScreen from './components/SplashScreen.vue'
import SideDrawer from './components/SideDrawer.vue'
import { useLoadingStore } from './stores/loading'
import { useAuthStore } from './stores/auth'

const loadingStore = useLoadingStore()
const authStore = useAuthStore()
const route = useRoute()
const drawerOpen = ref(false)

// 启动时：auth restore + loading 动画并行
onMounted(() => {
  loadingStore.start()
  // 静默后台登录，不阻塞启动页动画
  authStore.restore()
})

function onSplashDone() {
  // 启动页消失后可做一些初始化
}

// 所有页面都显示顶部导航栏
const showNav = computed(() => true)

// 动态页面标题
const titleMap: Record<string, string> = {
  Home: '诗语雅集',
  CreateRoom: '创建雅集',
  JoinRoom: '加入雅集',
  Room: '对战',
  Result: '对局结果',
  Profile: '个人中心',
  Badges: '徽章馆',
  Favorites: '我的收藏',
  SolarTerm: '节气',
  SolarTermDetail: '节气详情',
  ColorPalette: '中国传统色',
  Poets: '诗人雅集',
  Challenge: '题库闯关',
}
const pageTitle = computed(() => titleMap[route.name as string] || '')
</script>

<style>
.app {
  min-height: 100vh;
}

/* 顶部导航 */
.app-nav {
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
  background: rgba(215,232,222,0.97);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(60,102,78,0.1);
}
.nav-hamburger {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  background: none; border: none;
  color: var(--ink); font-size: 22px; cursor: pointer;
  border-radius: var(--radius-sm);
}
.nav-title {
  font-family: var(--font-display);
  font-size: 18px; color: var(--ink);
}
.nav-right { width: 36px; }

/* 页面切换动画 */
.page-fade-enter-active { transition: opacity 0.2s, transform 0.2s; }
.page-fade-leave-active { transition: opacity 0.15s; }
.page-fade-enter-from { opacity: 0; transform: translateX(10px); }
.page-fade-leave-to { opacity: 0; }
</style>
