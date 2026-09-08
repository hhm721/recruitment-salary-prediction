<template>
  <section id="platform" class="unified-platform section">
    <div class="home-container">
      <div class="section-header reveal">
        <h2>招聘数据智能分析一体化平台</h2>
        <p>从数据采集到智能预测，构建覆盖招聘全链路的统一分析能力</p>
      </div>

      <div class="solution-cards reveal">
        <article
          v-for="item in pillars"
          :key="item.key"
          class="solution-card"
          :class="{ active: activeKey === item.key }"
          @mouseenter="onCardEnter(item.key)"
          @mouseleave="onCardLeave"
          @click="onCardClick(item.key)"
        >
          <div class="card-bg">
            <img :src="item.image" :alt="item.label" loading="lazy" />
          </div>
          <div class="card-overlay" />

          <div class="card-body">
            <h3 class="card-title">{{ item.label }}</h3>

            <p class="card-brief">{{ item.brief }}</p>

            <div class="card-detail">
              <p class="detail-desc">{{ item.desc }}</p>
              <div class="detail-tags">
                <span class="tags-label">核心能力</span>
                <div class="tags-list">
                  <span v-for="tag in item.tags" :key="tag" class="tag-pill">{{ tag }}</span>
                </div>
              </div>
              <button class="detail-link" @click.stop="$emit('enter', item.route)">
                查看详情
                <el-icon><ArrowRight /></el-icon>
              </button>
            </div>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

defineEmits(['enter'])

const activeKey = ref('')
const isMobile = ref(false)

function updateMobile() {
  isMobile.value = window.innerWidth <= 960
}

function onCardEnter(key) {
  if (!isMobile.value) activeKey.value = key
}

function onCardLeave() {
  if (!isMobile.value) activeKey.value = ''
}

function onCardClick(key) {
  if (isMobile.value) {
    activeKey.value = activeKey.value === key ? '' : key
  }
}

onMounted(() => {
  updateMobile()
  window.addEventListener('resize', updateMobile, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('resize', updateMobile)
})

const pillars = [
  {
    key: 'crawl',
    label: '数据采集',
    brief: '整合 BOSS/智联/拉勾/猎聘四大平台，Scrapy 异步采集，任务状态实时监控。',
    desc: '招聘行业面临数据源分散、更新频率高、格式不统一等挑战。系统基于 Scrapy 框架构建独立触发的异步采集模块，支持关键词与城市筛选，数据自动持久化至 MySQL。',
    tags: ['BOSS直聘', '智联招聘', '拉勾网', '猎聘网'],
    image: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=480&h=640&fit=crop&q=80',
    route: '/app/crawl',
  },
  {
    key: 'clean',
    label: '数据清洗',
    brief: '自动解析薪资、提取技能标签，将原始数据转化为结构化高质量数据集。',
    desc: '原始招聘数据格式各异，薪资描述不规范。系统提供批量 ETL 处理，支持薪资智能解析、40+ 技能标签提取、学历经验标准化，并支持 Excel/JSON/TXT 导出。',
    tags: ['薪资解析', '技能提取', '批量ETL', '多格式导出'],
    image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=480&h=640&fit=crop&q=80',
    route: '/app/clean-data',
  },
  {
    key: 'viz',
    label: '可视化分析',
    brief: 'ECharts 动态大屏，展示平台分布、薪资区间、城市排名等多维洞察。',
    desc: '企业需要直观掌握招聘市场趋势。系统集成 ECharts 引擎，对接 Flask API 实时刷新，展示 8 类交互图表，支持中国地图与多端响应式布局。',
    tags: ['ECharts', '中国地图', '实时刷新', '多维分析'],
    image: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=480&h=640&fit=crop&q=80',
    route: '/app/dashboard',
  },
  {
    key: 'predict',
    label: '智能预测',
    brief: 'ML 薪资预测模型，上传简历即可推理匹配岗位的预估薪资区间。',
    desc: '系统利用历史数据训练 GradientBoosting 模型，自动解析简历技能与经验，推理输出预估薪资及匹配置信度，保留完整预测历史。',
    tags: ['GradientBoosting', '简历解析', '薪资推理', '置信度评估'],
    image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=480&h=640&fit=crop&q=80',
    route: '/app/predict',
  },
  {
    key: 'manage',
    label: '系统管理',
    brief: 'JWT 认证、数据 CRUD、多格式导出，保障全链路安全可控运维。',
    desc: '提供 JWT 登录认证、原始/清洗数据增删改查、分页筛选、Excel/JSON/TXT 导出及爬虫任务调度，保障数据全生命周期可控。',
    tags: ['JWT认证', '数据CRUD', '任务调度', '多格式导出'],
    image: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=480&h=640&fit=crop&q=80',
    route: '/app/raw-data',
  },
]
</script>

<style scoped lang="scss">
.unified-platform {
  background: transparent;
}

.section-header {
  text-align: center;
  margin-bottom: 48px;

  .section-eyebrow {
    display: inline-block;
    font-size: 13px;
    letter-spacing: 3px;
    color: var(--color-cyan);
    margin-bottom: 12px;
    text-transform: uppercase;
  }

  h2 {
    font-size: clamp(26px, 3.5vw, 38px);
    font-weight: 800;
    color: var(--text-primary);
    margin-bottom: 12px;
  }

  p {
    font-size: 16px;
    color: var(--text-secondary);
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.7;
  }
}

.solution-cards {
  display: flex;
  gap: 8px;
  align-items: stretch;
  height: 420px;

  @media (max-width: 960px) {
    flex-direction: column;
    height: auto;
    gap: 16px;
    overflow: visible;
    padding-bottom: 0;
  }
}

.solution-card {
  flex: 1 1 0;
  min-width: 0;
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: var(--shadow-card);
  cursor: default;
  transition: flex 0.35s ease, box-shadow 0.35s ease, border-color 0.35s ease;

  @media (max-width: 960px) {
    flex: none;
    width: 100%;
    min-height: 220px;
    height: auto;
    cursor: pointer;

    &.active {
      flex: none;
      width: 100%;
      min-height: 320px;
    }
  }

  &.active {
    flex: 4 1 0;
    z-index: 2;
    border-color: rgba(96, 165, 250, 0.35);
    box-shadow: var(--shadow-glow);

    .card-overlay {
      background: rgba(10, 14, 23, 0.92);
    }

    .card-bg img {
      opacity: 0.35;
      object-position: bottom right;
    }

    .card-brief {
      opacity: 0;
      max-height: 0;
      margin: 0;
      overflow: hidden;
    }

    .card-detail {
      opacity: 1;
      max-height: 320px;
      pointer-events: auto;
    }

    .card-title {
      color: #f1f5f9;
    }
  }
}

.card-bg {
  position: absolute;
  inset: 0;
  z-index: 0;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center center;
    transition: opacity 0.35s ease, transform 0.35s ease;
  }
}

.card-overlay {
  position: absolute;
  inset: 0;
  z-index: 1;
  background: linear-gradient(
    180deg,
    rgba(10, 14, 23, 0.92) 0%,
    rgba(10, 14, 23, 0.78) 28%,
    rgba(10, 14, 23, 0.45) 48%,
    rgba(10, 14, 23, 0.15) 72%,
    transparent 100%
  );
  transition: background 0.35s ease;
  pointer-events: none;
}

.card-body {
  position: relative;
  z-index: 2;
  height: 100%;
  padding: 24px 18px 20px;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 14px;
  line-height: 1.3;
  flex-shrink: 0;
  white-space: nowrap;

  @media (max-width: 960px) {
    white-space: normal;
  }
}

.card-brief {
  font-size: 13px;
  line-height: 1.75;
  color: #94a3b8;
  margin: 0;
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  transition: opacity 0.25s ease, max-height 0.35s ease, margin 0.35s ease;
}

.card-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  opacity: 0;
  max-height: 0;
  overflow: hidden;
  pointer-events: none;
  transition: opacity 0.3s ease 0.05s, max-height 0.35s ease;
}

.detail-desc {
  font-size: 13px;
  line-height: 1.85;
  color: var(--text-secondary);
  margin: 0 0 18px;
}

.detail-tags {
  margin-bottom: 20px;

  .tags-label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 10px;
  }

  .tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .tag-pill {
    padding: 4px 14px;
    border-radius: 4px;
    border: 1px solid rgba(96, 165, 250, 0.35);
    background: rgba(22, 119, 255, 0.12);
    color: #60a5fa;
    font-size: 12px;
    white-space: nowrap;
    transition: background 0.2s, border-color 0.2s;

    &:hover {
      background: rgba(22, 119, 255, 0.1);
      border-color: rgba(22, 119, 255, 0.5);
    }
  }
}

.detail-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: auto;
  padding: 0;
  background: none;
  border: none;
  color: var(--color-primary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s, gap 0.2s;

  .el-icon {
    font-size: 14px;
    transition: transform 0.2s;
  }

  &:hover {
    color: var(--color-primary-light);

    .el-icon {
      transform: translateX(3px);
    }
  }
}
</style>
