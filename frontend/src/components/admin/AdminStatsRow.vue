<template>
  <section class="admin-stats-grid">
    <!-- Card 1: Total Users -->
    <div class="stat-card">
      <div class="glow-orb primary" aria-hidden="true"></div>
      <div class="stat-header">
        <span class="stat-label">Tổng Số Đạo Hữu</span>
        <div class="stat-icon-wrap primary">
          <span class="material-symbols-outlined text-[18px]" aria-hidden="true">group</span>
        </div>
      </div>
      <div class="stat-main">
        <span class="stat-value font-mono">{{ totalUsersFormatted }}</span>
        <span class="stat-unit">Tài Khoản</span>
      </div>
      <div class="stat-footer">
        <span class="footer-tag-green">Toàn bộ tông môn</span>
        <span class="footer-sub">Hệ thống Càn Khôn Các</span>
      </div>
    </div>

    <!-- Card 2: Active Users -->
    <div class="stat-card">
      <div class="glow-orb jade" aria-hidden="true"></div>
      <div class="stat-header">
        <span class="stat-label">Đang Hoạt Động</span>
        <div class="stat-icon-wrap jade">
          <span class="material-symbols-outlined text-[18px]" aria-hidden="true">bolt</span>
        </div>
      </div>
      <div class="stat-main">
        <span class="stat-value jade font-mono">{{ activeUsersFormatted }}</span>
        <span class="stat-unit jade">Tu Sĩ</span>
      </div>
      <div class="progress-footer">
        <div class="progress-track" role="progressbar" :aria-valuenow="activeRate" aria-valuemin="0" aria-valuemax="100">
          <div class="progress-bar" :style="{ width: activeRate + '%' }"></div>
        </div>
        <span class="progress-percent font-mono">{{ activeRate }}%</span>
      </div>
    </div>

    <!-- Card 3: Locked Users -->
    <div class="stat-card">
      <div class="glow-orb error" aria-hidden="true"></div>
      <div class="stat-header">
        <span class="stat-label">Đang Bị Phong Ấn / Khóa</span>
        <div class="stat-icon-wrap error">
          <span class="material-symbols-outlined text-[18px]" aria-hidden="true">lock_reset</span>
        </div>
      </div>
      <div class="stat-main">
        <span class="stat-value error font-mono">{{ lockedUsersFormatted }}</span>
        <span class="stat-unit error">Tài Khoản</span>
      </div>
      <div class="stat-footer error">
        <span class="material-symbols-outlined text-[14px]" aria-hidden="true">gavel</span>
        <span>Vi phạm giới luật tông môn</span>
      </div>
    </div>
  </section>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'AdminStatsRow',
  props: {
    adminStats: {
      type: Object,
      default: () => ({ total_users: 0, active_users: 0, locked_users: 0 })
    }
  },
  setup(props) {
    const totalUsers = computed(() => props.adminStats?.total_users || 0)
    const activeUsers = computed(() => props.adminStats?.active_users || 0)
    const lockedUsers = computed(() => props.adminStats?.locked_users || 0)

    const totalUsersFormatted = computed(() => {
      return new Intl.NumberFormat('vi-VN').format(totalUsers.value)
    })

    const activeUsersFormatted = computed(() => {
      return new Intl.NumberFormat('vi-VN').format(activeUsers.value)
    })

    const lockedUsersFormatted = computed(() => {
      return new Intl.NumberFormat('vi-VN').format(lockedUsers.value)
    })

    const activeRate = computed(() => {
      if (totalUsers.value <= 0) return 100
      const rate = (activeUsers.value / totalUsers.value) * 100
      return Math.round(rate * 10) / 10
    })

    return {
      totalUsersFormatted,
      activeUsersFormatted,
      lockedUsersFormatted,
      activeRate
    }
  }
}
</script>

<style scoped>
.admin-stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-md, 1rem);
}

@media (min-width: 768px) {
  .admin-stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.stat-card {
  position: relative;
  border-radius: var(--radius-lg, 1rem);
  padding: var(--space-lg, 1.5rem);
  background: rgba(19, 27, 46, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: var(--space-sm, 0.5rem);
  overflow: hidden;
  transition: all 0.2s ease;
}

.stat-card:hover {
  background: rgba(23, 31, 51, 0.95);
  border-color: rgba(125, 214, 204, 0.25);
  transform: translateY(-1px);
}

.glow-orb {
  position: absolute;
  right: -1.5rem;
  bottom: -1.5rem;
  width: 6rem;
  height: 6rem;
  border-radius: 9999px;
  filter: blur(24px);
  pointer-events: none;
}

.glow-orb.primary {
  background: rgba(125, 214, 204, 0.08);
}

.glow-orb.jade {
  background: rgba(68, 159, 150, 0.15);
}

.glow-orb.error {
  background: rgba(239, 68, 68, 0.08);
}

.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-xs, 0.25rem);
}

.stat-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.stat-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md, 0.75rem);
  background: rgba(34, 42, 61, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon-wrap.primary {
  color: var(--color-primary, #7dd6cc);
}

.stat-icon-wrap.jade {
  color: #9af2e8;
}

.stat-icon-wrap.error {
  color: var(--color-error, #ffb4ab);
}

.stat-main {
  display: flex;
  align-items: baseline;
  gap: var(--space-xs, 0.25rem);
}

.stat-value {
  font-size: 2rem;
  font-weight: 600;
  line-height: 2.25rem;
  color: var(--color-on-surface, #dae2fd);
}

.stat-value.jade {
  color: var(--color-primary, #7dd6cc);
}

.stat-value.error {
  color: var(--color-error, #ffb4ab);
}

.stat-unit {
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.stat-unit.jade {
  color: #9af2e8;
}

.stat-unit.error {
  color: rgba(255, 180, 171, 0.8);
}

.stat-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin-top: var(--space-xs, 0.25rem);
}

.footer-tag-green {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-primary, #7dd6cc);
}

.footer-sub {
  font-size: 11px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.stat-footer.error {
  color: rgba(255, 180, 171, 0.85);
}

/* Progress Footer for Active Users */
.progress-footer {
  display: flex;
  align-items: center;
  gap: var(--space-sm, 0.5rem);
  margin-top: var(--space-xs, 0.25rem);
}

.progress-track {
  flex: 1;
  background: rgba(34, 42, 61, 0.8);
  border-radius: 9999px;
  height: 6px;
  overflow: hidden;
}

.progress-bar {
  background: var(--color-primary, #7dd6cc);
  height: 6px;
  border-radius: 9999px;
  transition: width 0.4s ease;
}

.progress-percent {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
  white-space: nowrap;
}
</style>
