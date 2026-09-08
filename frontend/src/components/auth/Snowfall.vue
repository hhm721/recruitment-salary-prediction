<template>
  <canvas ref="canvasRef" class="snow-canvas" aria-hidden="true" />
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const canvasRef = ref(null)

let animationId = 0
let flakes = []
let width = 0
let height = 0

function createFlakes(count) {
  flakes = Array.from({ length: count }, () => ({
    x: Math.random() * width,
    y: Math.random() * height,
    radius: Math.random() * 2.2 + 0.8,
    speed: Math.random() * 1.2 + 0.4,
    drift: Math.random() * 0.6 - 0.3,
    opacity: Math.random() * 0.5 + 0.3,
    swing: Math.random() * Math.PI * 2,
    swingSpeed: Math.random() * 0.02 + 0.008,
  }))
}

function resize() {
  const canvas = canvasRef.value
  if (!canvas) return
  width = window.innerWidth
  height = window.innerHeight
  canvas.width = width
  canvas.height = height
  if (!flakes.length) createFlakes(Math.min(120, Math.floor(width / 12)))
}

function draw() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, width, height)

  flakes.forEach((flake) => {
    flake.y += flake.speed
    flake.swing += flake.swingSpeed
    flake.x += Math.sin(flake.swing) * 0.6 + flake.drift

    if (flake.y > height + 8) {
      flake.y = -8
      flake.x = Math.random() * width
    }
    if (flake.x > width + 8) flake.x = -8
    if (flake.x < -8) flake.x = width + 8

    ctx.beginPath()
    ctx.arc(flake.x, flake.y, flake.radius, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(220, 235, 255, ${flake.opacity})`
    ctx.fill()

    ctx.beginPath()
    ctx.arc(flake.x, flake.y, flake.radius * 0.45, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(255, 255, 255, ${Math.min(flake.opacity + 0.2, 0.95)})`
    ctx.fill()
  })

  animationId = requestAnimationFrame(draw)
}

onMounted(() => {
  resize()
  draw()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  cancelAnimationFrame(animationId)
  window.removeEventListener('resize', resize)
})
</script>

<style scoped>
.snow-canvas {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}
</style>
