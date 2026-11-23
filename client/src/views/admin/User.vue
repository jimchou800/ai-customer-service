<template>
  <div class="page-card">
    <div class="page-head">
      <div><h2>用户管理</h2><p>维护管理员和普通用户</p></div>
      <el-button type="primary" @click="open()">新增用户</el-button>
    </div>
    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="用户名 / 昵称 / 手机" clearable style="width: 240px" />
      <el-select v-model="query.role" placeholder="角色" clearable style="width: 140px">
        <el-option label="管理员" value="admin" />
        <el-option label="普通用户" value="user" />
      </el-select>
      <el-button type="primary" @click="load(1)">查询</el-button>
    </div>
    <el-table :data="list">
      <el-table-column label="头像" min-width="80">
        <template #default="{ row }"><el-avatar :size="36" :src="row.avatar">{{ row.nickname.slice(0, 1) }}</el-avatar></template>
      </el-table-column>
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="nickname" label="昵称" min-width="120" />
      <el-table-column prop="gender" label="性别" min-width="80" />
      <el-table-column prop="phone" label="手机号" min-width="130" />
      <el-table-column label="角色" min-width="100"><template #default="{ row }">{{ row.role === 'admin' ? '管理员' : '普通用户' }}</template></el-table-column>
      <el-table-column label="状态" min-width="90"><template #default="{ row }"><el-tag :type="row.status ? 'success' : 'info'">{{ row.status ? '正常' : '禁用' }}</el-tag></template></el-table-column>
      <el-table-column label="注册时间" min-width="180"><template #default="{ row }">{{ formatDateTime(row.create_time) }}</template></el-table-column>
      <el-table-column label="操作" min-width="220">
        <template #default="{ row }">
          <el-button link type="primary" @click="open(row)">编辑</el-button>
          <el-button link type="primary" @click="reset(row)">重置密码</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pager"><el-pagination background layout="total, prev, pager, next" :total="total" :page-size="query.page_size" :current-page="query.page" @current-change="load" /></div>
    <el-dialog v-model="visible" :title="form.id ? '编辑用户' : '新增用户'" width="560px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="用户名" prop="username"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="昵称" prop="nickname"><el-input v-model="form.nickname" /></el-form-item>
        <el-form-item label="密码" prop="password"><el-input v-model="form.password" type="password" show-password placeholder="新增默认123456，编辑留空则不修改" /></el-form-item>
        <el-form-item label="确认密码" prop="confirm_password"><el-input v-model="form.confirm_password" type="password" show-password /></el-form-item>
        <el-form-item label="性别"><el-radio-group v-model="form.gender"><el-radio value="男">男</el-radio><el-radio value="女">女</el-radio></el-radio-group></el-form-item>
        <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="角色"><el-radio-group v-model="form.role"><el-radio value="user">普通用户</el-radio><el-radio value="admin">管理员</el-radio></el-radio-group></el-form-item>
        <el-form-item label="状态"><el-radio-group v-model="form.status"><el-radio :value="1">正常</el-radio><el-radio :value="0">禁用</el-radio></el-radio-group></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deleteUser, getUsers, resetUserPassword, saveUser } from '@/api'
import { formatDateTime } from '@/utils/format'

const list = ref([])
const total = ref(0)
const visible = ref(false)
const formRef = ref()
const query = reactive({ page: 1, page_size: 10, keyword: '', role: '' })
const empty = { id: null, username: '', nickname: '', password: '', confirm_password: '', gender: '男', phone: '', email: '', role: 'user', status: 1 }
const form = reactive({ ...empty })
const rules = {
  username: [{ required: true, min: 3, message: '用户名至少3位', trigger: 'blur' }],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  confirm_password: [{
    validator: (rule, value, callback) => {
      if ((form.password || value) && value !== form.password) callback(new Error('两次输入的密码不一致'))
      else callback()
    },
    trigger: 'blur',
  }],
}

/** 加载用户 */
async function load(page) {
  if (page) query.page = page
  const res = await getUsers(query)
  list.value = res.data.list
  total.value = res.data.total
}

/** 打开编辑框 */
function open(row) {
  Object.assign(form, empty, row || {}, { password: '', confirm_password: '' })
  visible.value = true
}

/** 保存用户 */
async function save() {
  await formRef.value.validate()
  await saveUser(form, form.id)
  ElMessage.success('保存成功')
  visible.value = false
  load()
}

/** 重置密码 */
async function reset(row) {
  await ElMessageBox.confirm(`确定把 ${row.nickname} 的密码重置为 123456 吗？`, '提示', { type: 'warning' })
  await resetUserPassword(row.id)
  ElMessage.success('已重置为123456')
}

/** 删除用户 */
async function remove(row) {
  await ElMessageBox.confirm(`确定删除 ${row.nickname} 吗？`, '提示', { type: 'warning' })
  await deleteUser(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(() => load())
</script>
