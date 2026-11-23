<template>
  <div class="page-card">
    <div class="page-head">
      <div><h2>商品管理</h2><p>维护在售商品、库存和图片</p></div>
      <el-button type="primary" @click="open()">新增商品</el-button>
    </div>
    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="商品名称" clearable style="width: 220px" />
      <el-select v-model="query.category" placeholder="分类" clearable style="width: 140px">
        <el-option v-for="item in productCategories" :key="item" :label="item" :value="item" />
      </el-select>
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 120px">
        <el-option label="上架" value="1" />
        <el-option label="下架" value="0" />
      </el-select>
      <el-button type="primary" @click="load(1)">查询</el-button>
    </div>
    <el-table :data="list">
      <el-table-column label="图片" min-width="90">
        <template #default="{ row }"><el-image :src="row.image" style="width: 52px; height: 52px; border-radius: 8px" fit="cover" /></template>
      </el-table-column>
      <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
      <el-table-column prop="category" label="分类" min-width="100" />
      <el-table-column label="单价" min-width="110"><template #default="{ row }">¥{{ Number(row.price).toFixed(2) }}</template></el-table-column>
      <el-table-column prop="stock" label="库存" min-width="90" />
      <el-table-column label="状态" min-width="90"><template #default="{ row }"><el-tag :type="row.status ? 'success' : 'info'">{{ row.status ? '上架' : '下架' }}</el-tag></template></el-table-column>
      <el-table-column label="更新时间" min-width="180"><template #default="{ row }">{{ formatDateTime(row.update_time) }}</template></el-table-column>
      <el-table-column label="操作" min-width="160">
        <template #default="{ row }">
          <el-button link type="primary" @click="open(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pager"><el-pagination background layout="total, prev, pager, next" :total="total" :page-size="query.page_size" :current-page="query.page" @current-change="load" /></div>
    <el-dialog v-model="visible" :title="form.id ? '编辑商品' : '新增商品'" width="640px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" style="width: 100%"><el-option v-for="item in productCategories" :key="item" :label="item" :value="item" /></el-select>
        </el-form-item>
        <el-form-item label="单价" prop="price"><el-input-number v-model="form.price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="库存" prop="stock"><el-input-number v-model="form.stock" :min="0" /></el-form-item>
        <el-form-item label="状态"><el-radio-group v-model="form.status"><el-radio :value="1">上架</el-radio><el-radio :value="0">下架</el-radio></el-radio-group></el-form-item>
        <el-form-item label="图片">
          <el-upload :show-file-list="false" accept="image/*" :http-request="onImage">
            <el-image v-if="form.image" :src="form.image" style="width: 88px; height: 88px; border-radius: 10px" fit="cover" />
            <el-button v-else>上传图片</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
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
import { deleteProduct, getProducts, saveProduct, uploadImage } from '@/api'
import { formatDateTime } from '@/utils/format'
import { productCategories } from '@/utils/options'

const list = ref([])
const total = ref(0)
const visible = ref(false)
const formRef = ref()
const query = reactive({ page: 1, page_size: 10, keyword: '', category: '', status: '' })
const form = reactive({ id: null, name: '', category: '数码', price: 0, stock: 0, image: '', description: '', status: 1 })
const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
}

/** 加载商品列表 */
async function load(page) {
  if (page) query.page = page
  const res = await getProducts(query)
  list.value = res.data.list
  total.value = res.data.total
}

/** 打开编辑框 */
function open(row) {
  Object.assign(form, row || { id: null, name: '', category: '数码', price: 0, stock: 0, image: '', description: '', status: 1 })
  visible.value = true
}

/** 上传商品图 */
async function onImage(option) {
  const res = await uploadImage(option.file, 'product')
  form.image = res.data.url
}

/** 保存商品 */
async function save() {
  await formRef.value.validate()
  await saveProduct(form, form.id)
  ElMessage.success('保存成功')
  visible.value = false
  load()
}

/** 删除商品 */
async function remove(row) {
  await ElMessageBox.confirm(`确定删除 ${row.name} 吗？`, '提示', { type: 'warning' })
  await deleteProduct(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(() => load())
</script>
