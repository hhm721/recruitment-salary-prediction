<template>
  <footer class="landing-footer">
    <div class="footer-top">
      <div class="home-container footer-grid">
        <!-- 品牌介绍 -->
        <div class="footer-col brand-col">
          <div class="footer-brand">
            <div class="brand-icon">
              <el-icon :size="22"><DataAnalysis /></el-icon>
            </div>
            <div>
              <h3>招聘数据智能分析平台</h3>
              <p class="brand-slogan">数据采集 · 清洗分析 · 智能预测</p>
            </div>
          </div>
          <p class="brand-desc">
            面向 BOSS直聘、智联招聘、拉勾网、猎聘网四大主流招聘渠道，
            构建从 Scrapy 异步采集到 ML 薪资预测的全链路智能分析系统。
          </p>
          <div class="tech-tags">
            <span v-for="t in techTags" :key="t">{{ t }}</span>
          </div>
        </div>

        <!-- 功能导航 -->
        <div class="footer-col">
          <h4>系统功能</h4>
          <ul>
            <li v-for="link in featureLinks" :key="link.label">
              <a @click.prevent="navigate(link)">{{ link.label }}</a>
            </li>
          </ul>
        </div>

        <!-- 快速入口 -->
        <div class="footer-col">
          <h4>快速入口</h4>
          <ul>
            <li v-for="link in quickLinks" :key="link.label">
              <a @click.prevent="navigate(link)">{{ link.label }}</a>
            </li>
          </ul>
        </div>

        <!-- 技术架构 -->
        <div class="footer-col">
          <h4>技术架构</h4>
          <ul>
            <li v-for="item in archItems" :key="item">{{ item }}</li>
          </ul>
        </div>

        <!-- 联系信息 -->
        <div class="footer-col contact-col">
          <h4>联系我们</h4>
          <ul class="contact-list">
            <li>
              <el-icon><Message /></el-icon>
              <span>support@recruitment-analytics.com</span>
            </li>
            <li>
              <el-icon><Location /></el-icon>
              <span>中国 · 教育实训项目</span>
            </li>
            <li>
              <el-icon><Clock /></el-icon>
              <span>服务时间：周一至周五 9:00-18:00</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 友情链接 -->
    <div class="footer-links-bar">
      <div class="home-container links-inner">
        <span class="links-label">相关平台：</span>
        <a v-for="p in platformLinks" :key="p.name" :href="p.url" target="_blank" rel="noopener">{{ p.name }}</a>
      </div>
    </div>

    <!-- 版权信息 -->
    <div class="footer-bottom">
      <div class="home-container bottom-inner">
        <p>© 2026 招聘数据采集、分析与智能薪资预测系统 · 教学实训项目</p>
        <div class="bottom-links">
          <a @click.prevent="scrollTo('#banner')">返回顶部</a>
          <span class="divider">|</span>
          <a @click.prevent="enterSystem">管理系统</a>
          <span class="divider">|</span>
          <span>Flask + Scrapy + Vue3 + MySQL + scikit-learn</span>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const techTags = ['Scrapy', 'Flask', 'Vue3', 'MySQL', 'ECharts', 'ML']

const featureLinks = [
  { label: '数据采集', path: '/app/crawl' },
  { label: '原始数据', path: '/app/raw-data' },
  { label: '数据清洗', path: '/app/clean-data' },
  { label: '可视化大屏', path: '/app/dashboard' },
  { label: '薪资预测', path: '/app/predict' },
]

const quickLinks = [
  { label: '首页 Banner', hash: '#banner' },
  { label: '平台能力', hash: '#platform' },
  { label: '应用场景', hash: '#scenarios' },
  { label: '数据概览', hash: '#stats' },
  { label: '资源中心', hash: '#tech' },
]

const archItems = [
  'Scrapy 异步爬虫采集',
  'Flask RESTful API 层',
  'Vue3 + Element Plus 前端',
  'MySQL 数据持久化',
  'ECharts 可视化引擎',
  'scikit-learn 薪资预测',
]

const platformLinks = [
  { name: 'BOSS直聘', url: 'https://www.zhipin.com' },
  { name: '智联招聘', url: 'https://www.zhaopin.com' },
  { name: '拉勾网', url: 'https://www.lagou.com' },
  { name: '猎聘网', url: 'https://www.liepin.com' },
]

function navigate(link) {
  if (link.path) {
    router.push(link.path)
  } else if (link.hash) {
    scrollTo(link.hash)
  }
}

function scrollTo(selector) {
  document.querySelector(selector)?.scrollIntoView({ behavior: 'smooth' })
}

function enterSystem() {
  if (userStore.isLoggedIn) {
    router.push('/app/dashboard')
  } else {
    router.push('/login')
  }
}
</script>

<style scoped lang="scss">
.landing-footer {
  background: rgba(10, 14, 23, 0.6);
  border-top: 1px solid var(--border-subtle);
}

.footer-top {
  padding: 48px 0 36px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1.2fr;
  gap: 40px;

  @media (max-width: 1100px) {
    grid-template-columns: 1fr 1fr 1fr;
  }
  @media (max-width: 700px) {
    grid-template-columns: 1fr;
    gap: 32px;
  }
}

.footer-col {
  h4 {
    font-size: 15px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border-subtle);
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;

    li {
      margin-bottom: 12px;
      font-size: 13px;
      color: var(--text-muted);

      a {
        color: var(--text-secondary);
        text-decoration: none;
        cursor: pointer;
        transition: color 0.3s;

        &:hover { color: var(--color-violet); }
      }
    }
  }
}

.brand-col {
  .footer-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;

    .brand-icon {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: var(--gradient-brand);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      flex-shrink: 0;
    }

    h3 {
      font-size: 16px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 2px;
    }

    .brand-slogan {
      font-size: 12px;
      color: var(--color-cyan);
    }
  }

  .brand-desc {
    font-size: 13px;
    line-height: 1.8;
    color: var(--text-muted);
    margin-bottom: 20px;
  }

  .tech-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    span {
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 11px;
      background: rgba(22, 119, 255, 0.1);
      border: 1px solid rgba(22, 119, 255, 0.2);
      color: var(--text-secondary);
    }
  }
}

.contact-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary) !important;

  .el-icon { color: var(--color-violet); flex-shrink: 0; }
}

.footer-cta {
  margin-top: 20px;
  width: 100%;
  background: var(--gradient-btn) !important;
  border: none !important;
}

.footer-links-bar {
  padding: 16px 0;
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.04);

  .links-inner {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px 20px;
  }

  .links-label {
    font-size: 13px;
    color: #6b8299;
    flex-shrink: 0;
  }

  a {
    font-size: 13px;
    color: var(--text-secondary);
    text-decoration: none;
    transition: color 0.3s;

    &:hover { color: var(--color-violet); }
  }
}

.footer-bottom {
  padding: 20px 0;

  .bottom-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
  }

  p {
    font-size: 12px;
    color: var(--text-muted);
    margin: 0;
  }

  .bottom-links {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 12px;
    color: var(--text-muted);

    a {
      color: var(--text-muted);
      cursor: pointer;
      text-decoration: none;
      transition: color 0.3s;

      &:hover { color: var(--color-violet); }
    }

    .divider { color: var(--border-subtle); }
  }
}
</style>
