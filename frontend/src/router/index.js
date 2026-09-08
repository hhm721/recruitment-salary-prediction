import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const visualRoutes = [
  { path: 'visual/national', name: 'VisualNational', component: () => import('@/views/visual/NationalVisual.vue'), meta: { title: '全国情况', requiresAuth: true, hideToolbar: true } },
  { path: 'visual/salary', name: 'VisualSalary', component: () => import('@/views/visual/VisualAnalysis.vue'), props: { type: 'salary' }, meta: { title: '薪资情况', requiresAuth: true, hideToolbar: true } },
  { path: 'visual/enterprise', name: 'VisualEnterprise', component: () => import('@/views/visual/VisualAnalysis.vue'), props: { type: 'enterprise' }, meta: { title: '企业情况', requiresAuth: true, hideToolbar: true } },
  { path: 'visual/welfare', name: 'VisualWelfare', component: () => import('@/views/visual/VisualAnalysis.vue'), props: { type: 'welfare' }, meta: { title: '福利情况', requiresAuth: true, hideToolbar: true } },
  { path: 'visual/education', name: 'VisualEducation', component: () => import('@/views/visual/VisualAnalysis.vue'), props: { type: 'education' }, meta: { title: '学历情况', requiresAuth: true, hideToolbar: true } },
  { path: 'visual/financing', name: 'VisualFinancing', component: () => import('@/views/visual/VisualAnalysis.vue'), props: { type: 'financing' }, meta: { title: '融资情况', requiresAuth: true, hideToolbar: true } },
  { path: 'visual/job-type', name: 'VisualJobType', component: () => import('@/views/visual/VisualAnalysis.vue'), props: { type: 'job-type' }, meta: { title: '职位类型', requiresAuth: true, hideToolbar: true } },
  { path: 'visual/skill-city', name: 'VisualSkillCity', component: () => import('@/views/visual/VisualAnalysis.vue'), props: { type: 'skill-city' }, meta: { title: '技能交叉', requiresAuth: true, hideToolbar: true } },
]

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '招聘数据智能分析', transition: 'page' },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', guest: true },
  },
  {
    path: '/app',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/app/home',
    meta: { requiresAuth: true },
    children: [
      { path: 'home', name: 'AppHome', component: () => import('@/views/AppHome.vue'), meta: { title: '首页', requiresAuth: true, hideToolbar: true } },
      { path: 'crawl', name: 'Crawl', component: () => import('@/views/CrawlManage.vue'), meta: { title: '爬虫管理', requiresAuth: true, hideToolbar: true } },
      { path: 'raw-data', name: 'RawData', component: () => import('@/views/RawData.vue'), meta: { title: '原始数据', requiresAuth: true, autoSearch: true } },
      { path: 'clean-data', name: 'CleanData', component: () => import('@/views/CleanData.vue'), meta: { title: '数据清洗', requiresAuth: true, autoSearch: true } },
      { path: 'predict', name: 'Predict', component: () => import('@/views/SalaryPredict.vue'), meta: { title: '薪资预测', requiresAuth: true, hideToolbar: true } },
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '可视化大屏', requiresAuth: true } },
      ...visualRoutes,
    ],
  },
  { path: '/dashboard', redirect: '/app/visual/national' },
  { path: '/raw-data', redirect: '/app/raw-data' },
  { path: '/clean-data', redirect: '/app/clean-data' },
  { path: '/crawl', redirect: '/app/crawl' },
  { path: '/predict', redirect: '/app/predict' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0 }
  },
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title
    ? `${to.meta.title} - 招聘数据分析系统`
    : '招聘数据智能分析平台'

  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  if (to.meta.guest && userStore.isLoggedIn) {
    next('/')
    return
  }

  next()
})

export default router
