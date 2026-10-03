<template>
  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- CÀN KHÔN LINH THẠCH CÁC v3.0 — GIAO DIỆN TU TIÊN     -->
  <!-- ═══════════════════════════════════════════════════════ -->

  <div class="finance-app-root" :class="{ 'modern-mode': currentTheme === 'modern' }">
    <!-- PERSISTENT XIANXIA CELESTIAL BACKDROP -->
    <XianxiaBackdrop />

    <!-- LOGIN SCREEN -->
    <LoginView v-if="!isLoggedIn" />

    <!-- MAIN APP -->
    <div v-else class="app-realm">
      <!-- HEADER -->
      <header class="realm-header">
        <div class="header-inner">
          <!-- REQUIREMENT 4: Click Title -> Switch to Dashboard -->
          <div class="header-left clickable-brand" @click="switchTab('dashboard')" title="Trở về Đạo Đường Tổng Quan">
            <span class="header-symbol">☯</span>
            <h1 class="header-title">Càn Khôn Linh Thạch Các</h1>
            <span class="version-badge">v3.0</span>
          </div>
          <div class="header-right">
            <!-- REQUIREMENT: Theme Switch Button -->
            <button id="btn-toggle-theme" class="theme-btn" @click="switchTheme" :title="currentTheme === 'modern' ? 'Chuyển sang Đạo Quán Tu Tiên' : 'Chuyển sang Giao Diện Hiện Đại'">
              {{ currentTheme === 'modern' ? '☀️ Giao Diện Sáng' : '🌙 Giao Diện Tối' }}
            </button>
            <!-- REQUIREMENT 5 & 6: User Badge click -> Open Account Management -->
            <button class="user-badge-btn" @click="openProfileModal" title="Quản Lý Đạo Tâm (Tài Khoản)">
              🧙 {{ userName }}
            </button>
            <button class="btn-logout" @click="doLogout">🚪 Hạ Sơn</button>
          </div>
        </div>
      </header>

      <!-- TAB NAVIGATION -->
      <nav class="tab-nav" :class="{ 'has-overflow-left': canScrollNavLeft, 'has-overflow-right': canScrollNavRight }">
        <div class="tab-nav-wrapper">
          <!-- Left Scroll Arrow -->
          <button v-show="canScrollNavLeft" class="tab-scroll-btn left" @click="scrollNav('left')" title="Cuộn sang trái" aria-label="Cuộn sang trái">
            ◀
          </button>

          <!-- Inner Nav Tabs Container -->
          <div ref="tabNavEl" class="tab-nav-inner" @scroll="checkNavScroll" @wheel.passive="handleNavWheel">
            <button v-for="tab in displayTabs" :key="tab.id"
                    :class="['tab-btn', { active: activeTab === tab.id, 'admin-tab-btn': tab.adminOnly }]"
                    @click="switchTab(tab.id)">
              <span class="tab-icon">{{ tab.icon }}</span>
              <span class="tab-label">{{ tab.label }}</span>
            </button>
          </div>

          <!-- Right Scroll Arrow -->
          <button v-show="canScrollNavRight" class="tab-scroll-btn right" @click="scrollNav('right')" title="Cuộn sang phải" aria-label="Cuộn sang phải">
            ▶
          </button>
        </div>
      </nav>

      <!-- CONTENT AREA: mỗi tab là một route (src/router.js) -->
      <main class="realm-content">
        <router-view />
      </main>

      <!-- Modal của từng tab được teleport vào đây: phải nằm ngoài main.realm-content (có z-index riêng) -->
      <div id="modal-root"></div>

      <!-- REQUIREMENT 5: ACCOUNT MANAGEMENT MODAL -->
      <div v-if="showProfileModal" class="modal-backdrop" @click.self="showProfileModal = false">
        <div class="modal-card modal-card-wide" style="max-width: 520px;">
          <div class="modal-header">
            <h3 class="modal-title">🧘 Quản Lý Đạo Tâm (Tài Khoản)</h3>
            <button class="modal-close" @click="showProfileModal = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="profile-section">
              <h4 class="sub-title-sm" style="font-size: 1rem; color: #48bb78; margin-bottom: 12px;">👤 Thông Tin Cá Nhân</h4>
              <div class="input-group-xianxia">
                <label>📧 Linh Bưu (Email)</label>
                <input :value="userEmail" type="email" disabled class="disabled-input" />
              </div>
              <div class="input-group-xianxia">
                <label>👤 Đạo Hiệu Hiển Thị</label>
                <input v-model="profileForm.full_name" type="text" placeholder="Nhập đạo hiệu mới..." @keyup.enter="saveProfile" />
              </div>
              <button class="btn-jade-sm" @click="saveProfile" :disabled="loadingProfile" style="margin-top: 8px;">
                {{ loadingProfile ? '⏳ Đang lưu...' : '✨ Lưu Đạo Hiệu' }}
              </button>
            </div>

            <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.12); margin: 20px 0;" />

            <div class="profile-section">
              <h4 class="sub-title-sm" style="font-size: 1rem; color: #ecc94b; margin-bottom: 6px;">🪔 Bản Mệnh Hồn Đăng (Xác Thực Khôi Phục Mật Khẩu)</h4>
              <p class="hint-text-small" style="font-size: 0.8rem; opacity: 0.75; margin-bottom: 12px; line-height: 1.3;">
                Đặt lại hoặc đổi giá trị bí mật dùng để xác thực danh tính khi quên mật khẩu. Yêu cầu nhập mật khẩu hiện tại để bảo mật.
              </p>
              <div class="input-group-xianxia">
                <label>🔑 Khẩu Quyết (Mật khẩu) Hiện Tại</label>
                <input v-model="soulLampForm.current_password" type="password" placeholder="••••••" />
              </div>
              <div class="input-group-xianxia">
                <label>🪔 Bản Mệnh Hồn Đăng Mới</label>
                <input v-model="soulLampForm.new_soul_lamp" type="text" placeholder="Nhập giá trị bí mật mới (tối thiểu 3 ký tự)..." @keyup.enter="saveSoulLamp" />
              </div>
              <button class="btn-jade-sm" @click="saveSoulLamp" :disabled="loadingSoulLamp || !soulLampForm.current_password || !soulLampForm.new_soul_lamp" style="margin-top: 8px; background: linear-gradient(135deg, #d69e2e, #b7791f);">
                {{ loadingSoulLamp ? '⏳ Đang lưu...' : '⚡ Cập Nhật Bản Mệnh Hồn Đăng' }}
              </button>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="showProfileModal = false">Đóng</button>
          </div>
        </div>
      </div>
    </div>

    <!-- TOAST (nằm ngoài app-realm để màn hình đăng nhập cũng hiển thị được) -->
    <div v-if="toast" class="toast-notification" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script>
import { computed, nextTick, onBeforeUnmount, onErrorCaptured, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import XianxiaBackdrop from './components/XianxiaBackdrop.vue'
import LoginView from './views/LoginView.vue'
import { useAppBindings } from './composables/useAppBindings'
import { useAppStore } from './stores/app'

export default {
  name: 'CankKhonApp',
  components: { XianxiaBackdrop, LoginView },
  setup() {
    const store = useAppStore()
    const route = useRoute()
    const activeTab = computed(() => route.name || 'dashboard')

    // ─── TAB NAVIGATION & SCROLL ─
    const tabNavEl = ref(null)
    const canScrollNavLeft = ref(false)
    const canScrollNavRight = ref(false)

    function checkNavScroll() {
      const el = tabNavEl.value
      if (!el) return
      canScrollNavLeft.value = el.scrollLeft > 6
      canScrollNavRight.value = el.scrollLeft + el.clientWidth < el.scrollWidth - 6
    }

    function scrollNav(direction) {
      const el = tabNavEl.value
      if (!el) return
      const scrollAmount = direction === 'left' ? -250 : 250
      el.scrollBy({ left: scrollAmount, behavior: 'smooth' })
      setTimeout(checkNavScroll, 350)
    }

    function handleNavWheel(e) {
      const el = tabNavEl.value
      if (!el) return
      if (el.scrollWidth > el.clientWidth && Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
        el.scrollLeft += e.deltaY
        checkNavScroll()
      }
    }

    // Đổi tab → cuộn nút tab đang chọn vào tầm nhìn (thanh tab cuộn ngang trên màn hình hẹp)
    watch(activeTab, () => nextTick(() => {
      const activeBtn = tabNavEl.value?.querySelector('.tab-btn.active')
      if (activeBtn) {
        activeBtn.scrollIntoView({ behavior: 'smooth', inline: 'nearest', block: 'nearest' })
      }
      checkNavScroll()
    }))
    // Thanh tab chỉ render sau khi đăng nhập → tính lại mũi tên cuộn
    watch(() => store.isLoggedIn, () => nextTick(checkNavScroll))

    // ─── INIT ─────────────────────
    onMounted(() => {
      document.body.setAttribute('data-theme', store.currentTheme)
      store.restoreSession()
      nextTick(checkNavScroll)
      window.addEventListener('resize', checkNavScroll)
    })
    onBeforeUnmount(() => window.removeEventListener('resize', checkNavScroll))

    onErrorCaptured((err, instance, info) => {
      console.error('Captured Vue Render Error:', err, info)
      store.showToast('Có lỗi xảy ra khi hiển thị thành phần giao diện!', 'error')
      return false
    })

    return {
      ...useAppBindings(),
      activeTab, tabNavEl, canScrollNavLeft, canScrollNavRight, checkNavScroll, scrollNav, handleNavWheel,
    }
  }
}
</script>
