<template>
  <nav class="landing-nav" :class="{ scrolled }">
    <div class="home-container nav-inner">
      <div class="brand" @click="scrollTo('#banner')">
        <div class="brand-icon">
          <el-icon :size="22"><DataAnalysis /></el-icon>
        </div>
        <span>招聘数据智能分析</span>
      </div>

      <div class="nav-links desktop-only">
        <a v-for="link in navLinks" :key="link.id" :href="link.id" @click.prevent="scrollTo(link.id)">
          {{ link.label }}
        </a>
      </div>

      <Teleport to="body">
        <Transition name="mobile-nav">
          <div v-if="menuOpen" class="mobile-nav-overlay" @click="menuOpen = false">
            <div class="mobile-nav-panel" @click.stop>
              <a
                v-for="link in navLinks"
                :key="link.id"
                :href="link.id"
                @click.prevent="scrollTo(link.id)"
              >
                {{ link.label }}
              </a>
            </div>
          </div>
        </Transition>
      </Teleport>

      <div class="nav-actions">
        <el-button
          v-if="!userStore.isLoggedIn"
          class="nav-btn ghost-btn"
          round
          @click="goLogin"
        >登录</el-button>
        <el-button
          v-else
          class="nav-btn logout-btn"
          round
          @click="handleLogout"
        >退出</el-button>
        <el-button type="primary" round class="nav-btn enter-btn" @click="enterSystem">
          免费体验
          <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
        <button class="menu-toggle" @click="menuOpen = !menuOpen">
          <span /><span /><span />
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const emit = defineEmits(['enter'])
const router = useRouter()
const userStore = useUserStore()
const scrolled = ref(false)
const menuOpen = ref(false)

const navLinks = [
  { id: '#banner', label: '首页' },
  { id: '#platform', label: '平台能力' },
  { id: '#scenarios', label: '应用场景' },
  { id: '#stats', label: '数据概览' },
  { id: '#tech', label: '资源中心' },
]

function onScroll() {
  scrolled.value = window.scrollY > 50
}

function scrollTo(selector) {
  menuOpen.value = false
  const el = document.querySelector(selector)
  if (!el) return
  const navHeight = document.querySelector('.landing-nav')?.offsetHeight || 64
  const top = el.getBoundingClientRect().top + window.scrollY - navHeight
  window.scrollTo({ top, behavior: 'smooth' })
}

function goLogin() {
  menuOpen.value = false
  router.push('/login')
}

function enterSystem() {
  menuOpen.value = false
  emit('enter')
  if (userStore.isLoggedIn) {
    router.push('/app/home')
  } else {
    router.push('/register')
  }
}

function handleLogout() {
  menuOpen.value = false
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '退出',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    userStore.logout()
    router.push('/login')
  }).catch(() => {})
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped lang="scss">
.landing-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 64px;
  display: flex;
  align-items: center;
  background: rgba(10, 14, 23, 0.75);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.3s;

  &.scrolled {
    background: rgba(10, 14, 23, 0.92);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
  }
}

.nav-inner {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: none;
  padding-right: 30px;
  gap: 24px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-weight: 700;
  font-size: 16px;
  color: #f0f4f8;
  flex-shrink: 0;

  .brand-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: var(--gradient-brand);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
  }
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 28px;
  flex: 1;

  a {
    color: #94a3b8;
    text-decoration: none;
    font-size: 14px;
    white-space: nowrap;
    transition: color 0.2s;

    &:hover { color: #60a5fa; }
  }
}

.mobile-nav-overlay {
  position: fixed;
  inset: 64px 0 0;
  z-index: 9998;
  background: rgba(10, 14, 23, 0.75);
  backdrop-filter: blur(8px);
}

.mobile-nav-panel {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  padding: 16px 20px 24px;
  background: rgba(10, 14, 23, 0.98);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);

  a {
    display: block;
    width: 100%;
    padding: 14px 12px;
    color: #e2e8f0;
    text-decoration: none;
    font-size: 15px;
    border-radius: 8px;
    transition: background 0.2s, color 0.2s;

    &:hover,
    &:active {
      background: rgba(96, 165, 250, 0.12);
      color: #60a5fa;
    }
  }
}

.mobile-nav-enter-active,
.mobile-nav-leave-active {
  transition: opacity 0.25s ease;

  .mobile-nav-panel {
    transition: transform 0.25s ease;
  }
}

.mobile-nav-enter-from,
.mobile-nav-leave-to {
  opacity: 0;

  .mobile-nav-panel {
    transform: translateY(-12px);
  }
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  margin-left: auto;
}

.nav-btn {
  border-radius: 30px !important;
  padding: 10px 22px !important;
  font-size: 14px !important;
  height: auto !important;
}

.ghost-btn {
  background: transparent !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  color: #e2e8f0 !important;

  &:hover {
    border-color: rgba(96, 165, 250, 0.6) !important;
    color: #60a5fa !important;
    background: rgba(96, 165, 250, 0.08) !important;
  }
}

.logout-btn {
  background: rgba(231, 76, 60, 0.15) !important;
  border: 1px solid rgba(231, 76, 60, 0.45) !important;
  color: #fca5a5 !important;

  &:hover {
    background: rgba(231, 76, 60, 0.28) !important;
    color: #fff !important;
  }
}

.enter-btn {
  background: linear-gradient(135deg, #f5a623, #e6951a) !important;
  border: none !important;
  color: #fff !important;
  box-shadow: 0 4px 16px rgba(245, 166, 35, 0.35);
}

.menu-toggle {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;

  span {
    display: block;
    width: 22px;
    height: 2px;
    background: #94a3b8;
  }
}

@media (max-width: 900px) {
  .nav-inner {
    padding-right: 16px;
  }

  .desktop-only {
    display: none;
  }

  .menu-toggle { display: flex; }
}
</style>
