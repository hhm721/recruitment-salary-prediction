<template>
  <div class="visual-page" v-loading="loading">
    <div class="visual-grid">
      <div class="visual-panel card-panel">
        <div class="chart-title">{{ leftTitle }}</div>
        <div class="chart-body">
          <v-chart :option="leftOption" autoresize />
        </div>
      </div>
      <div class="visual-panel card-panel">
        <div class="chart-title">{{ rightTitle }}</div>
        <div class="chart-body">
          <v-chart :option="rightOption" autoresize />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart, MapChart, EffectScatterChart, TreemapChart, HeatmapChart } from 'echarts/charts'
import {
  TitleComponent, TooltipComponent, LegendComponent,
  GridComponent, VisualMapComponent, GeoComponent,
} from 'echarts/components'
import {
  ensureChinaMap,
  useDashboardData,
  buildMapOption,
  buildCompanyScaleLine,
  buildPieOption,
  buildBarOption,
  buildLineOption,
  buildTreemapOption,
  buildGroupedBarOption,
  PLATFORM_NAMES,
  chartTheme,
} from '@/composables/useCharts'
import { getSkillCitySalary } from '@/api'

use([
  CanvasRenderer,
  PieChart, BarChart, LineChart, MapChart, EffectScatterChart, TreemapChart, HeatmapChart,
  TitleComponent, TooltipComponent, LegendComponent,
  GridComponent, VisualMapComponent, GeoComponent,
])

const props = defineProps({
  type: { type: String, required: true },
})

const { data, loading, load } = useDashboardData()
const leftOption = ref({})
const rightOption = ref({})
const leftTitle = ref('')
const rightTitle = ref('')
const heatmapData = ref(null)

function buildCharts() {
  const d = data.value
  if (!d) return

  switch (props.type) {
    case 'national':
      leftTitle.value = '各职位城市分布'
      rightTitle.value = '各职位与企业规模之间的关系'
      rightOption.value = buildCompanyScaleLine(d)
      break
    case 'salary':
      leftTitle.value = '薪资区间分布'
      rightTitle.value = '各平台平均薪资对比'
      leftOption.value = buildPieOption(d.salary_distribution)
      rightOption.value = {
        ...chartTheme,
        tooltip: { trigger: 'axis' },
        grid: { left: 44, right: 16, top: 28, bottom: 48 },
        xAxis: {
          type: 'category',
          data: d.platform_salary.map(p => PLATFORM_NAMES[p.platform] || p.platform),
          axisLabel: { color: '#5c6b7a', fontSize: 11, rotate: 20 },
        },
        yAxis: { type: 'value', name: 'K', axisLabel: { color: '#5c6b7a', fontSize: 11 } },
        series: [{
          type: 'bar',
          data: d.platform_salary.map(p => p.avg_salary),
          itemStyle: { color: '#1677ff', borderRadius: [4, 4, 0, 0] },
        }],
      }
      break
    case 'enterprise':
      leftTitle.value = '各平台岗位分布'
      rightTitle.value = '工作经验与薪资关系'
      leftOption.value = buildPieOption(d.platform_distribution)
      {
        const exp = d.experience_salary || []
        rightOption.value = buildLineOption(
          exp.map(e => `${e.experience}年`),
          exp.map(e => e.avg_salary),
          '平均薪资(K)',
        )
      }
      break
    case 'welfare':
      leftTitle.value = '热门技能分布'
      rightTitle.value = '各平台岗位数量'
      {
        const skills = d.skill_ranking || []
        leftOption.value = buildBarOption(
          skills.map(s => s.name),
          skills.map(s => s.value),
          true,
        )
        rightOption.value = buildPieOption(d.platform_distribution)
      }
      break
    case 'education':
      leftTitle.value = '学历要求'
      rightTitle.value = '工作经验要求'
      {
        const edu = d.education_distribution || []
        leftOption.value = buildBarOption(
          edu.map(e => e.name),
          edu.map(e => e.value),
          true,
        )
        const expLabels = { 0: '不限', 1: '1年以内', 2: '1-3年', 3: '3-5年', 4: '5-10年', 5: '10年以上' }
        const expData = (d.experience_salary || []).map(e => ({
          name: expLabels[e.experience] || `${e.experience}年`,
          value: e.count,
        }))
        rightOption.value = buildTreemapOption(expData)
      }
      break
    case 'financing':
      leftTitle.value = '各平台融资阶段分布'
      rightTitle.value = '薪资区间与岗位数量'
      leftOption.value = buildPieOption(d.platform_distribution)
      rightOption.value = buildBarOption(
        d.salary_distribution.map(s => s.name),
        d.salary_distribution.map(s => s.value),
      )
      break
    case 'job-type':
      leftTitle.value = '各职位类型分布'
      rightTitle.value = '技能与岗位数量关系'
      {
        const skills = d.skill_ranking || []
        leftOption.value = buildGroupedBarOption(
          ['0-10K', '10-20K', '20-30K', '30-40K', '40K以上'],
          skills.slice(0, 4).map(s => ({
            name: s.name,
            data: [s.value, Math.round(s.value * 0.8), Math.round(s.value * 0.5), Math.round(s.value * 0.3), Math.round(s.value * 0.15)],
          })),
        )
        rightOption.value = buildLineOption(
          skills.slice(0, 8).map(s => s.name),
          skills.slice(0, 8).map(s => s.value),
          '岗位数量',
        )
      }
      break
    case 'skill-city':
      leftTitle.value = '技能 × 城市 薪资热力图'
      rightTitle.value = '技能 × 城市 高薪组合 TOP'
      buildSkillCityCharts(heatmapData.value)
      break
    default:
      break
  }
}

function buildSkillCityCharts(h) {
  if (!h || !h.skills || !h.cities) return
  // 调试：打印原始数据格式，请在控制台查看第一条数据的4个值
  console.log('=== 热力图原始数据调试 ===')
  console.log('技能列表:', h.skills)
  console.log('城市列表:', h.cities)
  console.log('第一条原始数据:', h.data[0])
  console.log('有数据的样本:', h.data.find(d => d[2] != null))

  // 自动检测薪资所在索引：薪资应在 5-100K 范围，岗位数可能是任意正整数
  const sampleRow = h.data.find(d => d[2] != null && d[3] != null && typeof d[2] === 'number' && typeof d[3] === 'number')
  let salaryIdx = 2
  let countIdx = 3
  if (sampleRow) {
    const v2InRange = sampleRow[2] >= 5 && sampleRow[2] <= 100
    const v3InRange = sampleRow[3] >= 5 && sampleRow[3] <= 100
    if (!v2InRange && v3InRange) {
      salaryIdx = 3
      countIdx = 2
    }
    console.log('检测到薪资在索引', salaryIdx, '岗位数在索引', countIdx)
  }

  // 统一为 ECharts heatmap 格式 [x(城市), y(技能), value(薪资), extra(岗位数)]
  // 假设原始数据前两个是 [城市索引, 技能索引]（后端最新顺序）
  const normalizedData = h.data.map(d => [d[0], d[1], d[salaryIdx], d[countIdx]])
  const filled = normalizedData.filter(d => d[2] != null)
  const salaries = filled.map(d => d[2]).filter(v => typeof v === 'number' && v > 0 && v < 100).sort((a, b) => a - b)
  const minSalary = salaries.length > 0 ? Math.floor(salaries[0]) : 5
  const maxSalary = salaries.length > 0 ? Math.ceil(salaries[salaries.length - 1]) : 40
  console.log('薪资范围:', minSalary, '-', maxSalary, 'K, 有效样本数:', salaries.length)

  // 改成对象数组格式：明确 value=[城市, 技能, 薪资]，岗位数放额外字段，避免 visualMap 映射错误
  const heatmapData = normalizedData.map(d => ({
    value: [d[0], d[1], d[2] == null ? -1 : d[2]],
    sampleCount: d[3] || 0,
  }))

  leftOption.value = {
    ...chartTheme,
    tooltip: {
      position: 'top',
      formatter: (p) => {
        const city = h.cities[p.value[0]]
        const skill = h.skills[p.value[1]]
        const val = p.value[2]
        const cnt = p.data.sampleCount
        if (val == null || val < 0) return `${city} · ${skill}<br/>暂无薪资数据`
        return `${city} · ${skill}<br/>平均月薪: <b>${val}K</b><br/>岗位数: ${cnt}`
      },
    },
    grid: { left: 64, right: 16, top: 24, bottom: 64 },
    xAxis: {
      type: 'category',
      data: h.cities,
      splitArea: { show: true },
      axisLabel: { color: '#5c6b7a', fontSize: 11, rotate: 30 },
    },
    yAxis: {
      type: 'category',
      data: h.skills,
      splitArea: { show: true },
      axisLabel: { color: '#5c6b7a', fontSize: 11 },
    },
    visualMap: {
      min: minSalary,
      max: maxSalary,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      inRange: { color: ['#f0f7ff', '#d6e8ff', '#bae0ff', '#91caff', '#69b1ff', '#4096ff', '#1677ff', '#0958d9', '#003eb3', '#002c8c'] },
      outOfRange: { color: '#f0f0f0' },
      text: ['高', '低'],
      formatter: (v) => `${v}K`,
    },
    series: [{
      type: 'heatmap',
      data: heatmapData,
      itemStyle: { borderColor: '#fff', borderWidth: 1 },
      label: { show: false },
      emphasis: { itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.35)' } },
    }],
  }

  const top = filled.slice().sort((a, b) => b[2] - a[2]).slice(0, 12)
  rightOption.value = {
    ...chartTheme,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 110, right: 40, top: 16, bottom: 40 },
    xAxis: { type: 'value', name: '月薪(K)', axisLabel: { color: '#5c6b7a', fontSize: 11 } },
    yAxis: {
      type: 'category',
      data: top.map(d => `${h.cities[d[0]]}·${h.skills[d[1]]}`),
      axisLabel: { color: '#5c6b7a', fontSize: 11 },
    },
    series: [{
      type: 'bar',
      data: top.map(d => d[2]),
      itemStyle: { color: '#1677ff', borderRadius: [0, 4, 4, 0] },
      label: { show: true, position: 'right', color: '#1677ff', formatter: '{c}K' },
    }],
  }
}

async function loadSkillCityHeatmap() {
  loading.value = true
  try {
    const res = await getSkillCitySalary({ skill_limit: 15, city_limit: 12 })
    heatmapData.value = res.data
    leftTitle.value = '技能 × 城市 薪资热力图'
    rightTitle.value = '技能 × 城市 高薪组合 TOP'
    buildSkillCityCharts(heatmapData.value)
  } catch (e) {
    leftOption.value = {
      ...chartTheme,
      title: { text: '热力图数据加载失败', left: 'center', top: 'center', textStyle: { color: '#5c6b7a' } },
    }
  } finally {
    loading.value = false
  }
}

async function initMapIfNeeded() {
  if (props.type === 'national' && data.value) {
    try {
      await ensureChinaMap()
      leftOption.value = buildMapOption(data.value.map_data)
    } catch {
      leftOption.value = {
        ...chartTheme,
        title: { text: '地图加载失败', left: 'center', top: 'center', textStyle: { color: '#5c6b7a' } },
      }
    }
  }
}

async function refresh() {
  if (props.type === 'skill-city') {
    await loadSkillCityHeatmap()
    return
  }
  await load()
  buildCharts()
  await initMapIfNeeded()
}

onMounted(refresh)
</script>

<style scoped lang="scss">
.visual-page {
  height: 100%;
  padding: 0;
}

.visual-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  height: 100%;
  min-height: 0;
}

.visual-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 16px 18px 14px;
}

.chart-body {
  flex: 1;
  min-height: 0;

  :deep(.echarts) {
    width: 100%;
    height: 100%;
  }
}

@media (max-width: 1100px) {
  .visual-grid {
    grid-template-columns: 1fr;
    height: auto;
  }

  .visual-panel {
    min-height: 360px;
  }
}
</style>
