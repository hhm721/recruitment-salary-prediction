<template>
  <section id="highlights" class="highlights section">
    <div class="home-container">
      <div class="section-header reveal">
        <span class="section-tag">核心优势</span>
        <h2>一站式招聘数据<span class="accent">智能分析</span>解决方案</h2>
        <p>打破单一数据源边界，深度融汇采集、清洗、可视化与 AI 预测之大成</p>
      </div>

      <div class="cards-grid">
        <div
          v-for="(card, i) in cards"
          :key="i"
          class="highlight-card reveal"
          :class="`reveal-delay-${i + 1}`"
          @mouseenter="activeCard = i"
          @mouseleave="activeCard = -1"
        >
          <div class="card-glow" :class="{ active: activeCard === i }" />
          <div class="card-icon" :style="{ background: card.gradient }">
            <el-icon :size="28"><component :is="card.icon" /></el-icon>
          </div>
          <h3>{{ card.title }}</h3>
          <p class="card-sub">{{ card.subtitle }}</p>
          <p class="card-desc">{{ card.desc }}</p>
          <div class="card-footer">
            <span v-for="tag in card.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

const activeCard = ref(-1)

const cards = [
  {
    icon: 'Download',
    title: '四平台数据采集',
    subtitle: 'Scrapy 异步爬虫 · 一键触发',
    desc: '整合 BOSS直聘、智联招聘、拉勾网、猎聘网四大主流渠道，支持独立或全量采集，数据实时持久化至 MySQL。',
    gradient: 'linear-gradient(135deg, #9333ea, #6366f1)',
    tags: ['Scrapy', '异步采集', 'MySQL'],
  },
  {
    icon: 'Filter',
    title: '智能数据清洗',
    subtitle: '薪资解析 · 技能提取 · 标准化',
    desc: '自动解析薪资区间、提取技能标签、标准化学历与经验要求，将原始数据转化为高质量结构化数据集。',
    gradient: 'linear-gradient(135deg, #22d3ee, #34d399)',
    tags: ['数据清洗', 'NLP', '标准化'],
  },
  {
    icon: 'Monitor',
    title: '可视化分析大屏',
    subtitle: 'ECharts 动态图表 · 交互展示',
    desc: '岗位数量、薪资分布、城市排名、技能热词等 8 类动态图表，支持交互筛选与实时数据刷新。',
    gradient: 'linear-gradient(135deg, #c084fc, #818cf8)',
    tags: ['ECharts', '大屏', '实时分析'],
  },
  {
    icon: 'TrendCharts',
    title: 'AI 薪资预测',
    subtitle: 'ML 模型 · 简历智能推理',
    desc: '基于历史招聘数据训练 GradientBoosting 模型，上传简历即可推理输出匹配岗位的预估薪资水平。',
    gradient: 'linear-gradient(135deg, #f472b6, #fb923c)',
    tags: ['机器学习', '简历解析', '薪资预测'],
  },
]
</script>

<style scoped lang="scss">
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
}

.highlight-card {
  position: relative;
  padding: 28px 24px;
  border-radius: var(--radius-lg);
  background: var(--bg-glass);
  border: 1px solid var(--border-subtle);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1),
              border-color 0.4s,
              box-shadow 0.4s;
  overflow: hidden;
  cursor: default;
  backdrop-filter: blur(16px);

  &:hover {
    transform: translateY(-8px);
    border-color: var(--border-accent);
    box-shadow: var(--shadow-glow);
  }

  .card-glow {
    position: absolute;
    inset: 0;
    opacity: 0;
    background: radial-gradient(circle at 50% 0%, rgba(167, 139, 250, 0.18), transparent 70%);
    transition: opacity 0.4s;

    &.active { opacity: 1; }
  }

  .card-icon {
    width: 56px;
    height: 56px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    margin-bottom: 20px;
    transition: transform 0.4s;
  }

  &:hover .card-icon { transform: scale(1.1) rotate(-5deg); }

  h3 {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
  }

  .card-sub {
    font-size: 13px;
    color: var(--color-cyan);
    margin-bottom: 12px;
  }

  .card-desc {
    font-size: 14px;
    line-height: 1.7;
    color: var(--text-secondary);
    margin-bottom: 20px;
  }

  .card-footer {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .tag {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    background: rgba(167, 139, 250, 0.1);
    border: 1px solid rgba(167, 139, 250, 0.2);
    color: var(--text-secondary);
  }
}
</style>
