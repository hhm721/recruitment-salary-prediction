import { ref, onMounted, onUnmounted } from 'vue'

export function useScrollReveal(selector = '.reveal', options = {}) {
  let observer

  onMounted(() => {
    const elements = document.querySelectorAll(selector)
    if (!elements.length) return

    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed')
            if (options.once !== false) {
              observer.unobserve(entry.target)
            }
          } else if (options.once === false) {
            entry.target.classList.remove('revealed')
          }
        })
      },
      {
        threshold: options.threshold ?? 0.15,
        rootMargin: options.rootMargin ?? '0px 0px -40px 0px',
      }
    )

    elements.forEach((el) => observer.observe(el))
  })

  onUnmounted(() => observer?.disconnect())
}

export function useNavbarScroll(threshold = 60) {
  const scrolled = ref(false)

  function onScroll() {
    scrolled.value = window.scrollY > threshold
  }

  onMounted(() => {
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
  })

  onUnmounted(() => window.removeEventListener('scroll', onScroll))

  return { scrolled }
}
