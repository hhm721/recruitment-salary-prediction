<template>
  <section id="scenarios" class="pioneer-section section">
    <div class="home-container">
      <div class="section-header reveal">
        <h2>行业应用场景</h2>
        <p>招聘数据分析在各行业的典型应用实践，助力企业数字化人才决策</p>
      </div>

      <div class="pioneer-grid reveal">
        <div
          v-for="item in pioneers"
          :key="item.title"
          class="pioneer-card"
          @mouseenter="hoverKey = item.key"
          @mouseleave="hoverKey = ''"
        >
          <div class="card-top" :style="{ background: item.gradient }">
            <div class="card-icon">
              <el-icon :size="28"><component :is="item.icon" /></el-icon>
            </div>
            <div class="card-stat">
              <strong>{{ item.stat }}</strong>
              <span>{{ item.statLabel }}</span>
            </div>
          </div>
          <div class="card-body">
            <span class="card-industry">{{ item.industry }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
            <div class="card-tags">
              <span v-for="t in item.tags" :key="t">{{ t }}</span>
            </div>
            <div class="card-footer">
              <span class="card-highlight">{{ item.highlight }}</span>
              <el-icon class="arrow" :class="{ show: hoverKey === item.key }"><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <div class="pioneer-banner reveal">
        <div class="banner-inner">
          <div class="banner-stat" v-for="s in bannerStats" :key="s.label">
            <strong>{{ s.value }}</strong>
            <span>{{ s.label }}</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

const hoverKey = ref('')

const pioneers = [
  {
    key: 'internet',
    industry: '互联网 / IT',
    icon: 'Monitor',
    title: '技术岗位薪资趋势分析',
    desc: '实时采集四大平台 IT 岗位，分析 Python、Java、前端等技能热词分布，辅助制定有竞争力薪酬策略。',
    stat: '200万+',
    statLabel: 'IT 岗位覆盖',
    highlight: '技能热词 · 薪资趋势 · 城市分布',
    tags: ['Python', 'Java', 'Vue3', '全栈'],
    gradient: 'linear-gradient(135deg, rgba(22,119,255,0.25), rgba(22,119,255,0.05))',
  },
  {
    key: 'finance',
    industry: '金融 / 证券',
    icon: 'Money',
    title: '中高端人才薪资洞察',
    desc: '按学历、经验维度交叉分析金融岗位，可视化展示不同职级薪资分布，为人才招聘提供数据支撑。',
    stat: '15-50K',
    statLabel: '主流薪资区间',
    highlight: '学历分析 · 经验映射 · 职级分布',
    tags: ['风控', '量化', '投研', '合规'],
    gradient: 'linear-gradient(135deg, rgba(19,194,194,0.25), rgba(19,194,194,0.05))',
  },
  {
    key: 'manufacturing',
    industry: '制造业 / 能源',
    icon: 'OfficeBuilding',
    title: '区域化招聘布局优化',
    desc: '中国城市地图可视化展示各城市岗位数量与平均薪资排名，支持区域化招聘策略制定。',
    stat: '30+',
    statLabel: '覆盖城市',
    highlight: '地图可视化 · TOP10 排名 · 区域对比',
    tags: ['智能制造', '新能源', '供应链'],
    gradient: 'linear-gradient(135deg, rgba(114,46,209,0.25), rgba(114,46,209,0.05))',
  },
  {
    key: 'education',
    industry: '教育 / 实训',
    icon: 'Reading',
    title: '全栈数据分析实训',
    desc: '涵盖 Scrapy 爬虫、Flask API、Vue3 前端、MySQL 存储与 scikit-learn 建模的完整教学实践链路。',
    stat: '5',
    statLabel: '核心实训模块',
    highlight: '教学实训 · 项目驱动 · 全栈实践',
    tags: ['Scrapy', 'Flask', 'ML', 'Vue3'],
    gradient: 'linear-gradient(135deg, rgba(250,140,22,0.25), rgba(250,140,22,0.05))',
  },
  {
    key: 'hr',
    industry: '人力资源',
    icon: 'User',
    title: '招聘效率提升方案',
    desc: '一键导出 Excel/JSON 报表，批量清洗原始数据，快速生成结构化招聘市场分析报告。',
    stat: '3',
    statLabel: '导出格式',
    highlight: '批量清洗 · 多格式导出 · 报表生成',
    tags: ['HR', '报表', 'ETL', '导出'],
    gradient: 'linear-gradient(135deg, rgba(82,196,26,0.25), rgba(82,196,26,0.05))',
  },
  {
    key: 'ai',
    industry: 'AI / 算法',
    icon: 'TrendCharts',
    title: 'ML 薪资预测引擎',
    desc: 'GradientBoosting 模型基于历史数据训练，上传简历自动推理匹配岗位预估薪资及置信度。',
    stat: '85%',
    statLabel: '预测置信度',
    highlight: '简历解析 · ML 推理 · 置信评估',
    tags: ['机器学习', 'NLP', '特征工程'],
    gradient: 'linear-gradient(135deg, rgba(255,77,79,0.2), rgba(255,77,79,0.05))',
  },
]

const bannerStats = [
  { value: '4+', label: '主流招聘平台' },
  { value: '8+', label: '可视化图表' },
  { value: '1000+', label: '可分析指标' },
  { value: '全链路', label: '数据闭环' },
]
</script>

<style scoped lang="scss">
.pioneer-section {
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
  p { font-size: 16px; color: var(--text-secondary); }
}

.pioneer-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;

  @media (max-width: 960px) {
    grid-template-columns: repeat(2, 1fr);
  }
  @media (max-width: 600px) {
    grid-template-columns: 1fr;
  }
}

.pioneer-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-card);
  backdrop-filter: blur(12px);
  transition: all 0.35s;
  cursor: default;

  &:hover {
    background: var(--bg-card-hover);
    transform: translateY(-6px);
    border-color: rgba(96, 165, 250, 0.35);
    box-shadow: var(--shadow-glow);
  }
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 22px;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary-light);
}

.card-stat {
  text-align: right;

  strong {
    display: block;
    font-size: 22px;
    font-weight: 800;
    color: var(--text-primary);
  }
  span { font-size: 11px; color: var(--text-muted); }
}

.card-body {
  padding: 0 22px 22px;

  .card-industry {
    font-size: 11px;
    color: var(--color-primary-light);
    letter-spacing: 0.5px;
  }

  h3 {
    font-size: 17px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 8px 0 10px;
  }

  p {
    font-size: 13px;
    line-height: 1.7;
    color: var(--text-muted);
    margin-bottom: 14px;
    min-height: 66px;
  }
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 14px;

  span {
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 11px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-subtle);
    color: var(--text-muted);
  }
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid var(--border-subtle);

  .card-highlight {
    font-size: 12px;
    color: var(--color-cyan);
  }

  .arrow {
    color: var(--text-muted);
    transition: transform 0.3s, color 0.3s;

    &.show {
      transform: translateX(4px);
      color: var(--color-primary-light);
    }
  }
}

.pioneer-banner {
  margin-top: 40px;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, rgba(22, 119, 255, 0.12), rgba(19, 194, 194, 0.06));
  border: 1px solid rgba(22, 119, 255, 0.2);
  overflow: hidden;
}

.banner-inner {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  text-align: center;

  @media (max-width: 700px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.banner-stat {
  padding: 28px 16px;
  border-right: 1px solid rgba(255, 255, 255, 0.06);

  &:last-child { border-right: none; }

  @media (max-width: 700px) {
    &:nth-child(2) { border-right: none; }
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  }

  strong {
    display: block;
    font-size: 28px;
    font-weight: 800;
    background: var(--gradient-brand-soft);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  span { font-size: 13px; color: var(--text-muted); margin-top: 4px; display: block; }
}
</style>
