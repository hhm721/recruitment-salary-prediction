<template>
  <section id="tech" class="resource-section section reveal">
    <div class="home-container">
      <div class="section-header">
        <h2>主流技术栈<span class="accent">全栈赋能</span></h2>
        <p>覆盖采集、后端、前端、存储、可视化与机器学习全链路技术体系</p>
      </div>

      <div class="resource-primary">
        <div
          v-for="res in primaryResources"
          :key="res.title"
          class="resource-card"
          @click="scrollTo(res.link)"
        >
          <div class="res-icon" :style="{ background: res.gradient }">
            <el-icon :size="32"><component :is="res.icon" /></el-icon>
          </div>
          <h3>{{ res.title }}</h3>
          <p>{{ res.desc }}</p>
          <span class="res-link">
            了解更多 <el-icon><ArrowRight /></el-icon>
          </span>
        </div>
      </div>

      <div class="resource-secondary">
        <div v-for="tech in techs" :key="tech.name" class="tech-chip">
          <span class="chip-icon">{{ tech.icon }}</span>
          <div>
            <strong>{{ tech.name }}</strong>
            <span>{{ tech.role }}</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="cta-section section reveal">
    <div class="home-container">
      <div class="cta-box">
        <div class="cta-bg"><div class="cta-orb" /></div>
        <div class="cta-content">
          <h2>立即体验招聘数据智能分析平台</h2>
          <p>一键采集 · 智能清洗 · 可视化洞察 · AI 薪资预测</p>
          <div class="cta-buttons">
            <el-button type="primary" size="large" round class="cta-btn" @click="$emit('enter')">
              <el-icon><Monitor /></el-icon>
              进入管理系统
            </el-button>
            <el-button size="large" round class="cta-btn-secondary" @click="scrollTo('#platform')">
              了解更多功能
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
defineEmits(['enter'])

const primaryResources = [
  {
    icon: 'Document',
    title: '技术文档',
    desc: 'Flask RESTful API 接口说明、数据库表结构设计、爬虫配置与部署指南，助力快速上手开发。',
    gradient: 'linear-gradient(135deg, #1677ff, #0958d9)',
    link: '#platform',
  },
  {
    icon: 'VideoCamera',
    title: '实训教程',
    desc: '涵盖 Scrapy 爬虫开发、数据清洗 ETL、ECharts 可视化大屏与 ML 薪资预测的全流程实训教程。',
    gradient: 'linear-gradient(135deg, #722ed1, #531dab)',
    link: '#scenarios',
  },
  {
    icon: 'Bell',
    title: '更新动态',
    desc: '系统功能迭代记录：数据增删改查、多格式导出、智能聊天助手、Bonree 风格首页等最新特性。',
    gradient: 'linear-gradient(135deg, #13c2c2, #08979c)',
    link: '#stats',
  },
]

const techs = [
  { icon: '🕷️', name: 'Scrapy', role: '异步爬虫' },
  { icon: '⚡', name: 'Flask', role: 'RESTful API' },
  { icon: '💚', name: 'Vue 3', role: '响应式前端' },
  { icon: '🗄️', name: 'MySQL', role: '数据持久化' },
  { icon: '📊', name: 'ECharts', role: '可视化' },
  { icon: '🤖', name: 'scikit-learn', role: 'ML 预测' },
  { icon: '🎨', name: 'Element Plus', role: 'UI 组件' },
  { icon: '🔧', name: 'SQLAlchemy', role: 'ORM 层' },
]

function scrollTo(selector) {
  document.querySelector(selector)?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped lang="scss">
.resource-section {
  padding-bottom: 0;
}

.section-header {
  text-align: center;
  margin-bottom: 40px;

  .section-eyebrow {
    display: inline-block;
    font-size: 13px;
    letter-spacing: 3px;
    color: var(--color-cyan);
    margin-bottom: 12px;
  }

  h2 {
    font-size: clamp(26px, 3.5vw, 36px);
    font-weight: 800;
    color: var(--text-primary);
    margin-bottom: 12px;

    .accent {
      background: var(--gradient-brand-soft);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
  }
  p { font-size: 16px; color: var(--text-secondary); }
}

.resource-primary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 32px;

  @media (max-width: 800px) {
    grid-template-columns: 1fr;
  }
}

.resource-card {
  padding: 32px 28px;
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-card);
  backdrop-filter: blur(12px);
  cursor: pointer;
  transition: all 0.35s;

  &:hover {
    background: var(--bg-card-hover);
    transform: translateY(-6px);
    border-color: rgba(96, 165, 250, 0.35);
    box-shadow: var(--shadow-glow);

    .res-link { gap: 8px; color: var(--color-primary-light); }
  }

  .res-icon {
    width: 64px;
    height: 64px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    margin-bottom: 20px;
  }

  h3 {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 12px;
  }

  p {
    font-size: 14px;
    line-height: 1.75;
    color: var(--text-muted);
    margin-bottom: 20px;
    min-height: 72px;
  }

  .res-link {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
    color: var(--text-secondary);
    transition: gap 0.2s, color 0.2s;
  }
}

.resource-secondary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;

  @media (max-width: 800px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.tech-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  transition: border-color 0.2s;

  &:hover { border-color: rgba(22, 119, 255, 0.25); }

  .chip-icon { font-size: 24px; }

  strong {
    display: block;
    font-size: 14px;
    color: var(--text-primary);
  }
  span { font-size: 11px; color: var(--text-muted); }
}

.cta-section { padding-top: 48px; overflow: visible; }

.cta-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-box {
  position: relative;
  border-radius: var(--radius-xl);
  overflow: hidden;
  border: 1px solid var(--border-subtle);
  text-align: center;
  backdrop-filter: blur(20px);
}

.cta-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(22, 119, 255, 0.1), rgba(19, 194, 194, 0.05));
  pointer-events: none;
}

.cta-orb {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60%;
  height: 120%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(22, 119, 255, 0.12), transparent 70%);
  animation: pulse-orb 4s ease-in-out infinite;
}

.cta-content {
  position: relative;
  z-index: 1;
  padding: 48px 32px;

  h2 {
    font-size: clamp(24px, 4vw, 36px);
    font-weight: 800;
    color: var(--text-primary);
    margin-bottom: 16px;
  }
  p {
    color: var(--text-secondary);
    font-size: 16px;
    margin-bottom: 28px;
  }
}

.cta-btn {
  padding: 14px 36px !important;
  background: var(--gradient-btn) !important;
  border: none !important;
  box-shadow: 0 8px 32px rgba(22, 119, 255, 0.35);
}

.cta-btn-secondary {
  padding: 14px 36px !important;
  background: rgba(255, 255, 255, 0.05) !important;
  border-color: var(--border-subtle) !important;
  color: var(--text-secondary) !important;
}

@keyframes pulse-orb {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
  50% { transform: translate(-50%, -50%) scale(1.2); opacity: 1; }
}
</style>
