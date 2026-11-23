import { defineStore } from 'pinia'

/** 读取本地用户，数据损坏时清掉，避免首页导航中断后白屏 */
function readCachedUser() {
  const raw = localStorage.getItem('user')
  if (!raw) {
    localStorage.removeItem('token')
    return null
  }
  try {
    const data = JSON.parse(raw)
    if (!data || typeof data !== 'object' || (data.role !== 'admin' && data.role !== 'user')) {
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      return null
    }
    return data
  } catch {
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    return null
  }
}

/** 登录用户状态 */
export const useUserStore = defineStore('user', {
  state: () => {
    const user = readCachedUser()
    return {
      token: user ? localStorage.getItem('token') || '' : '',
      user,
    }
  },
  getters: {
    role: (state) => state.user?.role || '',
    nickname: (state) => state.user?.nickname || '',
    avatar: (state) => state.user?.avatar || '',
  },
  actions: {
    /** 保存登录结果 */
    setLogin(data) {
      this.token = data.token
      this.user = data.user
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))
    },
    /** 刷新本地用户资料 */
    setUser(user) {
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    /** 退出登录 */
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
  },
})
