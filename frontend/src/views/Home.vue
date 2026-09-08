<template>
  <div class="home-page dark-landing">
    <div class="ambient-bg" aria-hidden="true">
      <div class="orb orb-1" />
      <div class="orb orb-2" />
      <div class="grid-overlay" />
    </div>
    <!-- 导航条组件 -->
    <LandingNav @enter="enterSystem" />
    <!-- 轮播图组件 -->
    <BannerCarousel />
    <!-- 信息组件模块组件 -->
    <QuickInfoBar />
    <!-- 招聘数据智能分析一体化平台模块组件 -->
    <UnifiedPlatform @enter="enterModule" />
    <!-- 行业应用场景模块组件 -->
    <IndustrySolutions />
    <!-- 用数据说话洞察招聘市场模块组件 -->
    <StatsCounter />
    <!-- 主流技术栈模块组件 -->
    <TechStack @enter="enterSystem" />
    <!-- 底部信息栏组件 -->
    <LandingFooter />
    <!-- 智能助手组件 -->
    <ChatBot />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useScrollReveal } from '@/composables/useScrollReveal'
import LandingNav from '@/components/home/LandingNav.vue'
import BannerCarousel from '@/components/home/BannerCarousel.vue'
import QuickInfoBar from '@/components/home/QuickInfoBar.vue'
import UnifiedPlatform from '@/components/home/UnifiedPlatform.vue'
import IndustrySolutions from '@/components/home/IndustrySolutions.vue'
import StatsCounter from '@/components/home/StatsCounter.vue'
import TechStack from '@/components/home/TechStack.vue'
import LandingFooter from '@/components/home/LandingFooter.vue'
import ChatBot from '@/components/chat/ChatBot.vue'
import '@/styles/home.scss'

const router = useRouter()
const userStore = useUserStore()

useScrollReveal('.reveal')

function enterSystem() {
  router.push(userStore.isLoggedIn ? '/app/home' : '/login')
}

function enterModule(route) {
  const target = route || '/app/dashboard'
  if (userStore.isLoggedIn) {
    router.push(target)
  } else {
    router.push({ path: '/login', query: { redirect: target } })
  }
}

onMounted(() => {
  document.documentElement.style.scrollBehavior = 'smooth'
})
</script>

<style scoped lang="scss">
.home-page {
  position: relative;
  min-height: 100vh;
  background: var(--dark-page-bg);
  color: #e8eaed;
  overflow-x: hidden;
}

.home-page.dark-landing {
  background: var(--dark-page-bg);
}

.ambient-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  animation: drift 20s ease-in-out infinite alternate;
}

.orb-1 {
  width: 520px;
  height: 520px;
  top: -120px;
  right: -80px;
  background: rgba(22, 119, 255, 0.1);
}

.orb-2 {
  width: 420px;
  height: 420px;
  bottom: -100px;
  left: -60px;
  background: rgba(19, 194, 194, 0.08);
  animation-delay: -6s;
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(22, 119, 255, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(22, 119, 255, 0.04) 1px, transparent 1px);
  background-size: 64px 64px;
  mask-image: radial-gradient(ellipse at 50% 30%, black 20%, transparent 75%);
}

.home-page > :not(.ambient-bg) {
  position: relative;
  z-index: 1;
}

@keyframes drift {
  from { transform: translate(0, 0); }
  to { transform: translate(24px, -32px); }
}
</style>
