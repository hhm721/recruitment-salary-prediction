<template>
  <section id="modules" class="modules section">
    <div class="home-container">
      <div class="section-header reveal">
      <span class="section-tag">功能模块</span>
      <h2>覆盖招聘数据分析<span class="accent">全链路场景</span></h2>
      <p>从数据采集到智能预测，每个环节都经过精心设计</p>
    </div>

    <div class="module-tabs reveal">
      <button
        v-for="(tab, i) in tabs"
        :key="tab.key"
        class="tab-btn"
        :class="{ active: activeTab === i }"
        @click="switchTab(i)"
      >
        <el-icon :size="18"><component :is="tab.icon" /></el-icon>
        {{ tab.label }}
      </button>
    </div>

    <div class="module-panel reveal">
      <Transition name="slide-fade" mode="out-in">
        <div :key="activeTab" class="panel-content">
          <div class="panel-left">
            <span class="panel-tag">{{ currentTab.tag }}</span>
            <h3>{{ currentTab.title }}</h3>
            <p class="panel-desc">{{ currentTab.desc }}</p>

            <div class="feature-list">
              <div v-for="(feat, i) in currentTab.features" :key="i" class="feature-item">
                <div class="feature-icon">
                  <el-icon><Check /></el-icon>
                </div>
                <div>
                  <strong>{{ feat.title }}</strong>
                  <p>{{ feat.desc }}</p>
                </div>
              </div>
            </div>

            <el-button type="primary" round class="panel-cta" @click="$emit('enter', currentTab.route)">
              立即体验 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>

          <div class="panel-right">
            <div class="mock-screen">
              <div class="screen-header">
                <span /><span /><span />
                <span class="screen-title">{{ currentTab.screenTitle }}</span>
              </div>
              <div class="screen-body">
                <div v-for="(row, i) in currentTab.preview" :key="i" class="preview-row" :style="{ animationDelay: `${i * 0.1}s` }">
                  <span class="preview-label">{{ row.label }}</span>
                  <div class="preview-bar" :style="{ width: row.width, background: row.color }" />
                  <span class="preview-value">{{ row.value }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'

defineEmits(['enter'])

const activeTab = ref(0)

const tabs = [
  {
    key: 'crawl',
    label: '数据采集',
    icon: 'Download',
    tag: 'Scrapy 爬虫引擎',
    title: '四平台一键式异步采集',
    desc: '基于 Scrapy 框架构建独立触发的异步采集模块，支持 BOSS直聘、智联招聘、拉勾网、猎聘网四大平台，任务调度与状态实时监控。',
    route: '/app/crawl',
    screenTitle: '爬虫任务管理',
    features: [
      { title: '独立/全量采集', desc: '支持单平台独立触发或四平台一键全量采集' },
      { title: '任务状态监控', desc: '实时追踪 pending/running/completed/failed 状态' },
      { title: 'MySQL 持久化', desc: '采集数据自动写入 job_raw 原始数据表' },
    ],
    preview: [
      { label: 'BOSS直聘', width: '85%', value: '156条', color: 'linear-gradient(90deg, #409eff, #67c8ff)' },
      { label: '智联招聘', width: '72%', value: '132条', color: 'linear-gradient(90deg, #36d7b7, #5eead4)' },
      { label: '拉勾网', width: '68%', value: '124条', color: 'linear-gradient(90deg, #f5a623, #fbbf24)' },
      { label: '猎聘网', width: '60%', value: '110条', color: 'linear-gradient(90deg, #e74c6f, #f87171)' },
    ],
  },
  {
    key: 'clean',
    label: '数据清洗',
    icon: 'Filter',
    tag: 'ETL 数据处理',
    title: '智能清洗与结构化转换',
    desc: '对原始招聘数据进行薪资解析、技能标签提取、学历经验标准化，生成高质量结构化数据集供分析与建模使用。',
    route: '/app/clean-data',
    screenTitle: '数据清洗面板',
    features: [
      { title: '薪资智能解析', desc: '支持 15-25K、面议等多种薪资格式自动解析' },
      { title: '技能标签提取', desc: '从岗位描述中自动识别 Python、Java 等 40+ 技能' },
      { title: '批量清洗处理', desc: '一键清洗未处理数据，支持按平台筛选' },
    ],
    preview: [
      { label: '薪资解析', width: '92%', value: '98%', color: 'linear-gradient(90deg, #409eff, #67c8ff)' },
      { label: '技能提取', width: '88%', value: '95%', color: 'linear-gradient(90deg, #36d7b7, #5eead4)' },
      { label: '学历标准化', width: '95%', value: '99%', color: 'linear-gradient(90deg, #9b59b6, #a78bfa)' },
      { label: '经验映射', width: '90%', value: '97%', color: 'linear-gradient(90deg, #f5a623, #fbbf24)' },
    ],
  },
  {
    key: 'dashboard',
    label: '可视化大屏',
    icon: 'Monitor',
    tag: 'ECharts 数据可视化',
    title: '多维度动态图表分析',
    desc: '集成 ECharts 可视化引擎，展示平台分布、薪资区间、城市 TOP10、技能热词、经验-薪资关系等 8 类交互图表。',
    route: '/app/dashboard',
    screenTitle: '数据分析大屏',
    features: [
      { title: '实时数据刷新', desc: '对接 Flask RESTful API，图表数据动态更新' },
      { title: '多维度分析', desc: '平台、城市、技能、学历、经验等多角度洞察' },
      { title: '响应式布局', desc: '适配 PC、平板、手机等多端设备展示' },
    ],
    preview: [
      { label: '平台分布', width: '78%', value: '饼图', color: 'linear-gradient(90deg, #409eff, #67c8ff)' },
      { label: '薪资区间', width: '85%', value: '环形图', color: 'linear-gradient(90deg, #36d7b7, #5eead4)' },
      { label: '城市排名', width: '70%', value: '柱状图', color: 'linear-gradient(90deg, #f5a623, #fbbf24)' },
      { label: '技能热词', width: '82%', value: '条形图', color: 'linear-gradient(90deg, #e74c6f, #f87171)' },
    ],
  },
  {
    key: 'predict',
    label: '薪资预测',
    icon: 'TrendCharts',
    tag: 'ML 机器学习',
    title: '简历上传 · 智能薪资推理',
    desc: '利用历史招聘数据训练 GradientBoosting 回归模型，用户上传简历后自动提取技能与经验，推理输出匹配岗位的预估薪资。',
    route: '/app/predict',
    screenTitle: '薪资预测引擎',
    features: [
      { title: '多格式简历解析', desc: '支持 txt、pdf、doc、docx 格式简历上传' },
      { title: 'ML 模型推理', desc: 'GradientBoosting + 特征工程，置信度评估' },
      { title: '匹配岗位统计', desc: '基于技能重叠度统计历史匹配岗位数量' },
    ],
    preview: [
      { label: 'Python', width: '90%', value: '匹配', color: 'linear-gradient(90deg, #409eff, #67c8ff)' },
      { label: '5年经验', width: '75%', value: '+15K', color: 'linear-gradient(90deg, #36d7b7, #5eead4)' },
      { label: '本科学历', width: '65%', value: '+8K', color: 'linear-gradient(90deg, #9b59b6, #a78bfa)' },
      { label: '预测薪资', width: '95%', value: '22-28K', color: 'linear-gradient(90deg, #f5a623, #fbbf24)' },
    ],
  },
]

const currentTab = computed(() => tabs[activeTab.value])

function switchTab(i) {
  activeTab.value = i
}
</script>

<style scoped lang="scss">
.modules {
  background: linear-gradient(180deg, transparent, rgba(139, 92, 246, 0.04), transparent);
}

.module-tabs {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 28px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 50px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    border-color: var(--border-accent);
    color: var(--text-primary);
  }

  &.active {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.22), rgba(99, 102, 241, 0.12));
    border-color: rgba(167, 139, 250, 0.45);
    color: #fff;
    box-shadow: var(--shadow-glow);
  }
}

.module-panel {
  background: var(--bg-glass);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 40px;
  min-height: 400px;
  backdrop-filter: blur(20px);
}

.panel-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: center;
}

.panel-tag {
  display: inline-block;
  padding: 4px 14px;
  border-radius: var(--radius-xl);
  background: rgba(167, 139, 250, 0.12);
  color: var(--color-violet);
  font-size: 12px;
  margin-bottom: 16px;
}

.panel-left h3 {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.panel-desc {
  color: var(--text-secondary);
  line-height: 1.8;
  margin-bottom: 28px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 32px;
}

.feature-item {
  display: flex;
  gap: 14px;
  align-items: flex-start;

  .feature-icon {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: rgba(54, 215, 183, 0.15);
    color: #36d7b7;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  strong {
    color: #c0d8f0;
    font-size: 14px;
  }

  p {
    color: #6b8299;
    font-size: 13px;
    margin-top: 2px;
  }
}

.panel-cta {
  background: linear-gradient(135deg, #409eff, #2b7de9) !important;
  border: none !important;
}

.mock-screen {
  background: rgba(8, 14, 35, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(64, 158, 255, 0.15);
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.screen-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  background: rgba(16, 32, 64, 0.6);
  border-bottom: 1px solid rgba(64, 158, 255, 0.1);

  span:nth-child(1) { width: 10px; height: 10px; border-radius: 50%; background: #e74c6f; }
  span:nth-child(2) { width: 10px; height: 10px; border-radius: 50%; background: #f5a623; }
  span:nth-child(3) { width: 10px; height: 10px; border-radius: 50%; background: #36d7b7; }

  .screen-title {
    margin-left: auto;
    font-size: 12px;
    color: #6b8299;
  }
}

.screen-body {
  padding: 24px;
}

.preview-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
  animation: slideIn 0.5s ease both;

  .preview-label {
    width: 80px;
    font-size: 13px;
    color: #8ba4c7;
    flex-shrink: 0;
  }

  .preview-bar {
    flex: 1;
    height: 8px;
    border-radius: 4px;
    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .preview-value {
    width: 60px;
    text-align: right;
    font-size: 13px;
    color: #67c8ff;
    font-weight: 600;
  }
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

@media (max-width: 900px) {
  .panel-content { grid-template-columns: 1fr; }
  .module-panel { padding: 28px; }
}
</style>
