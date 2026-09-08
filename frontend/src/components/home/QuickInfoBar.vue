<template>
  <section class="quick-info section-sm">
    <div class="home-container">
      <div class="info-grid reveal">
        <div v-for="item in items" :key="item.title" class="info-card">
          <div class="info-icon" :style="{ background: item.gradient }">
            <el-icon :size="22"><component :is="item.icon" /></el-icon>
          </div>
          <div class="info-body">
            <h4>{{ item.title }}</h4>
            <p class="info-highlight">{{ item.highlight }}</p>
            <p class="info-desc">{{ item.desc }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const items = [
  {
    icon: 'Download',
    title: '数据采集',
    highlight: '四大平台 · 一键采集',
    desc: 'Scrapy 异步爬虫，支持 BOSS/智联/拉勾/猎聘',
    gradient: 'linear-gradient(135deg, #1677ff, #0958d9)',
  },
  {
    icon: 'Monitor',
    title: '可视化分析',
    highlight: '8+ 动态图表 · 实时洞察',
    desc: 'ECharts 大屏，多维度招聘市场分析',
    gradient: 'linear-gradient(135deg, #722ed1, #531dab)',
  },
  {
    icon: 'TrendCharts',
    title: 'AI 薪资预测',
    highlight: 'ML 模型 · 简历推理',
    desc: 'GradientBoosting 预估匹配岗位薪资',
    gradient: 'linear-gradient(135deg, #fa8c16, #d46b08)',
  },
  {
    icon: 'DataAnalysis',
    title: '全链路闭环',
    highlight: '采集 → 清洗 → 分析 → 预测',
    desc: 'Flask + Vue3 前后端完全解耦架构',
    gradient: 'linear-gradient(135deg, #13c2c2, #08979c)',
  },
]
</script>

<style scoped lang="scss">
.section-sm {
  padding: 0 0 40px;
  margin-top: -12px;
  position: relative;
  z-index: 2;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;

  @media (max-width: 960px) {
    grid-template-columns: repeat(2, 1fr);
  }
  @media (max-width: 520px) {
    grid-template-columns: 1fr;
  }
}

.info-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 22px 20px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(12px);
  transition: all 0.3s;

  &:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(96, 165, 250, 0.3);
    transform: translateY(-2px);
  }
}

.info-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.info-body {
  min-width: 0;

  h4 {
    font-size: 16px;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 6px;
  }

  .info-highlight {
    font-size: 13px;
    color: #4096ff;
    margin-bottom: 6px;
    font-weight: 500;
    line-height: 1.4;
  }

  .info-desc {
    font-size: 12px;
    color: #64748b;
    line-height: 1.55;
    margin: 0;
  }
}
</style>
