<template>
  <div class="page-container dashboard">
    <div class="dashboard-grid">
      <div class="column left">
        <div class="card-panel chart-panel">
          <div class="chart-title">平台岗位分布</div>
          <div class="chart-body">
            <v-chart :option="platformOption" autoresize />
          </div>
        </div>
        <div class="card-panel chart-panel">
          <div class="chart-title">薪资区间分布</div>
          <div class="chart-body">
            <v-chart :option="salaryOption" autoresize />
          </div>
        </div>
        <div class="card-panel chart-panel">
          <div class="chart-title">学历要求分布</div>
          <div class="chart-body">
            <v-chart :option="eduOption" autoresize />
          </div>
        </div>
      </div>

      <div class="column center">
        <div class="card-panel chart-panel map-panel">
          <div class="chart-title">招聘岗位地区分布</div>
          <div class="chart-body">
            <v-chart :option="mapOption" autoresize />
          </div>
        </div>
      </div>

      <div class="column right">
        <div class="card-panel chart-panel">
          <div class="chart-title">热门技能 TOP10</div>
          <div class="chart-body">
            <v-chart :option="skillOption" autoresize />
          </div>
        </div>
        <div class="card-panel chart-panel">
          <div class="chart-title">各平台平均薪资对比</div>
          <div class="chart-body">
            <v-chart :option="platformSalaryOption" autoresize />
          </div>
        </div>
        <div class="card-panel chart-panel">
          <div class="chart-title">数据趋势</div>
          <div class="chart-body">
            <v-chart :option="trendOption" autoresize />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use, registerMap } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart, MapChart, EffectScatterChart } from 'echarts/charts'
import {
  TitleComponent, TooltipComponent, LegendComponent,
  GridComponent, VisualMapComponent, GeoComponent,
} from 'echarts/components'
import { getDashboard } from '@/api'

use([
  CanvasRenderer,
  PieChart, BarChart, LineChart, MapChart, EffectScatterChart,
  TitleComponent, TooltipComponent, LegendComponent,
  GridComponent, VisualMapComponent, GeoComponent,
])

const CHINA_MAP_URL = '/data/china.json'  // 本地化地图数据，避免每次访问外网
const PLATFORM_NAMES = { lagou: '拉勾网', liepin: '猎聘网', qcwy: '前程无忧', zhaopin: '智联招聘', boss: 'BOSS直聘' }

const platformOption = ref({})
const salaryOption = ref({})
const eduOption = ref({})
const mapOption = ref({})
const skillOption = ref({})
const platformSalaryOption = ref({})
const trendOption = ref({})
const loading = ref(true)

const chartTheme = {
  textStyle: { color: '#5c6b7a' },
  backgroundColor: 'transparent',
}

function buildPieOption(data, nameField = 'name') {
  const colors = ['#1677ff', '#4096ff', '#13c2c2', '#722ed1', '#52c41a', '#faad14']
  return {
    ...chartTheme,
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { color: '#5c6b7a', fontSize: 11 } },
    color: colors,
    series: [{
      type: 'pie',
      radius: ['38%', '62%'],
      center: ['50%', '44%'],
      itemStyle: { borderRadius: 6, borderColor: '#ffffff', borderWidth: 2 },
      label: { color: '#1a1a2e', fontSize: 11 },
      data: data.map(d => ({
        name: PLATFORM_NAMES[d[nameField]] || d[nameField] || d.name,
        value: d.value,
      })),
    }],
  }
}

function buildMapOption(mapData) {
  const provinces = mapData?.provinces || []
  const cities = (mapData?.cities || []).filter(c => c.lng && c.lat)
  const maxVal = Math.max(...provinces.map(p => p.value), 1)

  return {
    ...chartTheme,
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.96)',
      borderColor: 'rgba(22, 119, 255, 0.2)',
      textStyle: { color: '#1a1a2e' },
      formatter(params) {
        if (params.seriesType === 'map') {
          return `${params.name}<br/>岗位数：${params.value || 0}`
        }
        if (params.seriesType === 'effectScatter') {
          const d = params.data
          return `${d.city}<br/>岗位：${d.count}<br/>均薪：${d.avg_salary}K`
        }
        return params.name
      },
    },
    visualMap: {
      min: 0,
      max: maxVal,
      left: 16,
      bottom: 16,
      text: ['高', '低'],
      calculable: true,
      inRange: {
        color: ['#e6f4ff', '#91caff', '#4096ff', '#1677ff', '#0958d9'],
      },
      textStyle: { color: '#5c6b7a' },
    },
    geo: {
      map: 'china',
      roam: true,
      zoom: 1.15,
      center: [105, 36],
      label: { show: false },
      itemStyle: {
        areaColor: '#e6f4ff',
        borderColor: 'rgba(22, 119, 255, 0.3)',
        borderWidth: 1,
      },
      emphasis: {
        itemStyle: { areaColor: '#91caff' },
        label: { show: true, color: '#1a1a2e', fontSize: 11 },
      },
    },
    series: [
      {
        name: '岗位分布',
        type: 'map',
        map: 'china',
        geoIndex: 0,
        data: provinces,
      },
      {
        name: '城市',
        type: 'effectScatter',
        coordinateSystem: 'geo',
        geoIndex: 0,
        data: cities.map(c => ({
          name: c.city,
          value: [c.lng, c.lat, c.count],
          city: c.city,
          count: c.count,
          avg_salary: c.avg_salary,
        })),
        symbolSize(val) {
          return Math.min(Math.max(val[2] / 10, 8), 24)
        },
        itemStyle: {
          color: '#1677ff',
          shadowBlur: 12,
          shadowColor: 'rgba(22, 119, 255, 0.35)',
        },
        rippleEffect: { brushType: 'stroke', scale: 3 },
      },
    ],
  }
}

async function ensureChinaMap() {
  const res = await fetch(CHINA_MAP_URL)
  const geoJson = await res.json()
  registerMap('china', geoJson)
}

async function loadDashboard() {
  loading.value = true
  try {
    const res = await getDashboard()
    const d = res.data

    platformOption.value = buildPieOption(d.platform_distribution)
    salaryOption.value = buildPieOption(d.salary_distribution)
    eduOption.value = buildPieOption(d.education_distribution)
    mapOption.value = buildMapOption(d.map_data)

    skillOption.value = {
      ...chartTheme,
      tooltip: { trigger: 'axis' },
      grid: { left: 72, right: 16, top: 8, bottom: 8 },
      yAxis: {
        type: 'category',
        data: d.skill_ranking.map(s => s.name).reverse(),
        axisLabel: { color: '#5c6b7a', fontSize: 11 },
        axisLine: { lineStyle: { color: 'rgba(22, 119, 255, 0.2)' } },
      },
      xAxis: {
        type: 'value',
        axisLabel: { color: '#5c6b7a', fontSize: 11 },
        splitLine: { lineStyle: { color: 'rgba(22, 119, 255, 0.08)' } },
      },
      series: [{
        type: 'bar',
        data: d.skill_ranking.map(s => s.value).reverse(),
        itemStyle: {
          borderRadius: [0, 4, 4, 0],
          color: {
            type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: 'rgba(22, 119, 255, 0.2)' },
              { offset: 1, color: '#1677ff' },
            ],
          },
        },
      }],
    }

    platformSalaryOption.value = {
      ...chartTheme,
      tooltip: { trigger: 'axis' },
      grid: { left: 44, right: 16, top: 28, bottom: 28 },
      xAxis: {
        type: 'category',
        data: d.platform_salary.map(p => PLATFORM_NAMES[p.platform] || p.platform),
        axisLabel: { color: '#5c6b7a', fontSize: 11, rotate: 20 },
        axisLine: { lineStyle: { color: 'rgba(22, 119, 255, 0.2)' } },
      },
      yAxis: {
        type: 'value',
        name: 'K',
        nameTextStyle: { color: '#5c6b7a', fontSize: 11 },
        axisLabel: { color: '#5c6b7a', fontSize: 11 },
        splitLine: { lineStyle: { color: 'rgba(22, 119, 255, 0.08)' } },
      },
      series: [{
        name: '平均薪资',
        type: 'bar',
        barWidth: 28,
        data: d.platform_salary.map(p => p.avg_salary),
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#4096ff' },
              { offset: 1, color: 'rgba(22, 119, 255, 0.25)' },
            ],
          },
        },
      }],
    }

    trendOption.value = {
      ...chartTheme,
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['岗位数量', '平均薪资'],
        textStyle: { color: '#5c6b7a', fontSize: 11 },
        top: 0,
      },
      grid: { left: 44, right: 44, top: 32, bottom: 24 },
      xAxis: {
        type: 'category',
        data: d.trend.dates,
        axisLabel: { color: '#5c6b7a', fontSize: 10, rotate: 30 },
        axisLine: { lineStyle: { color: 'rgba(22, 119, 255, 0.2)' } },
      },
      yAxis: [
        {
          type: 'value',
          name: '数量',
          nameTextStyle: { color: '#5c6b7a', fontSize: 11 },
          axisLabel: { color: '#5c6b7a', fontSize: 11 },
          splitLine: { lineStyle: { color: 'rgba(22, 119, 255, 0.08)' } },
        },
        {
          type: 'value',
          name: 'K',
          nameTextStyle: { color: '#5c6b7a', fontSize: 11 },
          axisLabel: { color: '#5c6b7a', fontSize: 11 },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: '岗位数量',
          type: 'bar',
          data: d.trend.counts,
          itemStyle: { color: 'rgba(22, 119, 255, 0.55)' },
        },
        {
          name: '平均薪资',
          type: 'line',
          yAxisIndex: 1,
          smooth: true,
          data: d.trend.salaries,
          lineStyle: { color: '#f5a623', width: 2 },
          itemStyle: { color: '#f5a623' },
        },
      ],
    }
  } catch (e) {
    console.error('加载仪表盘数据失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 地图加载与数据请求并行，避免串行等待外网/接口
  ensureChinaMap().catch(() => {
    mapOption.value = {
      ...chartTheme,
      title: {
        text: '地图加载失败，请检查网络',
        left: 'center',
        top: 'center',
        textStyle: { color: '#5c6b7a', fontSize: 14 },
      },
    }
  })
  loadDashboard()
})
</script>

<style scoped lang="scss">
.dashboard {
  padding: 16px;
  overflow: hidden;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.35fr) minmax(0, 1fr);
  gap: 16px;
  height: 100%;
  min-height: 0;
}

.column {
  display: grid;
  gap: 16px;
  min-height: 0;
}

.column.left,
.column.right {
  grid-template-rows: repeat(3, minmax(0, 1fr));
}

.column.center {
  grid-template-rows: minmax(0, 1fr);
}

.chart-panel {
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 14px 16px 12px;
}

.chart-title {
  margin-bottom: 10px;
  flex-shrink: 0;
}

.chart-body {
  flex: 1;
  min-height: 0;

  :deep(.echarts) {
    width: 100%;
    height: 100%;
  }
}

.map-panel {
  .chart-title {
    font-size: 17px;
  }
}

@media (max-width: 1200px) {
  .dashboard {
    overflow-y: auto;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
    height: auto;
  }

  .column.left,
  .column.right {
    grid-template-rows: none;
  }

  .chart-panel {
    min-height: 280px;
  }

  .map-panel {
    min-height: 420px;
  }
}
</style>
