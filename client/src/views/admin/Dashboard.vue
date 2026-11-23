<template>
  <div>
    <div class="cards">
      <div v-for="item in cards" :key="item.label" class="card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </div>
    </div>
    <div class="charts">
      <div class="page-card chart-card"><div ref="trendRef" class="chart"></div></div>
      <div class="page-card chart-card"><div ref="intentRef" class="chart"></div></div>
      <div class="page-card chart-card"><div ref="ticketRef" class="chart"></div></div>
      <div class="page-card chart-card"><div ref="saleRef" class="chart"></div></div>
    </div>
    <div class="page-card">
      <div class="page-head"><h2>最近订单</h2></div>
      <el-table :data="recent">
        <el-table-column prop="order_no" label="订单号" min-width="180" />
        <el-table-column prop="nickname" label="用户" min-width="100" />
        <el-table-column label="金额" min-width="110">
          <template #default="{ row }">¥{{ Number(row.total_amount).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="100" />
        <el-table-column label="下单时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.create_time) }}</template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, shallowRef } from 'vue'
import * as echarts from 'echarts'
import { getOverview } from '@/api'
import { formatDateTime } from '@/utils/format'

const data = ref(null)
const recent = ref([])
const trendRef = ref()
const intentRef = ref()
const ticketRef = ref()
const saleRef = ref()
const charts = shallowRef([])
const colors = ['#6d5efc', '#22c1c3', '#ff6b9a', '#ffb020', '#3d8bfd', '#7c5cff']

const cards = computed(() => {
  const item = data.value?.cards || {}
  return [
    { label: '用户总数', value: item.user_count || 0 },
    { label: '商品数量', value: item.product_count || 0 },
    { label: '订单数量', value: item.order_count || 0 },
    { label: '待处理工单', value: item.pending_ticket || 0 },
    { label: '知识条目', value: item.knowledge_count || 0 },
    { label: '今日订单', value: item.today_order || 0 },
    { label: '今日成交额', value: `¥${Number(item.today_amount || 0).toFixed(2)}` },
  ]
})

/** 绘制统计图表 */
function renderCharts() {
  charts.value.forEach((chart) => chart.dispose())
  const trend = echarts.init(trendRef.value)
  const intent = echarts.init(intentRef.value)
  const ticket = echarts.init(ticketRef.value)
  const sale = echarts.init(saleRef.value)
  const trendData = data.value.order_trend || []
  trend.setOption({
    color: colors,
    title: { text: '近7日订单', left: 12, top: 10, textStyle: { fontSize: 16 } },
    tooltip: { trigger: 'axis' },
    legend: { top: 12, right: 12 },
    grid: { left: 48, right: 24, bottom: 32, top: 64 },
    xAxis: { type: 'category', data: trendData.map((item) => item.date.slice(5)) },
    yAxis: [{ type: 'value' }, { type: 'value' }],
    series: [
      { name: '订单数', type: 'bar', data: trendData.map((item) => item.count), barWidth: 18, itemStyle: { borderRadius: 6 } },
      { name: '成交额', type: 'line', yAxisIndex: 1, smooth: true, data: trendData.map((item) => item.amount) },
    ],
  })
  const pie = (title, rows) => ({
    color: colors,
    title: { text: title, left: 12, top: 10, textStyle: { fontSize: 16 } },
    tooltip: { trigger: 'item' },
    legend: { bottom: 8 },
    series: [{ type: 'pie', radius: ['38%', '62%'], center: ['50%', '48%'], data: rows }],
  })
  intent.setOption(pie('咨询意图分布', data.value.intent_pie || []))
  ticket.setOption(pie('工单状态', data.value.ticket_status || []))
  sale.setOption({
    color: colors,
    title: { text: '分类销售额', left: 12, top: 10, textStyle: { fontSize: 16 } },
    tooltip: { trigger: 'axis' },
    grid: { left: 48, right: 16, bottom: 32, top: 58 },
    xAxis: { type: 'category', data: (data.value.category_sales || []).map((item) => item.name) },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: (data.value.category_sales || []).map((item) => item.value), barWidth: 22, itemStyle: { borderRadius: 8 } }],
  })
  charts.value = [trend, intent, ticket, sale]
}

/** 窗口变化时重绘 */
function resize() {
  charts.value.forEach((chart) => chart.resize())
}

onMounted(async () => {
  const res = await getOverview()
  data.value = res.data
  recent.value = res.data.recent_orders || []
  renderCharts()
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  charts.value.forEach((chart) => chart.dispose())
})
</script>

<style scoped>
.cards {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 10px 30px rgba(73, 68, 140, 0.06);
}

.card span {
  color: #8a90a6;
  font-size: 13px;
}

.card strong {
  display: block;
  margin-top: 8px;
  font-size: 22px;
  color: #5b4dff;
}

.charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.chart {
  height: 320px;
}

@media (max-width: 1200px) {
  .cards { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .charts { grid-template-columns: 1fr; }
}
</style>
