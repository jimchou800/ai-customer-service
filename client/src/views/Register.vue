<template>
  <div class="auth-page">
    <BrandPanel />
    <section class="auth-right">
      <div class="auth-card">
        <div class="hello">
          <img src="@/assets/logos/shield.svg" alt="" />
          <div>
            <h2>创建账号</h2>
            <p>注册后即可咨询智能客服</p>
          </div>
        </div>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @keyup.enter="submit">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="3到20位字母或数字" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" show-password placeholder="至少6位" />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirm_password">
            <el-input v-model="form.confirm_password" type="password" show-password placeholder="再次输入密码" />
          </el-form-item>
          <el-form-item label="昵称" prop="nickname">
            <el-input v-model="form.nickname" placeholder="请输入昵称" />
          </el-form-item>
          <el-form-item label="性别" prop="gender">
            <el-radio-group v-model="form.gender">
              <el-radio value="男">男</el-radio>
              <el-radio value="女">女</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="手机号">
            <el-input v-model="form.phone" placeholder="选填" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="form.email" placeholder="选填" />
          </el-form-item>
          <el-button class="submit" type="primary" :loading="loading" @click="submit">注 册</el-button>
        </el-form>
        <div class="extra">已有账号？<router-link to="/login">返回登录</router-link></div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import BrandPanel from '@/components/BrandPanel.vue'
import { register } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const store = useUserStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
  confirm_password: '',
  nickname: '',
  gender: '男',
  phone: '',
  email: '',
})
const rules = {
  username: [{ required: true, min: 3, max: 20, message: '用户名长度为3到20位', trigger: 'blur' }],
  password: [{ required: true, min: 6, max: 20, message: '密码至少6位', trigger: 'blur' }],
  confirm_password: [{
    validator: (rule, value, callback) => {
      if (value !== form.password) callback(new Error('两次输入的密码不一致'))
      else callback()
    },
    trigger: 'blur',
  }],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
}

/** 提交注册 */
async function submit() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await register(form)
    store.setLogin(res.data)
    ElMessage.success('注册成功')
    router.push('/user/chat')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  min-height: 100vh;
}

.auth-right {
  width: 640px;
  flex: 0 0 640px;
  height: 100vh;
  overflow: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at 18% 16%, rgba(109, 94, 252, 0.16), transparent 36%),
    radial-gradient(circle at 86% 84%, rgba(255, 93, 143, 0.16), transparent 34%),
    #f7f8fd;
}

.auth-card {
  width: 480px;
  margin: 28px 0;
  padding: 32px 0;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 24px 60px rgba(78, 64, 176, 0.14);
}

.hello,
.extra {
  padding: 0 28px;
}

.auth-right :deep(.el-form) {
  width: 480px;
  padding: 0 28px;
  box-sizing: border-box;
}

.hello {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.hello img {
  width: 48px;
  height: 48px;
}

.hello h2 {
  margin: 0;
  font-size: 28px;
  background: linear-gradient(90deg, #6d5efc, #ff5d8f);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hello p {
  margin: 4px 0 0;
  color: #8a90a6;
}

.submit {
  width: 100%;
  height: 46px;
  border: none;
  border-radius: 14px;
  letter-spacing: 4px;
  background: linear-gradient(90deg, #6d5efc, #ff5d8f);
}

.extra {
  margin-top: 14px;
  text-align: center;
  color: #8a90a6;
}
</style>
