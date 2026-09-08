<template>
  <AuthLayout subtitle="创建账号，开启招聘数据分析之旅">
    <div class="auth-form">
      <div class="form-header">
        <div class="mobile-brand" @click="goHome">
          <el-icon :size="20"><DataAnalysis /></el-icon>
        </div>
        <h2>注册账号</h2>
        <p>已有账号？<router-link to="/login">去登录</router-link></p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" size="large" class="auth-form-el" @keyup.enter="handleRegister">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名（3-20位字母数字下划线）" prefix-icon="User" clearable class="dark-input" />
        </el-form-item>
        <el-form-item prop="nickname">
          <el-input v-model="form.nickname" placeholder="昵称（可选）" prefix-icon="Avatar" clearable class="dark-input" />
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱（可选）" prefix-icon="Message" clearable class="dark-input" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码（至少6位）"
            prefix-icon="Lock"
            show-password
            clearable
            class="dark-input"
          />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认密码"
            prefix-icon="Lock"
            show-password
            clearable
            class="dark-input"
          />
        </el-form-item>
        <el-form-item>
          <el-button class="btn-pill btn-register submit-btn" round :loading="loading" @click="handleRegister">
            注 册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="form-footer">
        <el-button text @click="goHome">返回首页</el-button>
      </div>
    </div>
  </AuthLayout>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AuthLayout from '@/layouts/AuthLayout.vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  nickname: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const validateConfirm = (_rule, value, callback) => {
  if (!value) callback(new Error('请再次输入密码'))
  else if (value !== form.password) callback(new Error('两次输入的密码不一致'))
  else callback()
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]{3,20}$/, message: '用户名需为 3-20 位字母、数字或下划线', trigger: 'blur' },
  ],
  email: [
    {
      validator: (_rule, value, callback) => {
        if (!value || /^[\w.-]+@[\w.-]+\.\w+$/.test(value)) callback()
        else callback(new Error('邮箱格式不正确'))
      },
      trigger: 'blur',
    },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, validator: validateConfirm, trigger: 'blur' },
  ],
}

async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.register({
      username: form.username,
      password: form.password,
      email: form.email || undefined,
      nickname: form.nickname || undefined,
    })
    ElMessage.success('注册成功')
    userStore.logout()
    router.replace('/login')
  } catch {
    // 错误提示由 axios 拦截器处理
  } finally {
    loading.value = false
  }
}

function goHome() {
  router.push('/login')
}
</script>

<style scoped lang="scss">
.auth-form {
  width: 100%;
}

.form-header {
  margin-bottom: 24px;

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

.form-footer {
  margin-top: 16px;
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
