<template>
  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- HỆ THỐNG QUẢN LÝ CHI TIÊU — GIAO DIỆN HIỆN ĐẠI & THÔNG MINH  -->
  <!-- ═══════════════════════════════════════════════════════════ -->

  <div class="finance-app-root" :class="{ 'modern-mode': currentTheme === 'modern' }">
    <!-- VIDEO BACKGROUND -->
    <video
      id="bg-video"
      ref="bgVideo"
      autoplay
      loop
      muted
      playsinline
      :src="videoSource"
      class="global-video-bg"
    ></video>
    <div class="global-video-overlay"></div>

    <!-- AUDIO CONTROL FAB -->
    <button id="audio-fab-btn" class="audio-fab" @click="toggleAudio" :title="isMuted ? 'Bật Âm Thanh' : 'Tắt Âm Thanh'">
      <span v-if="isMuted">🔇</span>
      <span v-else>🎵</span>
    </button>

    <!-- WELCOME TOAST OVERLAY -->
    <div v-if="showWelcomeToast" class="welcome-overlay">
      <div class="welcome-content">
        <h1 class="welcome-text">Hệ Thống Quản Lý Chi Tiêu Xin Chào {{ welcomeName }}</h1>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 1. GIAO DIỆN CHƯA ĐĂNG NHẬP (LANDING PAGE TƯƠNG ĐỒNG DASHBOARD) -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <div v-if="!isLoggedIn" class="app-realm landing-mode">
      <!-- TOP NAVBAR -->
      <header class="realm-header glass-panel">
        <div class="header-inner">
          <div class="header-left clickable-brand" @click="activeTab = 'dashboard'" title="Hệ Thống Quản Lý Chi Tiêu">
            <span class="header-symbol"><i class="fa-solid fa-wallet"></i></span>
            <h1 class="header-title">Hệ Thống Quản Lý Chi Tiêu</h1>
            <span class="version-badge">v4.4 Enterprise</span>
          </div>
          <div class="header-right">
            <button id="btn-toggle-theme" class="theme-btn" @click="switchTheme" :title="currentTheme === 'modern' ? 'Chuyển sang chế độ Tối' : 'Chuyển sang chế độ Sáng'">
              {{ currentTheme === 'modern' ? '☀️ Giao Diện Sáng' : '🌙 Giao Diện Tối' }}
            </button>
            <button id="btn-nav-login" class="btn-auth-login" @click="openAuthModal('login')">
              <i class="fa-solid fa-key"></i> Đăng Nhập
            </button>
            <button id="btn-nav-register" class="btn-auth-register" @click="openAuthModal('register')">
              <i class="fa-solid fa-user-plus"></i> Đăng Ký
            </button>
          </div>
        </div>
      </header>

      <!-- TAB NAVIGATION (SIDEBAR / NAV) -->
      <nav class="tab-nav">
        <div class="tab-nav-inner">
          <button v-for="tab in publicTabs" :key="tab.id"
                  :id="'public-tab-' + tab.id"
                  :class="['tab-btn', { active: activeTab === tab.id }]"
                  @click="switchTab(tab.id)">
            <span class="tab-icon">
              <i v-if="isFontAwesome(tab.icon)" :class="tab.icon"></i>
              <span v-else>{{ tab.icon }}</span>
            </span>
            <span class="tab-label">{{ tab.label }}</span>
          </button>
        </div>
      </nav>

      <!-- MAIN CONTENT -->
      <main class="realm-content">
        <!-- HERO WELCOME PANEL -->
        <section class="landing-welcome-section glass-panel">
          <div class="welcome-badge">NỀN TẢNG QUẢN LÝ TÀI CHÍNH THÔNG MINH TÍCH HỢP GEMINI AI</div>
          <h2 class="landing-title">Quản Lý Thu Chi & Phân Tích Dự Báo Dòng Tiền Tự Động</h2>
          <p class="landing-desc">
            Chào mừng bạn đến với <strong>Hệ Thống Quản Lý Chi Tiêu</strong>. Tự động hóa theo dõi ngân sách, 
            nhận diện hóa đơn thông minh qua công nghệ OCR Vision AI, phân tích thói quen tiêu dùng hàng ngày, 
            cảnh báo chi tiêu hoang phí và dự báo số dư cuối tháng chính xác.
          </p>
          <div class="landing-cta-row">
            <button id="btn-hero-login" class="btn-jade btn-lg" @click="openAuthModal('login')">
              <i class="fa-solid fa-arrow-right-to-bracket"></i> Đăng Nhập Hệ Thống
            </button>
            <button id="btn-hero-register" class="btn-gold btn-lg" @click="openAuthModal('register')">
              <i class="fa-solid fa-sparkles"></i> Tạo Tài Khoản Mới
            </button>
          </div>
        </section>

        <!-- PREVIEW METRICS GRID -->
        <div class="metrics-grid preview-grid">
          <div class="metric-card jade">
            <div class="metric-icon"><i class="fa-solid fa-money-bill-trend-up"></i></div>
            <div class="metric-info">
              <span class="metric-label">Tổng Thu Nhập Tháng</span>
              <span class="metric-value">25,000,000 ₫</span>
            </div>
          </div>
          <div class="metric-card crimson">
            <div class="metric-icon"><i class="fa-solid fa-fire-flame-curved"></i></div>
            <div class="metric-info">
              <span class="metric-label">Tổng Chi Tiêu Tháng</span>
              <span class="metric-value">12,450,000 ₫</span>
            </div>
          </div>
          <div class="metric-card gold">
            <div class="metric-icon"><i class="fa-solid fa-scale-balanced"></i></div>
            <div class="metric-info">
              <span class="metric-label">Tiết Kiệm Tích Lũy</span>
              <span class="metric-value positive">12,550,000 ₫</span>
            </div>
          </div>
          <div class="metric-card purple">
            <div class="metric-icon"><i class="fa-solid fa-vault"></i></div>
            <div class="metric-info">
              <span class="metric-label">Tổng Số Dư Khả Dụng</span>
              <span class="metric-value">45,800,000 ₫</span>
            </div>
          </div>
        </div>

        <!-- HIGHLIGHT FEATURES -->
        <div class="features-grid">
          <div class="feature-card glass-panel" @click="openAuthModal('login')">
            <div class="feature-icon"><i class="fa-solid fa-chart-line"></i></div>
            <h3 class="feature-title">Phân Tích & Dự Báo Thông Minh</h3>
            <p class="feature-text">Tự động tính toán mức chi tiêu trung bình ngày (7 ngày / 30 ngày), phát hiện hành vi chi tiêu bất thường và dự báo thâm hụt cuối tháng.</p>
          </div>
          <div class="feature-card glass-panel" @click="openAuthModal('login')">
            <div class="feature-icon"><i class="fa-solid fa-receipt"></i></div>
            <h3 class="feature-title">Quét Hóa Đơn Tự Động OCR AI</h3>
            <p class="feature-text">Tích hợp AI Gemini Vision nhận diện tức thì hình ảnh hóa đơn, trích xuất chính xác số tiền, thời gian và danh mục tiêu dùng.</p>
          </div>
          <div class="feature-card glass-panel" @click="openAuthModal('login')">
            <div class="feature-icon"><i class="fa-solid fa-robot"></i></div>
            <h3 class="feature-title">Trợ Lý Cố Vấn Tài Chính AI</h3>
            <p class="feature-text">Trợ lý AI phân tích dòng tiền chuyên sâu, đề xuất kế hoạch phân bổ thu chi và lời khuyên tiết kiệm thực tế cho từng cá nhân.</p>
          </div>
        </div>
      </main>
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 2. GIAO DIỆN ĐÃ ĐĂNG NHẬP (AUTHENTICATED DASHBOARD)        -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <div v-else class="app-realm">
      <!-- HEADER -->
      <header class="realm-header glass-panel">
        <div class="header-inner">
          <div class="header-left clickable-brand" @click="switchTab('dashboard')" title="Trở về Tổng Quan">
            <span class="header-symbol"><i class="fa-solid fa-wallet"></i></span>
            <h1 class="header-title">Hệ Thống Quản Lý Chi Tiêu</h1>
            <span class="version-badge">v4.4 Enterprise</span>
          </div>
          <div class="header-right">
            <button id="btn-toggle-theme-auth" class="theme-btn" @click="switchTheme" :title="currentTheme === 'modern' ? 'Chuyển sang chế độ Tối' : 'Chuyển sang chế độ Sáng'">
              {{ currentTheme === 'modern' ? '☀️ Giao Diện Sáng' : '🌙 Giao Diện Tối' }}
            </button>
            <button id="btn-user-profile" class="user-badge-btn" @click="openProfileModal" title="Quản Lý Tài Khoản">
              <i class="fa-solid fa-user-circle"></i> {{ userName }}
            </button>
            <button id="btn-logout-app" class="btn-logout" @click="doLogout" title="Đăng Xuất">
              <i class="fa-solid fa-right-from-bracket"></i> Đăng Xuất
            </button>
          </div>
        </div>
      </header>

      <!-- TAB NAVIGATION -->
      <nav class="tab-nav">
        <div class="tab-nav-inner">
          <button v-for="tab in tabs" :key="tab.id"
                  :id="'tab-' + tab.id"
                  :class="['tab-btn', { active: activeTab === tab.id }]"
                  @click="switchTab(tab.id)">
            <span class="tab-icon">
              <i v-if="isFontAwesome(tab.icon)" :class="tab.icon"></i>
              <span v-else>{{ tab.icon }}</span>
            </span>
            <span class="tab-label">{{ tab.label }}</span>
          </button>
        </div>
      </nav>

      <!-- CONTENT AREA -->
      <main class="realm-content">
        <!-- ═══════ TAB 1: DASHBOARD ═══════ -->
        <section v-if="activeTab === 'dashboard'" id="panel-dashboard" class="tab-panel">
          <h2 class="section-title">📊 Báo Cáo Tổng Quan Tài Chính</h2>

          <!-- Metrics Cards -->
          <div class="metrics-grid">
            <div class="metric-card jade">
              <div class="metric-icon"><i class="fa-solid fa-money-bill-trend-up"></i></div>
              <div class="metric-info">
                <span class="metric-label">Tổng Thu Nhập Tháng</span>
                <span class="metric-value">{{ formatVND(summary.total_income) }}</span>
              </div>
            </div>
            <div class="metric-card crimson">
              <div class="metric-icon"><i class="fa-solid fa-fire-flame-curved"></i></div>
              <div class="metric-info">
                <span class="metric-label">Tổng Chi Tiêu Tháng</span>
                <span class="metric-value">{{ formatVND(summary.total_expense) }}</span>
              </div>
            </div>
            <div class="metric-card gold">
              <div class="metric-icon"><i class="fa-solid fa-scale-balanced"></i></div>
              <div class="metric-info">
                <span class="metric-label">Tiết Kiệm Tích Lũy</span>
                <span class="metric-value" :class="summary.net_savings >= 0 ? 'positive' : 'negative'">
                  {{ formatVND(summary.net_savings) }}
                </span>
              </div>
            </div>
            <div class="metric-card purple">
              <div class="metric-icon"><i class="fa-solid fa-vault"></i></div>
              <div class="metric-info">
                <span class="metric-label">Tổng Số Dư Các Ví</span>
                <span class="metric-value">{{ formatVND(summary.total_balance) }}</span>
              </div>
            </div>
          </div>

          <!-- ═══════ SMART ANALYTICS & FORECASTING PANEL ═══════ -->
          <div v-if="analyticsData" id="smart-analytics-card" class="smart-analytics-card glass-panel" :class="{ 'warning-border': analyticsData.is_overspending || analyticsData.is_deficit_projected }">
            <div class="analytics-header">
              <div class="analytics-title-group">
                <span class="analytics-icon">{{ analyticsData.is_overspending ? '⚠️' : '🔮' }}</span>
                <div>
                  <h3 class="analytics-title">Phân Tích Chi Tiêu & Dự Báo Thông Minh</h3>
                  <p class="analytics-subtitle">Cập nhật theo thời gian thực dựa trên hành vi tài chính của bạn</p>
                </div>
              </div>
              <div class="analytics-status-badge" :class="analyticsData.is_overspending ? 'badge-danger' : (analyticsData.is_deficit_projected ? 'badge-warning' : 'badge-success')">
                {{ analyticsData.is_overspending ? 'CẢNH BÁO CHI TIÊU' : (analyticsData.is_deficit_projected ? 'NGUY CƠ THÂM HỤT' : 'TÀI CHÍNH ỔN ĐỊNH') }}
              </div>
            </div>

            <!-- Mini Analytics Metrics -->
            <div class="analytics-metrics-grid">
              <div class="analytics-metric-box">
                <span class="box-label">📅 Chi Tiêu Hôm Nay</span>
                <strong class="box-value" :class="analyticsData.today_expense > 0 ? 'amt-expense' : ''">{{ formatVND(analyticsData.today_expense) }}</strong>
                <small class="box-sub">Thu nhập: {{ formatVND(analyticsData.today_income) }}</small>
              </div>
              <div class="analytics-metric-box">
                <span class="box-label">📊 Trung Bình 7 Ngày</span>
                <strong class="box-value">{{ formatVND(analyticsData.avg_daily_expense_7d) }}/ngày</strong>
                <small class="box-sub">30 ngày: {{ formatVND(analyticsData.avg_daily_expense_30d) }}/ngày</small>
              </div>
              <div class="analytics-metric-box">
                <span class="box-label">🔮 Dự Báo Chi Ngày Mai</span>
                <strong class="box-value gold-text">{{ formatVND(analyticsData.forecast_tomorrow_expense) }}</strong>
                <small class="box-sub">Còn {{ analyticsData.days_remaining_in_month }} ngày trong tháng</small>
              </div>
              <div class="analytics-metric-box">
                <span class="box-label">🎯 Dự Kiến Số Dư Cuối Tháng</span>
                <strong class="box-value" :class="analyticsData.forecast_month_end_balance >= 0 ? 'positive' : 'negative'">
                  {{ formatVND(analyticsData.forecast_month_end_balance) }}
                </strong>
                <small class="box-sub">Tổng chi dự kiến: {{ formatVND(analyticsData.forecast_total_month_expense) }}</small>
              </div>
            </div>

            <!-- Warning Reasons List -->
            <div v-if="analyticsData.warning_reasons && analyticsData.warning_reasons.length" class="warning-reasons-container">
              <div v-for="(reason, rIdx) in analyticsData.warning_reasons" :key="rIdx" class="warning-reason-item">
                <span class="reason-bullet">🚨</span>
                <span class="reason-text">{{ reason }}</span>
              </div>
            </div>

            <!-- Natural Language Forecast Banner -->
            <div class="forecast-message-box" :class="analyticsData.is_overspending ? 'box-danger' : (analyticsData.is_deficit_projected ? 'box-warning' : 'box-success')">
              <span class="message-icon">💬</span>
              <p class="message-content">{{ analyticsData.forecast_message }}</p>
            </div>
          </div>

          <!-- Budget Alerts -->
          <div v-if="budgetAlerts.length" class="alerts-section">
            <h3 class="sub-title">⚠️ Cảnh Báo Vượt Hạn Mức Ngân Sách</h3>
            <div v-for="alert in budgetAlerts" :key="alert.category"
                 :class="['alert-card', alert.level === 'DANGER' ? 'danger' : 'warning']">
              <span class="alert-icon">
                <i v-if="isFontAwesome(alert.icon)" :class="alert.icon"></i>
                <span v-else>{{ alert.icon }}</span>
              </span>
              <span class="alert-msg">{{ alert.message }}</span>
              <span class="alert-pct">{{ alert.percent }}%</span>
            </div>
          </div>

          <!-- Dashboard Charts Row -->
          <div class="dashboard-charts-row">
            <div class="chart-card" v-if="summary.expense_by_category && summary.expense_by_category.length">
              <ChartComponent
                type="doughnut"
                :chart-data="dashboardDoughnutData"
                title="🥧 Phân Bổ Chi Tiêu Theo Danh Mục"
              />
            </div>
            <div class="chart-card" v-if="trendData.trend && trendData.trend.length">
              <ChartComponent
                type="bar"
                :chart-data="dashboardBarData"
                title="📊 Diễn Biến Thu / Chi 6 Tháng Gần Nhất"
              />
            </div>
          </div>

          <!-- AI Saving Tips -->
          <div class="saving-tips-section">
            <div class="saving-tips-header">
              <h3 class="sub-title">💡 Lời Khuyên Tài Chính Cá Nhân AI (50/30/20)</h3>
              <button id="btn-saving-tips" class="btn-jade-sm" @click="loadSavingTips" :disabled="loadingTips">
                {{ loadingTips ? '⏳ AI đang phân tích...' : '✨ Nhận Lời Khuyên AI' }}
              </button>
            </div>
            <div v-if="savingTips" class="saving-tips-card glass-panel">
              <div class="tips-meta">
                <span>📅 Tháng: {{ savingTips.month_year }}</span>
                <span>📈 Tỷ lệ tiết kiệm: <strong :class="savingTips.savings_rate >= 20 ? 'positive' : 'negative'">{{ savingTips.savings_rate }}%</strong></span>
              </div>
              <div class="tips-content" v-html="formatChatText(savingTips.tips)"></div>
            </div>
          </div>

          <!-- Recent Transactions -->
          <h3 class="sub-title">📜 Giao Dịch Tài Chính Gần Đây</h3>
          <div class="table-scroll">
            <table class="xianxia-table">
              <thead>
                <tr>
                  <th>Ngày</th>
                  <th>Danh Mục</th>
                  <th>Ghi Chú</th>
                  <th>Ví Tiền</th>
                  <th>Số Tiền (VNĐ)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="txn in transactions.slice(0, 10)" :key="txn.id">
                  <td>{{ txn.transaction_date }}</td>
                  <td>
                    <span class="cat-badge">
                      <i v-if="isFontAwesome(txn.category_icon)" :class="txn.category_icon" class="cat-inline-icon"></i>
                      <span v-else class="cat-inline-icon">{{ txn.category_icon }}</span>
                      {{ txn.category_name }}
                    </span>
                  </td>
                  <td>{{ txn.note || '—' }}</td>
                  <td>{{ txn.wallet_name }}</td>
                  <td :class="txn.transaction_type === 'INCOME' ? 'amt-income' : 'amt-expense'">
                    {{ txn.transaction_type === 'INCOME' ? '+' : '-' }}{{ formatVND(txn.amount) }}
                  </td>
                </tr>
                <tr v-if="!transactions.length">
                  <td colspan="5" class="empty-row">Chưa có giao dịch nào...</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- ═══════ TAB 2: TRANSACTIONS ═══════ -->
        <section v-if="activeTab === 'transactions'" id="panel-transactions" class="tab-panel">
          <h2 class="section-title">💸 Quản Lý Chi Tiết Giao Dịch</h2>
          
          <!-- FORM THÊM GIAO DỊCH -->
          <div class="form-card glass-panel">
            <h3 class="form-card-title">✨ Ghi Nhận Thu / Chi Mới</h3>
            <div class="form-grid">
              <div class="input-group-xianxia">
                <label>Loại Giao Dịch</label>
                <select id="txn-type-select" v-model="txnForm.transaction_type">
                  <option value="EXPENSE">🔥 Chi Tiêu</option>
                  <option value="INCOME">💰 Thu Nhập</option>
                </select>
              </div>
              <div class="input-group-xianxia">
                <label>Số Tiền (VNĐ)</label>
                <input id="txn-amount-input" v-model.number="txnForm.amount" type="number" placeholder="Ví dụ: 150000" />
              </div>
              <div class="input-group-xianxia">
                <label>Ví Thanh Toán</label>
                <select id="txn-wallet-select" v-model="txnForm.wallet_id">
                  <option v-for="w in wallets" :key="w.id" :value="w.id">{{ w.wallet_name }} ({{ formatVND(w.balance) }})</option>
                </select>
              </div>
              <div class="input-group-xianxia">
                <label>Danh Mục</label>
                <select id="txn-category-select" v-model="txnForm.category_id">
                  <option :value="null">-- Chọn Danh Mục --</option>
                  <option v-for="c in filteredCategories" :key="c.id" :value="c.id">
                    {{ c.category_name }}
                  </option>
                </select>
              </div>
              <div class="input-group-xianxia">
                <label>Ngày Giao Dịch</label>
                <input id="txn-date-input" v-model="txnForm.transaction_date" type="date" />
              </div>
              <div class="input-group-xianxia">
                <label>Ghi Chú</label>
                <input id="txn-note-input" v-model="txnForm.note" type="text" placeholder="Ghi chú chi tiết..." />
              </div>
            </div>
            <div class="form-action-right">
              <button id="btn-save-txn" class="btn-jade" @click="createTransaction" :disabled="loading">
                {{ loading ? '⏳ Đang lưu...' : '⚡ Lưu Giao Dịch' }}
              </button>
            </div>
          </div>

          <!-- BẢNG LỊCH SỬ GIAO DỊCH -->
          <div class="table-card glass-panel">
            <h3 class="sub-title">📜 Toàn Bộ Lịch Sử Thu Chi</h3>
            <div class="table-scroll">
              <table class="xianxia-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Ngày</th>
                    <th>Danh Mục</th>
                    <th>Ví</th>
                    <th>Ghi Chú</th>
                    <th>Số Tiền</th>
                    <th>Thao Tác</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="txn in transactions" :key="txn.id">
                    <td>#{{ txn.id }}</td>
                    <td>{{ txn.transaction_date }}</td>
                    <td>
                      <span class="cat-badge">
                        <i v-if="isFontAwesome(txn.category_icon)" :class="txn.category_icon" class="cat-inline-icon"></i>
                        <span v-else class="cat-inline-icon">{{ txn.category_icon }}</span>
                        {{ txn.category_name }}
                      </span>
                    </td>
                    <td>{{ txn.wallet_name }}</td>
                    <td>{{ txn.note || '—' }}</td>
                    <td :class="txn.transaction_type === 'INCOME' ? 'amt-income' : 'amt-expense'">
                      {{ txn.transaction_type === 'INCOME' ? '+' : '-' }}{{ formatVND(txn.amount) }}
                    </td>
                    <td>
                      <button class="btn-del-sm" @click="deleteTransaction(txn.id)" title="Xóa giao dịch">🗑️</button>
                    </td>
                  </tr>
                  <tr v-if="!transactions.length">
                    <td colspan="7" class="empty-row">Chưa có giao dịch nào...</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <!-- ═══════ TAB 3: WALLETS ═══════ -->
        <section v-if="activeTab === 'wallets'" id="panel-wallets" class="tab-panel">
          <div class="section-header-flex">
            <h2 class="section-title">💳 Quản Lý Tài Khoản & Ví Tiền</h2>
            <button id="btn-cleanup-wallets" class="btn-secondary-sm" @click="doCleanupAll" title="Chuẩn hóa toàn bộ tên ví tiền và dữ liệu hệ thống">
              <i class="fa-solid fa-broom"></i> Dọn Rác & Chuẩn Hóa Ví Tiền
            </button>
          </div>

          <!-- DANH SÁCH VÍ -->
          <div class="wallet-grid">
            <div v-for="w in wallets" :key="w.id" class="wallet-card glass-panel">
              <div class="wallet-header">
                <span class="wallet-type-icon">{{ walletTypeIcon(w.wallet_type) }}</span>
                <span class="wallet-name">{{ w.wallet_name }}</span>
                <button v-if="wallets.length > 1" class="btn-del-sm" @click="deleteWallet(w.id)" title="Xóa ví">🗑️</button>
              </div>
              <div class="wallet-balance-val">{{ formatVND(w.balance) }}</div>
            </div>
          </div>

          <!-- THÊM VÍ VÀ CHUYỂN TIỀN -->
          <div class="two-col-grid">
            <div class="form-card glass-panel">
              <h3 class="form-card-title">✨ Thêm Ví Tiền Mới</h3>
              <div class="input-group-xianxia">
                <label>Tên Ví Tiền</label>
                <input id="new-wallet-name" v-model="walletForm.wallet_name" type="text" placeholder="Ví dụ: Ví MoMo, Tiền Mặt..." />
              </div>
              <div class="input-group-xianxia">
                <label>Số Dư Ban Đầu</label>
                <input id="new-wallet-balance" v-model.number="walletForm.balance" type="number" placeholder="0" />
              </div>
              <div class="input-group-xianxia">
                <label>Loại Ví</label>
                <select id="new-wallet-type" v-model="walletForm.wallet_type">
                  <option value="cash">💵 Tiền Mặt</option>
                  <option value="bank">🏦 Tài Khoản Ngân Hàng</option>
                  <option value="e-wallet">📱 Ví Điện Tử</option>
                </select>
              </div>
              <button id="btn-create-wallet" class="btn-jade" @click="createWallet" :disabled="loading">Tạo Ví Mới</button>
            </div>

            <div class="form-card glass-panel">
              <h3 class="form-card-title">🔄 Chuyển Tiền Giữa Các Ví</h3>
              <div class="input-group-xianxia">
                <label>Ví Nguồn</label>
                <select id="transfer-from-select" v-model="transferForm.from_wallet_id">
                  <option :value="null">-- Chọn Ví Nguồn --</option>
                  <option v-for="w in wallets" :key="w.id" :value="w.id">{{ w.wallet_name }} ({{ formatVND(w.balance) }})</option>
                </select>
              </div>
              <div class="input-group-xianxia">
                <label>Ví Đích</label>
                <select id="transfer-to-select" v-model="transferForm.to_wallet_id">
                  <option :value="null">-- Chọn Ví Đích --</option>
                  <option v-for="w in wallets" :key="w.id" :value="w.id">{{ w.wallet_name }}</option>
                </select>
              </div>
              <div class="input-group-xianxia">
                <label>Số Tiền Chuyển (VNĐ)</label>
                <input id="transfer-amount-input" v-model.number="transferForm.amount" type="number" placeholder="Ví dụ: 500000" />
              </div>
              <button id="btn-do-transfer" class="btn-gold" @click="doTransfer" :disabled="loading">⚡ Thực Hiện Chuyển Tiền</button>
            </div>
          </div>
        </section>

        <!-- ═══════ TAB 4: CATEGORIES (FONTAWESOME ICONS & MOJIBAKE FIX) ═══════ -->
        <section v-if="activeTab === 'categories'" id="panel-categories" class="tab-panel">
          <div class="section-header-flex">
            <h2 class="section-title">🏷️ Danh Mục Chi Tiêu & Thu Nhập</h2>
            <button id="btn-cleanup-categories" class="btn-secondary-sm" @click="doCleanupCategories" title="Dọn dẹp các danh mục bị lỗi font Mojibake và khởi tạo lại">
              <i class="fa-solid fa-broom"></i> Dọn Rác & Chuẩn Hóa Danh Mục
            </button>
          </div>
          
          <div class="two-col-grid">
            <div class="form-card glass-panel">
              <h3 class="form-card-title">✨ Tạo Danh Mục Mới</h3>
              <div class="input-group-xianxia">
                <label>Tên Danh Mục</label>
                <input id="new-cat-name" v-model="catForm.category_name" type="text" placeholder="Ví dụ: Ăn Uống, Du Lịch..." />
              </div>
              <div class="input-group-xianxia">
                <label>Loại Danh Mục</label>
                <select id="new-cat-type" v-model="catForm.category_type">
                  <option value="EXPENSE">🔥 Chi Tiêu</option>
                  <option value="INCOME">💰 Thu Nhập</option>
                </select>
              </div>
              <div class="input-group-xianxia">
                <label>Chọn Biểu Tượng Icon</label>
                <div class="icon-selector">
                  <span v-for="ico in iconOptions" :key="ico"
                        :class="['icon-choice', { active: catForm.icon === ico }]"
                        @click="catForm.icon = ico"
                        :title="ico">
                    <i v-if="isFontAwesome(ico)" :class="ico"></i>
                    <span v-else>{{ ico }}</span>
                  </span>
                </div>
              </div>
              <button id="btn-create-category" class="btn-jade" @click="createCategory" :disabled="loading">
                <i class="fa-solid fa-plus"></i> Tạo Danh Mục
              </button>
            </div>

            <div class="table-card glass-panel">
              <h3 class="sub-title">📋 Danh Sách Phân Loại Đang Dùng</h3>
              <div class="category-badges-list">
                <div v-for="c in categories" :key="c.id" class="cat-pill">
                  <span class="cat-pill-icon">
                    <i v-if="isFontAwesome(c.icon)" :class="c.icon"></i>
                    <span v-else>{{ c.icon }}</span>
                  </span>
                  <span class="cat-pill-name">{{ c.category_name }}</span>
                  <span class="cat-pill-type" :class="c.category_type">{{ c.category_type === 'INCOME' ? 'Thu' : 'Chi' }}</span>
                  <button class="btn-del-mini" @click="deleteCategory(c.id)" title="Xóa danh mục">✕</button>
                </div>
                <div v-if="!categories.length" class="empty-state">
                  Chưa có danh mục nào. Hãy bấm "Dọn Rác & Chuẩn Hóa Danh Mục" ở góc phải để tự động nạp danh mục chuẩn!
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- ═══════ TAB 5: OCR INVOICE SCANNING ═══════ -->
        <section v-if="activeTab === 'ocr'" id="panel-ocr" class="tab-panel">
          <h2 class="section-title">🧾 Quét & Nhận Diện Hóa Đơn Tự Động (OCR AI Vision)</h2>
          
          <div class="two-col-grid">
            <div class="form-card glass-panel" id="ocr-upload-card">
              <h3 class="form-card-title">📸 Tải Lên Ảnh Hóa Đơn Thanh Toán</h3>
              <div id="ocr-dropzone" class="ocr-dropzone" @dragover.prevent @drop.prevent="handleOCRDrop" @click="$refs.ocrInput.click()">
                <input id="ocr-file-input" type="file" ref="ocrInput" accept="image/*" class="ocr-file-input" @change="handleOCRUpload" />
                <div v-if="!ocrPreview" class="ocr-drop-placeholder">
                  <span class="ocr-camera-icon"><i class="fa-solid fa-camera"></i></span>
                  <p>Kéo thả ảnh hóa đơn vào đây hoặc <strong>Nhấp để chọn ảnh</strong></p>
                  <small>Hỗ trợ định dạng JPEG, PNG, WEBP (Tối đa 10MB)</small>
                </div>
                <div v-else class="ocr-preview-container" @click.stop>
                  <img :src="ocrPreview" alt="Xem trước hóa đơn" class="ocr-img-preview" />
                  <div>
                    <button id="btn-reupload-ocr" class="btn-reupload" @click="$refs.ocrInput.click()">
                      <i class="fa-solid fa-rotate-right"></i> Đổi ảnh khác
                    </button>
                  </div>
                </div>
              </div>
              <button id="btn-scan-ai" class="btn-jade btn-block" @click="scanInvoice" :disabled="loading || !ocrFile">
                {{ loading ? '👁️ AI Vision đang phân tích hóa đơn...' : '⚡ Bắt Đầu Quét OCR AI' }}
              </button>
            </div>

            <div class="form-card glass-panel" id="ocr-result-card">
              <h3 class="form-card-title">🔍 Kết Quả Phân Tích & Xác Nhận Giao Dịch</h3>
              <div v-if="ocrConfirmForm" id="ocr-confirm-box" class="ocr-confirm-box">
                <div class="input-group-xianxia">
                  <label>Số Tiền Nhận Diện (VNĐ)</label>
                  <input id="ocr-amount-input" v-model.number="ocrConfirmForm.amount" type="number" />
                </div>
                <div class="input-group-xianxia">
                  <label>Ngày Hóa Đơn</label>
                  <input id="ocr-date-input" v-model="ocrConfirmForm.transaction_date" type="date" />
                </div>
                <div class="input-group-xianxia">
                  <label>Nội Dung / Tên Cửa Hàng</label>
                  <input id="ocr-note-input" v-model="ocrConfirmForm.note" type="text" />
                </div>
                <div class="input-group-xianxia">
                  <label>Ví Thanh Toán</label>
                  <select id="ocr-wallet-select" v-model="ocrConfirmForm.wallet_id">
                    <option v-for="w in wallets" :key="w.id" :value="w.id">{{ w.wallet_name }} ({{ formatVND(w.balance) }})</option>
                  </select>
                </div>
                <div class="input-group-xianxia">
                  <label>Danh Mục Chi Tiêu</label>
                  <select id="ocr-category-select" v-model="ocrConfirmForm.category_id">
                    <option v-for="c in expenseCategories" :key="c.id" :value="c.id">
                      {{ c.category_name }}
                    </option>
                  </select>
                </div>
                <button id="btn-confirm-ocr" class="btn-gold btn-block" @click="confirmOCRTransaction" :disabled="loading">
                  ✨ Xác Nhận Lưu Giao Dịch Vào Sổ
                </button>
              </div>
              <div v-else class="empty-state">
                <span style="font-size: 36px; display: block; margin-bottom: 8px;"><i class="fa-solid fa-receipt"></i></span>
                Chưa có dữ liệu quét. Vui lòng tải ảnh hóa đơn và bấm nút <strong>Bắt Đầu Quét OCR AI</strong>.
              </div>
            </div>
          </div>
        </section>

        <!-- ═══════ TAB 6: BUDGETS ═══════ -->
        <section v-if="activeTab === 'budgets'" id="panel-budgets" class="tab-panel">
          <h2 class="section-title">🎯 Thiết Lập Ngân Sách & Hạn Mức Chi Tiêu</h2>
          
          <div class="form-card glass-panel">
            <h3 class="form-card-title">✨ Thiết Lập Hạn Mức Ngân Sách Tháng</h3>
            <div class="form-grid">
              <div class="input-group-xianxia">
                <label>Danh Mục Chi Tiêu</label>
                <select id="budget-cat-select" v-model="budgetForm.category_id">
                  <option :value="null">-- Chọn Danh Mục --</option>
                  <option v-for="c in expenseCategories" :key="c.id" :value="c.id">
                    {{ c.category_name }}
                  </option>
                </select>
              </div>
              <div class="input-group-xianxia">
                <label>Hạn Mức Tối Đa (VNĐ)</label>
                <input id="budget-limit-input" v-model.number="budgetForm.limit_amount" type="number" placeholder="Ví dụ: 3000000" />
              </div>
              <div class="input-group-xianxia">
                <label>Tháng Áp Dụng</label>
                <input id="budget-month-input" v-model="budgetForm.month_year" type="month" />
              </div>
            </div>
            <div class="form-action-right">
              <button id="btn-save-budget" class="btn-jade" @click="createBudget" :disabled="loading">Lưu Hạn Mức</button>
            </div>
          </div>

          <!-- TIẾN ĐỘ HẠN MỨC -->
          <div class="budget-list">
            <div v-for="b in budgets" :key="b.id" class="budget-item-card glass-panel">
              <div class="budget-card-head">
                <span class="budget-cat-name">
                  <i v-if="isFontAwesome(b.category_icon)" :class="b.category_icon" class="cat-inline-icon"></i>
                  <span v-else class="cat-inline-icon">{{ b.category_icon }}</span>
                  {{ b.category_name }}
                </span>
                <span class="budget-cat-val">{{ formatVND(b.spent_amount) }} / {{ formatVND(b.limit_amount) }}</span>
                <button class="btn-del-mini" @click="deleteBudget(b.id)">🗑️</button>
              </div>
              <div class="budget-progress-bar">
                <div class="budget-progress-fill"
                     :style="{ width: Math.min(budgetPct(b), 100) + '%' }"
                     :class="{ danger: budgetPct(b) >= 100, warning: budgetPct(b) >= 80 && budgetPct(b) < 100 }">
                </div>
              </div>
              <div class="budget-pct-text">Đã dùng: {{ budgetPct(b).toFixed(1) }}%</div>
            </div>
          </div>
        </section>

        <!-- ═══════ TAB 7: STATS ═══════ -->
        <section v-if="activeTab === 'stats'" id="panel-stats" class="tab-panel">
          <h2 class="section-title">📈 Phân Tích & Báo Cáo Thống Kê</h2>

          <!-- SO SÁNH 2 THÁNG -->
          <div class="compare-controls glass-panel">
            <div class="compare-row">
              <div class="input-group-xianxia">
                <label>Tháng 1</label>
                <input id="compare-m1" v-model="compareMonth1" type="month" @change="loadCompare" />
              </div>
              <div class="compare-vs">VS</div>
              <div class="input-group-xianxia">
                <label>Tháng 2</label>
                <input id="compare-m2" v-model="compareMonth2" type="month" @change="loadCompare" />
              </div>
            </div>
            <div v-if="compareData" class="compare-results">
              <div class="compare-card">
                <span>Chênh Lệch Thu Nhập: </span>
                <strong :class="compareData.diff_income >= 0 ? 'positive' : 'negative'">{{ formatVND(compareData.diff_income) }}</strong>
              </div>
              <div class="compare-card">
                <span>Chênh Lệch Chi Tiêu: </span>
                <strong :class="compareData.diff_expense <= 0 ? 'positive' : 'negative'">{{ formatVND(compareData.diff_expense) }}</strong>
              </div>
            </div>
          </div>

          <div class="charts-grid-stats">
            <div class="chart-card glass-panel" v-if="weeklyData.data && weeklyData.data.length">
              <ChartComponent
                type="line"
                :chart-data="weeklyLineData"
                title="📈 Dòng Tiền Chi Tiêu Theo Tuần"
              />
            </div>
            <div class="chart-card glass-panel" v-if="trendData.trend && trendData.trend.length">
              <ChartComponent
                type="bar"
                :chart-data="trendBarData"
                title="📊 Diễn Biến Thu / Chi 6 Tháng"
              />
            </div>
          </div>
        </section>

        <!-- ═══════ TAB 8: AI FINANCIAL ADVISOR CHAT ═══════ -->
        <section v-if="activeTab === 'chat'" id="panel-chat" class="tab-panel">
          <h2 class="section-title">💬 Trợ Lý Cố Vấn Tài Chính Cá Nhân AI (Gemini Assistant)</h2>

          <div id="ai-chat-container" class="chat-container glass-panel">
            <div id="chat-messages-box" class="chat-messages" ref="chatMessagesEl">
              <div class="chat-welcome">
                <div class="chat-ai-avatar"><i class="fa-solid fa-robot"></i></div>
                <div>
                  <p><strong>Trợ Lý Tài Chính Gemini AI:</strong> Xin chào {{ userName }}! Tôi là Trợ lý Cố vấn Tài chính Cá nhân. Tôi có thể giúp bạn giải đáp thắc mắc về phân bổ ngân sách, phương pháp tiết kiệm 50/30/20, hoặc phân tích số dư hiện tại của bạn.</p>
                </div>
              </div>
              <div v-for="(msg, idx) in chatMessages" :key="idx"
                   :class="['chat-bubble', msg.role === 'user' ? 'user-bubble' : 'ai-bubble']">
                <div class="bubble-avatar">
                  <i v-if="msg.role === 'user'" class="fa-solid fa-user"></i>
                  <i v-else class="fa-solid fa-robot"></i>
                </div>
                <div class="bubble-content" v-html="formatChatText(msg.text)"></div>
              </div>
              <div v-if="chatLoading" class="chat-bubble ai-bubble">
                <div class="bubble-avatar"><i class="fa-solid fa-robot"></i></div>
                <div class="bubble-content typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>

            <div class="chat-input-area">
              <input id="chat-input" v-model="chatInput" type="text"
                     placeholder="Đặt câu hỏi tài chính (ví dụ: Làm thế nào để tiết kiệm 20% thu nhập?)..."
                     @keyup.enter="sendChat" />
              <button id="chat-send-btn" class="btn-jade-sm" @click="sendChat" :disabled="chatLoading || !chatInput.trim()">
                <i class="fa-solid fa-paper-plane"></i> Gửi Tin
              </button>
            </div>
          </div>
        </section>

        <!-- ═══════ TAB 9: ADMIN ═══════ -->
        <section v-if="activeTab === 'admin' && userRole === 'admin'" id="panel-admin" class="tab-panel">
          <h2 class="section-title">👑 Bảng Quản Trị Hệ Thống (Admin Panel)</h2>

          <div class="table-card glass-panel">
            <h3 class="sub-title">👥 Quản Lý Danh Sách Người Dùng</h3>
            <div class="table-scroll">
              <table class="xianxia-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Email</th>
                    <th>Họ Tên</th>
                    <th>Vai Trò</th>
                    <th>Trạng Thái</th>
                    <th>Thao Tác</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="u in adminUsers" :key="u.id">
                    <td>#{{ u.id }}</td>
                    <td>{{ u.email }}</td>
                    <td>{{ u.full_name }}</td>
                    <td><span class="role-badge" :class="u.role.toLowerCase()">{{ u.role }}</span></td>
                    <td>
                      <span :class="u.is_blocked ? 'status-blocked' : 'status-active'">
                        {{ u.is_blocked ? '🔒 Đã Khóa' : '✅ Hoạt Động' }}
                      </span>
                    </td>
                    <td>
                      <button class="btn-block-sm" @click="toggleBlockUser(u.id)">
                        {{ u.is_blocked ? '🔓 Mở Khóa' : '🔒 Khóa' }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="table-card glass-panel" style="margin-top: 24px;">
            <h3 class="sub-title">📜 Giám Sát Toàn Bộ Giao Dịch Hệ Thống</h3>
            <div class="table-scroll">
              <table class="xianxia-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Người Dùng (Email)</th>
                    <th>Họ Tên</th>
                    <th>Danh Mục</th>
                    <th>Số Tiền (VNĐ)</th>
                    <th>Ngày</th>
                    <th>Thao Tác</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="tx in adminTransactions" :key="tx.id">
                    <td>#{{ tx.id }}</td>
                    <td>{{ tx.user_email }}</td>
                    <td>{{ tx.user_name }}</td>
                    <td>{{ tx.category_name }}</td>
                    <td :class="tx.transaction_type === 'INCOME' ? 'amt-income' : 'amt-expense'">
                      {{ formatVND(tx.amount) }}
                    </td>
                    <td>{{ tx.transaction_date }}</td>
                    <td>
                      <button class="btn-del-sm" @click="adminDeleteTx(tx.id)">🗑️</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </main>
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- AUTH MODAL (ĐĂNG NHẬP / ĐĂNG KÝ)                          -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <div v-if="showAuthModal" id="auth-modal" class="modal-backdrop" @click.self="showAuthModal = false">
      <div class="modal-card auth-modal-card glass-panel">
        <div class="modal-header">
          <div class="dao-symbol"><i class="fa-solid fa-shield-halved"></i></div>
          <h3 class="modal-title">{{ authMode === 'login' ? 'Đăng Nhập Tài Khoản' : 'Đăng Ký Tài Khoản Mới' }}</h3>
          <button id="btn-close-auth-modal" class="modal-close" @click="showAuthModal = false">✕</button>
        </div>

        <div class="modal-tabs">
          <button id="modal-tab-login" :class="['modal-tab-btn', { active: authMode === 'login' }]" @click="authMode = 'login'">Đăng Nhập</button>
          <button id="modal-tab-register" :class="['modal-tab-btn', { active: authMode === 'register' }]" @click="authMode = 'register'">Đăng Ký</button>
        </div>

        <!-- FORM ĐĂNG NHẬP -->
        <div v-if="authMode === 'login'" class="auth-form-inner">
          <div class="input-group-xianxia">
            <label>📧 Địa Chỉ Email</label>
            <input id="login-email" v-model="authForm.email" type="email" placeholder="admin@gmail.com" @keyup.enter="doLogin" />
          </div>
          <div class="input-group-xianxia">
            <label>🔑 Mật Khẩu</label>
            <input id="login-password" v-model="authForm.password" type="password" placeholder="••••••" @keyup.enter="doLogin" />
          </div>
          <button id="btn-submit-login" class="btn-jade btn-block" @click="doLogin" :disabled="loading">
            {{ loading ? '⏳ Đang xác thực...' : '🔑 Đăng Nhập Hệ Thống' }}
          </button>
        </div>

        <!-- FORM ĐĂNG KÝ -->
        <div v-else class="auth-form-inner">
          <div class="input-group-xianxia">
            <label>👤 Họ và Tên</label>
            <input id="register-name" v-model="authForm.full_name" type="text" placeholder="Nguyễn Văn A" />
          </div>
          <div class="input-group-xianxia">
            <label>📧 Địa Chỉ Email</label>
            <input id="register-email" v-model="authForm.email" type="email" placeholder="nguyenvana@gmail.com" />
          </div>
          <div class="input-group-xianxia">
            <label>🔑 Mật Khẩu</label>
            <input id="register-password" v-model="authForm.password" type="password" placeholder="••••••" />
          </div>
          <button id="btn-submit-register" class="btn-gold btn-block" @click="doRegister" :disabled="loading">
            {{ loading ? '⏳ Đang khởi tạo...' : '✨ Tạo Tài Khoản Mới' }}
          </button>
        </div>

        <div v-if="errorMsg" id="auth-error-banner" class="error-banner glass-panel-alert">⚠️ {{ errorMsg }}</div>
      </div>
    </div>

    <!-- PROFILE MODAL -->
    <div v-if="showProfileModal" id="profile-modal" class="modal-backdrop" @click.self="showProfileModal = false">
      <div class="modal-card glass-panel">
        <div class="modal-header">
          <h3 class="modal-title">👤 Thông Tin Tài Khoản Cá Nhân</h3>
          <button class="modal-close" @click="showProfileModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="input-group-xianxia">
            <label>📧 Địa Chỉ Email</label>
            <input :value="userEmail" type="email" disabled class="disabled-input" />
          </div>
          <div class="input-group-xianxia">
            <label>👤 Họ Tên Hiển Thị</label>
            <input id="profile-fullname-input" v-model="profileForm.full_name" type="text" placeholder="Nhập họ tên mới..." @keyup.enter="saveProfile" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showProfileModal = false">Hủy</button>
          <button id="btn-save-profile" class="btn-jade-sm" @click="saveProfile" :disabled="loadingProfile">
            {{ loadingProfile ? '⏳ Đang lưu...' : '✨ Lưu Thay Đổi' }}
          </button>
        </div>
      </div>
    </div>

    <!-- TOAST -->
    <div v-if="toast" id="toast-notify" class="toast-notification" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'
import ChartComponent from './components/ChartComponents.vue'

export default {
  name: 'ExpenseManagementApp',
  components: { ChartComponent },
  setup() {
    // ─── STATE ────────────────────
    const isLoggedIn = ref(false)
    const authMode = ref('login')
    const showAuthModal = ref(false)
    const authForm = ref({ email: '', password: '', full_name: '' })
    const token = ref('')
    const userName = ref('Người Dùng')
    const userEmail = ref('')
    const userRole = ref('user')
    const currentTheme = ref(localStorage.getItem('app_theme') || 'dark')

    const adminUsers = ref([])
    const adminTransactions = ref([])
    const loading = ref(false)
    const loadingTips = ref(false)
    const loadingProfile = ref(false)
    const errorMsg = ref('')
    const toast = ref(null)
    const activeTab = ref('dashboard')

    // ─── MEDIA & VIDEO BACKGROUND ─
    const bgVideo = ref(null)
    const isMuted = ref(true)
    const videoSource = ref('https://i.pinimg.com/originals/a0/0a/76/a00a76a88ab4d12c8ab2bc3bb6658097.mp4')
    const showWelcomeToast = ref(false)
    const welcomeName = ref('')

    function updateVideoSource() {
      if (!isLoggedIn.value) {
        videoSource.value = 'https://i.pinimg.com/originals/a0/0a/76/a00a76a88ab4d12c8ab2bc3bb6658097.mp4'
      } else {
        videoSource.value = 'https://i.pinimg.com/originals/11/ab/c7/11abc7a2e2be2d26fdfc9e83ec248239.mp4'
      }
      nextTick(() => {
        if (bgVideo.value && currentTheme.value !== 'modern') {
          bgVideo.value.load()
          bgVideo.value.play().catch(e => console.warn('Autoplay check:', e))
        }
      })
    }

    function toggleAudio() {
      isMuted.value = !isMuted.value
      if (bgVideo.value) {
        bgVideo.value.muted = isMuted.value
        if (!isMuted.value) bgVideo.value.volume = 1.0
      }
    }

    // ─── TABS ─────────────────────
    const publicTabs = [
      { id: 'dashboard',    icon: 'fa-solid fa-chart-pie', label: 'Tổng Quan' },
      { id: 'transactions', icon: 'fa-solid fa-money-bill-transfer', label: 'Giao Dịch' },
      { id: 'wallets',      icon: 'fa-solid fa-wallet', label: 'Ví Tiền' },
      { id: 'categories',   icon: 'fa-solid fa-tags', label: 'Danh Mục' },
      { id: 'ocr',          icon: 'fa-solid fa-receipt', label: 'Quét Hóa Đơn AI' },
      { id: 'budgets',      icon: 'fa-solid fa-bullseye', label: 'Hạn Mức' },
      { id: 'stats',        icon: 'fa-solid fa-chart-line', label: 'Thống Kê' },
      { id: 'chat',         icon: 'fa-solid fa-robot', label: 'Trợ Lý AI' },
    ]

    const baseTabs = [
      { id: 'dashboard',    icon: 'fa-solid fa-chart-pie', label: 'Tổng Quan' },
      { id: 'transactions', icon: 'fa-solid fa-money-bill-transfer', label: 'Giao Dịch' },
      { id: 'wallets',      icon: 'fa-solid fa-wallet', label: 'Ví Tiền' },
      { id: 'categories',   icon: 'fa-solid fa-tags', label: 'Danh Mục' },
      { id: 'ocr',          icon: 'fa-solid fa-receipt', label: 'Quét Hóa Đơn AI' },
      { id: 'budgets',      icon: 'fa-solid fa-bullseye', label: 'Hạn Mức' },
      { id: 'stats',        icon: 'fa-solid fa-chart-line', label: 'Thống Kê' },
      { id: 'chat',         icon: 'fa-solid fa-robot', label: 'Trợ Lý AI' },
    ]

    const tabs = computed(() => {
      if (userRole.value === 'admin') {
        return [...baseTabs, { id: 'admin', icon: 'fa-solid fa-crown', label: 'Quản Trị' }]
      }
      return baseTabs
    })

    // ─── DATA REFS ────────────────
    const wallets = ref([])
    const categories = ref([])
    const transactions = ref([])
    const budgets = ref([])
    const summary = ref({ total_income: 0, total_expense: 0, net_savings: 0, total_balance: 0, expense_by_category: [] })
    const budgetAlerts = ref([])
    const analyticsData = ref(null)
    const chatMessages = ref([])
    const chatInput = ref('')
    const chatMessagesEl = ref(null)
    const chatLoading = ref(false)

    const trendData = ref({ trend: [] })
    const weeklyData = ref({ data: [] })
    const compareData = ref(null)
    const savingTips = ref(null)

    const now = new Date()
    const compareMonth2 = ref(now.toISOString().slice(0, 7))
    const prevMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1)
    const compareMonth1 = ref(prevMonth.toISOString().slice(0, 7))

    const showProfileModal = ref(false)
    const profileForm = ref({ full_name: '' })

    const txnForm = ref({
      transaction_type: 'EXPENSE', amount: 0, wallet_id: null,
      category_id: null, transaction_date: new Date().toISOString().slice(0, 10), note: ''
    })
    const walletForm = ref({ wallet_name: '', balance: 0, wallet_type: 'cash' })
    const catForm = ref({ category_name: '', category_type: 'EXPENSE', icon: 'fa-solid fa-utensils' })
    const budgetForm = ref({
      category_id: null, limit_amount: 0,
      month_year: new Date().toISOString().slice(0, 7)
    })
    const transferForm = ref({ from_wallet_id: null, to_wallet_id: null, amount: 0 })

    const ocrFile = ref(null)
    const ocrPreview = ref(null)
    const ocrResult = ref(null)
    const ocrConfirmForm = ref({
      note: '',
      amount: 0,
      transaction_date: new Date().toISOString().slice(0, 10),
      wallet_id: null,
      category_id: null,
      transaction_type: 'EXPENSE'
    })

    // Danh sách các icon FontAwesome phong phú & chuẩn
    const iconOptions = [
      'fa-solid fa-utensils',
      'fa-solid fa-cart-shopping',
      'fa-solid fa-car',
      'fa-solid fa-book',
      'fa-solid fa-bolt',
      'fa-solid fa-heart-pulse',
      'fa-solid fa-plane',
      'fa-solid fa-money-bill-wave',
      'fa-solid fa-chart-line',
      'fa-solid fa-gift',
      'fa-solid fa-house',
      'fa-solid fa-graduation-cap',
      'fa-solid fa-film',
      'fa-solid fa-gamepad',
      'fa-solid fa-mug-saucer',
      'fa-solid fa-dumbbell',
      'fa-solid fa-briefcase',
      'fa-solid fa-mobile-screen-button',
      'fa-solid fa-shirt',
      'fa-solid fa-box'
    ]

    // ─── AXIOS CLIENT ─────────────
    const api = axios.create({ baseURL: '' })
    api.interceptors.request.use(config => {
      if (token.value) config.headers.Authorization = `Bearer ${token.value}`
      return config
    })

    // ─── COMPUTED ─────────────────
    const incomeCategories = computed(() => categories.value.filter(c => c.category_type === 'INCOME'))
    const expenseCategories = computed(() => categories.value.filter(c => c.category_type === 'EXPENSE'))
    const filteredCategories = computed(() =>
      categories.value.filter(c => c.category_type === txnForm.value.transaction_type)
    )

    const dashboardDoughnutData = computed(() => ({
      labels: (summary.value.expense_by_category || []).map(c => c.category_name),
      values: (summary.value.expense_by_category || []).map(c => c.total || c.total_amount),
    }))

    const dashboardBarData = computed(() => ({
      labels: (trendData.value.trend || []).map(t => t.month || t.month_year),
      income: (trendData.value.trend || []).map(t => t.income || t.total_income),
      expense: (trendData.value.trend || []).map(t => t.expense || t.total_expense),
    }))

    const trendBarData = computed(() => ({
      labels: (trendData.value.trend || []).map(t => t.month || t.month_year),
      income: (trendData.value.trend || []).map(t => t.income || t.total_income),
      expense: (trendData.value.trend || []).map(t => t.expense || t.total_expense),
    }))

    const weeklyLineData = computed(() => ({
      labels: (weeklyData.value.data || []).map(w => w.week_start || w.week),
      expense: (weeklyData.value.data || []).map(w => w.expense),
      income: (weeklyData.value.data || []).map(w => w.income),
    }))

    // ─── THEME TOGGLE ─────────────
    function switchTheme() {
      currentTheme.value = currentTheme.value === 'modern' ? 'dark' : 'modern'
      localStorage.setItem('app_theme', currentTheme.value)
      document.body.setAttribute('data-theme', currentTheme.value)
      if (currentTheme.value !== 'modern') {
        updateVideoSource()
      }
    }

    // ─── HELPERS ──────────────────
    function isFontAwesome(iconStr) {
      if (!iconStr) return false
      return iconStr.startsWith('fa') || iconStr.includes('fa-')
    }

    function formatVND(val) {
      if (val === undefined || val === null) return '0 ₫'
      return Number(val).toLocaleString('vi-VN') + ' ₫'
    }

    function extractErrorMessage(err) {
      if (!err) return 'Có lỗi không xác định xảy ra. Vui lòng thử lại.'
      if (err.response?.data?.detail) {
        const d = err.response.data.detail
        if (typeof d === 'string') return d
        if (Array.isArray(d) && d.length > 0) {
          return d[0].msg || JSON.stringify(d[0])
        }
        return JSON.stringify(d)
      }
      if (err.message) return err.message
      return 'Lỗi kết nối tới máy chủ. Vui lòng kiểm tra lại đường truyền mạng!'
    }

    function showToast(message, type = 'success') {
      toast.value = { message, type }
      setTimeout(() => { toast.value = null }, 3500)
    }

    function budgetPct(b) {
      const limit = b.limit_amount || 1
      const spent = b.spent_amount !== undefined ? b.spent_amount : (b.spent || 0)
      return (spent / limit) * 100
    }

    function formatChatText(text) {
      if (!text) return ''
      return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br/>')
    }

    function walletTypeIcon(type) {
      return type === 'cash' ? '💵' : type === 'bank' ? '🏦' : '📱'
    }

    function openAuthModal(mode = 'login') {
      authMode.value = mode
      errorMsg.value = ''
      showAuthModal.value = true
    }

    function resetAllState() {
      wallets.value = []
      categories.value = []
      transactions.value = []
      budgets.value = []
      summary.value = { total_income: 0, total_expense: 0, net_savings: 0, total_balance: 0, expense_by_category: [] }
      budgetAlerts.value = []
      analyticsData.value = null
      chatMessages.value = []
      chatInput.value = ''
      trendData.value = { trend: [] }
      weeklyData.value = { data: [] }
      compareData.value = null
      savingTips.value = null
      errorMsg.value = ''
    }

    // ─── AUTH METHODS ─────────────
    async function doLogin() {
      if (!authForm.value.email || !authForm.value.password) {
        errorMsg.value = 'Vui lòng nhập đầy đủ Email và Mật khẩu!'
        return
      }
      loading.value = true
      errorMsg.value = ''
      try {
        const { data } = await api.post('/api/auth/login', {
          email: authForm.value.email,
          password: authForm.value.password
        })
        token.value = data.token
        userName.value = data.full_name || 'Người Dùng'
        userEmail.value = data.email
        userRole.value = data.role || 'user'

        localStorage.setItem('auth_token', data.token)
        localStorage.setItem('auth_user', userName.value)
        localStorage.setItem('auth_email', data.email)
        localStorage.setItem('user_role', userRole.value)

        showAuthModal.value = false
        welcomeName.value = userName.value
        showWelcomeToast.value = true
        isLoggedIn.value = true
        updateVideoSource()

        await loadAllData()
        setTimeout(() => { showWelcomeToast.value = false }, 3000)
      } catch (err) {
        errorMsg.value = extractErrorMessage(err)
      }
      loading.value = false
    }

    async function doRegister() {
      if (!authForm.value.email || !authForm.value.password || !authForm.value.full_name) {
        errorMsg.value = 'Vui lòng điền đầy đủ Họ Tên, Email và Mật Khẩu!'
        return
      }
      loading.value = true
      errorMsg.value = ''
      try {
        const { data } = await api.post('/api/auth/register', {
          email: authForm.value.email,
          password: authForm.value.password,
          full_name: authForm.value.full_name
        })
        token.value = data.token
        userName.value = data.full_name || 'Người Dùng'
        userEmail.value = data.email
        userRole.value = data.role || 'user'

        localStorage.setItem('auth_token', data.token)
        localStorage.setItem('auth_user', userName.value)
        localStorage.setItem('auth_email', data.email)
        localStorage.setItem('user_role', userRole.value)

        showAuthModal.value = false
        welcomeName.value = userName.value
        showWelcomeToast.value = true
        isLoggedIn.value = true
        updateVideoSource()

        await loadAllData()
        setTimeout(() => { showWelcomeToast.value = false }, 3000)
      } catch (err) {
        errorMsg.value = extractErrorMessage(err)
      }
      loading.value = false
    }

    function doLogout() {
      isLoggedIn.value = false
      token.value = ''
      userName.value = 'Người Dùng'
      userEmail.value = ''
      userRole.value = 'user'
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
      localStorage.removeItem('auth_email')
      localStorage.removeItem('user_role')
      resetAllState()
      updateVideoSource()
      showToast('Đã đăng xuất khỏi hệ thống an toàn.')
    }

    // ─── PROFILE ──────────────────
    function openProfileModal() {
      profileForm.value.full_name = userName.value
      showProfileModal.value = true
    }

    async function saveProfile() {
      const newName = profileForm.value.full_name.trim()
      if (!newName) {
        showToast('Vui lòng nhập họ tên!', 'error')
        return
      }
      loadingProfile.value = true
      try {
        await api.put('/api/user/profile', { full_name: newName })
        userName.value = newName
        localStorage.setItem('auth_user', newName)
        showToast('✨ Cập nhật thông tin thành công!')
        showProfileModal.value = false
      } catch (err) {
        showToast(extractErrorMessage(err), 'error')
      }
      loadingProfile.value = false
    }

    // ─── DATA FETCHING ────────────
    async function loadAllData() {
      await Promise.all([
        loadWallets(), loadCategories(), loadTransactions(),
        loadSummary(), loadBudgets(), checkBudgetAlerts(),
        loadAnalytics(), loadTrend(), loadWeekly(), loadChatHistory(),
      ])
    }

    async function loadWallets() {
      try {
        const { data } = await api.get('/api/wallets')
        wallets.value = data
        if (data.length && !txnForm.value.wallet_id) {
          txnForm.value.wallet_id = data[0].id
        }
      } catch {}
    }

    async function loadCategories() {
      try {
        const { data } = await api.get('/api/categories')
        categories.value = data
      } catch {}
    }

    async function doCleanupAll() {
      loading.value = true
      try {
        const { data } = await api.post('/api/cleanup-all')
        showToast(data.message)
        await loadWallets()
        await loadCategories()
        await loadTransactions()
        await loadSummary()
      } catch (err) {
        showToast(extractErrorMessage(err), 'error')
      }
      loading.value = false
    }

    async function doCleanupCategories() {
      await doCleanupAll()
    }

    async function loadTransactions() {
      try {
        const { data } = await api.get('/api/transactions?limit=100')
        transactions.value = data
      } catch {}
    }

    async function loadSummary() {
      try {
        const { data } = await api.get('/api/reports/summary')
        summary.value = data
      } catch {}
    }

    async function loadAnalytics() {
      try {
        const { data } = await api.get('/api/analytics')
        analyticsData.value = data
      } catch (err) {
        console.warn('Lỗi tải phân tích chi tiêu:', err)
      }
    }

    async function loadBudgets() {
      try {
        const { data } = await api.get('/api/budgets')
        budgets.value = data
      } catch {}
    }

    async function checkBudgetAlerts() {
      try {
        const { data } = await api.post('/api/ai/check-budget')
        budgetAlerts.value = data.alerts || []
      } catch {}
    }

    async function loadTrend() {
      try {
        const { data } = await api.get('/api/reports/trend?months=6')
        trendData.value = data
      } catch {}
    }

    async function loadWeekly() {
      try {
        const { data } = await api.get('/api/reports/weekly?weeks=4')
        weeklyData.value = data
      } catch {}
    }

    async function loadCompare() {
      if (!compareMonth1.value || !compareMonth2.value) return
      try {
        const { data } = await api.get(`/api/reports/compare?month1=${compareMonth1.value}&month2=${compareMonth2.value}`)
        compareData.value = data
      } catch {}
    }

    async function loadSavingTips() {
      loadingTips.value = true
      try {
        const { data } = await api.post('/api/ai/saving-tips')
        savingTips.value = data
        showToast('💡 Đã nhận lời khuyên tài chính cá nhân!')
      } catch (err) {
        showToast(extractErrorMessage(err), 'error')
      }
      loadingTips.value = false
    }

    async function loadChatHistory() {
      try {
        const { data } = await api.get('/api/ai/chat-history')
        if (data && data.length) {
          const list = []
          for (const item of [...data].reverse()) {
            list.push({ role: 'user', text: item.prompt_question })
            list.push({ role: 'ai', text: item.ai_response })
          }
          chatMessages.value = list
        }
      } catch {}
    }

    // ─── CRUD OPERATIONS ──────────
    async function createTransaction() {
      if (!txnForm.value.amount || !txnForm.value.category_id) {
        showToast('Vui lòng nhập số tiền và chọn danh mục!', 'error')
        return
      }
      loading.value = true
      try {
        await api.post('/api/transactions', txnForm.value)
        showToast('⚡ Đã thêm giao dịch thành công!')
        txnForm.value.amount = 0
        txnForm.value.note = ''
        await loadAllData()
      } catch (err) {
        showToast(extractErrorMessage(err), 'error')
      }
      loading.value = false
    }

    async function deleteTransaction(id) {
      if (!confirm('Bạn có chắc muốn xóa giao dịch này?')) return
      try {
        await api.delete(`/api/transactions/${id}`)
        showToast('Đã xóa giao dịch.')
        await loadAllData()
      } catch (err) {
        showToast(extractErrorMessage(err), 'error')
      }
    }

    async function createWallet() {
      if (!walletForm.value.wallet_name) {
        showToast('Vui lòng nhập tên ví!', 'error')
        return
      }
      loading.value = true
      try {
        await api.post('/api/wallets', walletForm.value)
        showToast('✨ Ví tiền mới đã được tạo!')
        walletForm.value = { wallet_name: '', balance: 0, wallet_type: 'cash' }
        await loadWallets()
        await loadSummary()
      } catch (err) {
        showToast(extractErrorMessage(err), 'error')
      }
      loading.value = false
    }

    async function deleteWallet(id) {
      if (!confirm('Bạn có chắc muốn xóa ví này?')) return
      try {
        await api.delete(`/api/wallets/${id}`)
        showToast('Đã xóa ví.')
        await loadWallets()
        await loadSummary()
      } catch (err) {
        showToast(extractErrorMessage(err), 'error')
      }
    }

    async function doTransfer() {
      if (!transferForm.value.from_wallet_id || !transferForm.value.to_wallet_id || !transferForm.value.amount) {
        showToast('Vui lòng điền đầy đủ thông tin chuyển tiền!', 'error')
        return
      }
      loading.value = true
      try {
        const { data } = await api.post('/api/wallets/transfer', transferForm.value)
        showToast(`⚡ ${data.message}`)
        transferForm.value = { from_wallet_id: null, to_wallet_id: null, amount: 0 }
        await loadWallets()
        await loadSummary()
      } catch (err) {
        showToast(extractErrorMessage(err), 'error')
      }
      loading.value = false
    }

    async function createCategory() {
      if (!catForm.value.category_name) {
        showToast('Vui lòng nhập tên danh mục!', 'error')
        return
      }
      loading.value = true
      try {
        await api.post('/api/categories', catForm.value)
        showToast('✨ Danh mục mới đã được tạo!')
        catForm.value = { category_name: '', category_type: 'EXPENSE', icon: 'fa-solid fa-utensils' }
        await loadCategories()
      } catch (err) {
        showToast(extractErrorMessage(err), 'error')
      }
      loading.value = false
    }

    async function deleteCategory(id) {
      if (!confirm('Bạn có chắc muốn xóa danh mục này?')) return
      try {
        await api.delete(`/api/categories/${id}`)
        showToast('Đã xóa danh mục.')
        await loadCategories()
      } catch (err) {
        showToast(extractErrorMessage(err), 'error')
      }
    }

    async function createBudget() {
      if (!budgetForm.value.category_id || !budgetForm.value.limit_amount) {
        showToast('Vui lòng chọn danh mục và hạn mức!', 'error')
        return
      }
      loading.value = true
      try {
        await api.post('/api/budgets', budgetForm.value)
        showToast('🎯 Hạn mức chi tiêu đã được thiết lập!')
        await loadBudgets()
        await checkBudgetAlerts()
      } catch (err) {
        showToast(extractErrorMessage(err), 'error')
      }
      loading.value = false
    }

    async function deleteBudget(id) {
      if (!confirm('Xóa hạn mức này?')) return
      try {
        await api.delete(`/api/budgets/${id}`)
        showToast('Đã xóa hạn mức.')
        await loadBudgets()
      } catch (err) {
        showToast(extractErrorMessage(err), 'error')
      }
    }

    // ─── OCR METHODS ──────────────
    function handleOCRUpload(e) {
      const file = e.target.files[0]
      if (file) {
        ocrFile.value = file
        ocrPreview.value = URL.createObjectURL(file)
      }
    }

    function handleOCRDrop(e) {
      const file = e.dataTransfer.files[0]
      if (file && file.type.startsWith('image/')) {
        ocrFile.value = file
        ocrPreview.value = URL.createObjectURL(file)
      }
    }

    async function scanInvoice() {
      if (!ocrFile.value) {
        showToast('Vui lòng chọn ảnh hóa đơn trước khi quét!', 'error')
        return
      }
      loading.value = true
      try {
        const formData = new FormData()
        formData.append('file', ocrFile.value)
        const { data } = await api.post('/api/ocr', formData)
        
        const resData = data.data || data
        ocrResult.value = resData
        const dWallet = wallets.value.length ? wallets.value[0].id : null
        const dCat = expenseCategories.value.length ? expenseCategories.value[0].id : null
        
        ocrConfirmForm.value = {
          note: resData.items || resData.store_name || 'Hóa đơn mua sắm tiêu dùng',
          amount: resData.total_amount || resData.amount || 0,
          transaction_date: resData.date || new Date().toISOString().slice(0, 10),
          wallet_id: dWallet,
          category_id: dCat,
          transaction_type: 'EXPENSE'
        }
        showToast('🧾 AI Vision đã phân tích xong! Vui lòng kiểm tra và xác nhận.')
      } catch (err) {
        showToast(extractErrorMessage(err), 'error')
      }
      loading.value = false
    }

    async function confirmOCRTransaction() {
      if (!ocrConfirmForm.value.amount || !ocrConfirmForm.value.category_id) {
        showToast('Vui lòng chọn danh mục và nhập số tiền!', 'error')
        return
      }
      loading.value = true
      try {
        await api.post('/api/transactions', ocrConfirmForm.value)
        showToast('⚡ Giao dịch từ hóa đơn đã được lưu vào sổ thành công!')
        ocrPreview.value = null
        ocrFile.value = null
        ocrConfirmForm.value = null
        await loadAllData()
        activeTab.value = 'transactions'
      } catch (err) {
        showToast(extractErrorMessage(err), 'error')
      }
      loading.value = false
    }

    // ─── CHAT METHODS ─────────────
    async function sendChat() {
      if (!chatInput.value.trim() || chatLoading.value) return
      const msg = chatInput.value.trim()
      chatMessages.value.push({ role: 'user', text: msg })
      chatInput.value = ''
      await nextTick()
      scrollChat()

      chatLoading.value = true
      try {
        const { data } = await api.post('/api/ai/chat', { message: msg })
        chatMessages.value.push({ role: 'ai', text: data.response })
      } catch (err) {
        chatMessages.value.push({ role: 'ai', text: '⚠️ Không thể kết nối tới Cố vấn AI: ' + extractErrorMessage(err) })
      } finally {
        chatLoading.value = false
        await nextTick()
        scrollChat()
      }
    }

    function scrollChat() {
      if (chatMessagesEl.value) {
        chatMessagesEl.value.scrollTop = chatMessagesEl.value.scrollHeight
      }
    }

    // ─── ADMIN METHODS ────────────
    async function loadAdminData() {
      if (userRole.value !== 'admin') return
      try {
        const resU = await api.get('/api/admin/users')
        adminUsers.value = resU.data
        const resT = await api.get('/api/admin/transactions')
        adminTransactions.value = resT.data
      } catch (e) {
        showToast(extractErrorMessage(e), 'error')
      }
    }

    async function toggleBlockUser(uId) {
      try {
        const res = await api.post(`/api/admin/users/${uId}/block`)
        showToast(res.data.message)
        loadAdminData()
      } catch (e) {
        showToast(extractErrorMessage(e), 'error')
      }
    }

    async function adminDeleteTx(tId) {
      if (!confirm('Bạn có chắc muốn xóa giao dịch này khỏi hệ thống?')) return
      try {
        const res = await api.delete(`/api/admin/transactions/${tId}`)
        showToast(res.data.message)
        loadAdminData()
      } catch (e) {
        showToast(extractErrorMessage(e), 'error')
      }
    }

    function switchTab(tabId) {
      activeTab.value = tabId
      if (tabId === 'stats') {
        loadTrend()
        loadWeekly()
        loadCompare()
      } else if (tabId === 'admin') {
        loadAdminData()
      }
    }

    // ─── MOUNTED ──────────────────
    onMounted(() => {
      document.body.setAttribute('data-theme', currentTheme.value)
      updateVideoSource()

      const savedToken = localStorage.getItem('auth_token') || localStorage.getItem('xianxia_token')
      const savedUser = localStorage.getItem('auth_user') || localStorage.getItem('xianxia_user')
      const savedEmail = localStorage.getItem('auth_email') || localStorage.getItem('xianxia_email')
      const savedRole = localStorage.getItem('user_role')

      if (savedRole) userRole.value = savedRole
      if (savedToken) {
        token.value = savedToken
        userName.value = savedUser || 'Người Dùng'
        userEmail.value = savedEmail || 'admin@gmail.com'
        isLoggedIn.value = true
        updateVideoSource()
        loadAllData()
      }
    })

    return {
      isLoggedIn, authMode, showAuthModal, authForm, token, userName, userEmail, userRole, currentTheme,
      adminUsers, adminTransactions, loading, loadingTips, loadingProfile, errorMsg, toast, activeTab,
      bgVideo, isMuted, videoSource, showWelcomeToast, welcomeName, updateVideoSource, toggleAudio,
      publicTabs, tabs, wallets, categories, transactions, budgets, summary, budgetAlerts, analyticsData,
      chatMessages, chatInput, chatMessagesEl, chatLoading,
      trendData, weeklyData, compareData, savingTips, compareMonth1, compareMonth2,
      showProfileModal, profileForm,
      txnForm, walletForm, catForm, budgetForm, transferForm,
      ocrFile, ocrPreview, ocrResult, ocrConfirmForm, iconOptions,
      incomeCategories, expenseCategories, filteredCategories,
      dashboardDoughnutData, dashboardBarData, trendBarData, weeklyLineData,
      formatVND, showToast, budgetPct, formatChatText, walletTypeIcon, openAuthModal, isFontAwesome,
      doLogin, doRegister, doLogout, openProfileModal, saveProfile, doCleanupCategories, doCleanupAll,
      loadAllData, loadAnalytics, createTransaction, deleteTransaction, createWallet, deleteWallet, doTransfer,
      createCategory, deleteCategory, createBudget, deleteBudget,
      handleOCRUpload, handleOCRDrop, scanInvoice, confirmOCRTransaction,
      sendChat, switchTab, switchTheme, loadAdminData, toggleBlockUser, adminDeleteTx, loadSavingTips, loadCompare
    }
  }
}
</script>

<style>
/* ─── RESET & CSS VARIABLES ──────────────── */
*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --bg-primary: rgba(10, 15, 29, 0.7);
  --bg-secondary: rgba(17, 24, 39, 0.85);
  --bg-card: rgba(17, 27, 46, 0.75);
  --bg-card-hover: rgba(30, 41, 59, 0.85);
  --jade: #059669;
  --jade-glow: #10B981;
  --jade-dim: rgba(16, 185, 129, 0.15);
  --gold: #D97706;
  --gold-glow: #F59E0B;
  --gold-dim: rgba(245, 158, 11, 0.15);
  --purple: #7C3AED;
  --purple-glow: #A78BFA;
  --crimson: #DC2626;
  --crimson-glow: #EF4444;
  --text-primary: #F8FAFC;
  --text-secondary: #CBD5E1;
  --text-dim: #94A3B8;
  --border: rgba(255, 255, 255, 0.12);
  --border-glow: rgba(16, 185, 129, 0.4);
  --radius: 14px;
  --radius-lg: 20px;
  --font-body: 'Inter', -apple-system, sans-serif;
  --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  --cursor-pointer: pointer;
}

body {
  font-family: var(--font-body);
  background: #060913;
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
  overflow-x: hidden;
}

button, a, select, input, textarea, label {
  cursor: var(--cursor-pointer);
}

/* ─── VIDEO BACKGROUND ───────────────────── */
#bg-video, .global-video-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  object-fit: cover;
  z-index: -2;
  pointer-events: none;
}

.global-video-overlay {
  position: fixed;
  inset: 0;
  background: rgba(6, 9, 19, 0.72);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: -1;
  pointer-events: none;
}

/* ─── MODERN THEME OVERRIDES ─────────────── */
body[data-theme='modern'] {
  background: #F1F5F9;
  color: #0F172A;
}

body[data-theme='modern'] #bg-video,
body[data-theme='modern'] .global-video-bg,
body[data-theme='modern'] .global-video-overlay {
  display: none !important;
}

body[data-theme='modern'] {
  --bg-primary: #FFFFFF;
  --bg-secondary: #F8FAFC;
  --bg-card: #FFFFFF;
  --bg-card-hover: #F1F5F9;
  --text-primary: #0F172A;
  --text-secondary: #334155;
  --text-dim: #64748B;
  --border: #E2E8F0;
  --border-glow: #2563EB;
  --jade: #2563EB;
  --jade-glow: #3B82F6;
  --jade-dim: rgba(59, 130, 246, 0.1);
  --glass-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.08);
}

/* ─── AUDIO FAB & WELCOME ────────────────── */
.audio-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--bg-card);
  border: 1px solid var(--border);
  box-shadow: var(--glass-shadow);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  z-index: 999;
  backdrop-filter: blur(10px);
  transition: all 0.3s;
}
.audio-fab:hover {
  transform: scale(1.1);
  border-color: var(--gold-glow);
}

.welcome-overlay {
  position: fixed;
  inset: 0;
  background: rgba(6, 9, 19, 0.85);
  backdrop-filter: blur(16px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.5s ease-out;
}
.welcome-text {
  font-size: 32px;
  font-weight: 700;
  color: var(--gold-glow);
  text-shadow: 0 0 25px rgba(245, 158, 11, 0.5);
  text-align: center;
}

/* ─── GLASS PANEL UTILITY ────────────────── */
.glass-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: var(--glass-shadow);
}

/* ─── HEADER / NAVBAR ────────────────────── */
.realm-header {
  position: sticky;
  top: 12px;
  margin: 12px 24px 0;
  padding: 14px 28px;
  z-index: 100;
}
.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}
.header-symbol {
  font-size: 24px;
  color: var(--jade-glow);
}
.header-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.3px;
}
.version-badge {
  font-size: 11px;
  background: var(--jade-dim);
  color: var(--jade-glow);
  border: 1px solid var(--jade-glow);
  padding: 2px 8px;
  border-radius: 12px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.theme-btn {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.3s;
}
.theme-btn:hover {
  border-color: var(--gold-glow);
}

.btn-auth-login {
  background: linear-gradient(135deg, var(--jade), var(--jade-glow));
  color: white;
  border: none;
  padding: 8px 18px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s;
}
.btn-auth-login:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
}

.btn-auth-register {
  background: linear-gradient(135deg, var(--gold), var(--gold-glow));
  color: white;
  border: none;
  padding: 8px 18px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s;
}
.btn-auth-register:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
}

.user-badge-btn {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}
.user-badge-btn:hover {
  border-color: var(--jade-glow);
}

.btn-logout {
  background: rgba(220, 38, 38, 0.15);
  border: 1px solid var(--crimson-glow);
  color: var(--crimson-glow);
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s;
}
.btn-logout:hover {
  background: var(--crimson);
  color: white;
}

/* ─── TAB NAVIGATION ─────────────────────── */
.tab-nav {
  margin: 16px 24px 0;
}
.tab-nav-inner {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}
.tab-btn {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: 10px 18px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
  white-space: nowrap;
}
.tab-btn:hover {
  color: var(--text-primary);
  border-color: var(--gold-glow);
}
.tab-btn.active {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(245, 158, 11, 0.2));
  border-color: var(--gold-glow);
  color: var(--gold-glow);
  box-shadow: 0 0 15px rgba(245, 158, 11, 0.2);
}

/* ─── MAIN REALM CONTENT ─────────────────── */
.realm-content {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.section-header-flex {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.section-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--gold-glow);
}
.sub-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
}

/* ─── LANDING WELCOME HERO ───────────────── */
.landing-welcome-section {
  padding: 48px 36px;
  text-align: center;
  margin-bottom: 28px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(245, 158, 11, 0.1));
}
.welcome-badge {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.5px;
  background: var(--gold-dim);
  color: var(--gold-glow);
  border: 1px solid var(--gold-glow);
  padding: 4px 14px;
  border-radius: 20px;
  margin-bottom: 16px;
}
.landing-title {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 16px;
  color: var(--text-primary);
}
.landing-desc {
  max-width: 780px;
  margin: 0 auto 28px;
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.8;
}
.landing-cta-row {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn-lg {
  padding: 14px 28px;
  font-size: 15px;
  border-radius: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}
.btn-jade {
  background: linear-gradient(135deg, var(--jade), var(--jade-glow));
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}
.btn-jade:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
}
.btn-gold {
  background: linear-gradient(135deg, var(--gold), var(--gold-glow));
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}
.btn-gold:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
}
.btn-secondary-sm {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s;
}
.btn-secondary-sm:hover {
  border-color: var(--gold-glow);
  color: var(--gold-glow);
}

/* ─── METRICS CARDS ──────────────────────── */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}
.metric-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--glass-shadow);
  transition: transform 0.3s;
}
.metric-card:hover {
  transform: translateY(-3px);
}
.metric-card.jade { border-left: 4px solid var(--jade-glow); }
.metric-card.crimson { border-left: 4px solid var(--crimson-glow); }
.metric-card.gold { border-left: 4px solid var(--gold-glow); }
.metric-card.purple { border-left: 4px solid var(--purple-glow); }

.metric-icon {
  font-size: 28px;
  color: var(--gold-glow);
}
.metric-card.jade .metric-icon { color: var(--jade-glow); }
.metric-card.crimson .metric-icon { color: var(--crimson-glow); }
.metric-card.purple .metric-icon { color: var(--purple-glow); }

.metric-info {
  display: flex;
  flex-direction: column;
}
.metric-label {
  font-size: 13px;
  color: var(--text-dim);
}
.metric-value {
  font-size: 20px;
  font-weight: 700;
}
.metric-value.positive { color: var(--jade-glow); }
.metric-value.negative { color: var(--crimson-glow); }

/* ─── SMART ANALYTICS & FORECASTING CARD ── */
.smart-analytics-card {
  padding: 24px;
  margin-bottom: 28px;
  border-left: 4px solid var(--jade-glow);
  transition: all 0.3s ease;
}
.smart-analytics-card.warning-border {
  border-left: 4px solid var(--gold-glow);
}
.analytics-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.analytics-title-group {
  display: flex;
  align-items: center;
  gap: 14px;
}
.analytics-icon {
  font-size: 32px;
}
.analytics-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--gold-glow);
}
.analytics-subtitle {
  font-size: 13px;
  color: var(--text-dim);
}
.analytics-status-badge {
  font-size: 12px;
  font-weight: 700;
  padding: 6px 14px;
  border-radius: 20px;
  letter-spacing: 0.5px;
}
.badge-success {
  background: var(--jade-dim);
  color: var(--jade-glow);
  border: 1px solid var(--jade-glow);
}
.badge-warning {
  background: var(--gold-dim);
  color: var(--gold-glow);
  border: 1px solid var(--gold-glow);
}
.badge-danger {
  background: rgba(220, 38, 38, 0.15);
  color: var(--crimson-glow);
  border: 1px solid var(--crimson-glow);
}

.analytics-metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 18px;
}
.analytics-metric-box {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.box-label {
  font-size: 12px;
  color: var(--text-dim);
  font-weight: 600;
}
.box-value {
  font-size: 18px;
  font-weight: 800;
}
.box-sub {
  font-size: 11px;
  color: var(--text-dim);
}
.gold-text {
  color: var(--gold-glow);
}

.warning-reasons-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}
.warning-reason-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.3);
  padding: 10px 16px;
  border-radius: 10px;
  font-size: 13px;
  color: var(--gold-glow);
}
.reason-bullet {
  font-size: 16px;
}

.forecast-message-box {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 18px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
}
.message-icon {
  font-size: 20px;
  flex-shrink: 0;
}
.box-success {
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: var(--text-primary);
}
.box-warning {
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: var(--text-primary);
}
.box-danger {
  background: rgba(220, 38, 38, 0.12);
  border: 1px solid rgba(220, 38, 38, 0.3);
  color: var(--text-primary);
}

/* ─── FEATURES GRID ──────────────────────── */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}
.feature-card {
  padding: 28px;
  cursor: pointer;
  transition: all 0.3s;
}
.feature-card:hover {
  transform: translateY(-4px);
  border-color: var(--gold-glow);
}
.feature-icon {
  font-size: 32px;
  margin-bottom: 12px;
  color: var(--gold-glow);
}
.feature-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--gold-glow);
}
.feature-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* ─── CHARTS & SECTIONS ──────────────────── */
.dashboard-charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 28px;
}
.charts-grid-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
.chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
}

.saving-tips-section {
  margin-bottom: 28px;
}
.saving-tips-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.saving-tips-card {
  padding: 20px;
}
.tips-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
  font-size: 14px;
  color: var(--text-dim);
}
.tips-content {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
}

/* ─── TABLES ─────────────────────────────── */
.table-scroll {
  overflow-x: auto;
}
.xianxia-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}
.xianxia-table th {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-dim);
  font-size: 13px;
  font-weight: 600;
  border-bottom: 1px solid var(--border);
}
.xianxia-table td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
}
.xianxia-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}
.amt-income { color: var(--jade-glow); font-weight: 600; }
.amt-expense { color: var(--crimson-glow); font-weight: 600; }
.cat-badge {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.cat-inline-icon {
  color: var(--gold-glow);
  font-size: 14px;
}

/* ─── FORMS & INPUTS ─────────────────────── */
.form-card, .table-card {
  padding: 24px;
  margin-bottom: 24px;
}
.form-card-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--gold-glow);
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}
.two-col-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
.input-group-xianxia {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
}
.input-group-xianxia label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-dim);
}
.input-group-xianxia input,
.input-group-xianxia select {
  padding: 10px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
}
.input-group-xianxia input:focus,
.input-group-xianxia select:focus {
  border-color: var(--gold-glow);
}
.form-action-right {
  display: flex;
  justify-content: flex-end;
}
.btn-block {
  width: 100%;
}
.btn-jade-sm {
  padding: 8px 16px;
  background: var(--jade);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.btn-del-sm, .btn-del-mini {
  background: transparent;
  border: none;
  font-size: 14px;
  cursor: pointer;
  color: var(--text-dim);
  transition: color 0.2s;
}
.btn-del-sm:hover, .btn-del-mini:hover {
  color: var(--crimson-glow);
}

/* ─── WALLET CARDS ───────────────────────── */
.wallet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}
.wallet-card {
  padding: 20px;
}
.wallet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.wallet-type-icon { font-size: 24px; }
.wallet-name { font-size: 16px; font-weight: 700; }
.wallet-balance-val { font-size: 22px; font-weight: 800; color: var(--jade-glow); }

/* ─── CATEGORY CHOICES ───────────────────── */
.icon-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.icon-choice {
  font-size: 16px;
  width: 38px;
  height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s;
}
.icon-choice:hover {
  border-color: var(--gold-glow);
  color: var(--gold-glow);
}
.icon-choice.active {
  border-color: var(--gold-glow);
  background: var(--gold-dim);
  color: var(--gold-glow);
}
.category-badges-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.cat-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  padding: 8px 14px;
  border-radius: 12px;
  font-size: 14px;
}
.cat-pill-icon {
  color: var(--gold-glow);
  font-size: 15px;
}
.cat-pill-name {
  font-weight: 600;
}
.cat-pill-type {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 6px;
}
.cat-pill-type.INCOME { background: var(--jade-dim); color: var(--jade-glow); }
.cat-pill-type.EXPENSE { background: rgba(220, 38, 38, 0.15); color: var(--crimson-glow); }

/* ─── OCR DROPZONE ───────────────────────── */
.ocr-dropzone {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 32px 20px;
  text-align: center;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}
.ocr-dropzone:hover {
  border-color: var(--gold-glow);
  background: rgba(245, 158, 11, 0.05);
}
.ocr-file-input { display: none; }
.ocr-camera-icon { font-size: 36px; margin-bottom: 8px; display: block; color: var(--gold-glow); }
.ocr-img-preview { max-width: 100%; max-height: 250px; border-radius: 8px; margin-bottom: 12px; object-fit: contain; }
.btn-reupload {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 12px;
}
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-dim);
  font-size: 14px;
  line-height: 1.6;
}

/* ─── BUDGETS PROGRESS ───────────────────── */
.budget-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}
.budget-item-card {
  padding: 20px;
}
.budget-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.budget-cat-name { font-weight: 700; font-size: 15px; display: flex; align-items: center; gap: 8px; }
.budget-cat-val { font-size: 13px; color: var(--text-dim); }
.budget-progress-bar {
  width: 100%;
  height: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}
.budget-progress-fill {
  height: 100%;
  background: var(--jade-glow);
  border-radius: 4px;
  transition: width 0.4s;
}
.budget-progress-fill.warning { background: var(--gold-glow); }
.budget-progress-fill.danger { background: var(--crimson-glow); }
.budget-pct-text { font-size: 12px; color: var(--text-dim); text-align: right; }

/* ─── COMPARE CONTROLS ───────────────────── */
.compare-controls {
  padding: 20px;
  margin-bottom: 24px;
}
.compare-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}
.compare-vs { font-weight: 800; color: var(--gold-glow); }
.compare-results {
  display: flex;
  gap: 24px;
}
.compare-card {
  background: var(--bg-secondary);
  padding: 12px 18px;
  border-radius: 10px;
  font-size: 14px;
}

/* ─── CHAT CONTAINER ─────────────────────── */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 600px;
}
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.chat-welcome {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: rgba(124, 58, 237, 0.1);
  border: 1px solid rgba(124, 58, 237, 0.3);
  border-radius: 12px;
  padding: 16px;
}
.chat-ai-avatar { font-size: 24px; color: var(--purple-glow); }
.chat-bubble {
  display: flex;
  gap: 10px;
  max-width: 80%;
}
.user-bubble { align-self: flex-end; flex-direction: row-reverse; }
.ai-bubble { align-self: flex-start; }
.bubble-avatar { font-size: 18px; color: var(--gold-glow); display: flex; align-items: center; justify-content: center; }
.bubble-content {
  padding: 12px 16px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.6;
}
.user-bubble .bubble-content {
  background: var(--jade);
  color: white;
}
.ai-bubble .bubble-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-primary);
}
.typing-indicator span {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: var(--gold-glow);
  border-radius: 50%;
  margin: 0 2px;
  animation: bounce 1.2s infinite ease-in-out;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

.chat-input-area {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid var(--border);
}
.chat-input-area input {
  flex: 1;
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 10px;
  color: var(--text-primary);
}

/* ─── MODALS & BACKDROP ──────────────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.modal-card {
  width: 100%;
  max-width: 480px;
  padding: 28px;
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.modal-title { font-size: 18px; font-weight: 700; color: var(--gold-glow); }
.modal-close { background: transparent; border: none; font-size: 20px; color: var(--text-dim); }
.modal-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}
.modal-tab-btn {
  flex: 1;
  padding: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  border-radius: 8px;
  font-weight: 600;
}
.modal-tab-btn.active {
  background: var(--gold-dim);
  border-color: var(--gold-glow);
  color: var(--gold-glow);
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}
.btn-secondary {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  border-radius: 8px;
}

/* ─── TOASTS & ALERTS ────────────────────── */
.toast-notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  z-index: 9999;
}
.toast-notification.success { background: var(--jade); color: white; }
.toast-notification.error { background: var(--crimson); color: white; }

.error-banner {
  margin-top: 16px;
  padding: 12px;
  border-radius: 8px;
  background: rgba(220, 38, 38, 0.2);
  border: 1px solid var(--crimson-glow);
  color: var(--crimson-glow);
  font-size: 13px;
}

.alerts-section { margin-bottom: 24px; }
.alert-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 18px;
  border-radius: 10px;
  margin-bottom: 8px;
}
.alert-card.warning { background: rgba(245, 158, 11, 0.15); border: 1px solid var(--gold-glow); color: var(--gold-glow); }
.alert-card.danger { background: rgba(220, 38, 38, 0.15); border: 1px solid var(--crimson-glow); color: var(--crimson-glow); }
.alert-msg { flex: 1; font-size: 14px; }
.alert-pct { font-weight: 700; }

.role-badge.admin { background: var(--gold-dim); color: var(--gold-glow); padding: 2px 8px; border-radius: 6px; }
.role-badge.user { background: var(--jade-dim); color: var(--jade-glow); padding: 2px 8px; border-radius: 6px; }
.status-active { color: var(--jade-glow); }
.status-blocked { color: var(--crimson-glow); }
.btn-block-sm {
  padding: 4px 10px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-primary);
  border-radius: 6px;
}

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

@media (max-width: 768px) {
  .dashboard-charts-row, .two-col-grid, .charts-grid-stats, .analytics-metrics-grid { grid-template-columns: 1fr; }
  .header-inner { flex-direction: column; gap: 12px; }
  .landing-cta-row { flex-direction: column; }
  .analytics-header { flex-direction: column; align-items: flex-start; gap: 10px; }
}
</style>
