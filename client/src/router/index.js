import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import TopLayout from '@/layout/TopLayout.vue'
import Login from '@/views/Login.vue'

/** 当前登录角色对应的首页 */
function homePath(store) {
  return store.role === 'admin' ? '/admin/dashboard' : '/user/chat'
}

/** 令牌和角色必须同时有效，否则视为未登录 */
function isLoggedIn(store) {
  return Boolean(store.token) && (store.role === 'admin' || store.role === 'user')
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login },
    { path: '/register', component: () => import('@/views/Register.vue') },
    {
      path: '/',
      component: TopLayout,
      children: [
        { path: '', redirect: '/login' },
        { path: 'admin/dashboard', component: () => import('@/views/admin/Dashboard.vue'), meta: { role: 'admin', title: '控制台' } },
        { path: 'admin/chat', component: () => import('@/views/admin/ChatConsole.vue'), meta: { role: 'admin', title: '智能客服' } },
        { path: 'admin/products', component: () => import('@/views/admin/Product.vue'), meta: { role: 'admin', title: '商品管理' } },
        { path: 'admin/orders', component: () => import('@/views/admin/Order.vue'), meta: { role: 'admin', title: '订单管理' } },
        { path: 'admin/knowledge', component: () => import('@/views/admin/Knowledge.vue'), meta: { role: 'admin', title: '知识库管理' } },
        { path: 'admin/tickets', component: () => import('@/views/admin/Ticket.vue'), meta: { role: 'admin', title: '工单管理' } },
        { path: 'admin/users', component: () => import('@/views/admin/User.vue'), meta: { role: 'admin', title: '用户管理' } },
        { path: 'admin/profile', component: () => import('@/views/Profile.vue'), meta: { role: 'admin', title: '个人中心' } },
        { path: 'user/chat', component: () => import('@/views/user/Chat.vue'), meta: { role: 'user', title: '智能客服' } },
        { path: 'user/profile', component: () => import('@/views/Profile.vue'), meta: { role: 'user', title: '个人中心' } },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/login' },
  ],
})

/** 按登录状态和角色拦截页面，失败时回到登录页，避免停在空白页 */
router.beforeEach((to) => {
  try {
    const store = useUserStore()
    if (store.token && !isLoggedIn(store)) store.logout()
    const publicPage = to.path === '/login' || to.path === '/register'
    if (publicPage) {
      return isLoggedIn(store) ? homePath(store) : true
    }
    if (!isLoggedIn(store)) return '/login'
    if (to.path === '/' || (to.meta.role && to.meta.role !== store.role)) {
      const target = homePath(store)
      return to.path === target ? true : target
    }
    return true
  } catch {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    return to.path === '/login' ? true : '/login'
  }
})

/** 动态页面加载失败时重新进入目标页，避免路由中断后白屏 */
router.onError((error, to) => {
  const message = String(error?.message || error || '')
  const failed = message.includes('Failed to fetch dynamically imported module') || message.includes('Importing a module script failed')
  if (failed && to?.fullPath && sessionStorage.getItem('route-reload') !== to.fullPath) {
    sessionStorage.setItem('route-reload', to.fullPath)
    window.location.assign(to.fullPath)
  }
})

export default router
