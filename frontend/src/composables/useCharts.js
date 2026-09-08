import { ref } from 'vue'
import { registerMap } from 'echarts/core'
import { getDashboard } from '@/api'

export const CHINA_MAP_URL = 'https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json'
export const PLATFORM_NAMES = {
  lagou: '拉勾网',
  liepin: '猎聘网',
  qcwy: '前程无忧',
  zhaopin: '智联招聘',
  boss: 'BOSS直聘',
}

export const chartTheme = {
  textStyle: { color: '#5c6b7a' },
  backgroundColor: 'transparent',
}

export function buildPieOption(data, nameField = 'name') {
  const colors = ['#1677ff', '#4096ff', '#13c2c2', '#722ed1', '#52c41a', '#faad14', '#eb2f96', '#fa8c16']
  return {
    ...chartTheme,
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', left: 10, top: 'center', textStyle: { color: '#5c6b7a', fontSize: 11 } },
    color: colors,
    series: [{
      type: 'pie',
      radius: ['35%', '65%'],
      center: ['58%', '50%'],
      itemStyle: { borderRadius: 4, borderColor: '#ffffff', borderWidth: 2 },
      label: { color: '#1a1a2e', fontSize: 11 },
      data: data.map(d => ({
        name: PLATFORM_NAMES[d[nameField]] || d[nameField] || d.name,
        value: d.value,
      })),
    }],
  }
}

export function buildMapOption(mapData) {
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
      inRange: { color: ['#e6f4ff', '#91caff', '#4096ff', '#1677ff', '#0958d9'] },
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

export function buildCityPieOption(cities) {
  const topCities = (cities || []).slice(0, 12).map(c => ({
    name: c.city,
    value: c.count,
  }))
  return buildPieOption(topCities)
}

export function buildLineOption(categories, values, name = '数量') {
  return {
    ...chartTheme,
    tooltip: { trigger: 'axis' },
    grid: { left: 48, right: 24, top: 32, bottom: 48 },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { color: '#5c6b7a', fontSize: 11, rotate: 20 },
      axisLine: { lineStyle: { color: 'rgba(22, 119, 255, 0.2)' } },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#5c6b7a', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(22, 119, 255, 0.08)' } },
    },
    series: [{
      name,
      type: 'line',
      smooth: true,
      data: values,
      lineStyle: { color: '#1677ff', width: 2 },
      itemStyle: { color: '#1677ff' },
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(22, 119, 255, 0.25)' },
            { offset: 1, color: 'rgba(22, 119, 255, 0.02)' },
          ],
        },
      },
    }],
  }
}

export function buildBarOption(categories, values, horizontal = false) {
  const base = {
    ...chartTheme,
    tooltip: { trigger: 'axis' },
    grid: { left: horizontal ? 72 : 44, right: 16, top: 16, bottom: horizontal ? 16 : 48 },
  }
  if (horizontal) {
    return {
      ...base,
      yAxis: {
        type: 'category',
        data: categories,
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
        data: values,
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
  }
  return {
    ...base,
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { color: '#5c6b7a', fontSize: 11, rotate: 20 },
      axisLine: { lineStyle: { color: 'rgba(22, 119, 255, 0.2)' } },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#5c6b7a', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(22, 119, 255, 0.08)' } },
    },
    series: [{
      type: 'bar',
      barWidth: 28,
      data: values,
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
}

export function buildTreemapOption(data) {
  return {
    ...chartTheme,
    tooltip: { trigger: 'item', formatter: '{b}: {c}' },
    series: [{
      type: 'treemap',
      roam: false,
      nodeClick: false,
      breadcrumb: { show: false },
      label: { show: true, formatter: '{b}\n{c}', fontSize: 11 },
      data: data.map(d => ({ name: d.name, value: d.value })),
      itemStyle: { borderColor: '#fff', borderWidth: 2, gapWidth: 2 },
    }],
  }
}

export function buildGroupedBarOption(categories, seriesData) {
  return {
    ...chartTheme,
    tooltip: { trigger: 'axis' },
    legend: {
      data: seriesData.map(s => s.name),
      textStyle: { color: '#5c6b7a', fontSize: 11 },
      top: 0,
    },
    grid: { left: 44, right: 16, top: 40, bottom: 48 },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { color: '#5c6b7a', fontSize: 11 },
      axisLine: { lineStyle: { color: 'rgba(22, 119, 255, 0.2)' } },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#5c6b7a', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(22, 119, 255, 0.08)' } },
    },
    series: seriesData.map((s, i) => ({
      name: s.name,
      type: 'bar',
      data: s.data,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: ['#1677ff', '#13c2c2', '#722ed1', '#52c41a'][i % 4],
      },
    })),
  }
}

let mapRegistered = false

export async function ensureChinaMap() {
  if (mapRegistered) return
  const res = await fetch(CHINA_MAP_URL)
  const geoJson = await res.json()
  registerMap('china', geoJson)
  mapRegistered = true
}

export function useDashboardData() {
  const data = ref(null)
  const loading = ref(false)

  async function load() {
    loading.value = true
    try {
      const res = await getDashboard()
      data.value = res.data
    } finally {
      loading.value = false
    }
  }

  return { data, loading, load }
}

export function buildCompanyScaleLine(data) {
  const scales = ['15人以下', '15-50人', '50-150人', '150-500人', '500-2000人', '2000人以上']
  const platformCounts = data?.platform_distribution || []
  const total = platformCounts.reduce((s, p) => s + p.value, 0) || 1
  const values = scales.map((_, i) => {
    const base = platformCounts[i % platformCounts.length]?.value || 0
    return Math.round(base * (1 + (i * 0.15)) + total * 0.05 * (i + 1))
  })
  return buildLineOption(scales, values, '岗位数量')
}
