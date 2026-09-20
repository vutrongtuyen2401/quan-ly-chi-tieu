<template>
  <section class="admin-header-section">
    <div class="header-main-col">
      <div class="header-tag-row">
        <span class="material-symbols-outlined header-tag-icon" aria-hidden="true">admin_panel_settings</span>
        <span class="header-tag-text">Khu Vực Quản Trị Tông Môn</span>
      </div>
      <h1 class="header-title">Phân Quyền &amp; Quản Lý Tu Sĩ</h1>
      <p class="header-desc">
        Quản lý trạng thái hoạt động tài khoản và phân quyền chức vụ trong tông môn. Bảo vệ an ninh pháp trận và kết giới dữ liệu.
      </p>
    </div>

    <!-- Security Stamp Indicator -->
    <div class="security-stamp-card">
      <div class="security-stamp-icon-box">
        <span class="material-symbols-outlined text-[24px]" aria-hidden="true">verified_user</span>
      </div>
      <div class="security-stamp-info">
        <span class="stamp-label">Pháp Trận Phong Ấn</span>
        <span class="stamp-grade">Cấp Độ 4 • Bất Khả Xâm Phạm</span>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'AdminHeader'
}
</script>

<style scoped>
.admin-header-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 1rem);
  padding-top: var(--space-sm, 0.5rem);
  padding-bottom: var(--space-xs, 0.25rem);
}

@media (min-width: 1024px) {
  .admin-header-section {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.header-main-col {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs, 0.25rem);
  max-width: 48rem;
}

.header-tag-row {
  display: flex;
  align-items: center;
  gap: var(--space-xs, 0.25rem);
}

.header-tag-icon {
  color: var(--color-primary, #7dd6cc);
  font-size: 20px;
}

.header-tag-text {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-primary, #7dd6cc);
}

.header-title {
  font-size: 1.625rem;
  font-weight: 600;
  line-height: 2rem;
  color: var(--color-on-surface, #dae2fd);
  letter-spacing: -0.015em;
  margin: 0;
}

@media (min-width: 768px) {
  .header-title {
    font-size: 1.875rem;
    line-height: 2.25rem;
  }
}

.header-desc {
  font-size: 0.875rem;
  line-height: 1.35rem;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin: 0;
}

/* Security Stamp Indicator */
.security-stamp-card {
  display: flex;
  align-items: center;
  gap: var(--space-md, 1rem);
  align-self: flex-start;
  padding: var(--space-sm, 0.5rem) var(--space-md, 1rem);
  border-radius: var(--radius-lg, 1rem);
  background: rgba(19, 27, 46, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

@media (min-width: 1024px) {
  .security-stamp-card {
    align-self: center;
  }
}

.security-stamp-icon-box {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md, 0.75rem);
  background: rgba(34, 42, 61, 0.8);
  color: var(--color-tertiary, #e3c370);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.security-stamp-info {
  display: flex;
  flex-direction: column;
}

.stamp-label {
  font-size: 11px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.stamp-grade {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-tertiary, #e3c370);
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
