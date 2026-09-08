<template>
  <div class="page-container">
    <el-row :gutter="20">
      <el-col :xs="24" :lg="8">
        <div class="card-panel">
          <div class="chart-title">启动数据采集</div>
          <el-form :model="crawlForm" label-width="80px" style="margin-top: 20px">
            <el-form-item label="平台">
              <el-select v-model="crawlForm.platform" style="width: 100%">
                <el-option label="全部平台" value="all" />
                <el-option label="拉勾网" value="lagou" />
                <el-option label="猎聘网" value="liepin" />
                <el-option label="前程无忧" value="qcwy" />
                <el-option label="智联招聘" value="zhaopin" />
              </el-select>
            </el-form-item>
            <el-form-item label="关键词">
              <el-select
                v-model="crawlForm.keyword"
                filterable
                allow-create
                default-first-option
                placeholder="选择或输入关键词"
                style="width: 100%"
              >
                <el-option v-for="k in keywordOptions" :key="k" :label="k" :value="k" />
              </el-select>
            </el-form-item>
            <el-form-item label="城市">
              <el-cascader
                v-model="cityCodes"
                :options="regionOptions"
                :props="cascaderProps"
                filterable
                clearable
                placeholder="省 / 市 / 区"
                style="width: 100%"
                @change="onCityChange"
              />
            </el-form-item>
            <el-form-item label="页数">
              <el-input-number v-model="crawlForm.pages" :min="1" :max="10" />
            </el-form-item>
            <el-form-item>
              <el-button class="btn-pill btn-crawl" round @click="handleStart" :loading="starting" style="width: 100%">
                <el-icon><Download /></el-icon> 开始采集
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <el-col :xs="24" :lg="16">
        <div class="card-panel">
          <div class="toolbar">
            <div class="chart-title" style="margin-bottom: 0">采集任务记录</div>
            <el-button class="btn-pill btn-refresh" round @click="loadTasks" :loading="loading">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>

          <el-table :data="tasks" v-loading="loading" stripe style="width: 100%; margin-top: 16px">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="platform" label="平台" width="110">
              <template #default="{ row }">
                <el-tag :type="platformTagType(row.platform)" size="small">
                  {{ platformName(row.platform) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="keyword" label="关键词" width="110" show-overflow-tooltip />
            <el-table-column prop="city" label="城市" width="90" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">
                  {{ statusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total_count" label="采集数" width="80" />
            <el-table-column label="开始时间" width="170">
              <template #default="{ row }">{{ formatDateTime(row.start_time) }}</template>
            </el-table-column>
            <el-table-column label="结束时间" width="170">
              <template #default="{ row }">{{ formatDateTime(row.end_time) }}</template>
            </el-table-column>
            <el-table-column label="错误信息" min-width="180">
              <template #default="{ row }">
                <template v-if="row.error_msg">
                  <el-popover placement="left" :width="420" trigger="click">
                    <template #reference>
                      <el-button link type="danger" class="error-link">查看完整错误</el-button>
                    </template>
                    <pre class="error-full">{{ row.error_msg }}</pre>
                  </el-popover>
                </template>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="90" fixed="right">
              <template #default="{ row }">
                <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination">
            <el-pagination
              v-model:current-page="page"
              :total="total"
              :page-size="20"
              layout="total, prev, pager, next"
              @change="loadTasks"
            />
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { regionData, CodeToText } from 'element-china-area-data'
import { startCrawl, getCrawlTasks, deleteCrawlTask } from '@/api'

const PLATFORM_NAMES = {
  lagou: '拉勾网',
  liepin: '猎聘网',
  qcwy: '前程无忧',
  zhaopin: '智联招聘',
  boss: 'BOSS直聘',
  all: '全部平台',
}
const platformName = (k) => PLATFORM_NAMES[k] || k
const platformTagType = (k) => ({
  lagou: 'warning',
  liepin: 'danger',
  qcwy: 'info',
  zhaopin: 'success',
  boss: '',
}[k] || 'info')
const statusType = (s) => ({ pending: 'info', running: 'warning', completed: 'success', failed: 'danger' }[s] || 'info')
const statusLabel = (s) => ({ pending: '等待中', running: '运行中', completed: '已完成', failed: '失败' }[s] || s)

const keywordOptions = [
  'Python',
  '人工智能',
  '数据采集',
  '数据清洗',
  '深度学习',
  '机器学习',
  '计算机视觉',
  '大语言模型',
  '数据分析',
  'Java',
  '前端开发',
  '后端开发',
]

const regionOptions = regionData
const cascaderProps = { expandTrigger: 'hover' }

const crawlForm = ref({ platform: 'all', keyword: 'Python', city: '重庆', pages: 3 })
const cityCodes = ref(['500000', '500100', '500103'])
const starting = ref(false)
const loading = ref(false)
const tasks = ref([])
const total = ref(0)
const page = ref(1)
let pollTimer

function normalizeCityName(name) {
  if (!name) return ''
  if (name === '市辖区' || name === '县') return ''
  return name
    .replace(/特别行政区$/, '')
    .replace(/(壮族|回族|维吾尔)?自治区$/, '')
    .replace(/省$/, '')
    .replace(/市$/, '')
}

function codesToCityName(codes) {
  if (!codes?.length) return ''
  const labels = codes.map((c) => CodeToText[c]).filter(Boolean)
  let city = labels[1] || labels[0] || ''
  if (city === '市辖区' || city === '县') city = labels[0] || ''
  return normalizeCityName(city)
}

function onCityChange(codes) {
  crawlForm.value.city = codesToCityName(codes)
}

function formatDateTime(value) {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) {
    return String(value).replace('T', ' ').replace(/\.\d+.*$/, '').slice(0, 19)
  }
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

function handleStart() {
  if (!crawlForm.value.keyword) {
    ElMessage.warning('请选择或输入关键词')
    return
  }
  if (!crawlForm.value.city) {
    ElMessage.warning('请选择城市')
    return
  }
  starting.value = true
  startCrawl(crawlForm.value).then(() => {
    ElMessage.success(
      crawlForm.value.platform === 'all'
        ? '已同时启动四大平台采集任务'
        : '爬虫任务已启动'
    )
    loadTasks()
    startPolling()
  }).finally(() => { starting.value = false })
}

function loadTasks() {
  loading.value = true
  return getCrawlTasks({ page: page.value }).then(res => {
    tasks.value = res.data.items
    total.value = res.data.total
  }).finally(() => { loading.value = false })
}

function handleDelete(row) {
  ElMessageBox.confirm(`确认删除任务 #${row.id}（${platformName(row.platform)}）？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  }).then(() => {
    return deleteCrawlTask(row.id)
  }).then(() => {
    ElMessage.success('任务已删除')
    loadTasks()
  }).catch(() => {})
}

function startPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
  const stop = () => { if (pollTimer) { clearInterval(pollTimer); pollTimer = null } }
  let ticks = 0
  const MAX_TICKS = 200  // 最多轮询 10 分钟，防止任务状态异常时前端一直转圈
  const tick = async () => {
    ticks += 1
    if (ticks > MAX_TICKS) { stop(); return }
    // 关键：await 请求返回后再判断，避免用上一次的旧数据导致停止判断失效
    await loadTasks()
    const hasActive = tasks.value.some(t => t.status === 'running' || t.status === 'pending')
    if (!hasActive) stop()
  }
  tick()
  pollTimer = setInterval(tick, 3000)
}

onMounted(loadTasks)
onUnmounted(() => { if (pollTimer) clearInterval(pollTimer) })
</script>

<style scoped lang="scss">
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
.error-link {
  padding: 0;
}
.error-full {
  margin: 0;
  max-height: 320px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 12px;
  line-height: 1.5;
  color: #c45656;
}
</style>
