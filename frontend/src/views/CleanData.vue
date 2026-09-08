<template>

  <div class="page-container clean-data-page">

    <Teleport to="#page-filters" :disabled="!filtersActive">

      <div class="filter-row">

        <div class="filter-item">

          <span class="filter-label">平台</span>

          <el-select v-model="filters.platform" placeholder="选择平台" clearable class="filter-control">

            <el-option v-for="p in platforms" :key="p.key" :label="p.name" :value="p.key" />

          </el-select>

        </div>

        <div class="filter-item">

          <span class="filter-label">学历要求</span>

          <el-select v-model="filters.education" placeholder="选择学历" clearable class="filter-control">

            <el-option v-for="e in educationOptions" :key="e" :label="e" :value="e" />

          </el-select>

        </div>

        <div class="filter-item">

          <span class="filter-label">职位</span>

          <el-input v-model="filters.keyword" placeholder="请输入职位" clearable class="filter-control" />

        </div>

        <div class="filter-item">

          <span class="filter-label">公司名称</span>

          <el-input v-model="filters.company" placeholder="请输入公司名称" clearable class="filter-control" />

        </div>

        <div class="filter-item">

          <span class="filter-label">城市</span>

          <el-input v-model="filters.city" placeholder="请输入城市" clearable class="filter-control" />

        </div>

      </div>

    </Teleport>



    <div class="card-panel">

      <div class="toolbar">

        <el-button class="btn-pill btn-clean" round @click="handleClean" :loading="cleaning">

          <el-icon><Filter /></el-icon> 执行数据清洗

        </el-button>

        <div class="toolbar-spacer" />

        <el-button class="btn-pill btn-excel" round :loading="exporting === 'excel'" @click="handleExport('excel')">

          <el-icon><Document /></el-icon> 导出 Excel

        </el-button>

        <el-button class="btn-pill btn-json" round :loading="exporting === 'json'" @click="handleExport('json')">

          <el-icon><Tickets /></el-icon> 导出 JSON

        </el-button>

        <el-button class="btn-pill btn-txt" round :loading="exporting === 'txt'" @click="handleExport('txt')">

          <el-icon><Notebook /></el-icon> 导出 TXT

        </el-button>

      </div>



      <div class="table-wrapper">

        <el-table :data="tableData" v-loading="loading" stripe style="width: 100%; min-width: 1200px">

          <el-table-column prop="id" label="ID" width="70" />

          <el-table-column prop="platform" label="平台" width="100">

            <template #default="{ row }">

              <el-tag :type="platformTagType(row.platform)" size="small" class="dark-tag">

                {{ platformName(row.platform) }}

              </el-tag>

            </template>

          </el-table-column>

          <el-table-column prop="title" label="岗位名称" min-width="160" show-overflow-tooltip />

          <el-table-column prop="company" label="公司" min-width="130" show-overflow-tooltip />

          <el-table-column prop="city" label="城市" width="80" show-overflow-tooltip />

          <el-table-column label="薪资(K)" width="130" show-overflow-tooltip>

            <template #default="{ row }">

              <span v-if="row.salary_min && row.salary_max">

                {{ row.salary_min }} - {{ row.salary_max }}

              </span>

              <span v-else-if="row.salary_avg">{{ row.salary_avg }}</span>

              <span v-else>-</span>

            </template>

          </el-table-column>

          <el-table-column prop="salary_avg" label="平均(K)" width="90">

            <template #default="{ row }">

              <span class="salary-highlight">{{ row.salary_avg || '-' }}</span>

            </template>

          </el-table-column>

          <el-table-column prop="experience_years" label="经验(年)" width="90" />

          <el-table-column prop="education_level" label="学历" width="80">

            <template #default="{ row }">{{ eduLabel(row.education_level) }}</template>

          </el-table-column>

          <el-table-column prop="skill_count" label="技能数" width="80" />

          <el-table-column prop="clean_time" label="清洗时间" width="170" />

          <el-table-column label="操作" width="160" fixed="right">

            <template #default="{ row }">

              <el-button class="btn-pill btn-edit" round size="small" @click="openEdit(row)">修改</el-button>

              <el-button class="btn-pill btn-delete" round size="small" @click="handleDelete(row)">删除</el-button>

            </template>

          </el-table-column>

        </el-table>

      </div>



      <div class="pagination">

        <el-pagination

          v-model:current-page="page"

          v-model:page-size="pageSize"

          :total="total"

          :page-sizes="[10, 20, 50, 100]"

          background

          layout="total, sizes, prev, pager, next, jumper"

          @size-change="handlePageChange"

          @current-change="handlePageChange"

        />

      </div>

    </div>



    <el-dialog v-model="editVisible" title="修改清洗数据" width="520px" destroy-on-close>

      <el-form ref="formRef" :model="editForm" :rules="editRules" label-width="96px">

        <el-form-item label="平台" prop="platform">

          <el-select v-model="editForm.platform" style="width: 100%">

            <el-option v-for="p in platforms" :key="p.key" :label="p.name" :value="p.key" />

          </el-select>

        </el-form-item>

        <el-form-item label="岗位名称" prop="title">

          <el-input v-model="editForm.title" />

        </el-form-item>

        <el-form-item label="公司" prop="company">

          <el-input v-model="editForm.company" />

        </el-form-item>

        <el-form-item label="城市" prop="city">

          <el-input v-model="editForm.city" />

        </el-form-item>

        <el-form-item label="最低薪资(K)" prop="salary_min">

          <el-input-number v-model="editForm.salary_min" :min="0" :precision="1" style="width: 100%" />

        </el-form-item>

        <el-form-item label="最高薪资(K)" prop="salary_max">

          <el-input-number v-model="editForm.salary_max" :min="0" :precision="1" style="width: 100%" />

        </el-form-item>

        <el-form-item label="经验(年)" prop="experience_years">

          <el-input-number v-model="editForm.experience_years" :min="0" style="width: 100%" />

        </el-form-item>

        <el-form-item label="学历" prop="education_level">

          <el-select v-model="editForm.education_level" style="width: 100%">

            <el-option v-for="(label, val) in EDU_LABELS" :key="val" :label="label" :value="Number(val)" />

          </el-select>

        </el-form-item>

      </el-form>

      <template #footer>

        <el-button class="btn-pill btn-cancel" round @click="editVisible = false">取消</el-button>

        <el-button class="btn-pill btn-save" round :loading="saving" @click="submitEdit">保存</el-button>

      </template>

    </el-dialog>

  </div>

</template>



<script setup>

import { ref, onMounted, watch, onUnmounted, computed } from 'vue'

import { useRoute } from 'vue-router'

import { ElMessage, ElMessageBox } from 'element-plus'

import {

  getCleanJobs, getPlatforms, runClean,

  updateCleanJob, deleteCleanJob, exportCleanJobs,

} from '@/api'

import { usePageToolbar } from '@/composables/usePageToolbar'



const route = useRoute()

const filtersActive = computed(() => route.path === '/app/clean-data')



const PLATFORM_NAMES = { lagou: '拉勾网', liepin: '猎聘网', qcwy: '前程无忧', zhaopin: '智联招聘', boss: 'BOSS直聘' }

const platformName = (k) => PLATFORM_NAMES[k] || k

const platformTagType = (k) => ({ boss: '', zhaopin: 'success', lagou: 'warning', liepin: 'danger', qcwy: 'info' }[k] || 'info')

const EDU_LABELS = { 0: '不限', 1: '高中', 2: '大专', 3: '本科', 4: '硕士', 5: '博士' }

const eduLabel = (l) => EDU_LABELS[l] ?? '未知'



const educationOptions = ['不限', '高中/中专', '大专', '本科', '硕士', '博士']



const loading = ref(false)

const cleaning = ref(false)

const saving = ref(false)

const exporting = ref('')

const tableData = ref([])

const total = ref(0)

const page = ref(1)

const pageSize = ref(10)

const platforms = ref([])

const filters = ref({ platform: '', city: '', keyword: '', company: '', education: '' })

const skipFilterWatch = ref(false)

let searchTimer = null

const editVisible = ref(false)

const editForm = ref({})

const formRef = ref(null)

const editRules = {

  platform: [{ required: true, message: '请选择平台', trigger: 'change' }],

  title: [{ required: true, message: '请输入岗位名称', trigger: 'blur' }],

}



function buildQueryParams() {

  const params = {

    page: page.value,

    per_page: pageSize.value,

  }

  if (filters.value.platform) params.platform = filters.value.platform

  if (filters.value.city) params.city = filters.value.city

  if (filters.value.keyword) params.keyword = filters.value.keyword

  if (filters.value.company) params.company = filters.value.company

  if (filters.value.education && filters.value.education !== '不限') {

    params.education = filters.value.education

  }

  return params

}



function loadData() {

  loading.value = true

  getCleanJobs(buildQueryParams()).then(res => {

    tableData.value = res.data.items

    total.value = res.data.total

  }).finally(() => { loading.value = false })

}



function handlePageChange() {

  loadData()

}



function resetFilters() {

  skipFilterWatch.value = true

  filters.value = { platform: '', city: '', keyword: '', company: '', education: '' }

  page.value = 1

  loadData()

  setTimeout(() => { skipFilterWatch.value = false }, 100)

}



watch(

  filters,

  () => {

    if (skipFilterWatch.value) return

    clearTimeout(searchTimer)

    searchTimer = setTimeout(() => {

      page.value = 1

      loadData()

    }, 400)

  },

  { deep: true },

)



function handleClean() {

  cleaning.value = true

  runClean({ platform: filters.value.platform || undefined }).then(res => {

    ElMessage.success(`清洗完成，共处理 ${res.data.cleaned_count} 条数据`)

    loadData()

  }).finally(() => { cleaning.value = false })

}



function openEdit(row) {

  editForm.value = {

    id: row.id,

    platform: row.platform,

    title: row.title,

    company: row.company || '',

    city: row.city || '',

    salary_min: row.salary_min,

    salary_max: row.salary_max,

    experience_years: row.experience_years ?? 0,

    education_level: row.education_level ?? 0,

  }

  editVisible.value = true

}



function submitEdit() {

  formRef.value?.validate((valid) => {

    if (!valid) return

    saving.value = true

    const { id, ...payload } = editForm.value

    updateCleanJob(id, payload).then(() => {

      ElMessage.success('修改成功')

      editVisible.value = false

      loadData()

    }).finally(() => { saving.value = false })

  })

}



function handleDelete(row) {

  ElMessageBox.confirm(`确定删除「${row.title}」吗？`, '删除确认', {

    type: 'warning',

    confirmButtonText: '删除',

    cancelButtonText: '取消',

  }).then(() => {

    deleteCleanJob(row.id).then(() => {

      ElMessage.success('删除成功')

      if (tableData.value.length === 1 && page.value > 1) {

        page.value -= 1

      }

      loadData()

    })

  }).catch(() => {})

}



function handleExport(format) {

  exporting.value = format

  const { page: _p, per_page: _pp, ...exportFilters } = buildQueryParams()

  exportCleanJobs({ format, ...exportFilters }).then(() => {

    ElMessage.success('导出成功')

  }).catch(() => {

    ElMessage.error('导出失败')

  }).finally(() => { exporting.value = '' })

}



usePageToolbar({ onReset: resetFilters })



onMounted(() => {

  getPlatforms().then(res => { platforms.value = res.data })

  loadData()

})



onUnmounted(() => {

  if (searchTimer) clearTimeout(searchTimer)

})

</script>



<style scoped lang="scss">

.filter-row {

  display: flex;

  align-items: center;

  flex-wrap: wrap;

  gap: 12px 16px;

}



.filter-item {

  display: flex;

  align-items: center;

  gap: 8px;

}



.filter-label {

  font-size: 13px;

  color: #666;

  white-space: nowrap;

}



.filter-control {

  width: 140px;

}



.toolbar {

  display: flex;

  gap: 10px;

  flex-wrap: wrap;

  align-items: center;

  margin-bottom: 12px;

}



.toolbar-spacer {

  flex: 1;

  min-width: 8px;

}



.table-wrapper {

  width: 100%;

  overflow: auto;

  max-height: calc(100vh - 340px);

  border: 1px solid #f0f0f0;

  border-radius: 4px;



  :deep(.el-table .cell) {

    overflow: hidden;

    text-overflow: ellipsis;

    white-space: nowrap;

  }

}



.pagination {

  display: flex;

  justify-content: flex-start;

  margin-top: 16px;

  padding-top: 12px;

  border-top: 1px solid #f0f0f0;



  :deep(.el-pagination) {

    flex-wrap: wrap;

    gap: 8px 0;

  }



  :deep(.el-pagination.is-background .el-pager li.is-active) {

    background-color: #009688 !important;

    color: #fff !important;

  }



  :deep(.el-pagination.is-background .el-pager li:hover) {

    color: #009688;

  }



  :deep(.el-pagination__total) {

    color: #666;

    font-size: 13px;

  }



  :deep(.el-pagination__sizes .el-select) {

    width: 110px;

  }



  :deep(.el-pagination__jump .el-pagination__editor) {

    width: 48px;

  }

}



.salary-highlight {

  color: #009688;

  font-weight: 600;

}

</style>



<style lang="scss">

#page-filters .filter-row {

  display: flex;

  align-items: center;

  flex-wrap: wrap;

  gap: 12px 16px;

}



#page-filters .filter-item {

  display: flex;

  align-items: center;

  gap: 8px;

}



#page-filters .filter-label {

  font-size: 13px;

  color: #666;

  white-space: nowrap;

}



#page-filters .filter-control {

  width: 140px;

}

</style>


