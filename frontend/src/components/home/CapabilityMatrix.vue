<template>
  <section id="capabilities" class="capability-matrix section">
    <div class="home-container">
      <div
        v-for="(block, bi) in blocks"
        :key="block.title"
        class="cap-block reveal"
        :class="{ reverse: bi % 2 === 1 }"
      >
        <div class="cap-content">
          <span class="cap-tag">{{ block.tag }}</span>
          <h3>{{ block.title }}</h3>
          <p>{{ block.desc }}</p>
          <div class="cap-chips">
            <span v-for="chip in block.chips" :key="chip">{{ chip }}</span>
          </div>
        </div>
        <div class="cap-visual">
          <div class="visual-inner" :style="{ '--accent': block.accent }">
            <div class="visual-title">{{ block.visualTitle }}</div>
            <div class="visual-items">
              <div v-for="item in block.items" :key="item.label" class="visual-item">
                <span class="vi-label">{{ item.label }}</span>
                <div class="vi-bar"><div :style="{ width: item.width }" /></div>
                <span class="vi-val">{{ item.value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const blocks = [
  {
    tag: '数据采集层',
    title: '四平台全覆盖 · 异步高效采集',
    desc: '基于 Scrapy 框架构建独立触发的异步采集模块，支持 BOSS直聘、智联招聘、拉勾网、猎聘网，任务调度与状态实时监控，数据自动持久化。',
    accent: '#1677ff',
    visualTitle: '平台采集分布',
    chips: ['Scrapy', '异步调度', 'MySQL Pipeline', '任务监控', '关键词筛选'],
    items: [
      { label: 'BOSS直聘', width: '85%', value: '156条' },
      { label: '智联招聘', width: '72%', value: '132条' },
      { label: '拉勾网', width: '68%', value: '124条' },
      { label: '猎聘网', width: '60%', value: '110条' },
    ],
  },
  {
    tag: '数据处理层',
    title: '智能清洗 · 结构化数据治理',
    desc: '自动解析薪资文本、提取技能标签、标准化学历与经验要求，支持批量清洗与 Excel/JSON/TXT 多格式导出，构建高质量分析数据集。',
    accent: '#13c2c2',
    visualTitle: '清洗完成率',
    chips: ['薪资解析', '技能 NLP', '学历映射', '批量 ETL', '数据导出'],
    items: [
      { label: '薪资解析', width: '98%', value: '98%' },
      { label: '技能提取', width: '95%', value: '95%' },
      { label: '学历标准化', width: '99%', value: '99%' },
      { label: '经验映射', width: '97%', value: '97%' },
    ],
  },
  {
    tag: '分析预测层',
    title: '可视化洞察 · AI 薪资推理',
    desc: 'ECharts 动态大屏展示平台分布、薪资区间、城市排名、技能热词等 8 类图表；ML 模型基于历史数据训练，上传简历即可推理预估薪资。',
    accent: '#722ed1',
    visualTitle: '分析维度',
    chips: ['ECharts', '中国地图', 'GradientBoosting', '简历解析', 'RESTful API'],
    items: [
      { label: '平台分布', width: '78%', value: '饼图' },
      { label: '薪资区间', width: '85%', value: '环形图' },
      { label: '城市 TOP10', width: '70%', value: '柱状图' },
      { label: '技能热词', width: '82%', value: '条形图' },
    ],
  },
]
</script>

<style scoped lang="scss">
.cap-block {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
  margin-bottom: 80px;

  &:last-child { margin-bottom: 0; }

  &.reverse {
    direction: rtl;
    .cap-content, .cap-visual { direction: ltr; }
  }

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
    gap: 32px;
    margin-bottom: 56px;
    &.reverse { direction: ltr; }
  }
}

.cap-tag {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 20px;
  background: rgba(22, 119, 255, 0.1);
  border: 1px solid rgba(22, 119, 255, 0.2);
  color: var(--color-primary-light);
  font-size: 12px;
  margin-bottom: 16px;
}

.cap-content h3 {
  font-size: clamp(22px, 3vw, 28px);
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 14px;
}

.cap-content p {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.cap-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  span {
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 12px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-subtle);
    color: var(--text-muted);
    transition: all 0.2s;

    &:hover {
      border-color: rgba(22, 119, 255, 0.3);
      color: var(--text-secondary);
    }
  }
}

.visual-inner {
  padding: 28px;
  border-radius: var(--radius-lg);
  background: var(--bg-glass);
  border: 1px solid rgba(22, 119, 255, 0.15);
  border-left: 3px solid var(--accent);
}

.visual-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.visual-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;

  .vi-label { width: 72px; font-size: 12px; color: var(--text-muted); flex-shrink: 0; }
  .vi-bar {
    flex: 1;
    height: 8px;
    background: rgba(255, 255, 255, 0.06);
    border-radius: 4px;
    overflow: hidden;

    div {
      height: 100%;
      border-radius: 4px;
      background: linear-gradient(90deg, var(--accent), transparent);
      transition: width 1s ease;
    }
  }
  .vi-val { width: 48px; text-align: right; font-size: 12px; color: var(--color-primary-light); }
}
</style>
