<template>
  <div class="page-container predict-page">
    <div class="section-card info-section">
      <div class="section-title">信息选择</div>

      <el-tabs v-model="predictMode" class="mode-tabs">
        <el-tab-pane label="手动输入" name="manual" />
        <el-tab-pane label="文件上传" name="upload" />
      </el-tabs>

      <el-form v-if="predictMode === 'manual'" :model="form" label-width="88px" class="info-form">
        <div class="form-grid">
          <el-form-item label="职位">
            <el-select v-model="form.job" filterable allow-create placeholder="请选择职位" style="width: 100%">
              <el-option v-for="j in jobOptions" :key="j" :label="j" :value="j" />
            </el-select>
          </el-form-item>
          <el-form-item label="公司规模">
            <el-select v-model="form.companySize" placeholder="请选择公司规模" style="width: 100%">
              <el-option v-for="s in companySizeOptions" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>
          <el-form-item label="工作经验">
            <el-select v-model="form.experience" placeholder="请选择工作经验" style="width: 100%">
              <el-option v-for="e in experienceOptions" :key="e" :label="e" :value="e" />
            </el-select>
          </el-form-item>
          <el-form-item label="学历">
            <el-select v-model="form.education" placeholder="请选择学历" style="width: 100%">
              <el-option v-for="e in educationOptions" :key="e" :label="e" :value="e" />
            </el-select>
          </el-form-item>
          <el-form-item label="城市">
            <el-select v-model="form.city" filterable allow-create placeholder="请选择城市" style="width: 100%">
              <el-option v-for="c in cityOptions" :key="c" :label="c" :value="c" />
            </el-select>
          </el-form-item>
          <el-form-item label="模型">
            <el-select v-model="form.model" placeholder="请选择模型" style="width: 100%">
              <el-option
                v-for="m in modelOptions"
                :key="m.value"
                :label="m.label"
                :value="m.value"
              />
            </el-select>
          </el-form-item>
                    <el-form-item label="已有技能">
            <el-select
              v-model="form.userSkills"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="输入技能后回车添加，如 Python、Java"
              style="width: 100%"
            >
              <el-option v-for="s in skillSuggestions" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>


        </div>
      </el-form>

      <div v-else class="upload-section">
        <div class="upload-layout">
          <div class="upload-left">
            <el-upload
              class="upload-area"
              drag
              :auto-upload="false"
              :limit="1"
              accept=".txt,.pdf,.doc,.docx"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :file-list="fileList"
            >
              <el-icon :size="48" color="#409eff"><UploadFilled /></el-icon>
              <div class="el-upload__text">拖拽简历到此处，或 <em>点击上传</em></div>
              <template #tip>
                <div class="el-upload__tip">支持 txt / pdf / doc / docx 格式</div>
              </template>
            </el-upload>
            <el-form :model="uploadForm" label-width="88px" class="upload-extra">
              <el-form-item label="城市">
                <el-select v-model="uploadForm.city" filterable allow-create clearable placeholder="选填" style="width: 100%">
                  <el-option v-for="c in cityOptions" :key="c" :label="c" :value="c" />
                </el-select>
              </el-form-item>
              <el-form-item label="公司规模">
                <el-select v-model="uploadForm.companySize" clearable placeholder="选填" style="width: 100%">
                  <el-option v-for="s in companySizeOptions" :key="s" :label="s" :value="s" />
                </el-select>
              </el-form-item>
              <el-form-item label="模型">
                <el-select v-model="uploadForm.model" placeholder="请选择模型" style="width: 100%">
                  <el-option
                    v-for="m in modelOptions"
                    :key="m.value"
                    :label="m.label"
                    :value="m.value"
                  />
                </el-select>
              </el-form-item>
            </el-form>
          </div>

          <div class="upload-right">
            <div class="resume-preview" v-loading="previewLoading">
              <div v-if="previewPdfUrl" class="preview-pdf">
                <iframe :src="previewPdfUrl" title="简历预览" />
              </div>
              <pre v-else-if="previewText" class="preview-text">{{ previewText }}</pre>
              <div v-else class="preview-placeholder">预览简历</div>
              <div v-if="previewFileName" class="preview-filename">{{ previewFileName }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="section-card result-section">
      <div class="result-header">
        <div class="section-title result-title">薪资预测</div>
        <div class="form-actions">
          <el-button class="btn-pill btn-reset-action" round @click="handleReset">重置</el-button>
          <el-button class="btn-pill btn-submit-action" round :loading="predicting" @click="handleSubmit">提交</el-button>
        </div>
      </div>

      <div class="result-box">
        <div class="result-label">预测平均值</div>
        <div v-if="result" class="result-value">{{ avgSalaryText }}</div>
        <div v-else class="result-placeholder">提交后将在此显示预测薪资（平均值）</div>
        <div v-if="result" class="result-meta">
          <span>参考区间：{{ resultRangeText }}</span>
          <span>模型：{{ result.model_name || result.model || '-' }}</span>
          <span>置信度：{{ confidenceText }}</span>
          <span v-if="result.matched_jobs">匹配岗位：{{ result.matched_jobs }} 个</span>
        </div>
        <div v-if="result && parsedSkills.length" class="result-skills">
          <span class="skills-label">相关技能：</span>
          <el-tag v-for="s in parsedSkills" :key="s" size="small">{{ s }}</el-tag>
        </div>
      </div>
    </div>

    <div class="section-card gap-section">
      <div class="result-header">
        <div class="section-title result-title">技能缺口分析</div>
        <div class="form-actions">
          <el-button class="btn-pill btn-gap-action" round :loading="gapAnalyzing" @click="handleGapAnalyze">
            分析缺口
          </el-button>
        </div>
      </div>
      <div class="gap-desc">
        基于当前职位/城市，对比你的简历技能与目标岗位 JD 高频技能，输出「还差哪些技能」建议。
      </div>

      <div v-if="gapLoading" class="gap-loading" v-loading="gapLoading" style="height: 120px" />
      <div v-else-if="gapResult">
        <el-alert
          v-if="gapResult.total_matched_jobs === 0"
          type="warning"
          :closable="false"
          title="未匹配到相关岗位，建议更换职位或城市后重试"
          style="margin-bottom: 12px"
        />
        <div v-else class="gap-meta">
          匹配到 <b>{{ gapResult.total_matched_jobs }}</b> 个相关岗位，建议补充以下技能：
        </div>

        <div v-if="gapResult.skill_gaps.length" class="gap-list">
          <div v-for="g in gapResult.skill_gaps" :key="g.name" class="gap-item">
            <span class="gap-name">{{ g.name }}</span>
            <el-progress
              :percentage="Math.min(Math.round((g.ratio || 0) * 100), 100)"
              :stroke-width="10"
              :show-text="false"
            />
            <span class="gap-ratio">{{ Math.round((g.ratio || 0) * 100) }}% 岗位要求</span>
          </div>
        </div>
        <el-empty v-else description="很棒！你的技能已覆盖目标岗位的常见要求" :image-size="60" />

        <div v-if="gapResult.user_skills.length" class="gap-has">
          <span class="skills-label">我的技能：</span>
          <el-tag v-for="s in gapResult.user_skills" :key="s" size="small" type="success">{{ s }}</el-tag>
        </div>
      </div>
      <div v-else class="gap-placeholder">点击「分析缺口」查看目标岗位的技能要求差距</div>
    </div>

    <div class="section-card history-section">
      <div class="section-title">预测历史</div>
      <el-table :data="history" v-loading="historyLoading" stripe style="width: 100%">
        <el-table-column prop="resume_name" label="来源" min-width="140" show-overflow-tooltip />
        <el-table-column prop="predicted_salary_avg" label="预测薪资(K)" width="120">
          <template #default="{ row }">
            <span class="salary-highlight">{{ row.predicted_salary_avg }}</span>
          </template>
        </el-table-column>
        <el-table-column label="参考区间" width="140">
          <template #default="{ row }">
            <span>{{ row.predicted_salary_min }}—{{ row.predicted_salary_max }}K</span>
          </template>
        </el-table-column>
        <el-table-column prop="matched_jobs" label="匹配数" width="80" />
        <el-table-column prop="confidence" label="置信度" width="80">
          <template #default="{ row }">
            {{ row.confidence ? (row.confidence * 100).toFixed(0) + '%' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="170" />
      </el-table>
      <div class="pagination">
        <el-pagination
          v-model:current-page="historyPage"
          :page-size="historyPageSize"
          :total="historyTotal"
          background
          layout="total, prev, pager, next, jumper"
          @current-change="loadHistory"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { uploadResume, previewResume, manualPredict, getPredictHistory, analyzeSkillGap } from '@/api'
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'  // 第218行加 watch

const jobOptions = [
  'python', 'java', 'javascript', '前端开发', '数据分析',
  '产品经理', '运维工程师', '测试工程师', 'Go开发', '算法工程师',
]

const companySizeOptions = [
  '少于50人', '50-100人', '150-500人', '500-1000人', '1000-5000人', '5000人以上',
]

const experienceOptions = ['不限', '1年以下', '1-3年', '3-5年', '5-10年', '10年以上']

const educationOptions = ['不限', '初中', '高中', '中专', '大专', '本科', '硕士', '研究生', '博士']

const cityOptions = [
  '北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京',
  '西安', '重庆', '苏州', '天津', '长沙', '郑州', '东莞', '青岛',
]

const modelOptions = [
  { label: '梯度提升', value: 'gradient_boosting' },
  { label: 'CatBoost', value: 'catboost' },
  { label: 'Stacking集成', value: 'stacking_ensemble' },
]

const JOB_SKILL_PRESETS = {
  python: ['Python', 'Django', 'Flask', 'MySQL'],
  java: ['Java', 'Spring', 'MySQL'],
  javascript: ['JavaScript', 'Vue', 'React', 'Node.js'],
  前端开发: ['JavaScript', 'Vue', 'React', 'HTML'],
  数据分析: ['Python', '数据分析', 'SQL', 'Excel'],
  产品经理: ['产品设计', '数据分析', 'Axure'],
  运维工程师: ['Linux', 'Docker', 'Kubernetes', 'Shell'],
  测试工程师: ['测试', 'Python', 'Selenium'],
  Go开发: ['Go', 'MySQL', 'Redis'],
  算法工程师: ['Python', '机器学习', 'TensorFlow', 'PyTorch'],
}
const skillSuggestions = [
  'Python', 'Java', 'JavaScript', 'Go', 'C++', 'C#', 'PHP', 'Ruby',
  'MySQL', 'Redis', 'MongoDB', 'Oracle', 'PostgreSQL',
  'Django', 'Flask', 'Spring', 'SpringBoot', 'Vue', 'React', 'Angular',
  'Linux', 'Docker', 'Kubernetes', 'Git', 'Nginx',
  'SQL', 'HTML', 'CSS', 'Node.js', 'TypeScript',
  '数据分析', '机器学习', '深度学习', '算法', '数据结构',
]


const defaultForm = () => ({
  job: 'python',
  companySize: '150-500人',
  experience: '不限',
  education: '本科',
  city: '广州',
  model: 'gradient_boosting',
  userSkills: ['Python', 'Django', 'Flask', 'MySQL'],
})

const predictMode = ref('manual')
const form = ref(defaultForm())
const uploadForm = ref({ city: '广州', companySize: '', model: 'gradient_boosting' })
const uploadFile = ref(null)
const fileList = ref([])
const previewText = ref('')
const previewFileName = ref('')
const previewPdfUrl = ref('')
const previewLoading = ref(false)
const predicting = ref(false)
const result = ref(null)
const gapAnalyzing = ref(false)
const gapLoading = ref(false)
const gapResult = ref(null)
const history = ref([])
const historyLoading = ref(false)
const historyPage = ref(1)
const historyPageSize = 10
watch(() => form.value.job, (newJob) => {
  if (newJob) {
    const preset = skillsFromJob(newJob)
    if (preset.length && !form.value.userSkills?.length) {
      form.value.userSkills = [...preset]
    }
  }
})
const historyTotal = ref(0)

const avgSalaryText = computed(() => {
  if (!result.value) return ''
  const avg = result.value.predicted_salary_avg
  return `${avg}K`
})

const resultRangeText = computed(() => {
  if (!result.value) return ''
  const min = Math.round(result.value.predicted_salary_min)
  const max = Math.round(result.value.predicted_salary_max)
  return `${min}—${max}K`
})

const confidenceText = computed(() => {
  if (!result.value?.confidence) return '-'
  return `${(result.value.confidence * 100).toFixed(1)}%`
})

const parsedSkills = computed(() => {
  if (!result.value?.skills_extracted) return []
  try {
    return JSON.parse(result.value.skills_extracted)
  } catch {
    return []
  }
})

function skillsFromJob(job) {
  const key = (job || '').toLowerCase()
  if (JOB_SKILL_PRESETS[key]) return [...JOB_SKILL_PRESETS[key]]
  if (JOB_SKILL_PRESETS[job]) return [...JOB_SKILL_PRESETS[job]]
  return [job].filter(Boolean)
}

function clearPreview() {
  previewText.value = ''
  previewFileName.value = ''
  if (previewPdfUrl.value) {
    URL.revokeObjectURL(previewPdfUrl.value)
    previewPdfUrl.value = ''
  }
}

async function loadResumePreview(file) {
  clearPreview()
  if (!file) return

  const name = file.name || ''
  const ext = name.includes('.') ? name.split('.').pop().toLowerCase() : ''
  previewFileName.value = name
  previewLoading.value = true

  try {
    if (ext === 'pdf') {
      previewPdfUrl.value = URL.createObjectURL(file)
    } else if (ext === 'txt') {
      previewText.value = await file.text()
    } else {
      const formData = new FormData()
      formData.append('file', file)
      const res = await previewResume(formData)
      const text = res.data?.text || ''
      previewText.value = text.trim()
        ? text
        : `已选择文件：${name}\n\n未能提取到可读文本，仍可提交进行薪资预测。`
    }
  } catch (err) {
    previewText.value = `已选择文件：${name}\n\n预览加载失败，仍可提交进行薪资预测。`
    ElMessage.warning(err?.response?.data?.message || '简历预览失败')
  } finally {
    previewLoading.value = false
  }
}

function handleFileChange(file) {
  uploadFile.value = file.raw
  fileList.value = [file]
  loadResumePreview(file.raw)
}

function handleFileRemove() {
  uploadFile.value = null
  fileList.value = []
  clearPreview()
}

function handleManualSubmit() {
  if (!form.value.job) {
    ElMessage.warning('请选择或输入职位')
    return
  }
    const skills = form.value.userSkills?.length ? form.value.userSkills : skillsFromJob(form.value.job)
  predicting.value = true
  manualPredict({
    job: form.value.job,
    skills,
    experience: form.value.experience,
    education: form.value.education,
    city: form.value.city || '',
    company_size: form.value.companySize || '',
    model: form.value.model || 'gradient_boosting',
  }).then(res => {
    result.value = res.data
    ElMessage.success('预测完成')
    refreshHistoryToFirst()
  }).catch(err => {
    ElMessage.error(err?.response?.data?.message || err?.message || '预测失败')
  }).finally(() => {
    predicting.value = false
  })
}

function handleUploadSubmit() {
  if (!uploadFile.value) {
    ElMessage.warning('请先上传简历文件')
    return
  }
  predicting.value = true
  const formData = new FormData()
  formData.append('file', uploadFile.value)
  if (uploadForm.value.city) formData.append('city', uploadForm.value.city)
  if (uploadForm.value.companySize) formData.append('company_size', uploadForm.value.companySize)
  formData.append('model', uploadForm.value.model || 'gradient_boosting')

  uploadResume(formData).then(res => {
    result.value = res.data
    ElMessage.success('预测完成')
    refreshHistoryToFirst()
  }).catch(err => {
    ElMessage.error(err?.response?.data?.message || err?.message || '预测失败')
  }).finally(() => {
    predicting.value = false
  })
}

function handleSubmit() {
  if (predictMode.value === 'manual') {
    handleManualSubmit()
  } else {
    handleUploadSubmit()
  }
}

function handleGapAnalyze() {
  let skills = []
  let jobTitle = ''
  let city = ''
  if (predictMode.value === 'manual') {
    if (!form.value.job) {
      ElMessage.warning('请选择或输入职位')
      return
    }
    jobTitle = form.value.job
        skills = form.value.userSkills?.length ? form.value.userSkills : skillsFromJob(form.value.job)
    city = form.value.city || ''
  } else {
    // 上传模式：优先从简历解析结果中提取技能与目标职位
    const extracted = result.value?.extracted || {}
    skills = extracted.skills && extracted.skills.length ? extracted.skills : []
    jobTitle = extracted.job_title || ''
    city = uploadForm.value.city || extracted.city || ''
    if (!skills.length) {
      ElMessage.warning('请先上传简历并提交预测，系统将自动解析简历技能')
      return
    }
  }

  gapAnalyzing.value = true
  gapLoading.value = true
  gapResult.value = null
  analyzeSkillGap({
    skills,
    job: jobTitle || '',
    city,
    top_n: 12,
  }).then(res => {
    gapResult.value = res.data
    if (res.data?.warning) {
      ElMessage.warning(res.data.warning)
    }
  }).catch(err => {
    ElMessage.error(err?.response?.data?.message || err?.message || '技能缺口分析失败')
  }).finally(() => {
    gapAnalyzing.value = false
    gapLoading.value = false
  })
}

function handleReset() {
  form.value = defaultForm()
  uploadForm.value = { city: '广州', companySize: '', model: 'gradient_boosting' }
  uploadFile.value = null
  fileList.value = []
  result.value = null
  clearPreview()
}

function loadHistory(page) {
  if (typeof page === 'number' && page > 0) {
    historyPage.value = page
  }
  historyLoading.value = true
  getPredictHistory({
    page: historyPage.value,
    per_page: historyPageSize,
  }).then(res => {
    history.value = res.data.items || []
    historyTotal.value = res.data.total || 0
  }).finally(() => {
    historyLoading.value = false
  })
}

function refreshHistoryToFirst() {
  historyPage.value = 1
  loadHistory(1)
}

onMounted(() => loadHistory(1))
onBeforeUnmount(() => clearPreview())
</script>

<style scoped lang="scss">
.predict-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-bottom: 16px;
}

.section-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  padding: 20px 24px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #009688;
}

.mode-tabs {
  margin-bottom: 8px;

  :deep(.el-tabs__header) {
    margin-bottom: 16px;
  }
}

.info-form {
  .form-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px 24px;

    @media (max-width: 1100px) {
      grid-template-columns: repeat(2, 1fr);
    }

    @media (max-width: 700px) {
      grid-template-columns: 1fr;
    }
  }

  :deep(.el-form-item) {
    margin-bottom: 12px;
  }

  :deep(.el-form-item__label) {
    color: #666;
    font-size: 13px;
  }
}

.upload-section {
  .upload-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    align-items: stretch;
    min-height: 360px;

    @media (max-width: 900px) {
      grid-template-columns: 1fr;
    }
  }

  .upload-left,
  .upload-right {
    min-width: 0;
    display: flex;
    flex-direction: column;
  }

  .upload-area {
    width: 100%;

    :deep(.el-upload) {
      width: 100%;
    }

    :deep(.el-upload-dragger) {
      width: 100%;
      min-height: 180px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      border-color: #dcdfe6;
      background: #fafafa;

      &:hover {
        border-color: #409eff;
      }
    }
  }

  .upload-extra {
    margin-top: 16px;

    :deep(.el-form-item) {
      margin-bottom: 12px;
    }

    :deep(.el-select) {
      width: 100%;
    }
  }

  .resume-preview {
    position: relative;
    flex: 1;
    min-height: 320px;
    border: 1px solid #e8e8e8;
    border-radius: 4px;
    background: #fafafa;
    overflow: hidden;
  }

  .preview-placeholder {
    height: 100%;
    min-height: 320px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #c0c4cc;
    font-size: 15px;
    padding: 24px;
    text-align: center;
  }

  .preview-text {
    margin: 0;
    height: 100%;
    min-height: 320px;
    max-height: 480px;
    overflow: auto;
    padding: 16px 16px 36px;
    white-space: pre-wrap;
    word-break: break-word;
    font-family: Consolas, 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.6;
    color: #333;
    background: #fff;
  }

  .preview-pdf {
    height: 100%;
    min-height: 320px;

    iframe {
      width: 100%;
      height: 480px;
      border: none;
      background: #fff;
    }
  }

  .preview-filename {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    padding: 6px 12px;
    font-size: 12px;
    color: #909399;
    background: rgba(255, 255, 255, 0.92);
    border-top: 1px solid #f0f0f0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.result-title {
  margin-bottom: 0;
  flex-shrink: 0;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  margin-left: auto;
  position: relative;
  z-index: 2;
}

.result-section {
  min-height: 200px;
}

.result-box {
  position: relative;
  min-height: 140px;
  padding: 24px;
  background: #fafafa;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  text-align: center;
  clear: both;
}

.result-label {
  position: absolute;
  top: 16px;
  left: 20px;
  font-size: 14px;
  color: #666;
}

.result-value {
  font-size: 48px;
  font-weight: 700;
  color: #009688;
  line-height: 1.4;
  padding: 20px 0 8px;
  letter-spacing: 1px;
}

.result-placeholder {
  font-size: 16px;
  color: #999;
  padding: 40px 0;
}

.result-meta {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 16px 24px;
  font-size: 13px;
  color: #666;
  margin-top: 8px;
}

.result-skills {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 14px;

  .skills-label {
    font-size: 13px;
    color: #666;
  }
}

.btn-reset-action {
  background: #3498db !important;
  border: none !important;
  color: #fff !important;
  padding: 10px 28px !important;
  min-width: 88px;

  &:hover {
    background: #2980b9 !important;
  }
}

.btn-submit-action {
  background: #f5a623 !important;
  border: none !important;
  color: #fff !important;
  padding: 10px 28px !important;
  min-width: 88px;

  &:hover {
    background: #e6951a !important;
  }
}

.btn-gap-action {
  background: #009688 !important;
  border: none !important;
  color: #fff !important;
  padding: 10px 28px !important;
  min-width: 88px;

  &:hover {
    background: #007a6e !important;
  }
}

.gap-section {
  .gap-desc {
    font-size: 13px;
    color: #888;
    margin-bottom: 14px;
  }

  .gap-meta {
    font-size: 13px;
    color: #555;
    margin-bottom: 12px;
  }

  .gap-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-width: 640px;
  }

  .gap-item {
    display: flex;
    align-items: center;
    gap: 12px;

    .gap-name {
      width: 120px;
      font-size: 13px;
      font-weight: 500;
      color: #333;
      flex-shrink: 0;
    }

    :deep(.el-progress) {
      flex: 1;
    }

    .gap-ratio {
      width: 110px;
      font-size: 12px;
      color: #999;
      text-align: right;
      flex-shrink: 0;
    }
  }

  .gap-has {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 16px;

    .skills-label {
      font-size: 13px;
      color: #666;
    }
  }

  .gap-placeholder {
    font-size: 14px;
    color: #aaa;
    text-align: center;
    padding: 32px 0;
  }
}

.history-section {
  :deep(.el-table) {
    margin-top: 4px;
  }

  .pagination {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
  }

  :deep(.el-pagination.is-background .el-pager li.is-active) {
    background-color: #009688;
  }
}

.salary-highlight {
  color: #009688;
  font-weight: 600;
}
</style>
