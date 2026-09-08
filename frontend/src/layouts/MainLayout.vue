<template>
  <div class="main-layout">
    <aside class="sidebar" :class="{ collapsed: isCollapsed, expanding: isExpanding, 'hide-menu-text': hideMenuText || isCollapsed }">
      <div class="logo">
        <div class="logo-icon">
          <el-icon :size="22"><DataAnalysis /></el-icon>
        </div>
        <span v-show="!isCollapsed" class="logo-text">数据分析与可视化系统</span>
      </div>

      <el-menu
        :key="menuKey"
        :default-active="activeMenu"
        :default-openeds="menuOpeneds"
        router
        :collapse="isCollapsed"
        :collapse-transition="false"
        background-color="#2c3e50"
        text-color="#bfcbd9"
        active-text-color="#ffffff"
        class="sidebar-menu"
      >
        <template v-for="group in menuGroups" :key="group.key">
          <el-menu-item v-if="group.path" :index="group.path">
            <el-icon><component :is="group.icon" /></el-icon>
            <template #title>{{ group.title }}</template>
          </el-menu-item>

          <el-sub-menu v-else :index="group.key">
            <template #title>
              <el-icon><component :is="group.icon" /></el-icon>
              <span>{{ group.title }}</span>
            </template>
            <el-menu-item
              v-for="child in group.children"
              :key="child.path"
              :index="child.path"
            >
              <el-icon><component :is="child.icon" /></el-icon>
              <template #title>{{ child.title }}</template>
            </el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>
    </aside>

    <div class="main-content">
      <header class="header">
        <div class="header-left">
          <div class="collapse-btn-wrap">
            <el-icon class="header-btn collapse-btn" @click="toggleCollapse" :size="22">
              <Fold v-if="!isCollapsed" /><Menu v-else />
            </el-icon>
          </div>
          <div class="collapse-btn-wrap">
            <el-tooltip content="返回招聘数据智能分析" placement="bottom">
              <el-icon class="header-btn landing-btn" @click="goLanding" :size="20">
                <RefreshRight />
              </el-icon>
            </el-tooltip>
          </div>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleUserCommand">
            <div class="user-profile">
              <el-avatar :size="32" class="user-avatar">{{ avatarLetter }}</el-avatar>
              <span class="username">{{ userStore.displayName }}</span>
              <el-icon class="user-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <div class="tabs-bar">
        <div
          v-for="tab in visitedTabs"
          :key="tab.path"
          class="tab-item"
          :class="{ active: tab.path === route.path }"
          @click="router.push(tab.path)"
        >
          <span>{{ tab.title }}</span>
          <el-icon
            v-if="visitedTabs.length > 1"
            class="tab-close"
            @click.stop="closeTab(tab.path)"
          ><Close /></el-icon>
        </div>
      </div>

      <div class="page-nav-bar">
        <el-icon class="nav-home" @click="router.push('/app/home')"><HomeFilled /></el-icon>
        <span class="nav-sep">/</span>
        <span v-if="currentMenu?.groupTitle && currentMenu.groupTitle !== currentMenu.title" class="nav-group">
          {{ currentMenu.groupTitle }}
        </span>
        <span v-if="currentMenu?.groupTitle && currentMenu.groupTitle !== currentMenu.title" class="nav-sep">/</span>
        <span class="nav-current">{{ navTitle }}</span>
      </div>

      <div v-if="!route.meta.hideToolbar" class="page-toolbar">
        <div id="page-filters" class="page-filters"></div>
        <div class="toolbar-actions">
          <el-button v-if="!route.meta.autoSearch && !route.meta.hideToolbar" class="btn-pill btn-search" round @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button v-if="!route.meta.hideToolbar" class="btn-pill btn-reset" round @click="handleReset">
            <el-icon><RefreshRight /></el-icon> 重置
          </el-button>
        </div>
      </div>

      <main class="content">
        <router-view v-slot="{ Component }">
          <keep-alive>
            <component :is="Component" :key="route.path" />
          </keep-alive>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, provide } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { menuGroups, findMenuByPath } from '@/config/menu'
import { PAGE_TOOLBAR_KEY } from '@/composables/usePageToolbar'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isCollapsed = ref(false)
const isExpanding = ref(false)
const menuOpeneds = ref([])
const menuKey = ref(0)
const hideMenuText = ref(false)
const activeMenu = computed(() => route.path)
const pageToolbar = ref({ onSearch: null, onReset: null })

provide(PAGE_TOOLBAR_KEY, pageToolbar)

function toggleCollapse() {
  if (!isCollapsed.value) {
    hideMenuText.value = true
    menuOpeneds.value = []
    menuKey.value += 1
    isCollapsed.value = true
  } else {
    isExpanding.value = true
    hideMenuText.value = false
    isCollapsed.value = false
    menuKey.value += 1
    requestAnimationFrame(() => {
      isExpanding.value = false
    })
  }
}

const avatarLetter = computed(() => {
  const name = userStore.displayName || '用'
  return name.charAt(0).toUpperCase()
})

function goLanding() {
  router.push('/')
}

function handleUserCommand(command) {
  if (command === 'logout') {
    handleLogout()
  }
}

const currentMenu = computed(() => findMenuByPath(route.path))
const navTitle = computed(() => currentMenu.value?.title || route.meta.title || '首页')

const visitedTabs = ref([{ path: '/app/home', title: '首页' }])

watch(
  () => route.path,
  (path) => {
    const menu = findMenuByPath(path)
    const title = menu?.title || route.meta.title
    if (!title) return
    if (!visitedTabs.value.some(t => t.path === path)) {
      visitedTabs.value.push({ path, title })
    }
  },
  { immediate: true },
)

function closeTab(path) {
  const idx = visitedTabs.value.findIndex(t => t.path === path)
  if (idx === -1) return
  visitedTabs.value.splice(idx, 1)
  if (route.path === path) {
    const next = visitedTabs.value[idx] || visitedTabs.value[idx - 1]
    router.push(next?.path || '/app/home')
  }
}

function handleSearch() {
  pageToolbar.value.onSearch?.()
}

function handleReset() {
  pageToolbar.value.onReset?.()
}

function handleLogout() {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '退出',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    userStore.logout()
    router.replace('/login')
  }).catch(() => {})
}

onMounted(() => {
  if (userStore.isLoggedIn && !userStore.userInfo) {
    userStore.fetchProfile()
  }
})
</script>

<style scoped lang="scss">
.main-layout {
  display: flex;
  height: 100vh;
  background: #ffffff;
  overflow: hidden;
}

.sidebar {
  width: 240px;
  background: #2c3e50;
  transition: width 0.28s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;

  &.expanding {
    transition: none;
  }

  &.collapsed {
    width: 64px;

    .logo {
      justify-content: center;
      padding: 18px 0;
    }

    .logo-text {
      display: none;
    }
  }

  &.hide-menu-text {
    .logo-text {
      display: none;
    }

    :deep(.el-sub-menu__title > span),
    :deep(.el-menu-item .title),
    :deep(.el-menu-item span:not(.el-icon):not(svg)) {
      display: none !important;
      width: 0 !important;
      overflow: hidden !important;
    }
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 18px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);

    .logo-icon {
      width: 36px;
      height: 36px;
      border-radius: 8px;
      background: #009688;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      flex-shrink: 0;
    }

    .logo-text {
      font-size: 16px;
      font-weight: 700;
      color: #ffffff;
      white-space: nowrap;
      line-height: 1.4;
      letter-spacing: 0.5px;
    }
  }

  .sidebar-menu {
    border: none;
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;

    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      height: 46px;
      line-height: 46px;
      margin: 2px 8px;
      border-radius: 4px;

      &:hover {
        background-color: #34495e !important;
      }
    }

    :deep(.el-menu-item.is-active) {
      background-color: #009688 !important;
      color: #ffffff !important;
    }

    :deep(.el-sub-menu .el-menu-item) {
      padding-left: 48px !important;
      min-width: auto;
    }

    :deep(.el-sub-menu.is-active > .el-sub-menu__title) {
      color: #ffffff !important;
    }
  }

  &.collapsed .sidebar-menu {
    :deep(.el-menu--collapse) {
      width: 64px;
    }

    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 !important;
      margin: 4px auto;
      width: 48px;
    }

    :deep(.el-menu-item .el-menu-tooltip__trigger) {
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      width: 100% !important;
      padding: 0 !important;
    }

    :deep(.el-menu--collapse .el-menu-item.is-active) {
      padding: 0 !important;
      justify-content: center !important;
    }

    :deep(.el-menu-item .el-icon),
    :deep(.el-sub-menu__title .el-icon) {
      margin: 0 !important;
    }

    :deep(.el-sub-menu__title span),
    :deep(.el-menu-item span:not(.el-icon)) {
      display: none !important;
      width: 0 !important;
      overflow: hidden !important;
    }

    :deep(.el-sub-menu__icon-arrow) {
      display: none;
    }
  }
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
  background: #ffffff;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 50px;
  background: #ffffff;
  border-bottom: 1px solid #e8e8e8;
  flex-shrink: 0;

  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .collapse-btn-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
  }

  .header-btn {
    cursor: pointer;
    color: #666;
    padding: 6px;
    border-radius: 6px;
    transition: all 0.2s;

    &:hover {
      color: #009688;
      background: #f0f0f0;
    }

    &.collapse-btn,
    &.landing-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      padding: 0;
      font-size: 22px;
      color: #444;

      &:hover {
        color: #009688;
        background: #eef7f6;
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .user-profile {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 8px 4px 4px;
    border-radius: 20px;
    cursor: pointer;
    transition: background 0.2s;

    &:hover {
      background: #f5f5f5;
    }

    .user-avatar {
      background: #009688;
      color: #fff;
      font-size: 14px;
      font-weight: 600;
      flex-shrink: 0;
    }

    .username {
      color: #333;
      font-size: 13px;
      font-weight: 500;
      max-width: 120px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .user-arrow {
      color: #999;
      font-size: 12px;
    }
  }
}

.tabs-bar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 0 12px;
  height: 38px;
  background: #f5f5f5;
  border-bottom: 1px solid #e8e8e8;
  overflow-x: auto;
  flex-shrink: 0;

  .tab-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0 14px;
    height: 30px;
    font-size: 12px;
    color: #666;
    background: transparent;
    border-radius: 3px;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.2s;

    &:hover {
      color: #009688;
    }

    &.active {
      background: #ffffff;
      color: #009688;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }

    .tab-close {
      font-size: 12px;
      border-radius: 50%;
      padding: 1px;

      &:hover {
        background: #e8e8e8;
        color: #ff4d4f;
      }
    }
  }
}

.page-nav-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: #ffffff;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
  flex-shrink: 0;

  .nav-home {
    color: #009688;
    cursor: pointer;
    font-size: 16px;

    &:hover { opacity: 0.8; }
  }

  .nav-sep { color: #ccc; }
  .nav-group { color: #999; }
  .nav-current { color: #333; font-weight: 600; }
}

.page-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 20px;
  background: #ffffff;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;

  .page-filters {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
    flex-wrap: wrap;
    min-height: 32px;
  }

  .toolbar-actions {
    display: flex;
    gap: 10px;
    flex-shrink: 0;
  }

  .btn-search {
    background: #f5a623 !important;
    border: none !important;
    color: #fff !important;
    padding: 8px 22px;

    &:hover {
      background: #e6951a !important;
    }
  }

  .btn-reset {
    background: #3498db !important;
    border: none !important;
    color: #fff !important;
    padding: 8px 22px;

    &:hover {
      background: #2980b9 !important;
    }
  }
}

.content {
  flex: 1;
  overflow: hidden;
  background: #ffffff;
  padding: 16px 20px;
}
</style>
