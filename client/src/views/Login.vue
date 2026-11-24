<template>
  <div class="auth-page">
    <BrandPanel />
    <section class="auth-right">
      <div class="auth-card">
        <div class="hello">
          <img src="@/assets/logos/ai.svg" alt="" />
          <div>
            <h2>欢迎回来</h2>
            <p>登录后即可使用智能客服与管理功能</p>
          </div>
        </div>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="auth-form" @keyup.enter="submit">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" size="large" placeholder="请输入用户名" :prefix-icon="User" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" size="large" type="password" show-password placeholder="请输入密码" :prefix-icon="Lock" />
          </el-form-item>
          <el-button class="submit" type="primary" size="large" :loading="loading" @click="submit">登 录</el-button>
        </el-form>
        <div class="tips">
          <span>管理员 admin / 123456</span>
          <span>用户 zhangwei / 123456</span>
        </div>
        <div class="extra">还没有账号？<router-link to="/register">立即注册</router-link></div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Lock, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import BrandPanel from '@/components/BrandPanel.vue'
import { login } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const store = useUserStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

/** 提交登录 */
async function submit() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await login(form)
    store.setLogin(res.data)
    ElMessage.success('登录成功')
    router.push(res.data.user.role === 'admin' ? '/admin/dashboard' : '/user/chat')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(0, 1fr);
  min-height: 100vh;
  background: #f6f7fb;
}

.auth-right {
  width: auto;
  min-width: 0;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at 18% 16%, rgba(109, 94, 252, 0.16), transparent 36%),
    radial-gradient(circle at 86% 84%, rgba(255, 93, 143, 0.16), transparent 34%),
    #f7f8fd;
}

.auth-card {
  width: min(480px, calc(100% - 48px));
  padding: 42px 0 32px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 24px 60px rgba(78, 64, 176, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.hello,
.tips,
.extra {
  padding: 0 28px;
}

.hello {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-bottom: 26px;
}

.hello img {
  width: 54px;
  height: 54px;
}

.hello h2 {
  margin: 0;
  font-size: 30px;
  background: linear-gradient(90deg, #6d5efc, #ff5d8f);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hello p {
  margin: 6px 0 0;
  color: #8a90a6;
}

.auth-form {
  width: 100%;
  padding: 0 28px;
  box-sizing: border-box;
}

.auth-form :deep(.el-input__wrapper) {
  border-radius: 12px;
  min-height: 46px;
}

.submit {
  width: 100%;
  height: 48px;
  margin-top: 8px;
  border: none;
  border-radius: 14px;
  font-size: 16px;
  letter-spacing: 4px;
  background: linear-gradient(90deg, #6d5efc, #ff5d8f);
}

.submit:hover {
  opacity: 0.92;
}

.tips {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-top: 18px;
}

.tips span {
  flex: 1;
  text-align: center;
  padding: 8px 6px;
  border-radius: 999px;
  background: #f4f1ff;
  color: #6d5efc;
  font-size: 12px;
}

.extra {
  margin-top: 18px;
  text-align: center;
  color: #8a90a6;
}
</style>
