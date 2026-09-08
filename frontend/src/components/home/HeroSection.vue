<template>
  <section id="hero" class="hero">
    <div class="hero-bg">
      <div class="gradient-orb orb-1" />
      <div class="gradient-orb orb-2" />
      <div class="gradient-orb orb-3" />
      <canvas ref="canvasRef" class="particle-canvas" />
      <div class="grid-overlay" />
    </div>

    <div class="hero-content">
      <div class="hero-badge reveal">
        <span class="pulse-dot" />
        全链路招聘数据智能分析系统
      </div>

      <h1 class="hero-title reveal reveal-delay-1">
        <span class="line">整合四大招聘平台</span>
        <span class="line gradient-text">数据驱动 · 智能预测</span>
      </h1>

      <p class="hero-desc reveal reveal-delay-2">
        基于 Scrapy 异步采集、Flask RESTful API、Vue3 可视化大屏与 ML 薪资预测模型，
        实现从数据采集、清洗、存储到分析与智能推理的全链路闭环。
      </p>

      <div class="hero-actions reveal reveal-delay-3">
        <el-button type="primary" size="large" round class="cta-primary" @click="$emit('enter')">
          <el-icon><Monitor /></el-icon>
          立即体验系统
        </el-button>
        <el-button size="large" round class="cta-secondary" @click="scrollTo('#modules')">
          <el-icon><VideoPlay /></el-icon>
          了解核心功能
        </el-button>
      </div>

      <div class="hero-stats reveal reveal-delay-4">
        <div v-for="(item, i) in quickStats" :key="i" class="quick-stat">
          <span class="stat-num">{{ item.value }}</span>
          <span class="stat-label">{{ item.label }}</span>
        </div>
      </div>
    </div>

    <div class="scroll-hint">
      <div class="mouse">
        <div class="wheel" />
      </div>
      <span>向下滚动探索更多</span>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

defineEmits(['enter'])

const canvasRef = ref(null)
let animationId

const quickStats = [
  { value: '4+', label: '主流招聘平台' },
  { value: '8+', label: '可视化图表' },
  { value: 'ML', label: '薪资预测模型' },
  { value: '100%', label: '前后端解耦' },
]

function scrollTo(selector) {
  document.querySelector(selector)?.scrollIntoView({ behavior: 'smooth' })
}

function initParticles() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const particles = []
  const count = 60

  function resize() {
    canvas.width = canvas.offsetWidth * devicePixelRatio
    canvas.height = canvas.offsetHeight * devicePixelRatio
    ctx.scale(devicePixelRatio, devicePixelRatio)
  }

  resize()
  window.addEventListener('resize', resize)

  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * canvas.offsetWidth,
      y: Math.random() * canvas.offsetHeight,
      r: Math.random() * 2 + 0.5,
      dx: (Math.random() - 0.5) * 0.4,
      dy: (Math.random() - 0.5) * 0.4,
      opacity: Math.random() * 0.5 + 0.2,
    })
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight)
    particles.forEach((p, i) => {
      p.x += p.dx
      p.y += p.dy
      if (p.x < 0 || p.x > canvas.offsetWidth) p.dx *= -1
      if (p.y < 0 || p.y > canvas.offsetHeight) p.dy *= -1

      ctx.beginPath()
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(64, 158, 255, ${p.opacity})`
      ctx.fill()

      particles.slice(i + 1).forEach((p2) => {
        const dist = Math.hypot(p.x - p2.x, p.y - p2.y)
        if (dist < 120) {
          ctx.beginPath()
          ctx.moveTo(p.x, p.y)
          ctx.lineTo(p2.x, p2.y)
          ctx.strokeStyle = `rgba(64, 158, 255, ${0.08 * (1 - dist / 120)})`
          ctx.stroke()
        }
      })
    })
    animationId = requestAnimationFrame(draw)
  }

  draw()

  return () => {
    window.removeEventListener('resize', resize)
    cancelAnimationFrame(animationId)
  }
}

let cleanup
onMounted(() => { cleanup = initParticles() })
onUnmounted(() => cleanup?.())
</script>

<style scoped lang="scss">
.hero {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 120px 24px 80px;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 50% 0%, #0f1f4a 0%, #080e1f 50%, #050810 100%);
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  animation: float 8s ease-in-out infinite;

  &.orb-1 {
    width: 500px; height: 500px;
    background: rgba(64, 158, 255, 0.15);
    top: -10%; left: -5%;
  }
  &.orb-2 {
    width: 400px; height: 400px;
    background: rgba(54, 215, 183, 0.1);
    bottom: 10%; right: -5%;
    animation-delay: -3s;
  }
  &.orb-3 {
    width: 300px; height: 300px;
    background: rgba(155, 89, 182, 0.08);
    top: 40%; left: 50%;
    animation-delay: -5s;
  }
}

.particle-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(64, 158, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(64, 158, 255, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse at center, black 20%, transparent 70%);
}

.hero-content {
  position: relative;
  z-index: 2;
  max-width: 900px;
  text-align: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  border-radius: 50px;
  background: rgba(64, 158, 255, 0.1);
  border: 1px solid rgba(64, 158, 255, 0.25);
  color: #67c8ff;
  font-size: 13px;
  margin-bottom: 28px;

  .pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #36d7b7;
    animation: pulse 2s infinite;
  }
}

.hero-title {
  font-size: clamp(36px, 6vw, 58px);
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 24px;

  .line { display: block; color: #e8f0ff; }
  .gradient-text {
    background: linear-gradient(135deg, #409eff 0%, #36d7b7 50%, #67c8ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-size: 200% auto;
    animation: shimmer 4s linear infinite;
  }
}

.hero-desc {
  font-size: 17px;
  line-height: 1.8;
  color: #8ba4c7;
  max-width: 680px;
  margin: 0 auto 36px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 48px;
}

.cta-primary {
  padding: 12px 32px !important;
  font-size: 16px !important;
  background: linear-gradient(135deg, #409eff, #2b7de9) !important;
  border: none !important;
  box-shadow: 0 8px 30px rgba(64, 158, 255, 0.4);
  transition: transform 0.3s, box-shadow 0.3s;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(64, 158, 255, 0.5);
  }
}

.cta-secondary {
  padding: 12px 32px !important;
  font-size: 16px !important;
  background: rgba(255, 255, 255, 0.05) !important;
  border-color: rgba(255, 255, 255, 0.15) !important;
  color: #c0d8f0 !important;

  &:hover {
    background: rgba(64, 158, 255, 0.1) !important;
    border-color: rgba(64, 158, 255, 0.4) !important;
    color: #fff !important;
  }
}

.hero-stats {
  display: flex;
  gap: 48px;
  justify-content: center;
  flex-wrap: wrap;
}

.quick-stat {
  text-align: center;

  .stat-num {
    display: block;
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(90deg, #409eff, #36d7b7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .stat-label {
    font-size: 13px;
    color: #6b8299;
    margin-top: 4px;
  }
}

.scroll-hint {
  position: absolute;
  bottom: 32px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #6b8299;
  font-size: 12px;
  animation: bounce 2s infinite;

  .mouse {
    width: 24px;
    height: 38px;
    border: 2px solid rgba(139, 164, 199, 0.4);
    border-radius: 12px;
    display: flex;
    justify-content: center;
    padding-top: 6px;

    .wheel {
      width: 3px;
      height: 8px;
      background: #409eff;
      border-radius: 2px;
      animation: scroll-wheel 1.5s infinite;
    }
  }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -20px); }
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.3); }
}
@keyframes shimmer {
  0% { background-position: 0% center; }
  100% { background-position: 200% center; }
}
@keyframes bounce {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(8px); }
}
@keyframes scroll-wheel {
  0% { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(10px); }
}
</style>
