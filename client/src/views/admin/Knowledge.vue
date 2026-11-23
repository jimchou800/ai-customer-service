<template>
  <div class="page-card">
    <div class="page-head">
      <div><h2>知识库管理</h2><p>维护电商政策，并同步到 Chroma 向量库</p></div>
      <div>
        <el-button @click="searchVisible = true">检索测试</el-button>
        <el-button @click="rebuild">重建索引</el-button>
        <el-button type="primary" @click="open()">新增知识</el-button>
      </div>
    </div>
    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="标题或内容" clearable style="width: 220px" />
      <el-select v-model="query.category" placeholder="分类" clearable style="width: 160px">
        <el-option v-for="item in knowledgeCategories" :key="item" :label="item" :value="item" />
      </el-select>
      <el-button type="primary" @click="load(1)">查询</el-button>
    </div>
    <el-table :data="list">
      <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
      <el-table-column prop="category" label="分类" min-width="110" />
      <el-table-column prop="vector_status" label="向量状态" min-width="110" />
      <el-table-column prop="chunk_count" label="切片数" min-width="90" />
      <el-table-column label="更新时间" min-width="180"><template #default="{ row }">{{ formatDateTime(row.update_time) }}</template></el-table-column>
      <el-table-column label="操作" min-width="220">
        <template #default="{ row }">
          <el-button link type="primary" @click="open(row)">编辑</el-button>
          <el-button link type="primary" @click="vectorize(row)">向量化</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pager"><el-pagination background layout="total, prev, pager, next" :total="total" :page-size="query.page_size" :current-page="query.page" @current-change="load" /></div>
    <el-dialog v-model="visible" :title="form.id ? '编辑知识' : '新增知识'" width="760px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="标题" prop="title"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" style="width: 100%"><el-option v-for="item in knowledgeCategories" :key="item" :label="item" :value="item" /></el-select>
        </el-form-item>
        <el-form-item label="文件">
          <el-upload :show-file-list="false" accept=".txt,.md,.pdf,.docx" :http-request="onFile">
            <el-button>上传并解析文档</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="正文" prop="content"><el-input v-model="form.content" type="textarea" :rows="10" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="searchVisible" title="检索测试" width="680px">
      <el-input v-model="searchText" placeholder="输入问题，例如：退货要几天" @keyup.enter="doSearch" />
      <el-button type="primary" style="margin-top: 12px" @click="doSearch">检索</el-button>
      <div v-for="item in searchResult" :key="item.content" class="hit">
        <b>{{ item.category }} / {{ item.title }}</b>
        <p>{{ item.content }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deleteKnowledge, getKnowledge, rebuildKnowledge, saveKnowledge, searchKnowledge, uploadKnowledgeFile, vectorizeKnowledge } from '@/api'
import { formatDateTime } from '@/utils/format'
import { knowledgeCategories } from '@/utils/options'

const list = ref([])
const total = ref(0)
const visible = ref(false)
const searchVisible = ref(false)
const searchText = ref('')
const searchResult = ref([])
const formRef = ref()
const query = reactive({ page: 1, page_size: 10, keyword: '', category: '' })
const form = reactive({ id: null, title: '', category: '优惠政策', content: '', source_file: '' })
const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  content: [{ required: true, message: '请输入正文', trigger: 'blur' }],
}

/** 加载知识列表 */
async function load(page) {
  if (page) query.page = page
  const res = await getKnowledge(query)
  list.value = res.data.list
  total.value = res.data.total
}

/** 打开编辑框 */
function open(row) {
  Object.assign(form, row || { id: null, title: '', category: '优惠政策', content: '', source_file: '' })
  visible.value = true
}

/** 解析上传文档 */
async function onFile(option) {
  const res = await uploadKnowledgeFile(option.file)
  form.content = res.data.content
  form.source_file = res.data.source_file
  if (!form.title) form.title = (res.data.filename || '').replace(/\.[^.]+$/, '')
  ElMessage.success('文档已解析')
}

/** 保存知识 */
async function save() {
  await formRef.value.validate()
  const res = await saveKnowledge(form, form.id)
  ElMessage.success(res.msg || '保存成功')
  visible.value = false
  load()
}

/** 单条向量化 */
async function vectorize(row) {
  const res = await vectorizeKnowledge(row.id)
  ElMessage.success(res.msg || '向量化完成')
  load()
}

/** 重建全部索引 */
async function rebuild() {
  await ElMessageBox.confirm('将清空并重建全部向量，是否继续？', '提示', { type: 'warning' })
  const res = await rebuildKnowledge()
  ElMessage.success(`成功 ${res.data.success} 条，失败 ${res.data.failed} 条`)
  load()
}

/** 删除知识 */
async function remove(row) {
  await ElMessageBox.confirm(`确定删除 ${row.title} 吗？`, '提示', { type: 'warning' })
  await deleteKnowledge(row.id)
  load()
}

/** 检索测试 */
async function doSearch() {
  if (!searchText.value.trim()) return
  const res = await searchKnowledge({ query: searchText.value, top_k: 4 })
  searchResult.value = res.data || []
}

onMounted(() => load())
</script>

<style scoped>
.hit {
  margin-top: 12px;
  padding: 10px 12px;
  background: #f6f7fb;
  border-radius: 10px;
}
.hit p { margin: 6px 0 0; color: #606266; line-height: 1.6; }
</style>
