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
      // 拦截器 unwrap → res = Flask { data: { user: {...}, access_token: ... } }
      const res = await api.anonymousLogin()
      user.value = res.data.user as User
      token.value = res.data.access_token
      isLoggedIn.value = true
      localStorage.setItem('access_token', res.data.access_token)
      return true
    } catch (e) {
      console.error('登录失败', e)
      return false
    }
  }

  async function restore() {
    const savedToken = localStorage.getItem('access_token')
    if (savedToken) {
      token.value = savedToken
      try {
        // 拦截器 unwrap → res = Flask { data: { user: {...} } }
        const res = await api.getProfile()
        user.value = res.data as unknown as User
        isLoggedIn.value = true
      } catch {
        // token 失效，重新登录
        localStorage.removeItem('access_token')
        token.value = null
        await login()
      }
    } else {
      await login()
    }
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
