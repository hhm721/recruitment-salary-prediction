<template>
  <section id="flow" class="flow section">
    <div class="home-container">
      <div class="section-header reveal">
      <span class="section-tag">系统流程</span>
      <h2>从采集到预测<span class="accent">全链路闭环</span></h2>
      <p>五大核心环节无缝衔接，数据驱动决策</p>
    </div>

    <div class="timeline reveal">
      <div class="timeline-line">
        <div class="timeline-progress" :style="{ width: progressWidth }" />
      </div>

      <div
        v-for="(step, i) in steps"
        :key="i"
        class="timeline-step"
        :class="{ active: activeStep >= i, current: activeStep === i }"
        @mouseenter="activeStep = i"
      >
        <div class="step-node">
          <el-icon :size="22"><component :is="step.icon" /></el-icon>
          <span class="step-num">{{ i + 1 }}</span>
        </div>
        <div class="step-content">
          <h4>{{ step.title }}</h4>
          <p>{{ step.desc }}</p>
          <div class="step-tech">
            <span v-for="t in step.tech" :key="t">{{ t }}</span>
          </div>
        </div>
      </div>
    </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const activeStep = ref(0)
let autoTimer

const steps = [
  {
    icon: 'Download',
    title: '数据采集',
    desc: 'Scrapy 异步爬虫从四大平台抓取岗位数据，支持关键词与城市筛选，任务状态实时追踪。',
    tech: ['Scrapy', '异步调度', 'MySQL Pipeline'],
  },
  {
    icon: 'Filter',
    title: '数据清洗',
    desc: '解析薪资文本、提取技能标签、标准化学历经验，原始数据转化为结构化高质量数据集。',
    tech: ['ETL', '正则解析', 'NLP'],
  },
  {
    icon: 'Money',
    title: '数据存储',
    desc: '清洗后数据持久化至 MySQL，建立原始表与清洗表双层存储，支持分页查询与多维筛选。',
    tech: ['MySQL', 'SQLAlchemy', 'Flask ORM'],
  },
  {
    icon: 'DataAnalysis',
    title: '可视化分析',
    desc: 'ECharts 动态图表展示平台分布、薪资区间、城市排名、技能热词等多维度分析结果。',
    tech: ['Vue3', 'ECharts', 'RESTful API'],
  },
  {
    icon: 'TrendCharts',
    title: '智能预测',
    desc: 'ML 模型基于历史数据训练，用户上传简历后自动推理输出匹配岗位的预估薪资水平。',
    tech: ['scikit-learn', 'GradientBoosting', '简历解析'],
  },
]

const progressWidth = computed(() => `${(activeStep.value / (steps.length - 1)) * 100}%`)

onMounted(() => {
  autoTimer = setInterval(() => {
    activeStep.value = (activeStep.value + 1) % steps.length
  }, 3000)
})
onUnmounted(() => clearInterval(autoTimer))
</script>

<style scoped lang="scss">
.timeline {
  position: relative;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 0;
}

.timeline-line {
  position: absolute;
  top: 68px;
  left: 10%;
  right: 10%;
  height: 3px;
  background: rgba(167, 139, 250, 0.08);
  border-radius: 2px;

  .timeline-progress {
    height: 100%;
    background: var(--gradient-brand-soft);
    border-radius: 2px;
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  }
}

.timeline-step {
  flex: 1;
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s;

  &:hover { transform: translateY(-4px); }

  .step-node {
    position: relative;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: var(--bg-glass);
    border: 2px solid var(--border-subtle);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 20px;
    color: #6b8299;
    transition: all 0.4s;
    z-index: 2;

    .step-num {
      position: absolute;
      top: -8px;
      right: -8px;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: rgba(64, 158, 255, 0.2);
      font-size: 11px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #8ba4c7;
    }
  }

  &.active .step-node {
    border-color: var(--color-violet);
    color: var(--color-violet);
    box-shadow: 0 0 24px rgba(139, 92, 246, 0.35);

    .step-num {
      background: var(--color-violet);
      color: #fff;
    }
  }

  &.current .step-node {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(34, 211, 238, 0.1));
    transform: scale(1.15);
  }

  h4 {
    font-size: 16px;
    color: var(--text-secondary);
    margin-bottom: 8px;
    transition: color 0.3s;
  }

  &.active h4 { color: var(--text-primary); }

  p {
    font-size: 13px;
    color: #6b8299;
    line-height: 1.6;
    margin-bottom: 12px;
    padding: 0 8px;
  }

  .step-tech {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: center;

    span {
      padding: 2px 10px;
      border-radius: 12px;
      font-size: 11px;
      background: rgba(64, 158, 255, 0.06);
      color: #6b8299;
      transition: all 0.3s;
    }
  }

  &.active .step-tech span {
    background: rgba(64, 158, 255, 0.12);
    color: #8ba4c7;
  }
}

@media (max-width: 900px) {
  .timeline {
    flex-direction: column;
    align-items: center;
  }
  .timeline-line { display: none; }
  .timeline-step {
    max-width: 400px;
    width: 100%;
  }
}
</style>
