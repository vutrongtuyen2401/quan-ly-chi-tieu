<template>
  <header class="realm-header-stitch">
    <div class="header-container">
      <!-- ─── TOP LEVEL: BRAND, REALM STATUS, USER PROFILE, ACTIONS ─── -->
      <div class="header-top-bar">
        <!-- Brand & Logo -->
        <div class="brand-group" @click="handleBrandClick" title="Trở về Tổng Quan">
          <div class="brand-emblem-wrap">
            <span class="brand-yin-yang">☯</span>
          </div>
          <div class="brand-text-col">
            <div class="brand-title-row">
              <span class="brand-title">Càn Khôn Linh Thạch Các</span>
              <span class="brand-badge">v3.0</span>
            </div>
            <span class="brand-subtitle">Quản Lý Tài Chính & Tu Luyện Thạch</span>
          </div>
        </div>

        <!-- Telemetry & User Controls -->
        <div class="header-actions">
          <!-- Realm Cultivation Status Pill (Desktop only) -->
          <div class="realm-status-pill hidden-mobile">
            <span class="status-beacon pulse"></span>
            <span class="realm-status-text">Linh Thạch Khả Dụng • Khí Vận Hanh Thông</span>
          </div>

          <!-- Theme Toggle Button -->
          <button
            id="btn-toggle-theme"
            class="header-action-btn theme-btn"
            @click="$emit('switch-theme')"
            :title="currentTheme === 'modern' ? 'Chuyển sang Đạo Quán Tu Tiên' : 'Chuyển sang Giao Diện Hiện Đại'"
            aria-label="Đổi giao diện"
          >
            <span class="action-btn-icon">{{ currentTheme === 'modern' ? '☀️' : '🌙' }}</span>
            <span class="hidden-mobile">{{ currentTheme === 'modern' ? 'Sáng' : 'Tối' }}</span>
          </button>

          <!-- User Identity Pill & Modal Trigger -->
          <div class="user-profile-entry" @click="$emit('open-profile')" title="Quản Lý Hồ Sơ Đạo Tâm">
            <div class="user-meta hidden-mobile">
              <span class="user-display-name">{{ userName }}</span>
              <span class="user-role-label">{{ isUserAdmin ? 'Trưởng Lão Tông Môn' : 'Động Chủ Tu Sĩ' }}</span>
            </div>
            <div class="user-avatar-orb" :class="{ 'admin-orb': isUserAdmin }">
              <span class="avatar-glyph">{{ isUserAdmin ? '🛡️' : '🧙' }}</span>
            </div>
          </div>

          <!-- Logout Button -->
          <button
            id="btn-logout"
            class="header-action-btn logout-btn"
            @click="$emit('logout')"
            title="Đăng xuất khỏi Càn Khôn Các"
            aria-label="Hạ Sơn (Đăng xuất)"
          >
            <span class="action-btn-icon">🚪</span>
            <span class="hidden-mobile">Hạ Sơn</span>
          </button>
        </div>
      </div>

      <!-- ─── BOTTOM LEVEL: RESPONSIVE HORIZONTAL TAB NAVIGATION ─── -->
      <nav class="stitch-tab-navigation" aria-label="Điều hướng các phân khu tài chính">
        <!-- Scroll left indicator button if overflow -->
        <button
          v-if="hasScrollLeft"
          class="nav-scroll-arrow left"
          @click="scrollDirection('left')"
          aria-label="Cuộn sang trái"
        >
          ◀
        </button>

        <div
          ref="tabNavContainer"
          class="nav-tabs-scrollable"
          @scroll="onContainerScroll"
        >
          <button
            v-for="tab in visibleTabs"
            :key="tab.id"
            :id="'tab-nav-' + tab.id"
            :class="[
              'stitch-nav-item',
              {
                'active': activeTab === tab.id,
                'admin-tab': tab.adminOnly
              }
            ]"
            @click="handleTabClick(tab.id)"
            :aria-current="activeTab === tab.id ? 'page' : undefined"
          >
            <span class="tab-item-icon">{{ tab.icon }}</span>
            <span class="tab-item-label">{{ tab.label }}</span>
          </button>
        </div>

        <!-- Scroll right indicator button if overflow -->
        <button
          v-if="hasScrollRight"
          class="nav-scroll-arrow right"
          @click="scrollDirection('right')"
          aria-label="Cuộn sang phải"
        >
          ▶
        </button>
      </nav>
    </div>
  </header>
</template>

<script>
import { computed, ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'

export default {
  name: 'AppHeader',
  props: {
    activeTab: {
      type: String,
      required: true
    },
    tabs: {
      type: Array,
      default: () => []
    },
    userName: {
      type: String,
      default: 'Ký Chủ'
    },
    userRole: {
      type: String,
      default: 'user'
    },
    isUserAdmin: {
      type: Boolean,
      default: false
    },
    currentTheme: {
      type: String,
      default: 'xianxia'
    },
    canScrollNavLeft: {
      type: Boolean,
      default: false
    },
    canScrollNavRight: {
      type: Boolean,
      default: false
    }
  },
  emits: ['switch-tab', 'open-profile', 'switch-theme', 'logout', 'scroll-nav'],
  setup(props, { emit }) {
    const tabNavContainer = ref(null)
    const localScrollLeft = ref(false)
    const localScrollRight = ref(false)

    // Filter tabs based on admin authorization strictly
    const visibleTabs = computed(() => {
      return props.tabs.filter(tab => !tab.adminOnly || props.isUserAdmin)
    })

    const hasScrollLeft = computed(() => props.canScrollNavLeft || localScrollLeft.value)
    const hasScrollRight = computed(() => props.canScrollNavRight || localScrollRight.value)

    function checkInternalScroll() {
      const el = tabNavContainer.value
      if (!el) return
      localScrollLeft.value = el.scrollLeft > 4
      localScrollRight.value = el.scrollLeft < (el.scrollWidth - el.clientWidth - 4)
    }

    function onContainerScroll() {
      checkInternalScroll()
    }

    function scrollDirection(direction) {
      const el = tabNavContainer.value
      if (el) {
        const offset = direction === 'left' ? -220 : 220
        el.scrollBy({ left: offset, behavior: 'smooth' })
        setTimeout(checkInternalScroll, 300)
      }
      emit('scroll-nav', direction)
    }

    function handleTabClick(tabId) {
      emit('switch-tab', tabId)
    }

    function handleBrandClick() {
      emit('switch-tab', 'dashboard')
    }

    watch(() => props.activeTab, () => {
      nextTick(() => {
        const activeBtn = tabNavContainer.value?.querySelector('.stitch-nav-item.active')
        if (activeBtn) {
          activeBtn.scrollIntoView({ behavior: 'smooth', inline: 'nearest', block: 'nearest' })
        }
        checkInternalScroll()
      })
    })

    onMounted(() => {
      nextTick(() => {
        checkInternalScroll()
      })
      window.addEventListener('resize', checkInternalScroll)
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', checkInternalScroll)
    })

    return {
      tabNavContainer,
      visibleTabs,
      hasScrollLeft,
      hasScrollRight,
      handleBrandClick,
      handleTabClick,
      scrollDirection,
      onContainerScroll
    }
  }
}
</script>

<style scoped>
.realm-header-stitch {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(11, 19, 38, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.45);
}

.header-container {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: var(--space-xs) var(--gutter) 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  box-sizing: border-box;
}

/* ─── TOP BAR ─── */
.header-top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  padding: 4px 0;
}

/* Brand */
.brand-group {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  cursor: pointer;
  user-select: none;
  transition: opacity var(--transition-fast);
}

.brand-group:hover {
  opacity: 0.9;
}

.brand-emblem-wrap {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: rgba(43, 138, 130, 0.2);
  border: 1px solid rgba(125, 214, 204, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 12px rgba(125, 214, 204, 0.25);
  flex-shrink: 0;
}

.brand-yin-yang {
  font-size: 20px;
  color: var(--color-primary);
  text-shadow: 0 0 8px rgba(125, 214, 204, 0.6);
}

.brand-text-col {
  display: flex;
  flex-direction: column;
}

.brand-title-row {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.brand-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-on-surface);
  letter-spacing: -0.01em;
  white-space: nowrap;
}

.brand-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: var(--radius-full);
  background: rgba(125, 214, 204, 0.15);
  color: var(--color-primary);
  border: 1px solid rgba(125, 214, 204, 0.25);
}

.brand-subtitle {
  font-size: 11px;
  color: var(--color-on-surface-variant);
  white-space: nowrap;
}

/* Actions */
.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-shrink: 0;
}

.realm-status-pill {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: 4px 12px;
  border-radius: var(--radius-full);
  background: var(--color-surface-container-high);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.realm-status-text {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-primary);
  white-space: nowrap;
}

.header-action-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  height: 34px;
  padding: 0 10px;
  border-radius: var(--radius-DEFAULT);
  background: var(--color-surface-container-low);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--color-on-surface-variant);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  user-select: none;
}

.header-action-btn:hover {
  background: var(--color-surface-container-high);
  color: var(--color-on-surface);
  border-color: rgba(255, 255, 255, 0.16);
}

.logout-btn:hover {
  color: var(--color-error);
  border-color: rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.08);
}

.action-btn-icon {
  font-size: 14px;
}

/* User Profile Entry */
.user-profile-entry {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: 3px 6px;
  border-radius: var(--radius-DEFAULT);
  cursor: pointer;
  transition: background var(--transition-fast);
  user-select: none;
}

.user-profile-entry:hover {
  background: rgba(255, 255, 255, 0.05);
}

.user-meta {
  display: flex;
  flex-direction: column;
  text-align: right;
}

.user-display-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-on-surface);
  white-space: nowrap;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role-label {
  font-size: 10px;
  color: var(--color-on-surface-variant);
  white-space: nowrap;
}

.user-avatar-orb {
  width: 34px;
  height: 34px;
  border-radius: var(--radius-full);
  background: var(--color-surface-container-high);
  border: 2px solid var(--color-primary-core);
  box-shadow: 0 0 10px rgba(43, 138, 130, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.user-avatar-orb:hover {
  transform: scale(1.05);
  box-shadow: 0 0 16px rgba(125, 214, 204, 0.55);
}

.user-avatar-orb.admin-orb {
  border-color: var(--color-tertiary-gold);
  box-shadow: 0 0 10px rgba(232, 200, 116, 0.35);
}

.avatar-glyph {
  font-size: 16px;
}

/* ─── BOTTOM LEVEL: TAB NAVIGATION ─── */
.stitch-tab-navigation {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  padding-bottom: 6px;
}

.nav-tabs-scrollable {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding: 2px 0;
  width: 100%;
}

.nav-tabs-scrollable::-webkit-scrollbar {
  display: none;
}

.stitch-nav-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: var(--radius-DEFAULT);
  background: transparent;
  border: 1px solid transparent;
  color: var(--color-on-surface-variant);
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  transition: all var(--transition-normal);
  user-select: none;
}

.stitch-nav-item:hover {
  background: var(--color-surface-container-high);
  color: var(--color-on-surface);
}

/* Active State matches Stitch Design */
.stitch-nav-item.active {
  background: var(--color-primary-container);
  color: var(--color-on-primary-container);
  font-weight: 600;
  box-shadow: 0 0 14px rgba(68, 159, 150, 0.45);
  border-color: rgba(125, 214, 204, 0.3);
}

.stitch-nav-item.admin-tab {
  border-color: rgba(232, 200, 116, 0.2);
}

.stitch-nav-item.admin-tab.active {
  background: var(--color-tertiary-container);
  color: var(--color-on-tertiary-container);
  box-shadow: 0 0 14px rgba(232, 200, 116, 0.35);
}

.tab-item-icon {
  font-size: 15px;
}

.tab-item-label {
  letter-spacing: 0.01em;
}

.nav-scroll-arrow {
  background: var(--color-surface-container);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--color-on-surface);
  border-radius: var(--radius-DEFAULT);
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 10px;
  flex-shrink: 0;
  margin: 0 4px;
}

/* ─── RESPONSIVE BREAKPOINTS ─── */
@media (max-width: 900px) {
  .hidden-mobile {
    display: none !important;
  }
  
  .brand-subtitle {
    display: none;
  }
}

@media (max-width: 600px) {
  .header-container {
    padding: var(--space-xs) var(--space-sm) 0;
  }
  
  .stitch-nav-item {
    padding: 6px 10px;
    font-size: 12px;
  }
}
</style>
