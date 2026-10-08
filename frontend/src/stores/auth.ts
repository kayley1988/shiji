import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api'

export interface User {
  id: string
  nickname: string
  rank: string
  exp: number
  total_games: number
  total_wins: number
  total_correct: number
  avatar_url?: string
  role?: string
  email?: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoggedIn = ref(false)

  async function login() {
    try {
      // 拦截器 unwrap → res = Flask { data: { user_id, nickname, token, is_new } }
      // device_id 持久化：同一浏览器刷新/重开不换账号，闯关记录与错题集得以延续
      let deviceId = localStorage.getItem('device_id')
      if (!deviceId) {
        deviceId = 'web_' + Math.random().toString(36).slice(2) + Date.now().toString(36)
        localStorage.setItem('device_id', deviceId)
      }
      const res = await api.anonymousLogin(deviceId)
      const d = res.data || {}
      user.value = (d.user ?? {
        id: d.user_id,
        nickname: d.nickname || '匿名雅客',
      }) as User
      token.value = d.access_token || d.token
      isLoggedIn.value = true
      if (token.value) localStorage.setItem('access_token', token.value)
      return true
    } catch (e) {
      console.error('登录失败', e)
      return false
    }
  }

  async function restore() {
    // 匿名登录按 device_id 幂等：同一浏览器始终映射同一账号，
    // 闯关记录 / 错题集跨会话延续（/v1/me/profile 是 mock，不可信）
    const savedToken = localStorage.getItem('access_token')
    if (savedToken) token.value = savedToken
    await login()
  }

  async function emailLogin(email: string, password: string) {
    try {
      const res = await api.authLogin(email, password)
      user.value = res.data.user as User
      token.value = res.data.token
      isLoggedIn.value = true
      localStorage.setItem('access_token', res.data.token)
      return true
    } catch (e) {
      console.error('邮箱登录失败', e)
      return false
    }
  }

  async function emailRegister(email: string, password: string, nickname?: string) {
    try {
      const res = await api.authRegister(email, password, nickname)
      user.value = res.data.user as User
      token.value = res.data.token
      isLoggedIn.value = true
      localStorage.setItem('access_token', res.data.token)
      return true
    } catch (e) {
      console.error('邮箱注册失败', e)
      return false
    }
  }

  function logout() {
    user.value = null
    token.value = null
    isLoggedIn.value = false
    localStorage.removeItem('access_token')
  }

  return { user, token, isLoggedIn, login, restore, logout, emailLogin, emailRegister }
})
