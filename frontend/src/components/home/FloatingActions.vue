<template>

  <div class="floating-actions">

    <Transition name="fab">

      <div v-show="expanded" class="fab-menu">

        <button v-for="action in actions" :key="action.label" class="fab-item" @click="action.handler">

          <el-icon :size="18"><component :is="action.icon" /></el-icon>

          <span>{{ action.label }}</span>

        </button>

      </div>

    </Transition>



    <button class="fab-main" :class="{ expanded }" @click="toggle">

      <el-icon :size="22"><component :is="expanded ? 'Close' : 'ChatDotRound'" /></el-icon>

    </button>

  </div>

</template>



<script setup>

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const expanded = ref(false)



const actions = [

  {

    label: '进入系统',

    icon: 'Monitor',

    handler: () => {
      router.push(userStore.isLoggedIn ? '/app/dashboard' : '/login')
    },

  },

  {

    label: '数据采集',

    icon: 'Download',

    handler: () => router.push('/app/crawl'),

  },

  {

    label: '薪资预测',

    icon: 'TrendCharts',

    handler: () => router.push('/app/predict'),

  },

  {

    label: '回到顶部',

    icon: 'Top',

    handler: () => window.scrollTo({ top: 0, behavior: 'smooth' }),

  },

]



function toggle() {

  expanded.value = !expanded.value

}

</script>



<style scoped lang="scss">

.floating-actions {

  position: fixed;

  right: 24px;

  bottom: 32px;

  z-index: 999;

  display: flex;

  flex-direction: column;

  align-items: flex-end;

  gap: 12px;

}



.fab-menu {

  display: flex;

  flex-direction: column;

  gap: 8px;

}



.fab-item {

  display: flex;

  align-items: center;

  gap: 10px;

  padding: 10px 18px;

  border-radius: 50px;

  border: 1px solid var(--border-subtle);

  background: rgba(14, 10, 28, 0.92);

  backdrop-filter: blur(16px);

  color: var(--text-secondary);

  font-size: 13px;

  cursor: pointer;

  white-space: nowrap;

  transition: all 0.3s;

  box-shadow: var(--shadow-card);



  &:hover {

    background: rgba(167, 139, 250, 0.12);

    border-color: var(--border-accent);

    color: var(--text-primary);

    transform: translateX(-4px);

  }

}



.fab-main {

  width: 54px;

  height: 54px;

  border-radius: 50%;

  border: none;

  background: var(--gradient-brand);

  color: #fff;

  cursor: pointer;

  display: flex;

  align-items: center;

  justify-content: center;

  box-shadow: 0 6px 28px rgba(139, 92, 246, 0.45);

  transition: all 0.3s;



  &:hover { transform: scale(1.08); }

  &.expanded { background: var(--gradient-warm); }

}



.fab-enter-active,

.fab-leave-active {

  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

}

.fab-enter-from,

.fab-leave-to {

  opacity: 0;

  transform: translateY(10px) scale(0.9);

}

</style>


