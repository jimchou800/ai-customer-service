<template>
  <div class="profile-page">
    <div class="page-head">
      <div>
        <h2>个人中心</h2>
        <p>{{ isAdmin ? '维护管理员资料，并定期更新登录密码' : '完善个人资料，方便客服更快识别你的账号' }}</p>
      </div>
    </div>

    <div class="profile-layout">
      <aside class="identity page-card">
        <div class="cover">
          <span class="orb orb-a"></span>
          <span class="orb orb-b"></span>
        </div>
        <div class="identity-body">
          <el-upload
            class="avatar-uploader"
            :show-file-list="false"
            accept="image/*"
            :disabled="avatarLoading"
            :http-request="onAvatar"
          >
            <div class="avatar-box" v-loading="avatarLoading">
              <el-avatar :size="104" :src="store.avatar">{{ initial }}</el-avatar>
              <div class="avatar-hover">
                <el-icon><Camera /></el-icon>
                <span>更换头像</span>
              </div>
            </div>
          </el-upload>
          <h3>{{ store.nickname || '未设置昵称' }}</h3>
          <span class="role-pill" :class="isAdmin ? 'is-admin' : 'is-user'">
            {{ isAdmin ? '管理员' : '普通用户' }}
          </span>
          <ul class="meta">
            <li>
              <el-icon><User /></el-icon>
              <span>用户名</span>
              <b>{{ store.user?.username || '-' }}</b>
            </li>
            <li>
              <el-icon><Male v-if="profile.gender !== '女'" /><Female v-else /></el-icon>
              <span>性别</span>
              <b>{{ profile.gender || '男' }}</b>
            </li>
            <li>
              <el-icon><Iphone /></el-icon>
              <span>手机号</span>
              <b>{{ profile.phone || '未填写' }}</b>
            </li>
            <li>
              <el-icon><Message /></el-icon>
              <span>邮箱</span>
              <b>{{ profile.email || '未填写' }}</b>
            </li>
            <li>
              <el-icon><Calendar /></el-icon>
              <span>注册时间</span>
              <b>{{ joinTime }}</b>
            </li>
          </ul>
        </div>
      </aside>

      <section class="editor page-card">
        <div class="switch">
          <button type="button" :class="{ active: tab === 'profile' }" @click="tab = 'profile'">
            <el-icon><EditPen /></el-icon>
            个人资料
          </button>
          <button type="button" :class="{ active: tab === 'password' }" @click="tab = 'password'">
            <el-icon><Lock /></el-icon>
            密码修改
          </button>
        </div>

        <div v-show="tab === 'profile'" class="panel">
          <div class="panel-intro">
            <h3>编辑个人资料</h3>
            <p>昵称会显示在右上角。性别默认为男，手机号和邮箱选填。</p>
          </div>
          <el-form ref="profileRef" :model="profile" :rules="profileRules" label-position="top" class="inner-form">
            <el-form-item label="昵称" prop="nickname">
              <el-input v-model="profile.nickname" size="large" maxlength="50" placeholder="请输入昵称" :prefix-icon="User" />
            </el-form-item>
            <el-form-item label="性别" prop="gender">
              <div class="gender-pick">
                <button type="button" :class="{ on: profile.gender === '男' }" @click="profile.gender = '男'">
                  <el-icon><Male /></el-icon>
                  男
                </button>
                <button type="button" :class="{ on: profile.gender === '女' }" @click="profile.gender = '女'">
                  <el-icon><Female /></el-icon>
                  女
                </button>
              </div>
            </el-form-item>
            <div class="field-row">
              <el-form-item label="手机号" prop="phone">
                <el-input v-model="profile.phone" size="large" maxlength="11" placeholder="选填，11位手机号" :prefix-icon="Iphone" />
              </el-form-item>
              <el-form-item label="邮箱" prop="email">
                <el-input v-model="profile.email" size="large" maxlength="100" placeholder="选填，用于接收通知" :prefix-icon="Message" />
              </el-form-item>
            </div>
            <el-form-item>
              <el-button type="primary" size="large" class="submit" :loading="profileSaving" @click="saveProfile">保存资料</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div v-show="tab === 'password'" class="panel">
          <div class="panel-intro">
            <h3>修改登录密码</h3>
            <p>请先核对原密码。新密码长度为 6 到 20 位，并需要再次确认。</p>
          </div>
          <el-form ref="passwordRef" :model="password" :rules="passwordRules" label-position="top" class="inner-form password-form">
            <el-form-item label="原密码" prop="old_password">
              <el-input v-model="password.old_password" size="large" type="password" show-password placeholder="请输入当前密码" :prefix-icon="Lock" />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="password.new_password" size="large" type="password" show-password maxlength="20" placeholder="6 到 20 位" :prefix-icon="Key" />
              <div class="strength" :class="`level-${strength}`">
                <span></span>
                <span></span>
                <span></span>
                <em>{{ strengthText }}</em>
              </div>
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="password.confirm_password" size="large" type="password" show-password maxlength="20" placeholder="请再次输入新密码" :prefix-icon="Key" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" class="submit" :loading="passwordSaving" @click="savePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
          <div class="tips">
            <strong>安全提示</strong>
            <p>不要使用与用户名相同的密码，建议同时包含字母和数字。</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { Calendar, Camera, EditPen, Female, Iphone, Key, Lock, Male, Message, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { updatePassword, updateProfile, uploadAvatar } from '@/api'
import { useUserStore } from '@/stores/user'
import { formatDateTime } from '@/utils/format'

const store = useUserStore()
const profileRef = ref()
const passwordRef = ref()
const tab = ref('profile')
const avatarLoading = ref(false)
const profileSaving = ref(false)
const passwordSaving = ref(false)
const profile = reactive({ nickname: '', gender: '男', phone: '', email: '' })
const password = reactive({ old_password: '', new_password: '', confirm_password: '' })

const isAdmin = computed(() => store.role === 'admin')
const initial = computed(() => (store.nickname || '用').slice(0, 1))
const joinTime = computed(() => formatDateTime(store.user?.create_time) || '-')

/** 根据新密码长度和字符组合给出强度 */
const strength = computed(() => {
  const value = password.new_password
  if (!value) return 0
  let score = 1
  if (value.length >= 8) score += 1
  if (/[A-Za-z]/.test(value) && /\d/.test(value)) score += 1
  return Math.min(score, 3)
})
const strengthText = computed(() => ['请设置新密码', '强度较弱', '强度适中', '强度较好'][strength.value])

const profileRules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  phone: [{ pattern: /^$|^1\d{10}$/, message: '请输入11位手机号', trigger: 'blur' }],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
}
const passwordRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [{ required: true, min: 6, max: 20, message: '新密码长度为6到20位', trigger: 'blur' }],
  confirm_password: [{
    required: true,
    validator: (rule, value, callback) => {
      if (!value) callback(new Error('请再次输入新密码'))
      else if (value !== password.new_password) callback(new Error('两次输入的密码不一致'))
      else callback()
    },
    trigger: 'blur',
  }],
}

/** 用当前用户填充表单 */
function fillProfile() {
  profile.nickname = store.user?.nickname || ''
  profile.gender = store.user?.gender || '男'
  profile.phone = store.user?.phone || ''
  profile.email = store.user?.email || ''
}

/** 上传头像 */
async function onAvatar(option) {
  avatarLoading.value = true
  try {
    const res = await uploadAvatar(option.file)
    store.setUser(res.data)
    ElMessage.success('头像已更新')
  } finally {
    avatarLoading.value = false
  }
}

/** 保存个人资料 */
async function saveProfile() {
  await profileRef.value.validate()
  profileSaving.value = true
  try {
    const res = await updateProfile(profile)
    store.setUser(res.data)
    ElMessage.success('资料已更新')
  } finally {
    profileSaving.value = false
  }
}

/** 修改密码 */
async function savePassword() {
  await passwordRef.value.validate()
  passwordSaving.value = true
  try {
    await updatePassword(password)
    password.old_password = ''
    password.new_password = ''
    password.confirm_password = ''
    ElMessage.success('密码已修改')
  } finally {
    passwordSaving.value = false
  }
}

onMounted(fillProfile)
</script>

<style scoped>
.profile-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.identity {
  width: 340px;
  flex: 0 0 340px;
  padding: 0 0 8px;
  overflow: hidden;
}

.cover {
  position: relative;
  height: 118px;
  background: linear-gradient(125deg, #5b4df0 0%, #7a6bff 48%, #2ec5c8 100%);
}

.orb {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.16);
}

.orb-a {
  width: 120px;
  height: 120px;
  right: -24px;
  top: -36px;
}

.orb-b {
  width: 72px;
  height: 72px;
  left: 28px;
  bottom: -28px;
}

.identity-body {
  margin-top: -52px;
  padding: 0 22px 18px;
  text-align: center;
}

.avatar-uploader {
  display: inline-flex;
}

.avatar-box {
  position: relative;
  width: 104px;
  height: 104px;
  border-radius: 50%;
  padding: 4px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(80, 70, 180, 0.18);
  cursor: pointer;
}

.avatar-box :deep(.el-avatar) {
  width: 96px;
  height: 96px;
  font-size: 32px;
  background: linear-gradient(145deg, #7d70ff, #4f43e0);
}

.avatar-hover {
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  color: #fff;
  background: rgba(31, 27, 74, 0.55);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.avatar-box:hover .avatar-hover {
  opacity: 1;
}

.avatar-hover span {
  font-size: 12px;
}

.identity-body h3 {
  margin: 14px 0 8px;
  font-size: 22px;
}

.role-pill {
  display: inline-flex;
  align-items: center;
  height: 26px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.role-pill.is-admin {
  color: #6d4b16;
  background: #fff1d6;
}

.role-pill.is-user {
  color: #1d6b62;
  background: #e5f8f4;
}

.meta {
  margin: 22px 0 0;
  padding: 4px 0 0;
  list-style: none;
  text-align: left;
  border-top: 1px solid #f0f1f6;
}

.meta li {
  display: grid;
  grid-template-columns: 18px 72px 1fr;
  align-items: center;
  gap: 8px;
  min-height: 42px;
  color: #8b90a3;
  font-size: 13px;
}

.meta b {
  color: #2a3042;
  font-weight: 600;
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.editor {
  flex: 1;
  min-width: 0;
  padding: 18px 22px 22px;
}

.switch {
  display: inline-flex;
  gap: 6px;
  padding: 5px;
  border-radius: 14px;
  background: #f4f5fb;
}

.switch button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 18px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: #6b7288;
  font-size: 14px;
  cursor: pointer;
}

.switch button.active {
  color: #fff;
  background: linear-gradient(135deg, #6d5efc, #8578ff);
  box-shadow: 0 8px 16px rgba(109, 94, 252, 0.28);
}

.panel {
  padding-top: 22px;
}

.panel-intro h3 {
  margin: 0;
  font-size: 18px;
}

.panel-intro p {
  margin: 6px 0 18px;
  color: #8a90a4;
  font-size: 13px;
}

.inner-form {
  max-width: 680px;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.gender-pick {
  display: flex;
  gap: 12px;
}

.gender-pick button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 108px;
  height: 42px;
  border: 1px solid #e6e8f2;
  border-radius: 12px;
  background: #fff;
  color: #5c6378;
  cursor: pointer;
}

.gender-pick button.on {
  color: #5b4df0;
  border-color: #c9c3ff;
  background: #f4f2ff;
}

.submit {
  min-width: 132px;
  border: 0;
  background: linear-gradient(135deg, #6d5efc, #8578ff);
}

.password-form {
  max-width: 460px;
}

.strength {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
}

.strength span {
  width: 56px;
  height: 4px;
  border-radius: 99px;
  background: #eceef5;
}

.strength em {
  margin-left: 4px;
  color: #9aa0b3;
  font-size: 12px;
  font-style: normal;
}

.strength.level-1 span:nth-child(1) {
  background: #ff8a80;
}

.strength.level-2 span:nth-child(-n + 2) {
  background: #ffb020;
}

.strength.level-3 span {
  background: #22b07d;
}

.tips {
  max-width: 460px;
  margin-top: 4px;
  padding: 14px 16px;
  border-radius: 14px;
  background: #f7f8fd;
}

.tips strong {
  display: block;
  margin-bottom: 4px;
  font-size: 13px;
}

.tips p {
  margin: 0;
  color: #8a90a4;
  font-size: 13px;
  line-height: 1.6;
}

@media (max-width: 980px) {
  .profile-layout {
    flex-direction: column;
  }

  .identity {
    width: 100%;
    flex-basis: auto;
  }

  .field-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
}
</style>
