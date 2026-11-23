<template>
  <div class="page-card">
    <div class="page-head"><div><h2>订单管理</h2><p>查看订单、发货并更新状态</p></div></div>
    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="订单号 / 用户" clearable style="width: 220px" />
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px">
        <el-option v-for="item in orderStatus" :key="item" :label="item" :value="item" />
      </el-select>
      <el-button type="primary" @click="load(1)">查询</el-button>
    </div>
    <el-table :data="list">
      <el-table-column prop="order_no" label="订单号" min-width="180" />
      <el-table-column prop="nickname" label="用户" min-width="100" />
      <el-table-column label="商品" min-width="180" show-overflow-tooltip>
        <template #default="{ row }">{{ row.items.map((item) => item.product_name).join('、') }}</template>
      </el-table-column>
      <el-table-column label="金额" min-width="110"><template #default="{ row }">¥{{ Number(row.total_amount).toFixed(2) }}</template></el-table-column>
      <el-table-column prop="status" label="状态" min-width="100" />
      <el-table-column prop="pay_method" label="支付方式" min-width="110" />
      <el-table-column label="下单时间" min-width="180"><template #default="{ row }">{{ formatDateTime(row.create_time) }}</template></el-table-column>
      <el-table-column label="操作" min-width="220">
        <template #default="{ row }">
          <el-button link type="primary" @click="detail = row">详情</el-button>
          <el-button link type="primary" @click="openShip(row)">发货</el-button>
          <el-dropdown @command="(status) => changeStatus(row, status)">
            <el-button link type="primary">改状态</el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-for="item in orderStatus" :key="item" :command="item">{{ item }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>
    <div class="pager"><el-pagination background layout="total, prev, pager, next" :total="total" :page-size="query.page_size" :current-page="query.page" @current-change="load" /></div>
    <el-dialog v-model="shipVisible" title="订单发货" width="480px">
      <el-form :model="ship" label-width="90px">
        <el-form-item label="物流公司"><el-input v-model="ship.logistics_company" /></el-form-item>
        <el-form-item label="物流单号"><el-input v-model="ship.logistics_no" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="shipVisible = false">取消</el-button>
        <el-button type="primary" @click="doShip">确认发货</el-button>
      </template>
    </el-dialog>
    <el-dialog :model-value="!!detail" title="订单详情" width="680px" @close="detail = null">
      <template v-if="detail">
        <p>收货人：{{ detail.receiver }} {{ detail.phone }}</p>
        <p>地址：{{ detail.address }}</p>
        <p>物流：{{ detail.logistics_company || '暂无' }} {{ detail.logistics_no }}</p>
        <p>支付时间：{{ formatDateTime(detail.pay_time) || '—' }}　发货时间：{{ formatDateTime(detail.ship_time) || '—' }}　完成时间：{{ formatDateTime(detail.finish_time) || '—' }}</p>
        <el-table :data="detail.items">
          <el-table-column prop="product_name" label="商品" min-width="160" />
          <el-table-column label="单价" min-width="100"><template #default="{ row }">¥{{ Number(row.price).toFixed(2) }}</template></el-table-column>
          <el-table-column prop="quantity" label="数量" min-width="80" />
        </el-table>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getOrders, shipOrder, updateOrderStatus } from '@/api'
import { formatDateTime } from '@/utils/format'
import { orderStatus } from '@/utils/options'

const list = ref([])
const total = ref(0)
const detail = ref(null)
const shipVisible = ref(false)
const current = ref(null)
const query = reactive({ page: 1, page_size: 10, keyword: '', status: '' })
const ship = reactive({ logistics_company: '顺丰速运', logistics_no: '' })

/** 加载订单 */
async function load(page) {
  if (page) query.page = page
  const res = await getOrders(query)
  list.value = res.data.list
  total.value = res.data.total
}

/** 打开发货窗口 */
function openShip(row) {
  current.value = row
  ship.logistics_company = row.logistics_company || '顺丰速运'
  ship.logistics_no = row.logistics_no || ''
  shipVisible.value = true
}

/** 提交发货 */
async function doShip() {
  if (!ship.logistics_company || !ship.logistics_no) {
    ElMessage.warning('请填写物流公司和单号')
    return
  }
  await shipOrder(current.value.id, ship)
  ElMessage.success('已发货')
  shipVisible.value = false
  load()
}

/** 修改订单状态 */
async function changeStatus(row, status) {
  await updateOrderStatus(row.id, status)
  ElMessage.success('状态已更新')
  load()
}

onMounted(() => load())
</script>
