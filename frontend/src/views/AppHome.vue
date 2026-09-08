<template>

  <div class="page-container app-home">

    <el-row :gutter="16" class="stat-row">

      <el-col :xs="12" :sm="6" v-for="item in statCards" :key="item.label">

        <div class="stat-card">

          <div class="stat-icon" :style="{ background: item.gradient }">

            <el-icon :size="22"><component :is="item.icon" /></el-icon>

          </div>

          <div class="stat-body">

            <div class="stat-value">{{ item.value }}</div>

            <div class="stat-label">{{ item.label }}</div>

          </div>

        </div>

      </el-col>

    </el-row>



    <div class="card-panel">

      <div class="chart-title">招聘数据概况</div>



      <div class="table-wrapper">

        <el-table :data="tableData" v-loading="tableLoading" stripe style="width: 100%; min-width: 1100px">

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

          <el-table-column prop="salary_raw" label="薪资" width="110" show-overflow-tooltip />

          <el-table-column prop="experience" label="经验" width="90" />

          <el-table-column prop="education" label="学历" width="80" />

          <el-table-column prop="is_cleaned" label="已清洗" width="80">

            <template #default="{ row }">

              <el-tag :type="row.is_cleaned ? 'success' : 'info'" size="small" class="dark-tag">

                {{ row.is_cleaned ? '是' : '否' }}

              </el-tag>

            </template>

          </el-table-column>

          <el-table-column prop="crawl_time" label="采集时间" width="170" />

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

  </div>

</template>



<script setup>

import { ref, computed, onMounted } from 'vue'

import { getOverview, getRawJobs } from '@/api'



const PLATFORM_NAMES = { lagou: '拉勾网', liepin: '猎聘网', qcwy: '前程无忧', zhaopin: '智联招聘', boss: 'BOSS直聘' }

const platformName = (k) => PLATFORM_NAMES[k] || k

const platformTagType = (k) => ({ boss: '', zhaopin: 'success', lagou: 'warning', liepin: 'danger', qcwy: 'info' }[k] || 'info')



const overview = ref({})

const tableLoading = ref(false)

const tableData = ref([])

const total = ref(0)

const page = ref(1)

const pageSize = ref(10)



const statCards = computed(() => [

  {

    label: '原始数据量',

    value: overview.value.raw_total ?? '-',

    icon: 'Document',

    gradient: 'linear-gradient(135deg, #1677ff, #0958d9)',

  },

  {

    label: '清洗数据量',

    value: overview.value.clean_total ?? '-',

    icon: 'Filter',

    gradient: 'linear-gradient(135deg, #13c2c2, #08979c)',

  },

  {

    label: '平均薪资(K)',

    value: overview.value.avg_salary ?? '-',

    icon: 'Money',

    gradient: 'linear-gradient(135deg, #fa8c16, #d46b08)',

  },

  {

    label: '覆盖城市数',

    value: overview.value.city_count ?? '-',

    icon: 'Location',

    gradient: 'linear-gradient(135deg, #722ed1, #531dab)',

  },

])



async function loadOverview() {

  try {

    const res = await getOverview()

    overview.value = res.data

  } catch {

    overview.value = { raw_total: 0, clean_total: 0, avg_salary: 0, city_count: 0 }

  }

}



function loadData() {

  tableLoading.value = true

  getRawJobs({

    page: page.value,

    per_page: pageSize.value,

  }).then(res => {

    tableData.value = res.data.items

    total.value = res.data.total

  }).finally(() => { tableLoading.value = false })

}



function handlePageChange() {

  loadData()

}



onMounted(() => {

  loadOverview()

  loadData()

})

</script>



<style scoped lang="scss">

.app-home {

  height: 100%;

  overflow-y: auto;

}



.stat-row {

  margin-bottom: 16px;

}



.stat-card {

  display: flex;

  align-items: center;

  gap: 14px;

  padding: 20px 18px;

  background: #fff;

  border: 1px solid #f0f0f0;

  border-radius: 8px;

  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

  transition: all 0.3s;



  &:hover {

    border-color: rgba(0, 150, 136, 0.35);

    transform: translateY(-2px);

    box-shadow: 0 4px 16px rgba(0, 150, 136, 0.1);

  }

}



.stat-icon {

  width: 48px;

  height: 48px;

  border-radius: 12px;

  display: flex;

  align-items: center;

  justify-content: center;

  color: #fff;

  flex-shrink: 0;

}



.stat-body {

  min-width: 0;



  .stat-value {

    font-size: 28px;

    font-weight: 700;

    color: #333;

    line-height: 1.2;

    margin-bottom: 4px;

  }



  .stat-label {

    font-size: 13px;

    color: #666;

  }

}



.table-wrapper {

  width: 100%;

  overflow: auto;

  max-height: calc(100vh - 380px);

  border: 1px solid #f0f0f0;

  border-radius: 4px;

  margin-top: 12px;



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

</style>


