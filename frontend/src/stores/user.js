import { defineStore } from 'pinia'
import { getProfile, login as loginApi, register as registerApi } from '@/api'

const TOKEN_KEY = 'token'
const USER_KEY = 'userInfo'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    userInfo: JSON.parse(localStorage.getItem(USER_KEY) || 'null'),
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    displayName: (state) => state.userInfo?.nickname || state.userInfo?.username || '用户',
  },

  actions: {
    setAuth(token, user) {
      this.token = token
      this.userInfo = user
      localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    },

    clearAuth() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    },

    async login(payload) {
      const res = await loginApi(payload)
      this.setAuth(res.data.token, res.data.user)
      return res
    },

    async register(payload) {
      const res = await registerApi(payload)
      this.setAuth(res.data.token, res.data.user)
      return res
    },

    logout() {
      this.clearAuth()
    },

    async fetchProfile() {
      if (!this.token) return null
      try {
        const res = await getProfile()
        this.userInfo = res.data
        localStorage.setItem(USER_KEY, JSON.stringify(res.data))
        return res.data
      } catch {
        this.clearAuth()
        return null
      }
    },
  },
})
