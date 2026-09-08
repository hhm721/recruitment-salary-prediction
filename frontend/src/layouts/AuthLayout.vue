<template>
  <div class="auth-page">
    <Snowfall />
    <div class="ambient-bg" aria-hidden="true">
      <div class="orb orb-1" />
      <div class="orb orb-2" />
      <div class="grid-overlay" />
    </div>

    <div class="auth-shell">
      <aside class="auth-brand">
        <span class="brand-tag">全链路招聘数据分析系统</span>

        <div class="brand-head">
          <div class="brand-badge" @click="goHome">
            <el-icon :size="24"><DataAnalysis /></el-icon>
          </div>
          <div>
            <h1>招聘数据智能分析平台</h1>
            <p class="brand-slogan">让数据采集、清洗、分析与预测更高效</p>
          </div>
        </div>

        <p class="brand-desc">{{ subtitle }}</p>

        <div class="stat-grid">
          <div v-for="stat in stats" :key="stat.label" class="stat-item">
            <strong>{{ stat.value }}</strong>
            <span>{{ stat.label }}</span>
          </div>
        </div>

        <div class="highlight-list">
          <div v-for="item in highlights" :key="item.title" class="highlight-item">
            <div class="highlight-icon" :style="{ background: item.gradient }">
              <el-icon :size="20"><component :is="item.icon" /></el-icon>
            </div>
            <div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.desc }}</p>
            </div>
          </div>
        </div>

        <div class="flow-block">
          <div class="flow-title">系统流程</div>
          <div class="flow-steps">
            <span v-for="(step, i) in flowSteps" :key="step">
              <em>{{ i + 1 }}</em>{{ step }}
            </span>
          </div>
        </div>

        <div class="tech-tags">
          <span v-for="tag in techTags" :key="tag">{{ tag }}</span>
        </div>
      </aside>

      <main class="auth-panel">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import Snowfall from '@/components/auth/Snowfall.vue'

defineProps({
  subtitle: {
    type: String,
    default: '整合 BOSS直聘、智联招聘、拉勾网、猎聘网四大平台，构建从 Scrapy 异步采集到 ML 薪资预测的完整闭环。',
  },
})

const router = useRouter()

const stats = [
  { value: '4', label: '招聘平台' },
  { value: '7+', label: '可视化图表' },
  { value: 'ML', label: '薪资预测' },
  { value: 'REST', label: 'API 架构' },
]

const highlights = [
  {
    icon: 'Download',
    title: '四平台数据采集',
    desc: 'Scrapy 异步爬虫，支持关键词与城市筛选，任务状态实时追踪。',
    gradient: 'linear-gradient(135deg, #9333ea, #6366f1)',
  },
  {
    icon: 'Monitor',
    title: '可视化分析大屏',
    desc: 'ECharts 动态图表，地图分布、薪资趋势、技能热词一屏掌握。',
    gradient: 'linear-gradient(135deg, #22d3ee, #34d399)',
  },
  {
    icon: 'TrendCharts',
    title: 'AI 智能薪资预测',
    desc: '基于历史数据训练 ML 模型，上传简历即可推理预估薪资。',
    gradient: 'linear-gradient(135deg, #f472b6, #fb923c)',
  },
]

const flowSteps = ['数据采集', '数据清洗', '数据存储', '可视化分析', '智能预测']

const techTags = ['Scrapy', 'Flask', 'Vue3', 'MySQL', 'ECharts', 'scikit-learn']

function goHome() {
  router.push('/')
}
</script>

<style scoped lang="scss">
.auth-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 36px 24px;
  background: var(--dark-page-bg);
  overflow: hidden;
}

.ambient-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  animation: pulse 8s ease-in-out infinite alternate;
}

.orb-1 {
  width: 420px;
  height: 420px;
  top: -100px;
  left: 8%;
  background: rgba(22, 119, 255, 0.12);
}

.orb-2 {
  width: 360px;
  height: 360px;
  bottom: -60px;
  right: 10%;
  background: rgba(19, 194, 194, 0.08);
  animation-delay: -3s;
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(22, 119, 255, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(22, 119, 255, 0.04) 1px, transparent 1px);
  background-size: 64px 64px;
  mask-image: radial-gradient(ellipse at 50% 40%, black 15%, transparent 75%);
}

@keyframes pulse {
  from { transform: scale(1); opacity: 0.85; }
  to { transform: scale(1.08); opacity: 1; }
}

.auth-shell {
  position: relative;
  z-index: 2;
  width: min(1100px, 100%);
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 32px;
  align-items: stretch;

  @media (max-width: 960px) {
    grid-template-columns: 1fr;
    max-width: 480px;
  }
}

.auth-brand {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 36px 32px;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.35);

  @media (max-width: 960px) {
    display: none;
  }
}

.brand-tag {
  display: inline-block;
  width: fit-content;
  padding: 6px 14px;
  margin-bottom: 22px;
  border-radius: 999px;
  font-size: 12px;
  color: #60a5fa;
  background: rgba(22, 119, 255, 0.12);
  border: 1px solid rgba(96, 165, 250, 0.3);
}

.brand-head {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;

  .brand-badge {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    background: var(--gradient-brand);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    cursor: pointer;
    flex-shrink: 0;
    box-shadow: 0 8px 28px rgba(139, 92, 246, 0.4);
  }

  h1 {
    font-size: 26px;
    font-weight: 800;
    line-height: 1.3;
    background: linear-gradient(90deg, #60a5fa, #13c2c2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .brand-slogan {
    margin-top: 4px;
    font-size: 13px;
    color: #13c2c2;
  }
}

.brand-desc {
  color: #94a3b8;
  font-size: 14px;
  line-height: 1.8;
  margin-bottom: 24px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 24px;

  .stat-item {
    padding: 14px 10px;
    text-align: center;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);

    strong {
      display: block;
      font-size: 20px;
      font-weight: 800;
      background: linear-gradient(90deg, #60a5fa, #13c2c2);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 4px;
    }

    span {
      font-size: 11px;
      color: #64748b;
    }
  }
}

.highlight-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 22px;
}

.highlight-item {
  display: flex;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: border-color 0.25s, transform 0.25s;

  &:hover {
    border-color: rgba(96, 165, 250, 0.35);
    transform: translateX(4px);
  }

  .highlight-icon {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    flex-shrink: 0;
  }

  h3 {
    font-size: 14px;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 4px;
  }

  p {
    font-size: 12px;
    line-height: 1.6;
    color: #64748b;
  }
}

.flow-block {
  margin-bottom: 20px;

  .flow-title {
    font-size: 13px;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 10px;
  }

  .flow-steps {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    span {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 999px;
      font-size: 12px;
      color: #94a3b8;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.1);

      em {
        font-style: normal;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: rgba(22, 119, 255, 0.2);
        color: #60a5fa;
        font-size: 11px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        justify-content: center;
      }
    }
  }
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  span {
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 11px;
    color: #94a3b8;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
}

.auth-panel {
  padding: 40px 36px 36px;
  min-height: 520px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.35);

  :deep(.form-header) {
    h2 {
      color: #f1f5f9;
    }

    p {
      color: #94a3b8;

      a {
        color: #60a5fa;
      }
    }
  }

  :deep(.dark-input .el-input__wrapper) {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: none;

    &:hover,
    &.is-focus {
      border-color: rgba(96, 165, 250, 0.45);
      box-shadow: 0 0 0 1px rgba(96, 165, 250, 0.2);
    }
  }

  :deep(.dark-input .el-input__inner) {
    color: #e2e8f0;

    &::placeholder {
      color: #64748b;
    }
  }

  :deep(.dark-input .el-input__prefix .el-icon) {
    color: #64748b;
  }

  :deep(.demo-tip) {
    color: #64748b;
    background: rgba(22, 119, 255, 0.1);
    border-color: rgba(96, 165, 250, 0.25);
  }

  :deep(.form-footer .el-button.is-text) {
    color: #94a3b8 !important;

    &:hover,
    &:focus {
      color: #60a5fa !important;
      background-color: rgba(22, 119, 255, 0.12) !important;
    }
  }
}
</style>
