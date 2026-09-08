<template>
  <div class="announce-bar">
    <div class="home-container bar-inner">
      <el-icon class="bar-icon"><Bell /></el-icon>
      <p>
        <strong>系统升级</strong>
        整合 BOSS直聘、智联招聘、拉勾网、猎聘网四大平台，实现采集 → 清洗 → 分析 → 预测全链路闭环
      </p>
      <a href="#platform" @click.prevent="scrollTo('#platform')">了解更多 →</a>
    </div>
  </div>
</template>

<script setup>
function scrollTo(sel) {
  document.querySelector(sel)?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped lang="scss">
.announce-bar {
  background: linear-gradient(90deg, rgba(22, 119, 255, 0.12), rgba(19, 194, 194, 0.08));
  border-top: 1px solid rgba(22, 119, 255, 0.15);
  border-bottom: 1px solid rgba(22, 119, 255, 0.15);
}

.bar-inner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 0;
  flex-wrap: wrap;

  .bar-icon {
    color: var(--color-primary-light);
    flex-shrink: 0;
  }

  p {
    flex: 1;
    font-size: 14px;
    color: var(--text-secondary);
    margin: 0;
    min-width: 200px;

    strong {
      color: var(--color-primary-light);
      margin-right: 8px;
    }
  }

  a {
    font-size: 13px;
    color: var(--color-cyan);
    text-decoration: none;
    white-space: nowrap;
    transition: color 0.2s;

    &:hover { color: var(--color-primary-light); }
  }
}
</style>
