import { ref, onMounted, onUnmounted } from 'vue'

export function useCountUp(target, duration = 2000, decimals = 0) {
  const display = ref(0)
  let frameId

  function animate(startValue, endValue) {
    const startTime = performance.now()
    const diff = endValue - startValue

    function step(now) {
      const progress = Math.min((now - startTime) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      display.value = Number((startValue + diff * eased).toFixed(decimals))
      if (progress < 1) frameId = requestAnimationFrame(step)
    }

    frameId = requestAnimationFrame(step)
  }

  function startWhenVisible(el) {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          animate(0, target)
          observer.disconnect()
        }
      },
      { threshold: 0.3 }
    )
    if (el) observer.observe(el)
    return () => observer.disconnect()
  }

  onUnmounted(() => {
    if (frameId) cancelAnimationFrame(frameId)
  })

  return { display, animate, startWhenVisible }
}
