import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('./pages/Home.vue')
  },
  {
    path: '/room/create',
    name: 'CreateRoom',
    component: () => import('./pages/CreateRoom.vue')
  },
  {
    path: '/join',
    name: 'JoinRoom',
    component: () => import('./pages/JoinRoom.vue')
  },
  {
    path: '/room/join',
    name: 'JoinRoomOld',
    component: () => import('./pages/JoinRoom.vue')
  },
  {
    path: '/room/:id/result',
    name: 'Result',
    component: () => import('./pages/Result.vue')
  },
  {
    path: '/room/:id',
    name: 'Room',
    component: () => import('./pages/Room.vue')
  },
  {
    path: '/solar-term',
    name: 'SolarTerm',
    component: () => import('./pages/SolarTerm.vue')
  },
  {
    path: '/solar-term/:id',
    name: 'SolarTermDetail',
    component: () => import('./pages/SolarTerm.vue')
  },
  {
    path: '/me',
    name: 'Profile',
    component: () => import('./pages/Profile.vue')
  },
  {
    path: '/me/favorites',
    name: 'Favorites',
    component: () => import('./pages/Favorites.vue')
  },
  {
    path: '/badges',
    name: 'Badges',
    component: () => import('./pages/Badges.vue')
  },
  {
    path: '/colors',
    name: 'ColorPalette',
    component: () => import('./components/ColorPalette.vue')
  },
  {
    path: '/solo',
    name: 'Solo',
    component: () => import('./pages/Solo.vue')
  },
  {
    path: '/explore',
    name: 'Explore',
    component: () => import('./pages/Explore.vue')
  },
  {
    path: '/poets',
    name: 'Poets',
    component: () => import('./pages/Poets.vue')
  },
  {
    path: '/galaxy',
    name: 'Galaxy',
    component: () => import('./pages/Galaxy.vue')
  },
  {
    path: '/zen',
    name: 'AmbientPoetry',
    component: () => import('./pages/AmbientPoetry.vue')
  },
  {
    path: '/notes',
    name: 'PoemNotes',
    component: () => import('./pages/PoemNotes.vue')
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('./pages/Admin.vue')
  },
  {
    path: '/my-colors',
    name: 'MyColors',
    component: () => import('./pages/MyColors.vue')
  },
  {
    path: '/challenge',
    name: 'Challenge',
    component: () => import('./pages/Challenge.vue')
  },
  {
    path: '/challenge/dashboard',
    name: 'ChallengeDashboard',
    component: () => import('./pages/ChallengeDashboard.vue')
  },
  {
    path: '/tail-connect',
    name: 'TailConnect',
    component: () => import('./pages/TailConnect.vue')
  },
  {
    path: '/tail-connect/:roomId',
    name: 'TailConnectRoom',
    component: () => import('./pages/TailConnect.vue')
  },
  {
    path: '/poem-card/:id',
    name: 'PoemCard',
    component: () => import('./pages/PoemCard.vue')
  },
  {
    path: '/solo-feihua',
    name: 'SoloFeihua',
    component: () => import('./pages/SoloFeihua.vue')
  },
  {
    path: '/voice-battle',
    name: 'VoiceBattle',
    component: () => import('./pages/VoiceBattle.vue')
  },
  {
    path: '/library',
    name: 'Library',
    component: () => import('./pages/Library.vue')
  },
  {
    path: '/library/dynasty/:dynasty',
    name: 'LibraryDynasty',
    component: () => import('./pages/Library.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  if (to.path === '/admin') {
    const savedToken = localStorage.getItem('access_token')
    if (!savedToken) {
      // 未登录 → 去首页
      next('/')
      return
    }
    // 简单 token 校验：JWT payload 中 role=admin
    try {
      const parts = savedToken.split('.')
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
        if (payload.role !== 'admin') {
          alert('⚠️ 仅管理员可访问')
          next('/')
          return
        }
      }
    } catch {
      // token 格式异常，直接放行（后端会拦截）
    }
  }
  next()
})

export default router
