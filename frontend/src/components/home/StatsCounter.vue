<template>
  <section id="stats" class="stats-section section">
    <div class="home-container">
      <div class="stats-box reveal">
        <div class="stats-bg">
          <div class="stats-glow" />
        </div>
        <div class="stats-content">
          <div class="section-header">
            <span class="section-tag">数据概览</span>
            <h2>用数据说话<span class="accent">洞察招聘市场</span></h2>
          </div>

          <div class="stats-grid">
            <div v-for="(stat, i) in stats" :key="i" class="stat-card">
              <div class="stat-icon" :style="{ background: stat.gradient }">
                <el-icon :size="24"><component :is="stat.icon" /></el-icon>
              </div>
              <div class="stat-value">
                <span class="number">{{ stat.display }}</span>
                <span class="suffix">{{ stat.suffix }}</span>
              </div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getOverview } from '@/api'

const stats = ref([
  { icon: 'Document', label: '原始岗位数据', value: 0, display: '0', suffix: '条', gradient: 'linear-gradient(135deg, #9333ea, #6366f1)' },
  { icon: 'Filter', label: '清洗后数据', value: 0, display: '0', suffix: '条', gradient: 'linear-gradient(135deg, #22d3ee, #34d399)' },
  { icon: 'Money', label: '平均薪资', value: 0, display: '0', suffix: 'K', gradient: 'linear-gradient(135deg, #f472b6, #fb923c)' },
  { icon: 'Location', label: '覆盖城市', value: 0, display: '0', suffix: '个', gradient: 'linear-gradient(135deg, #c084fc, #818cf8)' },
])

let animated = false

function animateValue(index, target, decimals = 0) {
  const duration = 2000
  const start = performance.now()
  const startVal = 0

  function step(now) {
    const progress = Math.min((now - start) / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    const current = startVal + (target - startVal) * eased
    stats.value[index].display = decimals > 0 ? current.toFixed(decimals) : Math.round(current).toLocaleString()
    if (progress < 1) requestAnimationFrame(step)
  }

  requestAnimationFrame(step)
}

function startAnimation() {
  if (animated) return
  animated = true
  stats.value.forEach((s, i) => {
    animateValue(i, s.value, s.suffix === 'K' ? 1 : 0)
  })
}

onMounted(async () => {
  try {
    const res = await getOverview()
    const d = res.data
    stats.value[0].value = d.raw_total || 0
    stats.value[1].value = d.clean_total || 0
    stats.value[2].value = d.avg_salary || 0
    stats.value[3].value = d.city_count || 0
  } catch {
    stats.value[0].value = 180
    stats.value[1].value = 180
    stats.value[2].value = 22.5
    stats.value[3].value = 10
  }

  const observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        startAnimation()
        observer.disconnect()
      }
    },
    { threshold: 0.3 }
  )

  const el = document.querySelector('.stats-grid')
  if (el) observer.observe(el)
})
</script>

<style scoped lang="scss">
.stats-section {
  padding: 0;
}

.stats-box {
  position: relative;
  border-radius: var(--radius-xl);
  overflow: hidden;
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-card);
}

.stats-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(22, 119, 255, 0.08), rgba(10, 14, 23, 0.95));
  pointer-events: none;
}

.stats-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  height: 80%;
  background: radial-gradient(ellipse, rgba(22, 119, 255, 0.15), transparent 70%);
}

.stats-content {
  position: relative;
  z-index: 1;
  padding: 40px 32px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;

  @media (max-width: 900px) {
    grid-template-columns: repeat(2, 1fr);
  }
  @media (max-width: 500px) {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  text-align: center;
  padding: 28px 16px;
  border-radius: var(--radius-md);
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  transition: transform 0.4s, box-shadow 0.4s, border-color 0.4s;

  &:hover {
    transform: translateY(-6px);
    border-color: var(--border-accent);
    box-shadow: var(--shadow-glow);
  }

  .stat-icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    margin: 0 auto 16px;
  }

  .stat-value {
    margin-bottom: 8px;

    .number {
      font-size: 36px;
      font-weight: 800;
      background: var(--gradient-brand-soft);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .suffix {
      font-size: 16px;
      color: var(--text-muted);
      margin-left: 4px;
    }
  }

  .stat-label {
    font-size: 14px;
    color: var(--text-secondary);
  }
}
</style>
