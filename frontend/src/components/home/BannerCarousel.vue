<template>
  <section id="banner" class="banner-section">
    <div class="banner-carousel">
      <div class="banner-track" :style="{ transform: `translateX(-${currentIndex * 100}%)` }">
        <div
          v-for="(slide, index) in slides"
          :key="index"
          class="banner-slide"
          :style="{ background: slide.bg }"
        >
          <div class="slide-bg-decor">
            <div class="decor-circle c1" />
            <div class="decor-circle c2" />
            <div class="decor-grid" />
          </div>

          <div class="home-container slide-inner">
            <div class="slide-text">
              <span class="slide-tag">{{ slide.tag }}</span>
              <h2 class="slide-title">
                <span v-for="(line, i) in slide.titleLines" :key="i">{{ line }}</span>
              </h2>
              <p class="slide-desc">{{ slide.desc }}</p>
              <div class="slide-actions">
                <el-button type="primary" size="large" round class="slide-btn-primary" @click="handleAction(slide)">
                  {{ slide.btnText }}
                  <el-icon class="el-icon--right"><ArrowRight /></el-icon>
                </el-button>
                <el-button v-if="slide.btnSecondary" size="large" round class="slide-btn-secondary" @click="scrollTo(slide.secondaryLink)">
                  {{ slide.btnSecondary }}
                </el-button>
              </div>
              <div class="slide-stats">
                <div v-for="s in slide.stats" :key="s.label" class="slide-stat-item">
                  <strong>{{ s.value }}</strong>
                  <span>{{ s.label }}</span>
                </div>
              </div>
            </div>

            <div class="slide-visual">
              <div class="visual-card" :class="slide.visualType">
                <div class="visual-header">
                  <span /><span /><span />
                  <em>{{ slide.visualTitle }}</em>
                </div>
                <div class="visual-body">
                  <template v-if="slide.visualType === 'chart'">
                    <div v-for="(bar, bi) in slide.visualData" :key="bi" class="v-bar-row">
                      <label>{{ bar.label }}</label>
                      <div class="v-bar-track"><div class="v-bar-fill" :style="{ width: bar.width, background: bar.color }" /></div>
                      <span>{{ bar.value }}</span>
                    </div>
                  </template>
                  <template v-else-if="slide.visualType === 'platform'">
                    <div class="platform-grid">
                      <div v-for="p in slide.visualData" :key="p.name" class="platform-chip" :style="{ '--c': p.color }">
                        <strong>{{ p.short }}</strong>
                        <span>{{ p.name }}</span>
                      </div>
                    </div>
                  </template>
                  <template v-else-if="slide.visualType === 'predict'">
                    <div class="predict-display">
                      <div class="predict-salary">{{ slide.visualData.salary }}</div>
                      <div class="predict-range">{{ slide.visualData.range }}</div>
                      <div class="predict-skills">
                        <span v-for="sk in slide.visualData.skills" :key="sk">{{ sk }}</span>
                      </div>
                    </div>
                  </template>
                  <template v-else>
                    <div class="flow-mini">
                      <div v-for="(step, si) in slide.visualData" :key="si" class="flow-step">
                        <div class="flow-dot">{{ si + 1 }}</div>
                        <span>{{ step }}</span>
                      </div>
                    </div>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 左右箭头 -->
      <button class="banner-arrow prev" @click="prev" aria-label="上一张">
        <el-icon :size="20"><ArrowLeft /></el-icon>
      </button>
      <button class="banner-arrow next" @click="next" aria-label="下一张">
        <el-icon :size="20"><ArrowRight /></el-icon>
      </button>

      <!-- 指示器 -->
      <div class="banner-dots">
        <button
          v-for="(_, i) in slides"
          :key="i"
          class="dot"
          :class="{ active: currentIndex === i }"
          @click="goTo(i)"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const emit = defineEmits(['enter'])
const router = useRouter()
const userStore = useUserStore()

const currentIndex = ref(0)
let autoTimer

const slides = [
  {
    tag: '数据采集 · 四平台覆盖',
    titleLines: ['整合 前程无忧 / 智联 / 拉勾 / 猎聘', '一键异步采集招聘数据'],
    desc: '基于 Scrapy 框架构建可独立触发的异步采集模块，支持关键词与城市筛选，任务状态实时监控，数据自动持久化至 MySQL。',
    btnText: '立即体验采集',
    btnSecondary: '了解核心优势',
    secondaryLink: '#platform',
    action: 'crawl',
    bg: 'linear-gradient(145deg, #0a0e17 0%, rgba(22, 119, 255, 0.12) 55%, #0a0e17 100%)',
    visualType: 'platform',
    visualTitle: '四大招聘平台',
    stats: [
      { value: '4', label: '主流平台' },
      { value: 'Scrapy', label: '爬虫引擎' },
      { value: '实时', label: '任务监控' },
    ],
    visualData: [
      { short: '前程', name: '前程无忧', color: '#ff6a00' },
      { short: '智联', name: '智联招聘', color: '#0066cc' },
      { short: '拉勾', name: '拉勾网', color: '#00b38a' },
      { short: '猎聘', name: '猎聘网', color: '#ff6600' },
    ],
  },
  {
    tag: '可视化分析 · 数据大屏',
    titleLines: ['ECharts 动态图表', '多维度交互式数据洞察'],
    desc: '岗位数量、薪资分布、城市排名、技能热词、经验-薪资关系等 8 类动态图表，实时对接 Flask RESTful API，支持多端响应式展示。',
    btnText: '查看可视化大屏',
    btnSecondary: '功能模块介绍',
    secondaryLink: '#platform',
    action: 'dashboard',
    bg: 'linear-gradient(145deg, #0a0e17 0%, rgba(19, 194, 194, 0.1) 50%, #0a0e17 100%)',
    visualType: 'chart',
    visualTitle: '数据分析大屏',
    stats: [
      { value: '8+', label: '图表类型' },
      { value: '实时', label: '数据刷新' },
      { value: '多端', label: '响应适配' },
    ],
    visualData: [
      { label: '平台分布', width: '78%', value: '饼图', color: 'linear-gradient(90deg,#409eff,#67c8ff)' },
      { label: '薪资区间', width: '85%', value: '环形图', color: 'linear-gradient(90deg,#36d7b7,#5eead4)' },
      { label: '城市 TOP10', width: '70%', value: '柱状图', color: 'linear-gradient(90deg,#f5a623,#fbbf24)' },
      { label: '技能热词', width: '82%', value: '条形图', color: 'linear-gradient(90deg,#9b59b6,#a78bfa)' },
    ],
  },
  {
    tag: 'AI 智能 · 薪资预测',
    titleLines: ['上传简历 · ML 模型推理', '精准预估匹配岗位薪资'],
    desc: '利用历史招聘数据训练 GradientBoosting 回归模型，自动解析简历技能与经验，推理输出预估薪资区间及匹配置信度。',
    btnText: '开始薪资预测',
    btnSecondary: '查看系统流程',
    secondaryLink: '#scenarios',
    action: 'predict',
    bg: 'linear-gradient(145deg, #0a0e17 0%, rgba(114, 46, 209, 0.12) 48%, #0a0e17 100%)',
    visualType: 'predict',
    visualTitle: '薪资预测引擎',
    stats: [
      { value: 'ML', label: '机器学习' },
      { value: '85%', label: '预测置信度' },
      { value: '多格式', label: '简历支持' },
    ],
    visualData: {
      salary: '25.6K',
      range: '预估范围: 22K - 29K',
      skills: ['Python', 'Flask', 'Vue3', 'MySQL', '机器学习'],
    },
  },
  {
    tag: '全链路闭环 · 企业级架构',
    titleLines: ['采集 → 清洗 → 存储 → 分析 → 预测', 'Flask + Vue3 前后端完全解耦'],
    desc: '从 Scrapy 异步采集到数据清洗、MySQL 持久化、ECharts 可视化分析与 ML 薪资预测，构建完整的招聘数据智能分析闭环。',
    btnText: '进入管理系统',
    btnSecondary: null,
    action: 'enter',
    bg: 'linear-gradient(145deg, #0a0e17 0%, rgba(245, 166, 35, 0.08) 52%, #0a0e17 100%)',
    visualType: 'flow',
    visualTitle: '系统全链路',
    stats: [
      { value: '5', label: '核心环节' },
      { value: 'REST', label: 'API 架构' },
      { value: '100%', label: '前后端解耦' },
    ],
    visualData: ['数据采集', '数据清洗', '数据存储', '可视化分析', '智能预测'],
  },
]

function goTo(i) {
  currentIndex.value = i
  resetAutoPlay()
}

function next() {
  currentIndex.value = (currentIndex.value + 1) % slides.length
  resetAutoPlay()
}

function prev() {
  currentIndex.value = (currentIndex.value - 1 + slides.length) % slides.length
  resetAutoPlay()
}

function handleAction(slide) {
  const routes = {
    crawl: '/app/crawl',
    dashboard: '/app/dashboard',
    predict: '/app/predict',
    enter: '/app/dashboard',
  }
  const target = routes[slide.action] || '/app/dashboard'
  if (userStore.isLoggedIn) {
    router.push(target)
  } else {
    router.push({ path: '/login', query: { redirect: target } })
  }
}

function scrollTo(selector) {
  document.querySelector(selector)?.scrollIntoView({ behavior: 'smooth' })
}

function resetAutoPlay() {
  clearInterval(autoTimer)
  autoTimer = setInterval(next, 6000)
}

onMounted(() => {
  autoTimer = setInterval(next, 6000)
})
onUnmounted(() => clearInterval(autoTimer))
</script>

<style scoped lang="scss">
.banner-section {
  padding-top: 64px;
  margin-bottom: 0;
}

.banner-carousel {
  position: relative;
  overflow: hidden;
  height: 480px;

  @media (max-width: 900px) {
    height: auto;
    min-height: 520px;
  }
}

.banner-track {
  display: flex;
  height: 100%;
  transition: transform 0.7s cubic-bezier(0.4, 0, 0.2, 1);
}

.banner-slide {
  min-width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.slide-bg-decor {
  position: absolute;
  inset: 0;
  pointer-events: none;

  .decor-circle {
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);

    &.c1 {
      width: 400px; height: 400px;
      background: rgba(22, 119, 255, 0.18);
      top: -100px; right: 10%;
    }
    &.c2 {
      width: 300px; height: 300px;
      background: rgba(19, 194, 194, 0.12);
      bottom: -50px; left: 5%;
    }
  }

  .decor-grid {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(22, 119, 255, 0.05) 1px, transparent 1px),
      linear-gradient(90deg, rgba(22, 119, 255, 0.05) 1px, transparent 1px);
    background-size: 50px 50px;
    mask-image: radial-gradient(ellipse at 70% 50%, black 10%, transparent 60%);
  }
}

.slide-inner {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  align-items: center;
  padding: 16px 0 36px;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 20px 0 56px;
  }
}

.slide-tag {
  display: inline-block;
  padding: 5px 14px;
  border-radius: var(--radius-xl);
  background: rgba(22, 119, 255, 0.15);
  border: 1px solid rgba(96, 165, 250, 0.35);
  color: #60a5fa;
  font-size: 12px;
  margin-bottom: 12px;
}

.slide-title {
  margin-bottom: 12px;

  span {
    display: block;
    font-size: clamp(26px, 3.8vw, 40px);
    font-weight: 800;
    line-height: 1.25;
    color: #f1f5f9;
    letter-spacing: -0.5px;

    &:last-child {
      background: linear-gradient(90deg, #60a5fa, #1677ff, #13c2c2);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
  }
}

.slide-desc {
  font-size: 15px;
  line-height: 1.75;
  color: #94a3b8;
  margin-bottom: 20px;
  max-width: 520px;
}

.slide-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.slide-btn-primary {
  background: var(--gradient-btn) !important;
  border: none !important;
  box-shadow: 0 6px 28px rgba(22, 119, 255, 0.35);
  transition: transform 0.3s;

  &:hover { transform: translateY(-2px); }
}

.slide-btn-secondary {
  background: rgba(255, 255, 255, 0.06) !important;
  border-color: rgba(255, 255, 255, 0.15) !important;
  color: #e2e8f0 !important;

  &:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    border-color: rgba(96, 165, 250, 0.4) !important;
    color: #60a5fa !important;
  }
}

.slide-stats {
  display: flex;
  gap: 24px;

  .slide-stat-item {
    strong {
      display: block;
      font-size: 20px;
      font-weight: 800;
      background: linear-gradient(90deg, #60a5fa, #13c2c2);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    span {
      font-size: 12px;
      color: #64748b;
    }
  }
}

.visual-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(16px);
  animation: slideInRight 0.8s ease both;
}

.visual-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.04);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);

  span:nth-child(1) { width: 10px; height: 10px; border-radius: 50%; background: #e74c6f; }
  span:nth-child(2) { width: 10px; height: 10px; border-radius: 50%; background: #f5a623; }
  span:nth-child(3) { width: 10px; height: 10px; border-radius: 50%; background: #36d7b7; }

  em {
    margin-left: auto;
    font-style: normal;
    font-size: 12px;
    color: #64748b;
  }
}

.visual-body {
  padding: 16px;
}

.v-bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;

  label { width: 72px; font-size: 12px; color: #94a3b8; flex-shrink: 0; }
  .v-bar-track {
    flex: 1;
    height: 8px;
    background: rgba(255, 255, 255, 0.06);
    border-radius: 4px;
    overflow: hidden;
  }
  .v-bar-fill {
    height: 100%;
    border-radius: 4px;
    animation: barGrow 1s ease both;
  }
  span { width: 48px; text-align: right; font-size: 12px; color: #60a5fa; }
}

.platform-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.platform-chip {
  padding: 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-left: 3px solid var(--c);
  transition: transform 0.3s, background 0.3s;

  &:hover {
    transform: translateX(4px);
    background: rgba(255, 255, 255, 0.08);
  }

  strong { display: block; font-size: 16px; color: var(--c); margin-bottom: 4px; }
  span { font-size: 12px; color: #64748b; }
}

.predict-display {
  text-align: center;
  padding: 16px 0;

  .predict-salary {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(90deg, #60a5fa, #13c2c2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .predict-range {
    color: #94a3b8;
    font-size: 14px;
    margin: 8px 0 20px;
  }
  .predict-skills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;

    span {
      padding: 4px 12px;
      border-radius: 20px;
      background: rgba(22, 119, 255, 0.12);
      border: 1px solid rgba(96, 165, 250, 0.25);
      font-size: 12px;
      color: #94a3b8;
    }
  }
}

.flow-mini {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.flow-step {
  display: flex;
  align-items: center;
  gap: 12px;

  .flow-dot {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--gradient-brand);
    color: #fff;
    font-size: 12px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  span { font-size: 14px; color: #cbd5e1; }
}

.banner-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(10, 14, 23, 0.65);
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: all 0.3s;
  backdrop-filter: blur(12px);

  &:hover {
    background: rgba(22, 119, 255, 0.2);
    border-color: rgba(96, 165, 250, 0.45);
    color: #60a5fa;
  }

  &.prev { left: calc(10% - 22px); }
  &.next { right: calc(10% - 22px); }

  @media (max-width: 900px) {
    &.prev { left: 12px; }
    &.next { right: 12px; }
  }
}

.banner-dots {
  position: absolute;
  bottom: 22px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  z-index: 10;

  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    border: none;
    background: rgba(255, 255, 255, 0.15);
    cursor: pointer;
    transition: all 0.35s;
    padding: 0;

    &.active {
      width: 32px;
      border-radius: 5px;
      background: linear-gradient(90deg, #4096ff, #1677ff, #13c2c2);
    }
  }
}

@keyframes slideInRight {
  from { opacity: 0; transform: translateX(30px); }
  to { opacity: 1; transform: translateX(0); }
}
@keyframes barGrow {
  from { width: 0 !important; }
}
</style>
