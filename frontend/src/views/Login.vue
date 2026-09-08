<template>
  <AuthLayout subtitle="欢迎回来，登录后即可使用全部功能">
    <div class="auth-form">
      <div class="form-header">
        <div class="mobile-brand" @click="goHome">
          <el-icon :size="20"><DataAnalysis /></el-icon>
        </div>
        <h2>账号登录</h2>
        <p>还没有账号？<router-link to="/register">立即注册</router-link></p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" size="large" class="auth-form-el" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" clearable class="dark-input" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            show-password
            clearable
            class="dark-input"
          />
        </el-form-item>
        <el-form-item>
          <el-button class="btn-pill btn-login submit-btn" round :loading="loading" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="demo-tip">
        <span>演示账号：admin / admin123</span>
      </div>

      <div class="form-footer">
        <el-button text @click="goHome">返回首页</el-button>
      </div>
    </div>
  </AuthLayout>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AuthLayout from '@/layouts/AuthLayout.vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为 3-20 位', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.login({ ...form })
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/'
    router.replace(String(redirect))
  } catch {
    // 错误提示由 axios 拦截器处理
  } finally {
    loading.value = false
  }
}

function goHome() {
  router.push('/')
}
</script>

<style scoped lang="scss">
.auth-form {
  width: 100%;
}

.form-header {
  margin-bottom: 28px;

  .mobile-brand {
    display: none;
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: var(--gradient-brand);
    align-items: center;
    justify-content: center;
    color: #fff;
    margin-bottom: 14px;
    cursor: pointer;

    @media (max-width: 900px) {
      display: inline-flex;
    }
  }

  h2 {
    font-size: 26px;
    font-weight: 800;
    color: var(--text-primary);
    margin-bottom: 8px;
  }

  p {
    color: var(--text-secondary);
    font-size: 14px;

    a {
      color: var(--color-violet);
      text-decoration: none;
      margin-left: 4px;

      &:hover { text-decoration: underline; }
    }
  }
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 600;
}

.demo-tip {
  margin-top: 4px;
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: rgba(22, 119, 255, 0.06);
  border: 1px dashed rgba(22, 119, 255, 0.25);
}

.form-footer {
  margin-top: 20px;
  text-align: center;

  :deep(.el-button.is-text) {
    color: var(--text-secondary) !important;

    &:hover,
    &:focus {
      color: var(--color-violet) !important;
      background-color: rgba(22, 119, 255, 0.08) !important;
    }
  }
}
</style>
