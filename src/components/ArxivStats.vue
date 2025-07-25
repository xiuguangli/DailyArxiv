<template>
  <div class="arxiv-stats">
    <h2>arXiv 统计</h2>
    <el-button
      size="small"
      @click="reloadData"
      class="refresh-btn"
      style="margin-bottom: 16px;"
    >刷新数据</el-button>
    <div class="stats-grid" style="grid-template-columns: 1fr 1fr;">
      <div class="chart-item">
        <div ref="monthChartRef" style="width: 100%; height: 320px;"></div>
        <div class="chart-title">按月统计</div>
      </div>
      <div class="chart-item">
        <div ref="dayChartRef" style="width: 100%; height: 320px;"></div>
        <div class="chart-title">按日统计</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const monthChartRef = ref(null)
const dayChartRef = ref(null)
let monthChart = null
let dayChart = null
const categories = ['cs.AI', 'cs.CV', 'cs.LG']

const rawData = ref([]) // {date, category, count}

function parseFileName(fileName) {
  // e.g. 2025-07-16_cs.AI.json
  const match = fileName.match(/(\d{4})-(\d{2})-(\d{2})_(.+)\.json$/)
  if (!match) return null
  return {
    year: match[1],
    month: match[2],
    day: match[3],
    category: match[4]
  }
}

async function loadAllData() {
  rawData.value = []
  try {
    // 只读取 public/arxiv/2025/ 下所有 json 文件
    const year = '2025'
    const monthDirs = ['07'] // 可扩展
    for (const month of monthDirs) {
      const days = [16, 17, 18] // 可扩展
      for (const day of days) {
        const dayStr = String(day).padStart(2, '0')
        const categories = ['cs.AI', 'cs.CV', 'cs.LG'] // 可扩展
        for (const cat of categories) {
          const url = `/arxiv/${year}/${month}/${year}-${month}-${dayStr}_${cat}.json`
          try {
            const resp = await fetch(url)
            if (!resp.ok) continue
            const papers = await resp.json()
            rawData.value.push({
              date: `${year}-${month}-${dayStr}`,
              year,
              month,
              day: dayStr,
              category: cat,
              count: papers.length
            })
          } catch (e) {
            // 文件不存在跳过
          }
        }
      }
    }
  } catch (e) {
    ElMessage.error('数据加载失败')
  }
}

function getMonthOption() {
  // x轴为年月，y轴为数量，三个类别为堆叠柱状图
  const map = {}
  rawData.value.forEach(item => {
    const key = `${item.year}-${item.month}`
    if (!map[key]) map[key] = { 'cs.AI': 0, 'cs.CV': 0, 'cs.LG': 0 }
    map[key][item.category] += item.count
  })
  const xData = Object.keys(map).sort()
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: categories, top: 10 },
    xAxis: {
      type: 'category',
      data: xData,
      axisLabel: { fontSize: 18 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { fontSize: 18 }
    },
    series: categories.map(cat => ({
      name: cat,
      type: 'bar',
      stack: 'total',
      data: xData.map(x => map[x][cat]),
      label: {
        show: true,
        position: 'inside',
        fontSize: 18
      }
    }))
  }
}

function getDayOption() {
  // x轴为日期，y轴为数量，三类别堆叠柱状图+总量折线图
  const map = {}
  rawData.value.forEach(item => {
    if (!map[item.date]) map[item.date] = { 'cs.AI': 0, 'cs.CV': 0, 'cs.LG': 0 }
    map[item.date][item.category] += item.count
  })
  const xData = Object.keys(map).sort()
  // 计算总量
  const totalArr = xData.map(x => categories.reduce((sum, cat) => sum + map[x][cat], 0))
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: [...categories, '总量'], top: 10 },
    xAxis: {
      type: 'category',
      data: xData,
      axisLabel: { fontSize: 18 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { fontSize: 18 }
    },
    series: [
      // 堆叠柱状图
      ...categories.map(cat => ({
        name: cat,
        type: 'bar',
        stack: 'total',
        data: xData.map(x => map[x][cat]),
        label: {
          show: true,
          position: 'inside',
          fontSize: 18
        }
      })),
      // 总量折线
      {
        name: '总量',
        type: 'line',
        data: totalArr,
        smooth: true,
        label: {
          show: true,
          position: 'top',
          fontSize: 18
        },
        yAxisIndex: 0
      }
    ]
  }
}

function renderAllCharts() {
  if (!monthChart) monthChart = echarts.init(monthChartRef.value)
  if (!dayChart) dayChart = echarts.init(dayChartRef.value)
  monthChart.setOption(getMonthOption())
  dayChart.setOption(getDayOption())
}

async function reloadData() {
  await loadAllData()
  await nextTick()
  renderAllCharts()
}

onMounted(async () => {
  await loadAllData()
  await nextTick()
  renderAllCharts()
})
</script>

<style scoped>
.arxiv-stats {
  background: var(--bg-color-tertiary);
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px var(--shadow-color);
}
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-gap: 32px;
  margin-top: 16px;
}
.chart-item {
  background: var(--bg-color-secondary);
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 4px var(--shadow-color);
  display: flex;
  flex-direction: column;
  align-items: center;
}
.chart-title {
  margin-top: 8px;
  font-size: 18px;
  font-weight: bold;
  color: var(--text-color-primary);
}
</style>
/* 鼠标悬停时按钮颜色变化，兼容 Element Plus */
:deep(.refresh-btn):hover,
:deep(.refresh-btn):hover .el-button,
:deep(.refresh-btn):hover button {
  background: var(--bg-color-secondary) !important;
  color: var(--highlight-color) !important;
  border-color: var(--highlight-color) !important;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
}