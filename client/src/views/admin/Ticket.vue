<template>
  <div class="page-card">
    <div class="page-head"><div><h2>工单管理</h2><p>处理用户升级上来的售后问题</p></div></div>
    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="工单号 / 标题 / 用户" clearable style="width: 240px" />
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px">
        <el-option v-for="item in ticketStatus" :key="item" :label="item" :value="item" />
      </el-select>
      <el-button type="primary" @click="load(1)">查询</el-button>
    </div>
    <el-table :data="list">
      <el-table-column prop="ticket_no" label="工单号" min-width="180" />
      <el-table-column prop="nickname" label="用户" min-width="100" />
      <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
      <el-table-column prop="category" label="分类" min-width="110" />
      <el-table-column prop="priority" label="优先级" min-width="90" />
      <el-table-column prop="status" label="状态" min-width="100" />
      <el-table-column label="创建时间" min-width="180"><template #default="{ row }">{{ formatDateTime(row.create_time) }}</template></el-table-column>
      <el-table-column label="操作" min-width="120">
        <template #default="{ row }"><el-button link type="primary" @click="open(row)">处理</el-button></template>
      </el-table-column>
    </el-table>
    <div class="pager"><el-pagination background layout="total, prev, pager, next" :total="total" :page-size="query.page_size" :current-page="query.page" @current-change="load" /></div>
    <el-dialog v-model="visible" title="处理工单" width="680px">
      <p><b>{{ form.title }}</b> · {{ form.ticket_no }}</p>
      <p class="desc">{{ form.content }}</p>
      <el-form label-width="80px">
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%"><el-option v-for="item in ticketStatus" :key="item" :label="item" :value="item" /></el-select>
        </el-form-item>
        <el-form-item label="回复"><el-input v-model="form.reply" type="textarea" :rows="5" /></el-form-item>
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
import { ElMessage } from 'element-plus'
import { getTickets, handleTicket } from '@/api'
import { formatDateTime } from '@/utils/format'
import { ticketStatus } from '@/utils/options'

const list = ref([])
const total = ref(0)
const visible = ref(false)
const query = reactive({ page: 1, page_size: 10, keyword: '', status: '' })
const form = reactive({ id: null, ticket_no: '', title: '', content: '', status: '处理中', reply: '' })

/** 加载工单 */
async function load(page) {
  if (page) query.page = page
  const res = await getTickets(query)
  list.value = res.data.list
  total.value = res.data.total
}

/** 打开处理窗口 */
function open(row) {
  Object.assign(form, row)
  visible.value = true
}

/** 保存处理结果 */
async function save() {
  await handleTicket(form.id, { status: form.status, reply: form.reply })
  ElMessage.success('工单已更新')
  visible.value = false
  load()
}

onMounted(() => load())
</script>

<style scoped>
.desc { color: #606266; line-height: 1.7; white-space: pre-wrap; }
</style>
