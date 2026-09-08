<template>
  <Teleport to="body">
  <div class="chatbot-root">
    <Transition name="chat-panel">
      <div v-if="visible" class="chat-panel">
        <header class="chat-header">
          <div class="bot-avatar">
            <el-icon :size="22"><ChatDotRound /></el-icon>
          </div>
          <div class="bot-info">
            <strong>智能助手</strong>
            <span><i class="online-dot" />在线 · 随时为您解答</span>
          </div>
          <button class="close-btn" type="button" aria-label="关闭" @click="visible = false">
            <el-icon :size="18"><Close /></el-icon>
          </button>
        </header>

        <div ref="messageBox" class="chat-messages">
          <div
            v-for="(msg, i) in messages"
            :key="i"
            class="message-row"
            :class="msg.role"
          >
            <div v-if="msg.role === 'bot'" class="msg-avatar">
              <el-icon :size="16"><ChatDotRound /></el-icon>
            </div>
            <div class="message-bubble" v-html="msg.content" />
          </div>
          <div v-if="typing" class="message-row bot">
            <div class="msg-avatar"><el-icon :size="16"><ChatDotRound /></el-icon></div>
            <div class="message-bubble typing">
              <span /><span /><span />
            </div>
          </div>
        </div>

        <div class="quick-questions">
          <button
            v-for="q in quickQuestions"
            :key="q"
            class="quick-btn"
            @click="askQuestion(q)"
          >
            {{ q }}
          </button>
        </div>

        <footer class="chat-input">
          <el-input
            v-model="inputText"
            type="textarea"
            :rows="5"
            placeholder="输入您的问题..."
            resize="none"
            @keydown.ctrl.enter.prevent="sendMessage"
          />
          <el-button type="primary" circle @click="sendMessage" :disabled="!inputText.trim()">
            <el-icon><Promotion /></el-icon>
          </el-button>
        </footer>
      </div>
    </Transition>
  </div>
  </Teleport>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'

const visible = ref(false)
const typing = ref(false)
const inputText = ref('')
const messageBox = ref(null)

const quickQuestions = [
  '系统有哪些功能？',
  '支持哪些招聘平台？',
  '如何进行薪资预测？',
  '如何开始使用？',
]

const FAQ = [
  {
    keys: ['功能', '模块', '做什么', '介绍'],
    answer: '本系统包含五大核心模块：<b>爬虫管理</b>（Scrapy 异步采集）、<b>原始数据</b>（多条件查询与导出）、<b>数据清洗</b>（薪资解析与技能提取）、<b>可视化大屏</b>（ECharts 多维分析）、<b>薪资预测</b>（ML 模型推理）。',
  },
  {
    keys: ['平台', '招聘', 'boss', '智联', '拉勾', '猎聘'],
    answer: '目前整合 <b>BOSS直聘、智联招聘、拉勾网、猎聘网</b> 四大主流招聘平台，支持按关键词与城市筛选采集，数据自动写入 MySQL 数据库。',
  },
  {
    keys: ['薪资', '预测', '简历', 'ml', '机器学习'],
    answer: '在「薪资预测」模块上传 txt/pdf/doc 格式简历，系统自动提取技能与经验，基于 GradientBoosting 模型推理输出预估薪资区间及匹配置信度。',
  },
  {
    keys: ['开始', '登录', '注册', '使用', '体验', '进入'],
    answer: '点击右上角「免费体验」或「登录」注册账号（演示账号 admin/admin123），登录后即可进入管理系统使用全部功能。',
  },
  {
    keys: ['清洗', '导出', 'excel', '数据'],
    answer: '原始数据与清洗数据页面均支持 <b>修改、删除、导出 Excel/JSON/TXT</b>。在数据清洗页点击「执行数据清洗」可批量处理未清洗的原始记录。',
  },
  {
    keys: ['技术', '架构', '栈'],
    answer: '技术栈：Flask + Scrapy + MySQL + Vue3 + Element Plus + ECharts + scikit-learn，前后端完全解耦，RESTful API 驱动。',
  },
]

const messages = ref([
  {
    role: 'bot',
    content: '您好！我是<b>智能助手</b>，可为您解答系统功能、数据采集、薪资预测等问题。请问有什么可以帮您？',
  },
])

function scrollBottom() {
  nextTick(() => {
    if (messageBox.value) {
      messageBox.value.scrollTop = messageBox.value.scrollHeight
    }
  })
}

function getReply(text) {
  const lower = text.toLowerCase()
  for (const item of FAQ) {
    if (item.keys.some(k => lower.includes(k.toLowerCase()) || text.includes(k))) {
      return item.answer
    }
  }
  return '感谢您的提问！您可以尝试询问「系统功能」「招聘平台」「薪资预测」或「如何开始使用」。如需人工帮助，请登录系统后在各模块中操作体验。'
}

function askQuestion(q) {
  inputText.value = q
  sendMessage()
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text) return

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  scrollBottom()

  typing.value = true
  await new Promise(r => setTimeout(r, 600 + Math.random() * 400))
  typing.value = false

  messages.value.push({ role: 'bot', content: getReply(text) })
  scrollBottom()
}

onMounted(() => {
  setTimeout(() => {
    visible.value = true
  }, 1500)
})
</script>

<style scoped lang="scss">
.chatbot-root {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 9999;
}

.chat-panel {
  width: 380px;
  max-height: min(620px, calc(100vh - 48px));
  display: flex;
  flex-direction: column;
  background: var(--dark-page-bg, #0a0e17);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.45);
  overflow: hidden;

  @media (max-width: 480px) {
    width: calc(100vw - 32px);
  }
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 18px;
  background: rgba(255, 255, 255, 0.04);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);

  .bot-avatar {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: var(--gradient-btn);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    flex-shrink: 0;
  }

  .bot-info {
    flex: 1;
    min-width: 0;

    strong {
      display: block;
      font-size: 15px;
      color: #f1f5f9;
    }

    span {
      font-size: 12px;
      color: #64748b;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .online-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #52c41a;
      display: inline-block;
    }
  }

  .close-btn {
    flex-shrink: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.06);
    color: #94a3b8;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;

    &:hover {
      background: rgba(255, 255, 255, 0.12);
      color: #f1f5f9;
    }
  }
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 240px;
  max-height: 300px;
}

.message-row {
  display: flex;
  gap: 8px;
  align-items: flex-start;

  &.user {
    flex-direction: row-reverse;

    .message-bubble {
      background: var(--gradient-btn);
      color: #fff;
      border-radius: 14px 14px 4px 14px;
    }
  }

  &.bot .message-bubble {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #94a3b8;
    border-radius: 4px 14px 14px 14px;
  }
}

.msg-avatar {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(22, 119, 255, 0.2);
  color: #60a5fa;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-bubble {
  max-width: 82%;
  padding: 10px 14px;
  font-size: 13px;
  line-height: 1.65;

  :deep(b) { color: #60a5fa; font-weight: 600; }

  &.typing {
    display: flex;
    gap: 4px;
    padding: 14px 18px;

    span {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--text-muted);
      animation: blink 1.2s infinite;

      &:nth-child(2) { animation-delay: 0.2s; }
      &:nth-child(3) { animation-delay: 0.4s; }
    }
  }
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 0 16px 12px;
}

.quick-btn {
  padding: 5px 12px;
  border-radius: 20px;
  border: 1px solid rgba(96, 165, 250, 0.3);
  background: rgba(22, 119, 255, 0.12);
  color: #60a5fa;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(22, 119, 255, 0.22);
    border-color: rgba(96, 165, 250, 0.5);
  }
}

.chat-input {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);

  :deep(.el-textarea__inner) {
    min-height: 132px;
    padding: 10px 12px;
    line-height: 1.6;
    background: rgba(255, 255, 255, 0.04);
    border-color: rgba(255, 255, 255, 0.1);
    color: #e2e8f0;

    &::placeholder {
      color: #64748b;
    }
  }
}

.chat-panel-enter-active,
.chat-panel-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.chat-panel-enter-from,
.chat-panel-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.95);
}

@keyframes blink {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}
</style>
