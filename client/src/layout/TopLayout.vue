<template>
  <div class="site">
    <header class="topbar">
      <div class="brand" @click="goHome">
        <img src="@/assets/logos/ai.svg" alt="logo" />
        <div>
          <strong>基于LangGraph的AI智能电商客服系统</strong>
          <span>多Agent协作 · RAG知识库</span>
        </div>
      </div>
      <el-menu mode="horizontal" :default-active="route.path" router :ellipsis="false" class="nav">
        <el-menu-item v-for="item in menus" :key="item.path" :index="item.path">{{ item.label }}</el-menu-item>
      </el-menu>
      <el-dropdown trigger="click" @command="onCommand">
        <div class="user-entry">
          <el-avatar :size="36" :src="store.avatar">{{ store.nickname.slice(0, 1) }}</el-avatar>
          <span>{{ store.nickname }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人中心</el-dropdown-item>
            <el-dropdown-item command="logout" divided>安全退出</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </header>
    <main class="page-body">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()

const adminMenus = [
  { path: '/admin/dashboard', label: '控制台' },
  { path: '/admin/chat', label: '智能客服' },
  { path: '/admin/products', label: '商品管理' },
  { path: '/admin/orders', label: '订单管理' },
  { path: '/admin/knowledge', label: '知识库管理' },
  { path: '/admin/tickets', label: '工单管理' },
  { path: '/admin/users', label: '用户管理' },
]
const userMenus = [
  { path: '/user/chat', label: '智能客服' },
  { path: '/user/profile', label: '个人中心' },
]
const menus = computed(() => (store.role === 'admin' ? adminMenus : userMenus))

/** 回到当前角色首页 */
function goHome() {
  router.push(store.role === 'admin' ? '/admin/dashboard' : '/user/chat')
}

/** 处理右上角下拉菜单 */
function onCommand(command) {
  if (command === 'profile') {
    router.push(store.role === 'admin' ? '/admin/profile' : '/user/profile')
    return
  }
  store.logout()
  router.push('/login')
}
</script>

<style scoped>
.site {
  min-height: 100vh;
  background: #f3f5fb;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  height: 72px;
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 0 28px;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #eceef8;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  min-width: 280px;
}

.brand img {
  width: 42px;
  height: 42px;
}

.brand strong {
  display: block;
  font-size: 15px;
  line-height: 1.2;
}

.brand span {
  color: #8b90a5;
  font-size: 12px;
}

.nav {
  flex: 1;
  border-bottom: none;
  background: transparent;
  min-width: 0;
}

.user-entry {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  outline: none;
  color: #303133;
}

.page-body {
  padding: 20px 28px 32px;
}
</style>
