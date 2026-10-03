<template>
  <div class="login-realm">
    <div class="login-card">
      <div class="login-header">
        <div class="login-theme-toggle">
          <button id="btn-toggle-theme-login" class="theme-btn" @click="switchTheme" :title="currentTheme === 'modern' ? 'Chuyển sang Đạo Quán Tu Tiên' : 'Chuyển sang Giao Diện Hiện Đại'">
            {{ currentTheme === 'modern' ? '☀️ Giao Diện Sáng' : '🌙 Giao Diện Tối' }}
          </button>
        </div>
        <div class="dao-symbol">☯</div>
        <h1 class="title-calligraphy">Càn Khôn Linh Thạch Các</h1>
        <p class="subtitle-glow">Quản Lý Chi Tiêu AI — Phong Cách Tu Tiên</p>
      </div>

      <!-- Mode: Đăng Nhập -->
      <div v-if="authMode === 'login'" class="auth-form">
        <h2 class="form-title">🔮 Xác Thực Đạo Tâm</h2>
      <div class="input-group-xianxia">
        <label>📧 Linh Bưu (Email)</label>
        <input v-model="authForm.email" type="email" placeholder="dao.huu@tongmon.com" @keyup.enter="doLogin" />
      </div>
      <div class="input-group-xianxia">
        <label>🔑 Khẩu Quyết (Mật khẩu)</label>
        <input v-model="authForm.password" type="password" placeholder="••••••" @keyup.enter="doLogin" />
      </div>
      <button class="btn-jade" @click="doLogin" :disabled="loading">
        {{ loading ? '⏳ Đang xác thực...' : '⚡ Khai Mở Thần Thức' }}
      </button>
      <div class="auth-links">
        <p class="auth-switch" @click="authMode = 'register'">Chưa có Đạo Tâm? <span>Đăng ký</span></p>
        <p class="auth-switch" @click="openForgotPassword">Quên khẩu quyết? <span>Khôi phục</span></p>
      </div>
    </div>

    <!-- Mode: Đăng Ký -->
    <div v-else-if="authMode === 'register'" class="auth-form">
      <h2 class="form-title">✨ Khai Mở Đạo Tâm Mới</h2>
      <div class="input-group-xianxia">
        <label>👤 Đạo Hiệu (Họ tên)</label>
        <input v-model="authForm.full_name" type="text" placeholder="Ký Chủ" />
      </div>
      <div class="input-group-xianxia">
        <label>📧 Linh Bưu (Email)</label>
        <input v-model="authForm.email" type="email" placeholder="dao.huu@tongmon.com" />
      </div>
      <div class="input-group-xianxia">
        <label>🔑 Khẩu Quyết (Mật khẩu)</label>
        <input v-model="authForm.password" type="password" placeholder="Tối thiểu 6 ký tự..." />
      </div>
      <div class="input-group-xianxia">
        <label>🪔 Bản Mệnh Hồn Đăng (Bí mật bảo mật)</label>
        <input v-model="authForm.soul_lamp" type="text" placeholder="VD: Tên con vật đầu tiên, người thân..." />
        <p class="hint-text-small" style="font-size: 0.78rem; opacity: 0.8; margin-top: 4px; line-height: 1.3;">
          Đây là câu trả lời bí mật chỉ mình bạn biết, dùng để khôi phục tài khoản khi quên mật khẩu — hãy chọn thứ dễ nhớ nhưng khó đoán.
        </p>
      </div>
      <button class="btn-jade" @click="doRegister" :disabled="loading">
        {{ loading ? '⏳ Đang khai mở...' : '🌟 Nhập Môn Tông Phái' }}
      </button>
      <p class="auth-switch" @click="authMode = 'login'">Đã có Đạo Tâm? <span>Đăng nhập</span></p>
    </div>

    <!-- Mode: Quên Mật Khẩu -->
    <div v-else-if="authMode === 'forgot'" class="auth-form">
      <h2 class="form-title">🔑 Khôi Phục Khẩu Quyết</h2>
      <p class="hint-text" style="margin-bottom: 14px;">Nhập Email và Bản Mệnh Hồn Đăng để nhận mã xác thực đặt lại mật khẩu</p>
      <div class="input-group-xianxia">
        <label>📧 Linh Bưu (Email)</label>
        <input v-model="forgotForm.email" type="email" placeholder="dao.huu@tongmon.com" @keyup.enter="doForgotPassword" />
      </div>
      <div class="input-group-xianxia">
        <label>🪔 Bản Mệnh Hồn Đăng</label>
        <input v-model="forgotForm.soul_lamp" type="text" placeholder="Nhập câu trả lời bí mật..." @keyup.enter="doForgotPassword" />
      </div>
      <button class="btn-jade" @click="doForgotPassword" :disabled="loading || !forgotForm.email || !forgotForm.soul_lamp">
        {{ loading ? '⏳ Đang truyền tin...' : '📩 Gửi Mã Khôi Phục' }}
      </button>
      <p class="auth-switch" @click="authMode = 'login'">Trở về <span>Đăng nhập</span></p>
    </div>

    <!-- Mode: Đặt Lại Mật Khẩu -->
    <div v-else-if="authMode === 'reset'" class="auth-form">
      <h2 class="form-title">🔄 Đặt Khẩu Quyết Mới</h2>
      <div v-if="devResetToken" class="dev-token-notice">
        <span>⚡ Mã xác thực: <strong>{{ devResetToken }}</strong></span>
      </div>
      <p v-else class="hint-text" style="margin-bottom: 14px;">📧 Mã xác thực đã được gửi tới email của bạn. Kiểm tra cả thư mục Spam.</p>
      <div class="input-group-xianxia">
        <label>📧 Linh Bưu (Email)</label>
        <input v-model="resetForm.email" type="email" disabled class="disabled-input" />
      </div>
      <div class="input-group-xianxia">
        <label>🎫 Mã Xác Thực (OTP Token)</label>
        <input v-model="resetForm.token" type="text" placeholder="Nhập mã 8 ký tự..." />
      </div>
      <div class="input-group-xianxia">
        <label>🔑 Khẩu Quyết Mới</label>
        <input v-model="resetForm.new_password" type="password" placeholder="Tối thiểu 6 ký tự..." @keyup.enter="doResetPassword" />
      </div>
      <button class="btn-jade" @click="doResetPassword" :disabled="loading || !resetForm.token || !resetForm.new_password">
        {{ loading ? '⏳ Đang đổi...' : '✨ Đổi Khẩu Quyết Mới' }}
      </button>
      <p class="auth-switch" @click="authMode = 'login'">Trở về <span>Đăng nhập</span></p>
    </div>
    <div v-if="errorMsg" class="error-banner">🔥 {{ errorMsg }}</div>
  </div>
  </div>
</template>

<script>
import { useAppBindings } from '../composables/useAppBindings'

export default {
  name: 'LoginView',
  setup() {
    return useAppBindings()
  },
}
</script>
