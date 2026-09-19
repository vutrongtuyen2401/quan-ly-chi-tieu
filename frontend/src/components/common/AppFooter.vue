<template>
  <footer class="realm-footer-stitch">
    <div class="footer-container">
      <div class="footer-left">
        <span class="footer-brand">Càn Khôn Linh Thạch Các</span>
        <span class="footer-sub">• Hệ Thống Quản Lý Tài Chính & Khí Vận Tu Tiên</span>
      </div>
      <div class="footer-right">
        <span class="footer-copyright">© 2024–2025 Càn Khôn Các. Bảo lưu mọi đạo pháp linh thạch.</span>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter'
}
</script>

<style scoped>
.realm-footer-stitch {
  width: 100%;
  background: var(--color-surface-container-lowest);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding: var(--space-lg) var(--gutter);
  margin-top: var(--space-xl);
  box-sizing: border-box;
}

.footer-container {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  flex-wrap: wrap;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  flex-wrap: wrap;
}

.footer-brand {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-on-surface);
}

.footer-sub {
  font-size: 12px;
  color: var(--color-on-surface-variant);
}

.footer-right {
  font-size: 11px;
  color: var(--color-outline);
}

@media (max-width: 768px) {
  .footer-container {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-xs);
  }
}
</style>
