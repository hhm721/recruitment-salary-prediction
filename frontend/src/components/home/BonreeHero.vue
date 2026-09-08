<template>
  <section id="hero" class="bonree-hero">
    <div class="hero-bg">
      <div class="hero-grid" />
      <div class="hero-glow g1" />
      <div class="hero-glow g2" />
    </div>

    <div class="home-container hero-inner">
      <div class="hero-text reveal">
        <p class="hero-eyebrow">Recruitment Data Intelligence Platform</p>
        <h1>
          <span class="line1">招聘数据</span>
          <span class="line2">智能分析平台</span>
        </h1>
        <p class="hero-subtitle">
          从数据采集到清洗存储，从可视化洞察到 AI 薪资预测，全链路一体化解决方案
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" round class="btn-primary" @click="$emit('enter')">
            免费体验
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
          <el-button size="large" round class="btn-outline" @click="scrollTo('#platform')">
            了解平台能力
          </el-button>
        </div>
      </div>

      <div class="hero-visual reveal reveal-delay-2">
        <div class="visual-card">
          <div class="card-header">
            <span /><span /><span />
            <em>数据分析控制台</em>
          </div>
          <div class="card-body">
            <div class="metric-row" v-for="m in metrics" :key="m.label">
              <div class="metric-icon" :style="{ background: m.color }">
                <el-icon :size="18"><component :is="m.icon" /></el-icon>
              </div>
              <div class="metric-info">
                <span class="metric-label">{{ m.label }}</span>
                <strong>{{ m.value }}</strong>
              </div>
              <div class="metric-bar"><div :style="{ width: m.width, background: m.color }" /></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
defineEmits(['enter'])

const metrics = [
  { label: '原始岗位数据', value: '1,280+', width: '78%', color: 'linear-gradient(90deg,#1677ff,#4096ff)', icon: 'Document' },
  { label: '清洗结构化数据', value: '960+', width: '65%', color: 'linear-gradient(90deg,#13c2c2,#36cfc9)', icon: 'Filter' },
  { label: '平均薪资(K)', value: '22.5', width: '55%', color: 'linear-gradient(90deg,#faad14,#ffc53d)', icon: 'Money' },
  { label: '覆盖城市', value: '30+', width: '48%', color: 'linear-gradient(90deg,#722ed1,#9254de)', icon: 'Location' },
]

function scrollTo(sel) {
  document.querySelector(sel)?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped lang="scss">
.bonree-hero {
  position: relative;
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  padding: 100px 0 80px;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(22, 119, 255, 0.12), transparent 60%),
              linear-gradient(180deg, #0b1424 0%, #0d1a2e 100%);
}

.hero-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(22, 119, 255, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(22, 119, 255, 0.04) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse at 50% 40%, black 20%, transparent 70%);
}

.hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);

  &.g1 {
    width: 500px; height: 500px;
    top: -100px; right: 5%;
    background: rgba(22, 119, 255, 0.15);
  }
  &.g2 {
    width: 400px; height: 400px;
    bottom: 0; left: 10%;
    background: rgba(19, 194, 194, 0.1);
  }
}

.hero-inner {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;

  @media (max-width: 960px) {
    grid-template-columns: 1fr;
    gap: 40px;
  }
}

.hero-eyebrow {
  font-size: 13px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--color-cyan);
  margin-bottom: 16px;
}

.hero-text h1 {
  margin-bottom: 20px;

  .line1 {
    display: block;
    font-size: clamp(36px, 5vw, 52px);
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.15;
  }
  .line2 {
    display: block;
    font-size: clamp(36px, 5vw, 52px);
    font-weight: 800;
    background: var(--gradient-brand-soft);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.15;
  }
}

.hero-subtitle {
  font-size: 17px;
  line-height: 1.8;
  color: var(--text-secondary);
  max-width: 480px;
  margin-bottom: 32px;
}

.hero-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.btn-primary {
  padding: 12px 28px !important;
  background: var(--gradient-btn) !important;
  border: none !important;
  box-shadow: 0 8px 28px rgba(22, 119, 255, 0.35);
}

.btn-outline {
  padding: 12px 28px !important;
  background: transparent !important;
  border: 1px solid rgba(22, 119, 255, 0.4) !important;
  color: var(--text-secondary) !important;

  &:hover {
    border-color: var(--color-primary) !important;
    color: var(--color-primary-light) !important;
    background: rgba(22, 119, 255, 0.08) !important;
  }
}

.visual-card {
  background: rgba(12, 22, 40, 0.85);
  border: 1px solid rgba(22, 119, 255, 0.2);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 32px 80px rgba(0, 0, 0, 0.4);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  background: rgba(0, 0, 0, 0.25);
  border-bottom: 1px solid var(--border-subtle);

  span:nth-child(1) { width: 10px; height: 10px; border-radius: 50%; background: #ff4d4f; }
  span:nth-child(2) { width: 10px; height: 10px; border-radius: 50%; background: #faad14; }
  span:nth-child(3) { width: 10px; height: 10px; border-radius: 50%; background: #52c41a; }
  em { margin-left: auto; font-style: normal; font-size: 12px; color: var(--text-muted); }
}

.card-body { padding: 20px; }

.metric-row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 12px;
  align-items: center;
  margin-bottom: 18px;

  &:last-child { margin-bottom: 0; }
}

.metric-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.metric-info {
  .metric-label { display: block; font-size: 12px; color: var(--text-muted); }
  strong { font-size: 18px; color: var(--text-primary); }
}

.metric-bar {
  width: 80px;
  height: 6px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 3px;
  overflow: hidden;

  div { height: 100%; border-radius: 3px; transition: width 1s ease; }
}
</style>
