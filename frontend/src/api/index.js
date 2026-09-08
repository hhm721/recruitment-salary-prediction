import axios from 'axios'
import { ElMessage } from 'element-plus'
import { downloadExport } from '@/utils/download'

const TOKEN_KEY = 'token'

const request = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code && res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message))
    }
    return res
  },
  (error) => {
    const message = error.response?.data?.message || error.message || '网络错误'
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem('userInfo')
      if (!window.location.pathname.startsWith('/login') && !window.location.pathname.startsWith('/register')) {
        ElMessage.error(message || '登录已过期，请重新登录')
        window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`
      }
    } else {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

export default request

// Auth API
export const login = (data) => request.post('/auth/login', data)
export const register = (data) => request.post('/auth/register', data)
export const getProfile = () => request.get('/auth/me')
export const logout = () => request.post('/auth/logout')

// Jobs API
export const getRawJobs = (params) => request.get('/jobs/raw', { params })
export const updateRawJob = (id, data) => request.put(`/jobs/raw/${id}`, data)
export const deleteRawJob = (id) => request.delete(`/jobs/raw/${id}`)
export const exportRawJobs = (params) => downloadExport('/api/jobs/raw/export', params, '原始数据.xlsx')

export const getCleanJobs = (params) => request.get('/rinse/clean', { params })
export const updateCleanJob = (id, data) => request.put(`/rinse/clean/${id}`, data)
export const deleteCleanJob = (id) => request.delete(`/rinse/clean/${id}`)
export const exportCleanJobs = (params) => downloadExport('/api/rinse/clean/export', params, '清洗数据.xlsx')

export const runClean = (data) => request.post('/rinse/clean/run', data)
export const getPlatforms = () => request.get('/jobs/platforms')

// Crawl API
export const startCrawl = (data) => request.post('/crawl/start', data)
export const getCrawlTasks = (params) => request.get('/crawl/tasks', { params })
export const deleteCrawlTask = (id) => request.delete(`/crawl/tasks/${id}`)

// Stats API
export const getDashboard = () => request.get('/stats/dashboard')
export const getOverview = () => request.get('/stats/overview')



// Predict API
export const uploadResume = (formData) => request.post('/predict/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
})
export const previewResume = (formData) => request.post('/predict/preview', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
})
export const manualPredict = (data) => request.post('/predict/manual', data)
export const getPredictHistory = (params) => request.get('/predict/history', { params })
export const analyzeSkillGap = (data) => request.post('/predict/skill-gap', data)

// Stats API 扩展
export const getSkillCitySalary = (params) => request.get('/stats/skill-city-salary', { params })