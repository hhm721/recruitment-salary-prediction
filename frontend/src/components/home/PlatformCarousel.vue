<template>
  <section id="platforms" class="platforms section">
    <div class="home-container">
      <div class="section-header reveal">
      <span class="section-tag">招聘平台</span>
      <h2>四大主流渠道<span class="accent">全覆盖</span></h2>
      <p>深度整合国内头部招聘平台，构建统一的数据采集与分析体系</p>
    </div>

    <div class="platform-carousel reveal">
      <div class="carousel-track" :style="{ transform: `translateX(-${activeIndex * 100}%)` }">
        <div v-for="(platform, i) in platforms" :key="i" class="carousel-slide">
          <div class="platform-card" :style="{ '--accent': platform.color }">
            <div class="platform-header">
              <div class="platform-logo">{{ platform.shortName }}</div>
              <div>
                <h3>{{ platform.name }}</h3>
                <span class="platform-domain">{{ platform.domain }}</span>
              </div>
            </div>
            <p class="platform-desc">{{ platform.desc }}</p>
            <div class="platform-metrics">
              <div v-for="m in platform.metrics" :key="m.label" class="metric">
                <span class="metric-value">{{ m.value }}</span>
                <span class="metric-label">{{ m.label }}</span>
              </div>
            </div>
            <div class="platform-fields">
              <span v-for="f in platform.fields" :key="f" class="field-tag">{{ f }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="carousel-controls">
        <button v-for="(_, i) in platforms" :key="i" class="dot" :class="{ active: activeIndex === i }" @click="goTo(i)" />
      </div>

      <button class="nav-btn prev" @click="prev"><el-icon><ArrowLeft /></el-icon></button>
      <button class="nav-btn next" @click="next"><el-icon><ArrowRight /></el-icon></button>
    </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const activeIndex = ref(0)
let autoTimer

const platforms = [
  {
    shortName: 'BOSS',
    name: 'BOSS直聘',
    domain: 'zhipin.com',
    color: '#00bebd',
    desc: '国内领先的在线招聘平台，以"直聊"模式著称，覆盖互联网、金融、制造业等多个行业，岗位更新频率高，薪资信息透明。',
    metrics: [
      { value: '1500万+', label: '活跃岗位' },
      { value: '1亿+', label: '注册用户' },
      { value: '实时', label: '数据更新' },
    ],
    fields: ['岗位名称', '公司名称', '薪资范围', '经验要求', '技能标签'],
  },
  {
    shortName: '智联',
    name: '智联招聘',
    domain: 'zhaopin.com',
    color: '#0066cc',
    desc: '成立最早的在线招聘平台之一，覆盖全行业全职能，拥有庞大的企业用户基础和完善的简历库体系。',
    metrics: [
      { value: '800万+', label: '合作企业' },
      { value: '2.6亿+', label: '职场用户' },
      { value: '全国', label: '城市覆盖' },
    ],
    fields: ['职位详情', '企业信息', '工作地点', '学历要求', '福利待遇'],
  },
  {
    shortName: '拉勾',
    name: '拉勾网',
    domain: 'lagou.com',
    color: '#00b38a',
    desc: '专注于互联网行业的垂直招聘平台，以精准的互联网岗位和较高的薪资水平著称，是互联网从业者首选渠道。',
    metrics: [
      { value: '200万+', label: '互联网岗位' },
      { value: '50万+', label: 'IT企业' },
      { value: '精准', label: '行业定位' },
    ],
    fields: ['技术栈', '团队规模', '融资阶段', '工作地址', '岗位标签'],
  },
  {
    shortName: '猎聘',
    name: '猎聘网',
    domain: 'liepin.com',
    color: '#ff6600',
    desc: '中高端人才招聘平台，以猎头服务和年薪制岗位为主，覆盖管理层和技术专家等高薪职位，数据质量高。',
    metrics: [
      { value: '7000万+', label: '中高端用户' },
      { value: '50万+', label: '认证猎头' },
      { value: '高薪', label: '岗位特色' },
    ],
    fields: ['年薪范围', '职级要求', '行业领域', '管理幅度', '核心技能'],
  },
]

function goTo(i) { activeIndex.value = i }
function next() { activeIndex.value = (activeIndex.value + 1) % platforms.length }
function prev() { activeIndex.value = (activeIndex.value - 1 + platforms.length) % platforms.length }

onMounted(() => {
  autoTimer = setInterval(next, 5000)
})
onUnmounted(() => clearInterval(autoTimer))
</script>

<style scoped lang="scss">
.platform-carousel {
  position: relative;
  overflow: hidden;
  border-radius: 20px;
}

.carousel-track {
  display: flex;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.carousel-slide {
  min-width: 100%;
  padding: 0 4px;
}

.platform-card {
  padding: 36px;
  background: var(--bg-glass);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  border-left: 4px solid var(--accent);
  backdrop-filter: blur(16px);
}

.platform-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;

  .platform-logo {
    width: 64px;
    height: 64px;
    border-radius: 16px;
    background: var(--accent);
    color: #fff;
    font-weight: 800;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  h3 {
    font-size: 24px;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .platform-domain {
    font-size: 13px;
    color: var(--text-muted);
  }
}

.platform-desc {
  color: var(--text-secondary);
  line-height: 1.8;
  margin-bottom: 28px;
  max-width: 700px;
}

.platform-metrics {
  display: flex;
  gap: 48px;
  margin-bottom: 28px;

  .metric-value {
    display: block;
    font-size: 24px;
    font-weight: 800;
    color: var(--accent);
  }
  .metric-label {
    font-size: 13px;
    color: #6b8299;
  }
}

.platform-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;

  .field-tag {
    padding: 6px 16px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #9bb0cc;
    font-size: 13px;
  }
}

.carousel-controls {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 24px;

  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    border: none;
    background: rgba(64, 158, 255, 0.2);
    cursor: pointer;
    transition: all 0.3s;

    &.active {
      width: 28px;
      border-radius: 5px;
      background: #409eff;
    }
  }
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid rgba(64, 158, 255, 0.2);
  background: rgba(8, 14, 35, 0.8);
  color: #c0d8f0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;

  &:hover {
    background: rgba(64, 158, 255, 0.2);
    border-color: #409eff;
  }

  &.prev { left: -22px; }
  &.next { right: -22px; }
}

@media (max-width: 768px) {
  .platform-card { padding: 28px; }
  .platform-metrics { gap: 24px; flex-wrap: wrap; }
  .nav-btn { display: none; }
}
</style>
