<template>
  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- CÀN KHÔN LINH THẠCH CÁC v3.0 — GIAO DIỆN TU TIÊN     -->
  <!-- ═══════════════════════════════════════════════════════ -->

  <div class="finance-app-root" :class="{ 'modern-mode': currentTheme === 'modern' }">
    <!-- PERSISTENT XIANXIA CELESTIAL BACKDROP -->
    <div class="xianxia-backdrop">
      <div class="sun-aura-glow"></div>
      <div class="mountain-layer far-mountains">
        <svg viewBox="0 0 1440 320" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
          <path fill="#7ba3c4" fill-opacity="0.45" d="M0,160 Q120,80 240,150 T480,100 T720,170 T960,90 T1200,160 T1440,110 L1440,320 L0,320 Z"></path>
        </svg>
      </div>
      <div class="mountain-layer mid-mountains">
        <svg viewBox="0 0 1440 320" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
          <path fill="#4b759a" fill-opacity="0.65" d="M0,210 L60,160 L90,185 L140,130 L180,175 L250,110 L310,180 L380,135 L440,200 L510,120 L580,190 L670,140 L740,210 L820,125 L900,200 L980,130 L1060,190 L1150,140 L1230,210 L1320,150 L1440,190 L1440,320 L0,320 Z"></path>
        </svg>
      </div>
      <div class="mountain-layer near-mountains">
        <svg viewBox="0 0 1440 320" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
          <path fill="#2c4660" fill-opacity="0.9" d="M0,260 L40,210 L80,240 L130,170 L180,230 L230,190 L290,270 L350,195 L400,245 L480,175 L540,255 L610,190 L680,275 L760,185 L820,245 L890,170 L950,235 L1020,180 L1100,265 L1180,190 L1250,250 L1340,195 L1440,240 L1440,320 L0,320 Z"></path>
        </svg>
      </div>
      <div class="sea-of-clouds-wrapper">
        <div class="sea-of-clouds wave-1"></div>
        <div class="sea-of-clouds wave-2"></div>
      </div>
      <div class="floating-clouds">
        <div class="cloud-cluster cloud-1"></div>
        <div class="cloud-cluster cloud-2"></div>
        <div class="cloud-cluster cloud-3"></div>
      </div>
      <div class="spirit-particle-field">
        <div v-for="n in 25" :key="n" :class="'spirit-particle p-' + n"></div>
      </div>
    </div>

    <!-- AUTHENTICATION REALM (STITCH CELESTIAL TREASURY) -->
    <AuthShell
      v-if="!isLoggedIn"
      :current-theme="currentTheme"
      @switch-theme="switchTheme"
    >
      <LoginCard
        v-if="authMode === 'login'"
        :form="authForm"
        :loading="loading"
        :error-msg="errorMsg"
        @submit="doLogin"
        @switch-mode="handleSwitchAuthMode"
      />
      <RegisterCard
        v-else-if="authMode === 'register'"
        :form="authForm"
        :loading="loading"
        :error-msg="errorMsg"
        @submit="doRegister"
        @switch-mode="handleSwitchAuthMode"
      />
      <ForgotPasswordCard
        v-else-if="authMode === 'forgot'"
        :form="forgotForm"
        :loading="loading"
        :error-msg="errorMsg"
        @submit="doForgotPassword"
        @switch-mode="handleSwitchAuthMode"
      />
      <ResetPasswordCard
        v-else-if="authMode === 'reset'"
        :form="resetForm"
        :loading="loading"
        :error-msg="errorMsg"
        @submit="doResetPassword"
        @switch-mode="handleSwitchAuthMode"
      />
    </AuthShell>

  <!-- MAIN APP -->
  <div v-else class="app-realm" :class="{ 'app-realm-behind-overlay': isKhiLinhOpen }">
    <!-- ═══ APP HEADER & NAVIGATION (STITCH CELESTIAL DESIGN) ═══ -->
    <AppHeader
      :active-tab="activeTab"
      :tabs="tabs"
      :user-name="userName"
      :user-role="userRole"
      :is-user-admin="isUserAdmin"
      :current-theme="currentTheme"
      :can-scroll-nav-left="canScrollNavLeft"
      :can-scroll-nav-right="canScrollNavRight"
      @switch-tab="switchTab"
      @open-profile="openProfileModal"
      @switch-theme="switchTheme"
      @logout="doLogout"
      @scroll-nav="scrollNav"
    />

    <!-- CONTENT AREA -->
    <main class="realm-content">
      <!-- ═══════ TAB 1: DASHBOARD (STITCH CELESTIAL MODERN) ═══════ -->
      <section v-if="activeTab === 'dashboard'" class="tab-panel">
        <DashboardView
          :summary="summary"
          :budget-alerts="budgetAlerts"
          :trend-data="trendData"
          :dashboard-doughnut-data="dashboardDoughnutData"
          :dashboard-bar-data="dashboardBarData"
          :saving-tips="savingTips"
          :loading-tips="loadingTips"
          :transactions="transactions"
          :user-name="userName"
          :user-role="userRole"
          :max-category-expense="maxCategoryExpense"
          :format-v-n-d="formatVND"
          :format-chat-text="formatChatText"
          @load-saving-tips="loadSavingTips"
          @switch-tab="switchTab"
        />
      </section>

      <!-- ═══════ TAB 2: TRANSACTIONS (STITCH CELESTIAL LEDGER) ═══════ -->
      <section v-if="activeTab === 'transactions'" class="tab-panel">
        <TransactionsView
          :wallets="wallets"
          :categories="categories"
          :transactions="transactions"
          :recurring-list="recurringList"
          :txn-form="txnForm"
          :recurring-form="recurringForm"
          :txn-filter="txnFilter"
          :txn-pagination="txnPagination"
          :total-pages="totalPages"
          :loading="loading"
          :formatVND="formatVND"
          @create-transaction="createTransaction"
          @delete-transaction="deleteTransaction"
          @create-recurring="createRecurring"
          @toggle-recurring="toggleRecurring"
          @delete-recurring="deleteRecurring"
          @edit-recurring="openEditRecurring"
          @change-page="changeTxnPage"
          @reset-filter="resetTxnFilter"
          @filter-change="loadTransactions(true)"
          @export-reports="doExportReports"
        />
      </section>

      <!-- ═══════ TAB: DEBTS (SỔ NỢ / VAY MƯỢN — CELESTIAL TREASURY) ═══════ -->
      <section v-if="activeTab === 'debts'" class="tab-panel">
        <DebtsView
          :debts="debts"
          :debts-summary="debtsSummary"
          :debt-filter="debtFilter"
          :debt-form="debtForm"
          :wallets="wallets"
          :loading="loading"
          :formatVND="formatVND"
          @create-debt="createDebt"
          @delete-debt="deleteDebt"
          @open-edit-debt="openEditDebt"
          @toggle-settle-debt="toggleSettleDebt"
          @load-debts="loadDebts"
        />
      </section>

      <!-- ═══════ TAB: WALLETS (TÚI CÀN KHÔN — CELESTIAL TREASURY) ═══════ -->
      <section v-if="activeTab === 'wallets'" class="tab-panel">
        <WalletsView
          :wallets="wallets"
          :wallet-form="walletForm"
          :transfer-form="transferForm"
          :loading="loading"
          :formatVND="formatVND"
          :wallet-type-icon="walletTypeIcon"
          @create-wallet="createWallet"
          @delete-wallet="deleteWallet"
          @edit-wallet="openEditWallet"
          @do-transfer="doTransfer"
        />
      </section>

      <!-- ═══════ TAB 4: CATEGORIES (CÀN KHÔN BÁCH KHOA ẤN — CELESTIAL TREASURY) ═══════ -->
      <section v-if="activeTab === 'categories'" class="tab-panel">
        <CategoriesView
          :categories="categories"
          :income-categories="incomeCategories"
          :expense-categories="expenseCategories"
          :cat-form="catForm"
          :icon-options="iconOptions"
          :loading="loading"
          @create-category="createCategory"
          @delete-category="deleteCategory"
          @open-edit-category="openEditCategory"
          @load-categories="loadCategories"
        />
      </section>

      <!-- ═══════ TAB 5: OCR INVOICE (LINH NHÃN TẦM BẢO — CELESTIAL TREASURY) ═══════ -->
      <section v-if="activeTab === 'ocr'" class="tab-panel">
        <OcrView
          :ocr-file="ocrFile"
          :ocr-preview="ocrPreview"
          :ocr-result="ocrResult"
          :ocr-confirm-form="ocrConfirmForm"
          :wallets="wallets"
          :expense-categories="expenseCategories"
          :loading="loading"
          :formatVND="formatVND"
          @ocr-upload="handleOCRUpload"
          @ocr-drop="handleOCRDrop"
          @scan-invoice="scanInvoice"
          @confirm-ocr-transaction="confirmOCRTransaction"
          @reset-ocr="resetOCR"
        />
      </section>

      <!-- ═══════ TAB 6: BUDGETS (HẠN MỨC TU LUYỆN — CELESTIAL TREASURY) ═══════ -->
      <section v-if="activeTab === 'budgets'" class="tab-panel">
        <BudgetsView
          :budgets="budgets"
          :budget-month="budgetMonth"
          :expense-categories="expenseCategories"
          :budget-form="budgetForm"
          :loading="loading"
          :formatVND="formatVND"
          @update:budget-month="onBudgetMonthChange"
          @create-budget="createBudget"
          @open-edit-budget="openEditBudget"
          @delete-budget="deleteBudget"
          @load-budgets="loadBudgets"
        />
      </section>

      <!-- ═══════ TAB: SAVING GOALS (MỤC TIÊU TIẾT KIỆM — CELESTIAL TREASURY) ═══════ -->
      <section v-if="activeTab === 'goals'" class="tab-panel">
        <SavingGoalsView
          :saving-goals="savingGoals"
          :goals-summary="goalsSummary"
          :goal-form="goalForm"
          :loading="loading"
          :formatVND="formatVND"
          @create-goal="createSavingGoal"
          @open-edit-goal="openEditGoal"
          @open-deposit-goal="openDepositGoal"
          @delete-goal="deleteSavingGoal"
          @load-goals="loadSavingGoals"
        />
      </section>

      <!-- ═══════ TAB 7: STATISTICS (THIÊN CƠ THỐNG KÊ — CELESTIAL TREASURY) ═══════ -->
      <section v-if="activeTab === 'stats'" class="tab-panel">
        <StatisticsView
          :trend-data="trendData"
          :weekly-data="weeklyData"
          :summary="summary"
          :trend-bar-data="trendBarData"
          :weekly-line-data="weeklyLineData"
          :stats-doughnut-data="statsDoughnutData"
          :stats-date-range="statsDateRange"
          :preset-ranges="presetRanges"
          :compare-month1="compareMonth1"
          :compare-month2="compareMonth2"
          :compare-data="compareData"
          :saving-tips="savingTips"
          :loading="loading"
          :loading-tips="loadingTips"
          :current-theme="currentTheme"
          :vi-locale="viLocale"
          :formatVND="formatVND"
          :formatChatText="formatChatText"
          @update:stats-date-range="statsDateRange = $event"
          @stats-date-change="onStatsDateChange"
          @do-export="doExport"
          @update:compare-month1="compareMonth1 = $event"
          @update:compare-month2="compareMonth2 = $event"
          @load-compare="loadCompare"
          @load-saving-tips="loadSavingTips"
        />
      </section>

      <!-- ═══════ TAB 8: KHÍ LINH KNOWLEDGE (CELESTIAL TREASURY) ═══════ -->
      <section v-if="activeTab === 'chat'" class="tab-panel">
        <KnowledgePanel
          :chat-messages="chatMessages"
          :chat-loading="chatLoading"
          :suggested-questions="suggestedQuestions"
          :user-name="userName"
          @send-message="sendChat($event)"
          @clear-history="chatMessages = []"
        />
      </section>

      <!-- ═══════ TAB: ADMIN & ROLE MANAGEMENT (CELESTIAL TREASURY) ═══════ -->
      <section v-if="activeTab === 'admin' && isUserAdmin" class="tab-panel">
        <AdminPanel
          :admin-stats="adminStats"
          :admin-users="adminUsers"
          :current-user-id="currentUserId"
          :loading="loading"
          @toggle-user-active="toggleUserActive"
          @change-user-role="changeUserRole($event.user, $event.newRole)"
          @refresh-users="loadAdminUsers(); loadAdminStats()"
        />
      </section>

      <!-- ═══════ TAB: PROFILE (HỒ SƠ BẢO MẬT — CELESTIAL TREASURY) ═══════ -->
      <section v-if="activeTab === 'profile'" class="tab-panel">
        <ProfileView
          :is-modal="false"
          :user-name="userName"
          :user-email="userEmail"
          :user-role="userRole"
          :is-user-admin="isUserAdmin"
          :total-balance="summary?.total_balance || 0"
          :loading-profile="loadingProfile"
          :loading-soul-lamp="loadingSoulLamp"
          :loading-password="loadingPassword"
          :format-v-n-d="formatVND"
          @save-profile="saveProfile"
          @save-soul-lamp="saveSoulLamp"
          @change-password="changePassword"
          @logout="doLogout"
        />
      </section>
    </main>

    <!-- ═══ APP FOOTER (STITCH CELESTIAL DESIGN) ═══ -->
    <AppFooter />

    <!-- REQUIREMENT 5: ACCOUNT MANAGEMENT MODAL (STITCH CELESTIAL DESIGN) -->
    <ProfileView
      v-if="showProfileModal"
      :is-modal="true"
      :user-name="userName"
      :user-email="userEmail"
      :user-role="userRole"
      :is-user-admin="isUserAdmin"
      :total-balance="summary?.total_balance || 0"
      :loading-profile="loadingProfile"
      :loading-soul-lamp="loadingSoulLamp"
      :loading-password="loadingPassword"
      :format-v-n-d="formatVND"
      @close="showProfileModal = false"
      @save-profile="saveProfile"
      @save-soul-lamp="saveSoulLamp"
      @change-password="changePassword"
      @logout="doLogout"
    />

    <!-- EDIT WALLET MODAL -->
    <div v-if="showEditWalletModal" class="modal-backdrop" @click.self="showEditWalletModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">✏️ Chỉnh Sửa Túi Càn Khôn</h3>
          <button class="modal-close" @click="showEditWalletModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="input-group-xianxia">
            <label>Tên Ví</label>
            <input v-model="editWalletForm.wallet_name" type="text" list="bankList" placeholder="Tên ví..." />
          </div>
          <div class="input-group-xianxia">
            <label>Loại Ví</label>
            <select v-model="editWalletForm.wallet_type">
              <option value="cash">💵 Tiền Mặt</option>
              <option value="bank">🏦 Ngân Hàng</option>
              <option value="e-wallet">📱 Ví Điện Tử</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showEditWalletModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="updateWallet" :disabled="loading">
            {{ loading ? '⏳...' : '💾 Cập Nhật Ví' }}
          </button>
        </div>
      </div>
    </div>

    <!-- EDIT CATEGORY MODAL -->
    <div v-if="showEditCatModal" class="modal-backdrop" @click.self="showEditCatModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">✏️ Chỉnh Sửa Danh Mục</h3>
          <button class="modal-close" @click="showEditCatModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="input-group-xianxia">
            <label>Tên Danh Mục</label>
            <input v-model="editCatForm.category_name" type="text" placeholder="Tên danh mục..." />
          </div>
          <div class="input-group-xianxia">
            <label>Biểu Tượng (Icon)</label>
            <select v-model="editCatForm.icon">
              <option v-for="ic in iconOptions" :key="'edit-ic-'+ic" :value="ic">{{ ic }}</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showEditCatModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="updateCategory" :disabled="loading">
            {{ loading ? '⏳...' : '💾 Cập Nhật Danh Mục' }}
          </button>
        </div>
      </div>
    </div>

    <!-- EDIT RECURRING MODAL -->
    <div v-if="showEditRecurringModal" class="modal-backdrop" @click.self="showEditRecurringModal = false">
      <div class="modal-card" style="max-width: 520px;">
        <div class="modal-header">
          <h3 class="modal-title">✏️ Sửa Linh Trận Định Kỳ</h3>
          <button class="modal-close" @click="showEditRecurringModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="input-group-xianxia">
              <label>Loại</label>
              <select v-model="editRecurringForm.transaction_type">
                <option value="EXPENSE">🔥 Tiêu Hao</option>
                <option value="INCOME">💎 Thu Hoạch</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Số Tiền (VNĐ)</label>
              <input v-model.number="editRecurringForm.amount" type="number" min="0" />
            </div>
            <div class="input-group-xianxia">
              <label>Túi Càn Khôn</label>
              <select v-model="editRecurringForm.wallet_id">
                <option v-for="w in wallets" :key="'ed-rec-w-'+w.id" :value="w.id">{{ w.wallet_name }}</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Danh Mục</label>
              <select v-model="editRecurringForm.category_id">
                <option v-for="c in categories.filter(cat => cat.category_type === editRecurringForm.transaction_type)" :key="'ed-rec-c-'+c.id" :value="c.id">
                  {{ c.icon }} {{ c.category_name }}
                </option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Tần Suất</label>
              <select v-model="editRecurringForm.frequency">
                <option value="monthly">📅 Hàng Tháng</option>
                <option value="weekly">📆 Hàng Tuần</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Ngày Chạy Kế Tiếp</label>
              <input v-model="editRecurringForm.next_run_date" type="date" />
            </div>
            <div class="input-group-xianxia" style="grid-column: 1 / -1;">
              <label>Ghi Chú</label>
              <input v-model="editRecurringForm.note" type="text" />
            </div>
            <div class="input-group-xianxia" style="grid-column: 1 / -1;">
              <label>Trạng Thái</label>
              <select v-model.number="editRecurringForm.is_active">
                <option :value="1">✅ Đang Kích Hoạt</option>
                <option :value="0">⏸️ Tạm Dừng</option>
              </select>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showEditRecurringModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="updateRecurring" :disabled="loading">
            {{ loading ? '⏳...' : '💾 Lưu Thay Đổi' }}
          </button>
        </div>
      </div>
    </div>

    <!-- EDIT DEBT MODAL -->
    <div v-if="showEditDebtModal" class="modal-backdrop" @click.self="showEditDebtModal = false">
      <div class="modal-card" style="max-width: 520px;">
        <div class="modal-header">
          <h3 class="modal-title">✏️ Chỉnh Sửa Khoản Nợ</h3>
          <button class="modal-close" @click="showEditDebtModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="input-group-xianxia">
              <label>Loại Khoản Nợ</label>
              <select v-model="editDebtForm.debt_type">
                <option value="BORROW">🔴 Tôi Vay Nợ (Cần trả)</option>
                <option value="LEND">🟢 Tôi Cho Vay (Cần thu)</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Đối Tác</label>
              <input v-model="editDebtForm.person_name" type="text" />
            </div>
            <div class="input-group-xianxia">
              <label>Số Tiền (VNĐ)</label>
              <input v-model.number="editDebtForm.amount" type="number" min="0" />
            </div>
            <div class="input-group-xianxia">
              <label>Ngày Đến Hạn</label>
              <input v-model="editDebtForm.due_date" type="date" />
            </div>
            <div class="input-group-xianxia">
              <label>Ví Liên Kết</label>
              <select v-model="editDebtForm.wallet_id">
                <option value="">— Không liên kết —</option>
                <option v-for="w in wallets" :key="'ed-debt-w-'+w.id" :value="w.id">{{ w.wallet_name }}</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Trạng Thái</label>
              <select v-model.number="editDebtForm.is_settled">
                <option :value="0">⏳ Chưa Tất Toán</option>
                <option :value="1">✅ Đã Tất Toán</option>
              </select>
            </div>
            <div class="input-group-xianxia" style="grid-column: 1 / -1;">
              <label>Ghi Chú</label>
              <input v-model="editDebtForm.note" type="text" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showEditDebtModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="updateDebt" :disabled="loading">
            {{ loading ? '⏳...' : '💾 Lưu Thay Đổi' }}
          </button>
        </div>
      </div>
    </div>

    <!-- EDIT SAVING GOAL MODAL -->
    <div v-if="showEditGoalModal" class="modal-backdrop" @click.self="showEditGoalModal = false">
      <div class="modal-card" style="max-width: 520px;">
        <div class="modal-header">
          <h3 class="modal-title">✏️ Chỉnh Sửa Mục Tiêu Tiết Kiệm</h3>
          <button class="modal-close" @click="showEditGoalModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="input-group-xianxia">
              <label>Tên Mục Tiêu</label>
              <input v-model="editGoalForm.target_name" type="text" />
            </div>
            <div class="input-group-xianxia">
              <label>Số Tiền Đích (VNĐ)</label>
              <input v-model.number="editGoalForm.target_amount" type="number" min="0" />
            </div>
            <div class="input-group-xianxia">
              <label>Số Tiền Đang Có (VNĐ)</label>
              <input v-model.number="editGoalForm.current_amount" type="number" min="0" />
            </div>
            <div class="input-group-xianxia">
              <label>Thời Hạn</label>
              <input v-model="editGoalForm.target_date" type="date" />
            </div>
            <div class="input-group-xianxia">
              <label>Biểu Tượng</label>
              <select v-model="editGoalForm.icon">
                <option value="🎯">🎯 Mục Tiêu</option>
                <option value="💻">💻 Thiết Bị</option>
                <option value="🚗">🚗 Phương Tiện</option>
                <option value="🏠">🏠 Nhà Cửa</option>
                <option value="✈️">✈️ Du Ngoạn</option>
                <option value="🛡️">🛡️ Quỹ Dự Phòng</option>
                <option value="🎓">🎓 Học Tập</option>
                <option value="🎁">🎁 Quà Tặng</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Trạng Thái Hoàn Thành</label>
              <select v-model.number="editGoalForm.is_completed">
                <option :value="0">⏳ Đang Tích Lũy</option>
                <option :value="1">🎉 Đã Hoàn Thành</option>
              </select>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showEditGoalModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="updateSavingGoal" :disabled="loading">
            {{ loading ? '⏳...' : '💾 Lưu Thay Đổi' }}
          </button>
        </div>
      </div>
    </div>

    <!-- DEPOSIT / WITHDRAW SAVING GOAL MODAL -->
    <div v-if="showDepositModal" class="modal-backdrop" @click.self="showDepositModal = false">
      <div class="modal-card" style="max-width: 480px;">
        <div class="modal-header">
          <h3 class="modal-title">{{ depositForm.action === 'deposit' ? '➕ Nạp Linh Thạch Tích Lũy' : '➖ Rút Linh Thạch Khỏi Mục Tiêu' }}</h3>
          <button class="modal-close" @click="showDepositModal = false">✕</button>
        </div>
        <div class="modal-body">
          <p class="hint-text" style="margin-bottom: 16px;">Mục tiêu: <strong>{{ depositForm.goal_name }}</strong></p>
          <div class="input-group-xianxia">
            <label>Số Tiền {{ depositForm.action === 'deposit' ? 'Nạp (VNĐ)' : 'Rút (VNĐ)' }}</label>
            <input v-model.number="depositForm.amount" type="number" placeholder="0" min="0" />
          </div>
          <div class="input-group-xianxia">
            <label>{{ depositForm.action === 'deposit' ? 'Trừ Tiền Từ Ví (Tùy chọn)' : 'Cộng Tiền Vào Ví (Tùy chọn)' }}</label>
            <select v-model="depositForm.wallet_id">
              <option value="">— Không qua ví (tích lũy độc lập) —</option>
              <option v-for="w in wallets" :key="'dep-w-'+w.id" :value="w.id">{{ w.wallet_name }} ({{ formatVND(w.balance) }})</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showDepositModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="submitDepositWithdrawGoal" :disabled="loading || !depositForm.amount">
            {{ loading ? '⏳...' : (depositForm.action === 'deposit' ? '✨ Xác Nhận Nạp' : '⚡ Xác Nhận Rút') }}
          </button>
        </div>
      </div>
    </div>

    <!-- EDIT BUDGET MODAL -->
    <div v-if="showEditBudgetModal" class="modal-backdrop" @click.self="showEditBudgetModal = false">
      <div class="modal-card" style="max-width: 480px;">
        <div class="modal-header">
          <h3 class="modal-title">✏️ Chỉnh Sửa Hạn Mức Tu Luyện</h3>
          <button class="modal-close" @click="showEditBudgetModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="editBudgetForm.category_name" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; background: rgba(125,214,204,0.08); border: 1px solid rgba(125,214,204,0.2);">
            <div style="font-weight: 600; color: #7dd6cc; font-size: 1rem; display: flex; align-items: center; gap: 8px;">
              <span>{{ editBudgetForm.category_icon || '🎯' }}</span>
              <span>{{ editBudgetForm.category_name }}</span>
            </div>
            <div style="font-size: 0.85rem; color: #a3a3a3; margin-top: 4px;">
              Chu kỳ áp dụng: Tháng {{ editBudgetForm.month_year }}
            </div>
          </div>
          <div class="form-grid">
            <div class="input-group-xianxia">
              <label>Mức Giới Hạn Mới (VNĐ)</label>
              <input v-model.number="editBudgetForm.limit_amount" type="number" min="1" step="1000" placeholder="0" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showEditBudgetModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="updateBudget" :disabled="loading || !editBudgetForm.limit_amount || editBudgetForm.limit_amount <= 0">
            {{ loading ? '⏳...' : '💾 Lưu Thay Đổi' }}
          </button>
        </div>
      </div>
    </div>

    <!-- TOAST -->
    <div v-if="toast" class="toast-notification" :class="toast.type">
      {{ toast.message }}
    </div>

    <!-- PERSISTENT KHÍ LINH ASSISTANT COMPANION (Available across all pages) -->
    <KhiLinhAssistant
      v-if="isLoggedIn"
      :api="api"
      :is-open="isKhiLinhOpen"
      @update:is-open="isKhiLinhOpen = $event"
      @transaction-completed="onKhiLinhTransactionCompleted"
      @switch-tab="switchTab"
    />
  </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick, onErrorCaptured, watch } from 'vue'
import axios from 'axios'
import ChartComponent from './components/ChartComponents.vue'
import KhiLinhAssistant from './components/KhiLinhAssistant.vue'
import AppHeader from './components/common/AppHeader.vue'
import AppFooter from './components/common/AppFooter.vue'
import DashboardView from './components/dashboard/DashboardView.vue'
import TransactionsView from './components/transactions/TransactionsView.vue'
import WalletsView from './components/wallets/WalletsView.vue'
import DebtsView from './components/debts/DebtsView.vue'
import SavingGoalsView from './components/goals/SavingGoalsView.vue'
import BudgetsView from './components/budgets/BudgetsView.vue'
import CategoriesView from './components/categories/CategoriesView.vue'
import OcrView from './components/ocr/OcrView.vue'
import StatisticsView from './components/statistics/StatisticsView.vue'
import AuthShell from './components/auth/AuthShell.vue'
import LoginCard from './components/auth/LoginCard.vue'
import RegisterCard from './components/auth/RegisterCard.vue'
import ForgotPasswordCard from './components/auth/ForgotPasswordCard.vue'
import ResetPasswordCard from './components/auth/ResetPasswordCard.vue'
import ProfileView from './components/profile/ProfileView.vue'
import AdminPanel from './components/admin/AdminPanel.vue'
import KnowledgePanel from './components/khi-linh/KnowledgePanel.vue'
import { VueDatePicker } from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { vi } from 'date-fns/locale'

export default {
  name: 'CankKhonApp',
  components: {
    ChartComponent,
    VueDatePicker,
    KhiLinhAssistant,
    AppHeader,
    AppFooter,
    DashboardView,
    TransactionsView,
    WalletsView,
    DebtsView,
    SavingGoalsView,
    BudgetsView,
    CategoriesView,
    OcrView,
    StatisticsView,
    AuthShell,
    LoginCard,
    RegisterCard,
    ForgotPasswordCard,
    ResetPasswordCard,
    ProfileView,
    AdminPanel,
    KnowledgePanel
  },
  setup() {
    // ─── STATE ────────────────────
    const isLoggedIn = ref(false)
    const authMode = ref('login')
    const authForm = ref({ email: '', password: '', full_name: '', soul_lamp: '' })
    const currentTheme = ref(localStorage.getItem('app_theme') || 'xianxia')
    const forgotForm = ref({ email: '', soul_lamp: '' })
    const resetForm = ref({ email: '', token: '', new_password: '' })
    const token = ref('')
    const userName = ref('Ký Chủ')
    const userEmail = ref('')
    const loading = ref(false)
    const loadingTips = ref(false)
    const loadingProfile = ref(false)
    const loadingSoulLamp = ref(false)
    const loadingPassword = ref(false)
    const errorMsg = ref('')
    const toast = ref(null)
    const activeTab = ref('dashboard')
    const isKhiLinhOpen = ref(false)

    // Profile modal state
    const showProfileModal = ref(false)
    const profileForm = ref({ full_name: '' })
    const soulLampForm = ref({ current_password: '', new_soul_lamp: '' })

    // Edit Modals state
    const showEditWalletModal = ref(false)
    const editWalletForm = ref({ id: null, wallet_name: '', wallet_type: 'cash' })

    const showEditCatModal = ref(false)
    const editCatForm = ref({ id: null, category_name: '', icon: '📦' })

    const showEditBudgetModal = ref(false)
    const editBudgetForm = ref({ id: null, limit_amount: 0, category_name: '', category_icon: '🎯', month_year: '' })

    const showEditRecurringModal = ref(false)
    const editRecurringForm = ref({
      id: null, wallet_id: null, category_id: null, amount: 0,
      transaction_type: 'EXPENSE', frequency: 'monthly', next_run_date: '', note: '', is_active: 1
    })

    const userRole = ref(localStorage.getItem('xianxia_role') || 'user')
    const currentUserId = ref(parseInt(localStorage.getItem('xianxia_uid')) || null)

    const tabs = [
      { id: 'dashboard',    icon: '📊', label: 'Tổng Quan' },
      { id: 'transactions', icon: '💸', label: 'Giao Dịch' },
      { id: 'debts',        icon: '📜', label: 'Sổ Nợ' },
      { id: 'goals',        icon: '🎯', label: 'Mục Tiêu' },
      { id: 'wallets',      icon: '💳', label: 'Túi Càn Khôn' },
      { id: 'categories',   icon: '🏷️', label: 'Danh Mục' },
      { id: 'ocr',          icon: '🧾', label: 'Linh Nhãn OCR' },
      { id: 'budgets',      icon: '🎯', label: 'Hạn Mức' },
      { id: 'stats',        icon: '📈', label: 'Thống Kê' },
      { id: 'chat',         icon: '💬', label: 'Khí Linh AI' },
      { id: 'admin',        icon: '🛡️', label: 'Phân Quyền', adminOnly: true },
    ]

    // Navigation Scroll State
    const tabNavEl = ref(null)
    const canScrollNavLeft = ref(false)
    const canScrollNavRight = ref(false)

    // Admin State
    const adminStats = ref({})
    const adminUsers = ref([])
    const adminFilter = ref({ search: '', role: '', status: '' })

    // Data
    const wallets = ref([])
    const categories = ref([])
    const transactions = ref([])
    const budgets = ref([])
    const summary = ref({ total_income: 0, total_expense: 0, net_savings: 0, total_balance: 0, expense_by_category: [] })
    const budgetAlerts = ref([])
    const chatMessages = ref([])
    const chatInput = ref('')
    const chatMessagesEl = ref(null)
    const suggestedQuestions = ref([])

    // Debts State
    const debts = ref([])
    const debtsSummary = ref({
      total_borrow_unsettled: 0,
      total_lend_unsettled: 0,
      total_borrow_settled: 0,
      total_lend_settled: 0
    })
    const debtFilter = ref({ type: '', is_settled: '' })
    const debtForm = ref({
      debt_type: 'BORROW',
      person_name: '',
      amount: null,
      due_date: '',
      wallet_id: '',
      note: ''
    })
    const showEditDebtModal = ref(false)
    const editDebtForm = ref({
      id: null,
      debt_type: 'BORROW',
      person_name: '',
      amount: 0,
      due_date: '',
      wallet_id: '',
      note: '',
      is_settled: 0
    })

    // Saving Goals State
    const savingGoals = ref([])
    const goalsSummary = ref({
      total_target: 0,
      total_saved: 0,
      completed_count: 0,
      active_count: 0,
      overall_percent: 0
    })
    const goalForm = ref({
      target_name: '',
      target_amount: null,
      current_amount: 0,
      target_date: '',
      icon: '🎯'
    })
    const showEditGoalModal = ref(false)
    const editGoalForm = ref({
      id: null,
      target_name: '',
      target_amount: 0,
      current_amount: 0,
      target_date: '',
      icon: '🎯',
      is_completed: 0
    })
    const showDepositModal = ref(false)
    const depositForm = ref({
      goal_id: null,
      goal_name: '',
      amount: null,
      wallet_id: '',
      action: 'deposit'
    })

    // Recurring Transactions Data
    const showRecurringSection = ref(false)
    const recurringList = ref([])
    const recurringForm = ref({
      wallet_id: null, category_id: null, amount: 0,
      transaction_type: 'EXPENSE', frequency: 'monthly',
      next_run_date: new Date().toISOString().slice(0, 10), note: ''
    })

    // Transactions Filter & Pagination
    const txnFilter = ref({
      start_date: '', end_date: '', category_id: '',
      wallet_id: '', transaction_type: '', keyword: ''
    })
    const txnPagination = ref({
      page: 1,
      limit: 15,
      totalCount: 0
    })

    // New v3 data
    const trendData = ref({ trend: [] })
    const weeklyData = ref({ data: [] })
    const compareData = ref(null)
    const savingTips = ref(null)

    // Compare month defaults
    const now = new Date()
    const compareMonth2 = ref(now.toISOString().slice(0, 7))
    const prevMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1)
    const compareMonth1 = ref(prevMonth.toISOString().slice(0, 7))

    const budgetMonth = ref(now.toISOString().slice(0, 7))

    watch(budgetMonth, async (newVal) => {
      if (newVal) {
        await loadBudgets()
      }
    })

    const viLocale = vi

    const endNow = new Date()
    const start30Days = new Date(endNow)
    start30Days.setDate(endNow.getDate() - 30)
    const statsDateRange = ref([start30Days, endNow])
    
    const presetRanges = ref([
      { label: '7 ngày qua', value: () => { const e = new Date(); const s = new Date(e); s.setDate(e.getDate() - 7); return [s, e] } },
      { label: '30 ngày qua', value: () => { const e = new Date(); const s = new Date(e); s.setDate(e.getDate() - 30); return [s, e] } },
      { label: 'Tháng này', value: () => { const e = new Date(); const s = new Date(e.getFullYear(), e.getMonth(), 1); return [s, e] } },
      { label: 'Tháng trước', value: () => { const e = new Date(); const s = new Date(e.getFullYear(), e.getMonth() - 1, 1); const e2 = new Date(e.getFullYear(), e.getMonth(), 0); return [s, e2] } },
      { label: '3 tháng gần đây', value: () => { const e = new Date(); const s = new Date(e); s.setMonth(e.getMonth() - 3); return [s, e] } },
      { label: '6 tháng gần đây', value: () => { const e = new Date(); const s = new Date(e); s.setMonth(e.getMonth() - 6); return [s, e] } }
    ])

    function onStatsDateChange() {
      if (!statsDateRange.value || !statsDateRange.value[0] || !statsDateRange.value[1]) return
      
      let start = new Date(statsDateRange.value[0])
      let end = new Date(statsDateRange.value[1])
      
      if (end < start) {
        const tmp = start
        start = end
        end = tmp
        statsDateRange.value = [start, end]
      }
      
      let m = (end.getFullYear() - start.getFullYear()) * 12 + end.getMonth() - start.getMonth() + 1
      if (m < 1) m = 1; if (m > 12) m = 12
      
      let w = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24 * 7))
      if (w < 1) w = 1; if (w > 12) w = 12
      
      const yyyy = end.getFullYear()
      const mm = String(end.getMonth() + 1).padStart(2, '0')
      const my = `${yyyy}-${mm}`
      
      loadTrend(m)
      loadWeekly(w)
      loadSummary(my)
    }

    // Forms
    const txnForm = ref({
      transaction_type: 'EXPENSE', amount: 0, wallet_id: null,
      category_id: null, transaction_date: new Date().toISOString().slice(0, 10), note: ''
    })
    const walletForm = ref({ wallet_name: '', balance: 0, wallet_type: 'cash' })
    const catForm = ref({ category_name: '', category_type: 'EXPENSE', icon: '📦' })
    const budgetForm = ref({
      category_id: null, limit_amount: 0,
      month_year: new Date().toISOString().slice(0, 7)
    })
    const transferForm = ref({ from_wallet_id: null, to_wallet_id: null, amount: 0 })

    // OCR
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
    const chatLoading = ref(false)

    const iconOptions = ['🍕','🛍️','🚗','💵','🎁','🏠','💊','📚','🎮','☕','🍜','🎬','🏋️','✈️','📱','👕','🎵','🐾','🔧','📦']

    // ─── AXIOS CONFIG ─────────────
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
    const maxCategoryExpense = computed(() => {
      if (!summary.value.expense_by_category?.length) return 1
      return Math.max(...summary.value.expense_by_category.map(c => c.total), 1)
    })
    const totalPages = computed(() =>
      Math.max(1, Math.ceil(txnPagination.value.totalCount / txnPagination.value.limit))
    )

    // ─── CHART DATA COMPUTED ──────
    const dashboardDoughnutData = computed(() => ({
      labels: (summary.value.expense_by_category || []).map(c => `${c.icon} ${c.category_name}`),
      values: (summary.value.expense_by_category || []).map(c => c.total),
    }))

    const dashboardBarData = computed(() => ({
      labels: (trendData.value.trend || []).map(t => t.month),
      income: (trendData.value.trend || []).map(t => t.income),
      expense: (trendData.value.trend || []).map(t => t.expense),
    }))

    const trendBarData = computed(() => ({
      labels: (trendData.value.trend || []).map(t => t.month),
      income: (trendData.value.trend || []).map(t => t.income),
      expense: (trendData.value.trend || []).map(t => t.expense),
    }))

    const weeklyLineData = computed(() => ({
      labels: (weeklyData.value.data || []).map(w => w.week_start || w.week),
      expense: (weeklyData.value.data || []).map(w => w.expense),
      income: (weeklyData.value.data || []).map(w => w.income),
    }))

    const statsDoughnutData = computed(() => ({
      labels: (summary.value.expense_by_category || []).map(c => `${c.icon} ${c.category_name}`),
      values: (summary.value.expense_by_category || []).map(c => c.total),
    }))

    const isUserAdmin = computed(() => {
      const r = (userRole.value || '').toString().toLowerCase().trim()
      return r === 'admin'
    })

    const displayTabs = computed(() => {
      return tabs.filter(t => !t.adminOnly || isUserAdmin.value)
    })

    const filteredAdminUsers = computed(() => {
      return adminUsers.value.filter(u => {
        if (adminFilter.value.search) {
          const q = adminFilter.value.search.toLowerCase()
          const match = (u.full_name && u.full_name.toLowerCase().includes(q)) ||
                        (u.email && u.email.toLowerCase().includes(q))
          if (!match) return false
        }
        if (adminFilter.value.role && u.role !== adminFilter.value.role) return false
        if (adminFilter.value.status === 'active' && u.is_active !== 1) return false
        if (adminFilter.value.status === 'locked' && u.is_active !== 0) return false
        return true
      })
    })

    // ─── THEME TOGGLE ─────────────
    function switchTheme() {
      currentTheme.value = currentTheme.value === 'modern' ? 'xianxia' : 'modern'
      localStorage.setItem('app_theme', currentTheme.value)
      document.body.setAttribute('data-theme', currentTheme.value)
    }

    // ─── HELPERS ──────────────────
    function resetAllState() {
      wallets.value = []
      categories.value = []
      transactions.value = []
      debts.value = []
      savingGoals.value = []
      adminUsers.value = []
      adminStats.value = {}
      recurringList.value = []
      budgets.value = []
      summary.value = { total_income: 0, total_expense: 0, net_savings: 0, total_balance: 0, expense_by_category: [] }
      budgetAlerts.value = []
      chatMessages.value = []
      chatInput.value = ''
      chatLoading.value = false
      trendData.value = { trend: [] }
      weeklyData.value = { data: [] }
      compareData.value = null
      savingTips.value = null
      ocrFile.value = null
      ocrPreview.value = null
      ocrResult.value = null
      ocrConfirmForm.value = {
        note: '',
        amount: 0,
        transaction_date: new Date().toISOString().slice(0, 10),
        wallet_id: null,
        category_id: null,
        transaction_type: 'EXPENSE'
      }
      errorMsg.value = ''
      toast.value = null
    }

    function formatVND(val) {
      if (val === undefined || val === null) return '0 ₫'
      return Number(val).toLocaleString('vi-VN') + ' ₫'
    }

    function showToast(message, type = 'success') {
      toast.value = { message, type }
      setTimeout(() => { toast.value = null }, 3500)
    }

    function budgetPct(b) {
      return b.limit_amount > 0 ? (b.spent / b.limit_amount * 100) : 0
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

    // ─── AUTH ─────────────────────
    async function doLogin() {
      loading.value = true
      errorMsg.value = ''
      resetAllState()
      try {
        const { data } = await api.post('/api/auth/login', {
          email: authForm.value.email,
          password: authForm.value.password
        })
        token.value = data.token
        userName.value = data.full_name || 'Ký Chủ'
        userEmail.value = data.email
        userRole.value = data.role || 'user'
        currentUserId.value = data.user_id
        isLoggedIn.value = true
        localStorage.setItem('xianxia_token', data.token)
        localStorage.setItem('xianxia_user', userName.value)
        localStorage.setItem('xianxia_email', data.email)
        localStorage.setItem('xianxia_role', userRole.value)
        localStorage.setItem('xianxia_uid', data.user_id)
        await loadAllData()
      } catch (err) {
        errorMsg.value = err.response?.data?.detail || 'Lỗi đăng nhập!'
      }
      loading.value = false
    }

    async function doRegister() {
      if (!authForm.value.soul_lamp || authForm.value.soul_lamp.trim().length < 3) {
        errorMsg.value = 'Bản Mệnh Hồn Đăng không được để trống và phải có ít nhất 3 ký tự.'
        return
      }
      loading.value = true
      errorMsg.value = ''
      resetAllState()
      try {
        const regForm = {
          ...authForm.value,
          full_name: authForm.value.full_name.trim() || 'Ký Chủ',
          soul_lamp: authForm.value.soul_lamp.trim()
        }
        const { data } = await api.post('/api/auth/register', regForm)
        token.value = data.token
        userName.value = data.full_name || 'Ký Chủ'
        userEmail.value = data.email
        userRole.value = data.role || 'user'
        currentUserId.value = data.user_id
        isLoggedIn.value = true
        localStorage.setItem('xianxia_token', data.token)
        localStorage.setItem('xianxia_user', userName.value)
        localStorage.setItem('xianxia_email', data.email)
        localStorage.setItem('xianxia_role', userRole.value)
        localStorage.setItem('xianxia_uid', data.user_id)
        await loadAllData()
      } catch (err) {
        errorMsg.value = err.response?.data?.detail || 'Lỗi đăng ký!'
      }
      loading.value = false
    }

    function handleSwitchAuthMode(mode) {
      errorMsg.value = ''
      if (mode === 'forgot') {
        forgotForm.value.email = authForm.value.email || ''
        forgotForm.value.soul_lamp = ''
      } else if (mode === 'reset') {
        resetForm.value.email = forgotForm.value.email || authForm.value.email || ''
        resetForm.value.token = ''
        resetForm.value.new_password = ''
      } else if (mode === 'login') {
        if (resetForm.value.email) {
          authForm.value.email = resetForm.value.email
        }
      }
      authMode.value = mode
    }

    function openForgotPassword() {
      handleSwitchAuthMode('forgot')
    }

    async function doForgotPassword() {
      if (!forgotForm.value.email || !forgotForm.value.soul_lamp) {
        errorMsg.value = 'Vui lòng nhập đầy đủ Email và Bản Mệnh Hồn Đăng!'
        return
      }
      loading.value = true
      errorMsg.value = ''
      try {
        const { data } = await api.post('/api/auth/forgot-password', {
          email: forgotForm.value.email,
          soul_lamp: forgotForm.value.soul_lamp.trim()
        })
        resetForm.value.email = forgotForm.value.email
        resetForm.value.token = ''
        resetForm.value.new_password = ''
        authMode.value = 'reset'
        showToast('🔑 ' + (data?.message || 'Đã tạo mã xác thực khôi phục mật khẩu!'))
      } catch (err) {
        errorMsg.value = err.response?.data?.detail || 'Thông tin xác thực không chính xác, vui lòng kiểm tra lại'
      }
      loading.value = false
    }

    async function doResetPassword() {
      if (!resetForm.value.token || !resetForm.value.new_password) {
        errorMsg.value = 'Vui lòng nhập đầy đủ mã xác thực và mật khẩu mới!'
        return
      }
      loading.value = true
      errorMsg.value = ''
      try {
        await api.post('/api/auth/reset-password', resetForm.value)
        showToast('✨ Mật khẩu đã được đặt lại thành công! Hãy đăng nhập.')
        authForm.value.email = resetForm.value.email
        authForm.value.password = ''
        authMode.value = 'login'
      } catch (err) {
        errorMsg.value = err.response?.data?.detail || 'Lỗi đặt lại mật khẩu!'
      }
      loading.value = false
    }

    function doLogout() {
      isLoggedIn.value = false
      token.value = ''
      userName.value = 'Ký Chủ'
      userEmail.value = ''
      userRole.value = 'user'
      currentUserId.value = null
      localStorage.removeItem('xianxia_token')
      localStorage.removeItem('xianxia_user')
      localStorage.removeItem('xianxia_email')
      localStorage.removeItem('xianxia_role')
      localStorage.removeItem('xianxia_uid')
      authForm.value = { email: '', password: '', full_name: '', soul_lamp: '' }
      forgotForm.value = { email: '', soul_lamp: '' }
      resetAllState()
    }

    // ─── USER PROFILE MANAGEMENT ──
    function openProfileModal() {
      profileForm.value.full_name = userName.value
      soulLampForm.value = { current_password: '', new_soul_lamp: '' }
      showProfileModal.value = true
    }

    async function saveProfile(payload) {
      let newName = ''
      if (typeof payload === 'string') {
        newName = payload.trim()
      } else if (payload && payload.full_name) {
        newName = payload.full_name.trim()
      } else {
        newName = profileForm.value.full_name.trim()
      }

      if (!newName) {
        showToast('Vui lòng nhập đạo hiệu!', 'error')
        return
      }
      loadingProfile.value = true
      try {
        await api.put('/api/user/profile', { full_name: newName })
        userName.value = newName
        profileForm.value.full_name = newName
        localStorage.setItem('xianxia_user', newName)
        showToast('✨ Đạo hiệu đã được cập nhật!')
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi cập nhật tên!', 'error')
      } finally {
        loadingProfile.value = false
      }
    }

    async function saveSoulLamp(payload) {
      const curPwd = payload?.current_password || soulLampForm.value.current_password
      const newPhrase = (payload?.new_soul_lamp || soulLampForm.value.new_soul_lamp || '').trim()

      if (!curPwd) {
        showToast('Vui lòng nhập khẩu quyết (mật khẩu) hiện tại!', 'error')
        return
      }
      if (!newPhrase || newPhrase.length < 3) {
        showToast('Bản Mệnh Hồn Đăng mới phải có ít nhất 3 ký tự!', 'error')
        return
      }
      loadingSoulLamp.value = true
      try {
        const { data } = await api.put('/api/user/soul-lamp', {
          current_password: curPwd,
          new_soul_lamp: newPhrase
        })
        showToast(data.message || '✨ Đã cập nhật Bản Mệnh Hồn Đăng thành công!')
        soulLampForm.value = { current_password: '', new_soul_lamp: '' }
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi khi cập nhật Bản Mệnh Hồn Đăng!', 'error')
      } finally {
        loadingSoulLamp.value = false
      }
    }

    async function changePassword(payload) {
      const curPwd = payload?.current_password || ''
      const newPwd = payload?.new_password || ''

      if (!curPwd) {
        showToast('Vui lòng nhập mật khẩu hiện tại!', 'error')
        return
      }
      if (!newPwd || newPwd.length < 4) {
        showToast('Mật khẩu mới phải có ít nhất 4 ký tự!', 'error')
        return
      }
      loadingPassword.value = true
      try {
        const { data } = await api.put('/api/user/password', {
          current_password: curPwd,
          new_password: newPwd
        })
        showToast(data.message || 'Đổi mật khẩu thành công! Các phiên cũ đã hủy, vui lòng đăng nhập lại.')
        setTimeout(() => {
          showProfileModal.value = false
          doLogout()
        }, 1500)
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi khi đổi mật khẩu!', 'error')
      } finally {
        loadingPassword.value = false
      }
    }

    async function fetchUserProfile() {
      try {
        const { data } = await api.get('/api/user/profile')
        if (data && data.full_name) {
          userName.value = data.full_name
          userEmail.value = data.email
          userRole.value = data.role || 'user'
          currentUserId.value = data.id
          localStorage.setItem('xianxia_user', data.full_name)
          localStorage.setItem('xianxia_email', data.email)
          localStorage.setItem('xianxia_role', userRole.value)
          localStorage.setItem('xianxia_uid', data.id)
        }
      } catch {}
    }

    // ─── ADMIN MANAGEMENT (CHƯỞNG MÔN CÁC) ────
    async function loadAdminStats() {
      if (userRole.value !== 'admin') return
      try {
        const { data } = await api.get('/api/admin/stats')
        adminStats.value = data || {}
      } catch (err) {
        console.error('Lỗi tải thống kê admin:', err)
      }
    }

    async function loadAdminUsers() {
      if (userRole.value !== 'admin') return
      try {
        const { data } = await api.get('/api/admin/users')
        adminUsers.value = data || []
      } catch (err) {
        console.error('Lỗi tải danh sách người dùng:', err)
      }
    }

    async function toggleUserActive(u) {
      const action = u.is_active === 1 ? 'phong ấn (khóa)' : 'mở phong ấn cho'
      if (!confirm(`Đạo hữu có chắc chắn muốn ${action} tài khoản "${u.email}"?`)) return
      try {
        const { data } = await api.put(`/api/admin/users/${u.id}/toggle-active`)
        showToast(data.message || 'Thao tác thành công!')
        await loadAdminUsers()
        await loadAdminStats()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi khi cập nhật trạng thái người dùng!', 'error')
      }
    }

    async function changeUserRole(u, newRole) {
      const title = newRole === 'admin' ? 'thăng cấp Chưởng Môn' : 'giáng xuống Đệ Tử'
      if (!confirm(`Đạo hữu có chắc chắn muốn ${title} cho "${u.email}"?`)) return
      try {
        const { data } = await api.put(`/api/admin/users/${u.id}/role`, { role: newRole })
        showToast(data.message || 'Thao tác thành công!')
        await loadAdminUsers()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi khi thay đổi vai trò!', 'error')
      }
    }

    // ─── DATA LOADING ─────────────
    async function loadAllData() {
      await Promise.all([
        fetchUserProfile(),
        loadWallets(), loadCategories(), loadTransactions(true),
        loadDebts(), loadSavingGoals(),
        loadRecurring(), loadSummary(), loadBudgets(), checkBudgetAlerts(),
        loadTrend(), loadWeekly(), loadSuggestedQuestions(),
      ])
      if (userRole.value === 'admin') {
        loadAdminStats()
        loadAdminUsers()
      }
    }

    async function loadSuggestedQuestions() {
      try {
        const { data } = await api.get('/api/chat/suggested-questions')
        suggestedQuestions.value = data || []
      } catch {}
    }

    async function loadWallets() {
      try { wallets.value = (await api.get('/api/wallets')).data } catch {}
    }
    async function loadCategories() {
      try { categories.value = (await api.get('/api/categories')).data } catch {}
    }

    // Change 4: loadTransactions with filter and pagination
    async function loadTransactions(resetPage = false) {
      if (resetPage) txnPagination.value.page = 1
      const offset = (txnPagination.value.page - 1) * txnPagination.value.limit
      const params = {
        limit: txnPagination.value.limit,
        offset: offset,
      }
      if (txnFilter.value.start_date) params.start_date = txnFilter.value.start_date
      if (txnFilter.value.end_date) params.end_date = txnFilter.value.end_date
      if (txnFilter.value.category_id) params.category_id = txnFilter.value.category_id
      if (txnFilter.value.wallet_id) params.wallet_id = txnFilter.value.wallet_id
      if (txnFilter.value.transaction_type) params.transaction_type = txnFilter.value.transaction_type
      if (txnFilter.value.keyword) params.keyword = txnFilter.value.keyword

      try {
        const { data } = await api.get('/api/transactions', { params })
        if (data && data.data) {
          transactions.value = data.data
          txnPagination.value.totalCount = data.total_count || 0
        } else if (Array.isArray(data)) {
          transactions.value = data
          txnPagination.value.totalCount = data.length
        }
      } catch {}
    }

    function changeTxnPage(newPage) {
      if (newPage >= 1 && newPage <= totalPages.value) {
        txnPagination.value.page = newPage
        loadTransactions(false)
      }
    }

    function resetTxnFilter() {
      txnFilter.value = {
        start_date: '', end_date: '', category_id: '',
        wallet_id: '', transaction_type: '', keyword: ''
      }
      loadTransactions(true)
    }

    // Change 7: Export reports (CSV / Excel)
    async function doExportReports(format = 'excel') {
      try {
        showToast(`⏳ Đang kết xuất báo cáo ${format.toUpperCase()}...`)
        const params = { format }
        if (txnFilter.value.start_date) params.start_date = txnFilter.value.start_date
        if (txnFilter.value.end_date) params.end_date = txnFilter.value.end_date

        const response = await api.get('/api/reports/export', {
          params,
          responseType: 'blob'
        })

        const blob = new Blob([response.data], {
          type: format === 'csv'
            ? 'text/csv;charset=utf-8;'
            : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        const todayStr = new Date().toISOString().slice(0, 10).replace(/-/g, '')
        a.href = url
        a.download = `bao_cao_chi_tieu_${todayStr}.${format === 'csv' ? 'csv' : 'xlsx'}`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
        showToast(`📥 Xuất báo cáo ${format.toUpperCase()} thành công!`)
      } catch (err) {
        showToast('Lỗi khi xuất file báo cáo!', 'error')
      }
    }

    // ─── SAVING GOALS (MỤC TIÊU TIẾT KIỆM) ────
    async function loadSavingGoals() {
      try {
        const { data } = await api.get('/api/saving-goals')
        if (data) {
          savingGoals.value = data.goals || []
          goalsSummary.value = data.summary || {
            total_target: 0,
            total_saved: 0,
            completed_count: 0,
            active_count: 0,
            overall_percent: 0
          }
        }
      } catch (err) {
        console.error('Lỗi tải mục tiêu tiết kiệm:', err)
      }
    }

    async function createSavingGoal() {
      if (!goalForm.value.target_name.trim() || !goalForm.value.target_amount || goalForm.value.target_amount <= 0) {
        showToast('Vui lòng nhập tên mục tiêu và số tiền đích hợp lệ!', 'error')
        return
      }
      loading.value = true
      try {
        const payload = {
          target_name: goalForm.value.target_name.trim(),
          target_amount: Number(goalForm.value.target_amount),
          current_amount: Number(goalForm.value.current_amount || 0),
          target_date: goalForm.value.target_date || '',
          icon: goalForm.value.icon || '🎯'
        }
        await api.post('/api/saving-goals', payload)
        showToast('🎯 Khởi tạo mục tiêu tiết kiệm thành công!')
        goalForm.value = { target_name: '', target_amount: null, current_amount: 0, target_date: '', icon: '🎯' }
        await loadSavingGoals()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi tạo mục tiêu!', 'error')
      } finally {
        loading.value = false
      }
    }

    function openEditGoal(g) {
      editGoalForm.value = {
        id: g.id,
        target_name: g.target_name,
        target_amount: g.target_amount,
        current_amount: g.current_amount,
        target_date: g.target_date || '',
        icon: g.icon || '🎯',
        is_completed: g.is_completed
      }
      showEditGoalModal.value = true
    }

    async function updateSavingGoal() {
      if (!editGoalForm.value.target_name.trim() || !editGoalForm.value.target_amount || editGoalForm.value.target_amount <= 0) {
        showToast('Vui lòng nhập tên mục tiêu và số tiền đích hợp lệ!', 'error')
        return
      }
      loading.value = true
      try {
        const payload = {
          target_name: editGoalForm.value.target_name.trim(),
          target_amount: Number(editGoalForm.value.target_amount),
          current_amount: Number(editGoalForm.value.current_amount || 0),
          target_date: editGoalForm.value.target_date || '',
          icon: editGoalForm.value.icon || '🎯',
          is_completed: Number(editGoalForm.value.is_completed)
        }
        await api.put(`/api/saving-goals/${editGoalForm.value.id}`, payload)
        showToast('✨ Đã cập nhật mục tiêu tiết kiệm!')
        showEditGoalModal.value = false
        await loadSavingGoals()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi cập nhật mục tiêu!', 'error')
      } finally {
        loading.value = false
      }
    }

    function openDepositGoal(g, action = 'deposit') {
      depositForm.value = {
        goal_id: g.id,
        goal_name: g.target_name,
        amount: null,
        wallet_id: wallets.value.length ? wallets.value[0].id : '',
        action: action
      }
      showDepositModal.value = true
    }

    async function submitDepositWithdrawGoal() {
      if (!depositForm.value.amount || depositForm.value.amount <= 0) {
        showToast('Vui lòng nhập số tiền hợp lệ!', 'error')
        return
      }
      loading.value = true
      try {
        const payload = {
          amount: Number(depositForm.value.amount),
          wallet_id: depositForm.value.wallet_id ? Number(depositForm.value.wallet_id) : null
        }
        const endpoint = depositForm.value.action === 'deposit' ? 'deposit' : 'withdraw'
        const { data } = await api.post(`/api/saving-goals/${depositForm.value.goal_id}/${endpoint}`, payload)
        showToast(data.message || 'Thao tác thành công!')
        showDepositModal.value = false
        await loadSavingGoals()
        await loadWallets()
        await loadSummary()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi khi nạp/rút linh thạch!', 'error')
      } finally {
        loading.value = false
      }
    }

    async function deleteSavingGoal(id) {
      if (!confirm('Đạo hữu có chắc chắn muốn xóa mục tiêu này?')) return
      try {
        await api.delete(`/api/saving-goals/${id}`)
        showToast('🗑️ Đã xóa mục tiêu tiết kiệm!')
        await loadSavingGoals()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi khi xóa mục tiêu!', 'error')
      }
    }

    // Change 8: Recurring transactions
    async function loadRecurring() {
      try {
        recurringList.value = (await api.get('/api/recurring-transactions')).data
      } catch {}
    }

    async function createRecurring() {
      if (!recurringForm.value.amount || !recurringForm.value.wallet_id || !recurringForm.value.category_id) {
        showToast('Vui lòng chọn đầy đủ ví, danh mục và số tiền!', 'error')
        return
      }
      loading.value = true
      try {
        await api.post('/api/recurring-transactions', recurringForm.value)
        showToast('✨ Linh trận định kỳ đã được thiết lập!')
        recurringForm.value = {
          wallet_id: wallets.value.length ? wallets.value[0].id : null,
          category_id: null,
          amount: 0,
          transaction_type: 'EXPENSE',
          frequency: 'monthly',
          next_run_date: new Date().toISOString().slice(0, 10),
          note: ''
        }
        await loadRecurring()
        await loadTransactions()
        await loadSummary()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi tạo giao dịch định kỳ!', 'error')
      }
      loading.value = false
    }

    async function toggleRecurring(rec) {
      try {
        const newStatus = rec.is_active ? 0 : 1
        await api.put(`/api/recurring-transactions/${rec.id}`, { is_active: newStatus })
        showToast(newStatus ? '✅ Đã kích hoạt linh trận!' : '⏸️ Đã tạm dừng linh trận!')
        await loadRecurring()
      } catch {}
    }

    async function deleteRecurring(id) {
      if (!confirm('Hủy bỏ linh trận định kỳ này?')) return
      try {
        await api.delete(`/api/recurring-transactions/${id}`)
        showToast('Linh trận đã bị hủy!')
        await loadRecurring()
      } catch {}
    }

    function openEditRecurring(rec) {
      editRecurringForm.value = {
        id: rec.id,
        wallet_id: rec.wallet_id,
        category_id: rec.category_id,
        amount: rec.amount,
        transaction_type: rec.transaction_type,
        frequency: rec.frequency,
        next_run_date: rec.next_run_date,
        note: rec.note || '',
        is_active: rec.is_active
      }
      showEditRecurringModal.value = true
    }

    async function updateRecurring() {
      loading.value = true
      try {
        await api.put(`/api/recurring-transactions/${editRecurringForm.value.id}`, editRecurringForm.value)
        showToast('✨ Linh trận định kỳ đã được cập nhật!')
        showEditRecurringModal.value = false
        await loadRecurring()
        await loadTransactions()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi cập nhật linh trận!', 'error')
      }
      loading.value = false
    }

    function openEditBudget(b) {
      editBudgetForm.value = {
        id: b.id,
        limit_amount: b.limit_amount,
        category_name: b.category_name || '',
        category_icon: b.category_icon || '🎯',
        month_year: b.month_year || budgetMonth.value
      }
      showEditBudgetModal.value = true
    }

    async function updateBudget() {
      if (!editBudgetForm.value.limit_amount || editBudgetForm.value.limit_amount <= 0) {
        return showToast('Vui lòng nhập số tiền hợp lệ!', 'error')
      }
      loading.value = true
      try {
        await api.put(`/api/budgets/${editBudgetForm.value.id}`, { limit_amount: editBudgetForm.value.limit_amount })
        showToast('Đã cập nhật hạn mức!')
        showEditBudgetModal.value = false
        await loadBudgets()
        await checkBudgetAlerts()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi cập nhật!', 'error')
      }
      loading.value = false
    }

    function onBudgetMonthChange(newMonth) {
      budgetMonth.value = newMonth
      budgetForm.value.month_year = newMonth
    }

    async function doExport(format) {
      try {
        let url = `/api/reports/export?format=${format}`
        if (statsDateRange.value && statsDateRange.value[0] && statsDateRange.value[1]) {
          const s = statsDateRange.value[0].toISOString().split('T')[0]
          const e = statsDateRange.value[1].toISOString().split('T')[0]
          url += `&start_date=${s}&end_date=${e}`
        }
        
        const response = await api.get(url, { responseType: 'blob' })
        const blob = new Blob([response.data])
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = `bao_cao_${format}_${new Date().getTime()}.${format === 'csv' ? 'csv' : 'xlsx'}`
        link.click()
        showToast('Đã xuất báo cáo thành công!')
      } catch (err) {
        showToast('Lỗi xuất báo cáo!', 'error')
      }
    }

    // Change 3: Edit Wallet & Category
    function openEditWallet(w) {
      editWalletForm.value = { id: w.id, wallet_name: w.wallet_name, wallet_type: w.wallet_type }
      showEditWalletModal.value = true
    }

    async function updateWallet() {
      if (!editWalletForm.value.wallet_name.trim()) {
        showToast('Tên ví không được để trống!', 'error')
        return
      }
      loading.value = true
      try {
        await api.put(`/api/wallets/${editWalletForm.value.id}`, {
          wallet_name: editWalletForm.value.wallet_name,
          wallet_type: editWalletForm.value.wallet_type
        })
        showToast('✨ Túi Càn Khôn đã được cập nhật!')
        showEditWalletModal.value = false
        await loadWallets()
        await loadSummary()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi cập nhật ví!', 'error')
      }
      loading.value = false
    }

    function openEditCategory(c) {
      editCatForm.value = { id: c.id, category_name: c.category_name, icon: c.icon }
      showEditCatModal.value = true
    }

    async function updateCategory() {
      if (!editCatForm.value.category_name.trim()) {
        showToast('Tên danh mục không được để trống!', 'error')
        return
      }
      loading.value = true
      try {
        await api.put(`/api/categories/${editCatForm.value.id}`, {
          category_name: editCatForm.value.category_name,
          icon: editCatForm.value.icon
        })
        showToast('✨ Danh mục đã được cập nhật!')
        showEditCatModal.value = false
        await loadCategories()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi cập nhật danh mục!', 'error')
      }
      loading.value = false
    }

    // ─── DEBTS (SỔ NỢ / VAY MƯỢN) ────
    async function loadDebts() {
      try {
        const params = {}
        if (debtFilter.value.type) params.debt_type = debtFilter.value.type
        if (debtFilter.value.is_settled !== '') params.is_settled = debtFilter.value.is_settled
        const { data } = await api.get('/api/debts', { params })
        if (data) {
          debts.value = data.debts || []
          debtsSummary.value = data.summary || {
            total_borrow_unsettled: 0,
            total_lend_unsettled: 0,
            total_borrow_settled: 0,
            total_lend_settled: 0
          }
        }
      } catch (err) {
        console.error('Lỗi tải sổ nợ:', err)
      }
    }

    async function createDebt() {
      if (!debtForm.value.person_name || !debtForm.value.amount || debtForm.value.amount <= 0) {
        showToast('Vui lòng nhập đối tác và số tiền hợp lệ!', 'error')
        return
      }
      loading.value = true
      try {
        const payload = {
          debt_type: debtForm.value.debt_type,
          person_name: debtForm.value.person_name.trim(),
          amount: Number(debtForm.value.amount),
          due_date: debtForm.value.due_date || '',
          wallet_id: debtForm.value.wallet_id ? Number(debtForm.value.wallet_id) : null,
          note: debtForm.value.note || ''
        }
        await api.post('/api/debts', payload)
        showToast('📜 Đã ghi nhận khoản nợ thành công!')
        debtForm.value = { debt_type: 'BORROW', person_name: '', amount: null, due_date: '', wallet_id: '', note: '' }
        await loadDebts()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi ghi sổ nợ!', 'error')
      } finally {
        loading.value = false
      }
    }

    function openEditDebt(d) {
      editDebtForm.value = {
        id: d.id,
        debt_type: d.debt_type,
        person_name: d.person_name,
        amount: d.amount,
        due_date: d.due_date || '',
        wallet_id: d.wallet_id || '',
        note: d.note || '',
        is_settled: d.is_settled
      }
      showEditDebtModal.value = true
    }

    async function updateDebt() {
      if (!editDebtForm.value.person_name || !editDebtForm.value.amount || editDebtForm.value.amount <= 0) {
        showToast('Vui lòng nhập đối tác và số tiền hợp lệ!', 'error')
        return
      }
      loading.value = true
      try {
        const payload = {
          debt_type: editDebtForm.value.debt_type,
          person_name: editDebtForm.value.person_name.trim(),
          amount: Number(editDebtForm.value.amount),
          due_date: editDebtForm.value.due_date || '',
          wallet_id: editDebtForm.value.wallet_id ? Number(editDebtForm.value.wallet_id) : null,
          note: editDebtForm.value.note || '',
          is_settled: Number(editDebtForm.value.is_settled)
        }
        await api.put(`/api/debts/${editDebtForm.value.id}`, payload)
        showToast('✨ Đã cập nhật khoản nợ!')
        showEditDebtModal.value = false
        await loadDebts()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi cập nhật khoản nợ!', 'error')
      } finally {
        loading.value = false
      }
    }

    async function toggleSettleDebt(d) {
      try {
        const { data } = await api.post(`/api/debts/${d.id}/settle`)
        showToast(data.message || 'Đã cập nhật trạng thái tất toán!')
        await loadDebts()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi tất toán khoản nợ!', 'error')
      }
    }

    async function deleteDebt(id) {
      if (!confirm('Đạo hữu có chắc chắn muốn xóa khoản nợ này khỏi sổ?')) return
      try {
        await api.delete(`/api/debts/${id}`)
        showToast('🗑️ Đã xóa khoản nợ khỏi sổ!')
        await loadDebts()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi khi xóa khoản nợ!', 'error')
      }
    }

    function getDebtStatus(debt) {
      if (debt.is_settled) return { label: 'Đã Tất Toán', class: 'badge-settled', icon: '✅' }
      if (!debt.due_date) return { label: 'Chưa Đặt Hạn', class: 'badge-no-due', icon: '⏳' }
      const today = new Date().toISOString().split('T')[0]
      if (debt.due_date < today) {
        const diffTime = Math.abs(new Date(today) - new Date(debt.due_date))
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
        return { label: `Quá Hạn ${diffDays} Ngày`, class: 'badge-overdue', icon: '⚠️' }
      } else if (debt.due_date === today) {
        return { label: 'Hôm Nay Đến Hạn', class: 'badge-due-today', icon: '⚡' }
      } else {
        const diffTime = new Date(debt.due_date) - new Date(today)
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
        return { label: `Còn ${diffDays} Ngày`, class: 'badge-pending', icon: '⏳' }
      }
    }

    async function loadSummary(monthYear = null) {
      let url = '/api/reports/summary'
      if (monthYear) url += `?month_year=${monthYear}`
      try { summary.value = (await api.get(url)).data } catch {}
    }
    async function loadBudgets() {
      try { budgets.value = (await api.get(`/api/budgets?month_year=${budgetMonth.value}`)).data } catch {}
    }
    async function checkBudgetAlerts() {
      try { budgetAlerts.value = (await api.post('/api/ai/check-budget')).data.alerts } catch {}
    }
    async function loadTrend(months = 6) {
      try { trendData.value = (await api.get(`/api/reports/trend?months=${months}`)).data } catch {}
    }
    async function loadWeekly(weeks = 4) {
      try { weeklyData.value = (await api.get(`/api/reports/weekly?weeks=${weeks}`)).data } catch {}
    }
    async function loadCompare() {
      if (!compareMonth1.value || !compareMonth2.value) return
      try {
        compareData.value = (await api.get(`/api/reports/compare?month1=${compareMonth1.value}&month2=${compareMonth2.value}`)).data
      } catch {}
    }
    async function loadSavingTips() {
      loadingTips.value = true
      try {
        savingTips.value = (await api.post('/api/ai/saving-tips')).data
        showToast('🔮 Khai Thị Tiết Kiệm đã đến!')
      } catch (err) {
        showToast(err.response?.data?.detail || 'Không thể nhận khai thị (cần API key Gemini)', 'error')
      }
      loadingTips.value = false
    }

    // ─── CRUD ─────────────────────
    async function createTransaction() {
      if (!txnForm.value.amount || !txnForm.value.wallet_id || !txnForm.value.category_id) {
        showToast('Vui lòng điền đầy đủ thông tin!', 'error')
        return
      }
      loading.value = true
      try {
        await api.post('/api/transactions', txnForm.value)
        showToast('⚡ Giao dịch Linh Thạch đã ghi nhận!')
        txnForm.value = {
          transaction_type: 'EXPENSE', amount: 0, wallet_id: txnForm.value.wallet_id,
          category_id: null, transaction_date: new Date().toISOString().slice(0, 10), note: ''
        }
        await loadAllData()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi tạo giao dịch!', 'error')
      }
      loading.value = false
    }

    async function deleteTransaction(id) {
      if (!confirm('Xóa giao dịch này?')) return
      try {
        await api.delete(`/api/transactions/${id}`)
        showToast('Giao dịch đã xóa!')
        await loadTransactions()
        await loadWallets()
        await loadSummary()
      } catch {}
    }

    async function createWallet() {
      if (!walletForm.value.wallet_name) {
        showToast('Vui lòng nhập tên ví!', 'error')
        return
      }
      loading.value = true
      try {
        await api.post('/api/wallets', walletForm.value)
        showToast('✨ Túi Càn Khôn mới đã khai mở!')
        walletForm.value = { wallet_name: '', balance: 0, wallet_type: 'cash' }
        await loadWallets()
        await loadSummary()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi tạo ví!', 'error')
      }
      loading.value = false
    }

    async function deleteWallet(id) {
      if (!confirm('Xóa ví này? Các giao dịch thuộc ví cũng sẽ bị ảnh hưởng.')) return
      try {
        await api.delete(`/api/wallets/${id}`)
        showToast('Ví đã xóa!')
        await loadAllData()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi xóa ví!', 'error')
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
        showToast(err.response?.data?.detail || 'Lỗi chuyển tiền!', 'error')
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
        showToast('✨ Danh mục mới đã khai mở!')
        catForm.value = { category_name: '', category_type: 'EXPENSE', icon: '📦' }
        await loadCategories()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi!', 'error')
      }
      loading.value = false
    }

    async function deleteCategory(id) {
      if (!confirm('Xóa danh mục này?')) return
      try {
        await api.delete(`/api/categories/${id}`)
        showToast('Danh mục đã xóa!')
        await loadCategories()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Không thể xóa danh mục!', 'error')
      }
    }

    async function createBudget() {
      if (!budgetForm.value.category_id || !budgetForm.value.limit_amount) {
        showToast('Vui lòng điền đầy đủ!', 'error')
        return
      }
      loading.value = true
      try {
        await api.post('/api/budgets', budgetForm.value)
        showToast('🎯 Hạn mức tu luyện đã thiết lập!')
        await loadBudgets()
        await checkBudgetAlerts()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi!', 'error')
      }
      loading.value = false
    }

    async function deleteBudget(id) {
      if (!confirm('Xóa hạn mức này?')) return
      try {
        await api.delete(`/api/budgets/${id}`)
        showToast('Hạn mức đã xóa!')
        await loadBudgets()
      } catch {}
    }

    // ─── OCR ──────────────────────
    function resetOCR() {
      ocrFile.value = null
      if (ocrPreview.value) {
        try { URL.revokeObjectURL(ocrPreview.value) } catch {}
      }
      ocrPreview.value = null
      ocrResult.value = null
      const defaultWallet = wallets.value.length ? wallets.value[0].id : null
      const defaultCat = expenseCategories.value.length ? expenseCategories.value[0].id : null
      ocrConfirmForm.value = {
        note: '',
        amount: 0,
        transaction_date: new Date().toISOString().slice(0, 10),
        wallet_id: defaultWallet,
        category_id: defaultCat,
        transaction_type: 'EXPENSE'
      }
    }

    function handleOCRUpload(e) {
      const file = e.target.files[0]
      if (file) {
        if (ocrPreview.value) {
          try { URL.revokeObjectURL(ocrPreview.value) } catch {}
        }
        ocrFile.value = file
        ocrPreview.value = URL.createObjectURL(file)
        ocrResult.value = null
      }
    }

    function handleOCRDrop(e) {
      const file = e.dataTransfer.files[0]
      if (file && file.type.startsWith('image/')) {
        if (ocrPreview.value) {
          try { URL.revokeObjectURL(ocrPreview.value) } catch {}
        }
        ocrFile.value = file
        ocrPreview.value = URL.createObjectURL(file)
        ocrResult.value = null
      }
    }

    async function scanInvoice() {
      if (!ocrFile.value) return
      loading.value = true
      try {
        const formData = new FormData()
        formData.append('file', ocrFile.value)
        const { data } = await api.post('/api/ai/scan-invoice', formData)
        ocrResult.value = data.data

        const defaultWallet = wallets.value.length ? wallets.value[0].id : null
        const defaultCat = expenseCategories.value.length ? expenseCategories.value[0].id : null
        ocrConfirmForm.value = {
          note: data.data.store_name || 'Chi tiêu từ hóa đơn',
          amount: data.data.total_amount || 0,
          transaction_date: data.data.date || new Date().toISOString().slice(0, 10),
          wallet_id: defaultWallet,
          category_id: defaultCat,
          transaction_type: 'EXPENSE'
        }
        showToast('👁️ Linh Nhãn đã hoàn thành phân tích! Vui lòng kiểm tra và xác nhận.')
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi OCR!', 'error')
      }
      loading.value = false
    }

    async function confirmOCRTransaction() {
      if (!ocrConfirmForm.value.amount || ocrConfirmForm.value.amount <= 0) {
        showToast('Vui lòng nhập số tiền hợp lệ!', 'error')
        return
      }
      if (!ocrConfirmForm.value.wallet_id || !ocrConfirmForm.value.category_id) {
        showToast('Vui lòng chọn Túi Càn Khôn và Danh Mục Chi!', 'error')
        return
      }
      loading.value = true
      try {
        await api.post('/api/transactions', ocrConfirmForm.value)
        showToast('⚡ Giao dịch từ hóa đơn đã được thêm vào lịch sử!')
        ocrResult.value = null
        ocrFile.value = null
        if (ocrPreview.value) {
          try { URL.revokeObjectURL(ocrPreview.value) } catch {}
        }
        ocrPreview.value = null
        await loadAllData()
        activeTab.value = 'transactions'
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi lưu giao dịch!', 'error')
      }
      loading.value = false
    }

    // ─── AI CHAT ──────────────────
    async function sendChat(customMsg = null) {
      const msg = (typeof customMsg === 'string' && customMsg.trim()) ? customMsg.trim() : chatInput.value.trim()
      if (!msg || chatLoading.value) return
      if (!Array.isArray(chatMessages.value)) {
        chatMessages.value = []
      }
      chatMessages.value.push({ role: 'user', text: msg })
      chatInput.value = ''
      await nextTick()
      scrollChat()

      chatLoading.value = true
      try {
        const { data } = await api.post('/api/ai/chat', { message: msg, mode: 'knowledge' }, { timeout: 25000 })
        if (!Array.isArray(chatMessages.value)) chatMessages.value = []
        chatMessages.value.push({ role: 'ai', text: data.response || 'Đã tiếp nhận mệnh lệnh.' })
        if (data.state === 'SUCCESS' && data.tool_executed) {
          await onKhiLinhTransactionCompleted()
        }
      } catch (err) {
        if (!Array.isArray(chatMessages.value)) chatMessages.value = []
        const errMsg = err.code === 'ECONNABORTED'
          ? '🔮 Tiên Trí phản hồi quá lâu do nghẽn mạng, vui lòng thử lại.'
          : (err.response?.data?.detail || 'Không thể kết nối với thần trí AI.')
        chatMessages.value.push({
          role: 'ai',
          text: '⚠️ ' + errMsg
        })
      } finally {
        chatLoading.value = false
        await nextTick()
        scrollChat()
      }
    }

    // ─── KHÍ LINH EVENT HANDLER ───
    async function onKhiLinhTransactionCompleted(payload) {
      await Promise.all([
        loadWallets(),
        loadTransactions(true),
        loadSummary(),
        loadBudgets(),
        checkBudgetAlerts(),
        loadDebts(),
        loadSavingGoals(),
        loadTrend(),
        loadWeekly()
      ])
      showToast('✨ Khí Linh đã đồng bộ thành công vào sổ sách!', 'success')
    }

    function scrollChat() {
      const el = chatMessagesEl.value
      if (el) el.scrollTop = el.scrollHeight
    }

    // ─── TAB NAVIGATION & SCROLL ─
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

    // ─── TAB SWITCH ───────────────
    function switchTab(tabId) {
      activeTab.value = tabId
      if (tabId === 'stats') {
        onStatsDateChange()
        loadCompare()
      } else if (tabId === 'budgets') {
        loadBudgets()
      } else if (tabId === 'admin') {
        loadAdminStats()
        loadAdminUsers()
      } else if (tabId === 'chat') {
        if (!suggestedQuestions.value.length) {
          loadSuggestedQuestions()
        }
      }
      nextTick(() => {
        const activeBtn = tabNavEl.value?.querySelector('.tab-btn.active')
        if (activeBtn) {
          activeBtn.scrollIntoView({ behavior: 'smooth', inline: 'nearest', block: 'nearest' })
        }
        checkNavScroll()
      })
    }

    // ─── INIT ─────────────────────
    onMounted(() => {
      document.body.setAttribute('data-theme', currentTheme.value)
      const savedToken = localStorage.getItem('xianxia_token')
      const savedUser = localStorage.getItem('xianxia_user')
      const savedEmail = localStorage.getItem('xianxia_email')
      const savedRole = localStorage.getItem('xianxia_role')
      const savedUid = localStorage.getItem('xianxia_uid')
      if (savedRole) userRole.value = savedRole
      if (savedUid) currentUserId.value = parseInt(savedUid)
      if (savedToken) {
        token.value = savedToken
        userName.value = (savedUser && savedUser !== 'Đạo Hữu Admin') ? savedUser : 'Ký Chủ'
        userEmail.value = savedEmail || 'admin@gmail.com'
        isLoggedIn.value = true
        loadAllData()
      }
      nextTick(() => {
        checkNavScroll()
      })
      window.addEventListener('resize', checkNavScroll)
    })

    onErrorCaptured((err, instance, info) => {
      console.error('Captured Vue Render Error:', err, info)
      showToast('Có lỗi xảy ra khi hiển thị thành phần giao diện!', 'error')
      return false
    })

    return {
      api,
      isLoggedIn, authMode, authForm, forgotForm, resetForm,
      loading, loadingTips, loadingProfile, loadingSoulLamp, loadingPassword, errorMsg, toast,
      activeTab, tabs, displayTabs, userName, userEmail, userRole, currentUserId, currentTheme, isUserAdmin,
      tabNavEl, canScrollNavLeft, canScrollNavRight, checkNavScroll, scrollNav, handleNavWheel,
      showProfileModal, profileForm, soulLampForm, saveSoulLamp, changePassword,
      showEditWalletModal, editWalletForm,
      showEditCatModal, editCatForm,
      showEditRecurringModal, editRecurringForm,
      showRecurringSection, recurringList, recurringForm,
      // debts
      debts, debtsSummary, debtFilter, debtForm, showEditDebtModal, editDebtForm,
      loadDebts, createDebt, openEditDebt, updateDebt, toggleSettleDebt, deleteDebt, getDebtStatus,
      // saving goals
      savingGoals, goalsSummary, goalForm, showEditGoalModal, editGoalForm, showDepositModal, depositForm,
      loadSavingGoals, createSavingGoal, openEditGoal, updateSavingGoal, openDepositGoal, submitDepositWithdrawGoal, deleteSavingGoal,
      // admin
      adminStats, adminUsers, adminFilter, filteredAdminUsers,
      loadAdminStats, loadAdminUsers, toggleUserActive, changeUserRole,
      txnFilter, txnPagination, totalPages, loadTransactions,
      wallets, categories, transactions, budgets, summary, budgetAlerts,
      chatMessages, chatInput, chatMessagesEl, chatLoading, suggestedQuestions,
      txnForm, walletForm, catForm, budgetForm, transferForm,
      ocrFile, ocrPreview, ocrResult, ocrConfirmForm,
      iconOptions,
      incomeCategories, expenseCategories, filteredCategories, maxCategoryExpense,
      // v3 data
      trendData, weeklyData, compareData, savingTips,
      compareMonth1, compareMonth2,
      // chart computed
      dashboardDoughnutData, dashboardBarData,
      trendBarData, weeklyLineData, statsDoughnutData,
      // methods
      formatVND, showToast, budgetPct, formatChatText, walletTypeIcon,
      handleSwitchAuthMode, doLogin, doRegister, doLogout, openForgotPassword, doForgotPassword, doResetPassword,
      openProfileModal, saveProfile,
      openEditWallet, updateWallet, openEditCategory, updateCategory,
      openEditRecurring, updateRecurring,
      changeTxnPage, resetTxnFilter, doExportReports,
      loadRecurring, createRecurring, toggleRecurring, deleteRecurring,
      switchTab, switchTheme, loadAllData, loadCompare, loadSavingTips,
      createTransaction, deleteTransaction,
      budgetMonth, statsDateRange, presetRanges, onStatsDateChange, viLocale, doExport,
      showEditBudgetModal, editBudgetForm, openEditBudget, updateBudget, onBudgetMonthChange,
      createWallet, deleteWallet, doTransfer,
      loadCategories, createCategory, deleteCategory,
      loadBudgets, createBudget, deleteBudget,
      handleOCRUpload, handleOCRDrop, scanInvoice, confirmOCRTransaction, resetOCR,
      sendChat,
      isKhiLinhOpen, onKhiLinhTransactionCompleted,
    }
  }
}
</script>

<style>
/* ═══════════════════════════════════════════════════════════
   CÀN KHÔN LINH THẠCH CÁC v3.5 — CELESTIAL XIANXIA THEME
   ═══════════════════════════════════════════════════════════ */

/* ─── RESET & BASE ─────────────────────── */
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

/* ─── KHÍ LINH SYSTEM WINDOW BACKDROP BLUR ─── */
.app-realm.app-realm-behind-overlay {
  filter: blur(8px) brightness(0.55);
  pointer-events: none;
  user-select: none;
  transition: filter 0.3s ease, brightness 0.3s ease;
}

:root {
  --bg-primary: #1a3a5c;
  --bg-secondary: rgba(255, 255, 255, 0.7);
  --bg-card: rgba(255, 255, 255, 0.78);
  --bg-card-hover: rgba(255, 255, 255, 0.92);
  --bg-body-gradient: linear-gradient(180deg, #1a3a5c 0%, #3f688e 25%, #6d9bc3 50%, #9cbcdb 75%, #eef4f8 100%);

  --header-bg: rgba(255, 255, 255, 0.82);
  --tab-nav-bg: rgba(255, 255, 255, 0.75);
  --input-bg: rgba(255, 255, 255, 0.92);
  --table-th-bg: rgba(232, 200, 116, 0.2);
  --table-border: rgba(232, 200, 116, 0.25);
  --table-hover: rgba(232, 200, 116, 0.15);
  --chat-input-bg: rgba(238, 244, 248, 0.6);
  --card-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);

  --jade: #2b8a82;
  --jade-glow: #4fa8a0;
  --jade-dim: #1e5a55;

  --gold: #b38217;
  --gold-glow: #e8c874;
  --gold-dim: #78530b;

  --purple: #6d4ab8;
  --purple-glow: #8e6ee8;

  --crimson: #c0392b;
  --crimson-glow: #e74c3c;

  --text-primary: #1a3a5c;
  --text-secondary: #476582;
  --text-dim: #6b88a5;
  --text-light: #f5f5f0;

  --border: rgba(232, 200, 116, 0.45);
  --border-glow: rgba(232, 200, 116, 0.85);

  --radius: 12px;
  --radius-lg: 20px;

  --shadow-jade: 0 8px 25px rgba(79, 168, 160, 0.25), 0 0 15px rgba(79, 168, 160, 0.15);
  --shadow-gold: 0 8px 25px rgba(232, 200, 116, 0.35), 0 0 20px rgba(232, 200, 116, 0.2);
  --glass-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);

  --font-calligraphy: 'Lora', 'Cormorant Garamond', 'Georgia', serif;
  --font-body: 'Inter', -apple-system, sans-serif;

  /* Custom Cursor: Embedded Sword SVG với Hotspot chính xác tại ĐẦU MŨI KIẾM (4 4) */
  --cursor-sword: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48' width='48' height='48' fill='none'> <defs> <linearGradient id='blade_lei' x1='4' y1='4' x2='28' y2='28' gradientUnits='userSpaceOnUse'> <stop offset='0%' stop-color='%23F5D0FE'/> <stop offset='30%' stop-color='%23C084FC'/> <stop offset='70%' stop-color='%237E22CE'/> <stop offset='100%' stop-color='%233B0764'/> </linearGradient> <linearGradient id='blade_lei_edge' x1='4' y1='4' x2='25' y2='25' gradientUnits='userSpaceOnUse'> <stop offset='0%' stop-color='%23FFFFFF'/> <stop offset='40%' stop-color='%23E879F9'/> <stop offset='100%' stop-color='%239333EA'/> </linearGradient> <linearGradient id='guard_lei' x1='18' y1='18' x2='38' y2='38' gradientUnits='userSpaceOnUse'> <stop offset='0%' stop-color='%23F8FAFC'/> <stop offset='50%' stop-color='%2394A3B8'/> <stop offset='100%' stop-color='%23334155'/> </linearGradient> <filter id='cursor_glow_v2' x='-25%' y='-25%' width='150%' height='150%'> <feDropShadow dx='0' dy='2' stdDeviation='2' flood-color='%23090514' flood-opacity='0.95'/> <feDropShadow dx='0' dy='0' stdDeviation='1.5' flood-color='%23C084FC' flood-opacity='0.85'/> </filter> </defs> <g filter='url(%23cursor_glow_v2)'> <path d='M 4 4 L 13 8 L 22 22 L 25 25 L 22 27 L 20 25 L 8 13 Z' fill='%23090514' stroke='%23090514' stroke-width='2.6' stroke-linejoin='round'/> <path d='M 18 16 L 31 13 L 26 21 L 34 29 L 26 31 L 25 41 L 19 28 L 14 20 Z' fill='%23090514' stroke='%23090514' stroke-width='2.2' stroke-linejoin='round'/> <path d='M 4 4 L 13 8 L 23 24 Z' fill='url(%23blade_lei_edge)'/> <path d='M 4 4 L 8 13 L 23 24 Z' fill='url(%23blade_lei)'/> <path d='M 5 5 L 11 11 L 9 13 L 17 19 L 15 21 L 22 24' stroke='%23FFFFFF' stroke-width='0.85' stroke-linecap='round' stroke-linejoin='bevel'/> <path d='M 17 18 L 28 14 L 24 21 L 30 25 L 24 27 L 19 32 L 18 25 Z' fill='url(%23guard_lei)' stroke='%23E2E8F0' stroke-width='0.5'/> <polygon points='24,21 27,24 24,27 21,24' fill='%2338BDF8' stroke='%23FFFFFF' stroke-width='0.6'/> <path d='M 25 25 L 35 35' stroke='%231E1B4B' stroke-width='2.8' stroke-linecap='round'/> <line x1='27' y1='26' x2='26' y2='27' stroke='%2338BDF8' stroke-width='0.8'/> <line x1='30' y1='29' x2='29' y2='30' stroke='%2338BDF8' stroke-width='0.8'/> <line x1='33' y1='32' x2='32' y2='33' stroke='%2338BDF8' stroke-width='0.8'/> <polygon points='36,33 39,36 36,39 33,36' fill='url(%23guard_lei)' stroke='%23090514' stroke-width='1'/> <circle cx='36' cy='36' r='1.1' fill='%23C084FC'/> <path d='M 38 38 Q 43 40 43 45' stroke='%2338BDF8' stroke-width='1.2' stroke-linecap='round'/> <path d='M 37 39 Q 40 43 39 46' stroke='%23C084FC' stroke-width='1' stroke-linecap='round'/> <circle cx='4' cy='4' r='0.9' fill='%23FFFFFF'/> </g> </svg>") 4 4, auto;
  --cursor-pointer: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48' width='48' height='48' fill='none'> <defs> <linearGradient id='blade_lei' x1='4' y1='4' x2='28' y2='28' gradientUnits='userSpaceOnUse'> <stop offset='0%' stop-color='%23F5D0FE'/> <stop offset='30%' stop-color='%23C084FC'/> <stop offset='70%' stop-color='%237E22CE'/> <stop offset='100%' stop-color='%233B0764'/> </linearGradient> <linearGradient id='blade_lei_edge' x1='4' y1='4' x2='25' y2='25' gradientUnits='userSpaceOnUse'> <stop offset='0%' stop-color='%23FFFFFF'/> <stop offset='40%' stop-color='%23E879F9'/> <stop offset='100%' stop-color='%239333EA'/> </linearGradient> <linearGradient id='guard_lei' x1='18' y1='18' x2='38' y2='38' gradientUnits='userSpaceOnUse'> <stop offset='0%' stop-color='%23F8FAFC'/> <stop offset='50%' stop-color='%2394A3B8'/> <stop offset='100%' stop-color='%23334155'/> </linearGradient> <filter id='cursor_glow_v2' x='-25%' y='-25%' width='150%' height='150%'> <feDropShadow dx='0' dy='2' stdDeviation='2' flood-color='%23090514' flood-opacity='0.95'/> <feDropShadow dx='0' dy='0' stdDeviation='1.5' flood-color='%23C084FC' flood-opacity='0.85'/> </filter> </defs> <g filter='url(%23cursor_glow_v2)'> <path d='M 4 4 L 13 8 L 22 22 L 25 25 L 22 27 L 20 25 L 8 13 Z' fill='%23090514' stroke='%23090514' stroke-width='2.6' stroke-linejoin='round'/> <path d='M 18 16 L 31 13 L 26 21 L 34 29 L 26 31 L 25 41 L 19 28 L 14 20 Z' fill='%23090514' stroke='%23090514' stroke-width='2.2' stroke-linejoin='round'/> <path d='M 4 4 L 13 8 L 23 24 Z' fill='url(%23blade_lei_edge)'/> <path d='M 4 4 L 8 13 L 23 24 Z' fill='url(%23blade_lei)'/> <path d='M 5 5 L 11 11 L 9 13 L 17 19 L 15 21 L 22 24' stroke='%23FFFFFF' stroke-width='0.85' stroke-linecap='round' stroke-linejoin='bevel'/> <path d='M 17 18 L 28 14 L 24 21 L 30 25 L 24 27 L 19 32 L 18 25 Z' fill='url(%23guard_lei)' stroke='%23E2E8F0' stroke-width='0.5'/> <polygon points='24,21 27,24 24,27 21,24' fill='%2338BDF8' stroke='%23FFFFFF' stroke-width='0.6'/> <path d='M 25 25 L 35 35' stroke='%231E1B4B' stroke-width='2.8' stroke-linecap='round'/> <line x1='27' y1='26' x2='26' y2='27' stroke='%2338BDF8' stroke-width='0.8'/> <line x1='30' y1='29' x2='29' y2='30' stroke='%2338BDF8' stroke-width='0.8'/> <line x1='33' y1='32' x2='32' y2='33' stroke='%2338BDF8' stroke-width='0.8'/> <polygon points='36,33 39,36 36,39 33,36' fill='url(%23guard_lei)' stroke='%23090514' stroke-width='1'/> <circle cx='36' cy='36' r='1.1' fill='%23C084FC'/> <path d='M 38 38 Q 43 40 43 45' stroke='%2338BDF8' stroke-width='1.2' stroke-linecap='round'/> <path d='M 37 39 Q 40 43 39 46' stroke='%23C084FC' stroke-width='1' stroke-linecap='round'/> <circle cx='4' cy='4' r='0.9' fill='%23FFFFFF'/> </g> </svg>") 4 4, pointer;
}

/* ─── MODERN THEME (THEME 2 — GIAO DIỆN THƯỜNG / SÁNG) ─────── */
body[data-theme='modern'] {
  background: #F1F5F9 !important;
  color: #0F172A !important;
  cursor: auto !important;
}

body[data-theme='modern'] .xianxia-backdrop,
.modern-mode .xianxia-backdrop {
  display: none !important;
}

body[data-theme='modern'],
.modern-mode {
  --bg-primary: #FFFFFF;
  --bg-secondary: #F8FAFC;
  --bg-card: #FFFFFF;
  --bg-card-hover: #F1F5F9;
  --bg-body-gradient: #F1F5F9;

  --header-bg: rgba(255, 255, 255, 0.95);
  --tab-nav-bg: rgba(255, 255, 255, 0.92);
  --input-bg: #FFFFFF;
  --table-th-bg: #F8FAFC;
  --table-border: #E2E8F0;
  --table-hover: #F1F5F9;
  --chat-input-bg: #F8FAFC;
  --card-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.08);

  --text-primary: #0F172A;
  --text-secondary: #334155;
  --text-dim: #64748B;
  --text-light: #F8FAFC;

  --border: #E2E8F0;
  --border-glow: #2563EB;

  --jade: #2563EB;
  --jade-glow: #3B82F6;
  --jade-dim: rgba(59, 130, 246, 0.1);

  --gold: #D97706;
  --gold-glow: #F59E0B;
  --gold-dim: rgba(245, 158, 11, 0.15);

  --purple: #7C3AED;
  --purple-glow: #A78BFA;

  --crimson: #DC2626;
  --crimson-glow: #EF4444;

  --shadow-jade: 0 8px 25px rgba(37, 99, 235, 0.2), 0 0 15px rgba(37, 99, 235, 0.1);
  --shadow-gold: 0 8px 25px rgba(217, 119, 6, 0.2), 0 0 20px rgba(217, 119, 6, 0.1);
  --glass-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.08);

  --font-calligraphy: 'Inter', -apple-system, sans-serif;
  --cursor-sword: auto;
  --cursor-pointer: pointer;
}

body[data-theme='modern'] button,
body[data-theme='modern'] a,
body[data-theme='modern'] select,
body[data-theme='modern'] input,
body[data-theme='modern'] textarea,
body[data-theme='modern'] label,
body[data-theme='modern'] [role="button"],
body[data-theme='modern'] .clickable-brand,
body[data-theme='modern'] .user-badge-btn,
body[data-theme='modern'] .tab-btn,
body[data-theme='modern'] .btn-jade,
body[data-theme='modern'] .btn-jade-sm,
body[data-theme='modern'] .ocr-dropzone {
  cursor: pointer !important;
}

body[data-theme='modern'] .btn-jade,
.modern-mode .btn-jade {
  background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%) !important;
  color: #ffffff !important;
  border: 1px solid #3B82F6 !important;
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.35) !important;
}
body[data-theme='modern'] .btn-jade:hover:not(:disabled),
.modern-mode .btn-jade:hover:not(:disabled) {
  box-shadow: 0 8px 25px rgba(37, 99, 235, 0.45) !important;
}
body[data-theme='modern'] .btn-jade-sm,
.modern-mode .btn-jade-sm {
  background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%) !important;
  color: #ffffff !important;
  border: 1px solid #3B82F6 !important;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
}
body[data-theme='modern'] .user-bubble .bubble-content,
.modern-mode .user-bubble .bubble-content {
  background: linear-gradient(135deg, #2563EB, #3B82F6) !important;
  color: #ffffff !important;
}
body[data-theme='modern'] .tab-btn.active,
.modern-mode .tab-btn.active {
  color: #2563EB !important;
  border-bottom-color: #2563EB !important;
  background: rgba(37, 99, 235, 0.08) !important;
}
body[data-theme='modern'] .clickable-brand:hover,
.modern-mode .clickable-brand:hover {
  background: rgba(37, 99, 235, 0.08) !important;
}
body[data-theme='modern'] .user-badge-btn,
.modern-mode .user-badge-btn {
  background: var(--bg-secondary) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-primary) !important;
}
body[data-theme='modern'] .user-badge-btn:hover,
.modern-mode .user-badge-btn:hover {
  background: var(--bg-card-hover) !important;
  border-color: #2563EB !important;
}

body {
  font-family: var(--font-body);
  background: var(--bg-body-gradient) attachment fixed;
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  cursor: var(--cursor-sword);
}

body,
.realm-header,
.tab-nav,
.tab-btn,
.metric-card,
.chart-card,
.saving-tips-card,
.xianxia-table,
.form-card,
.wallet-card,
.budget-card,
.stats-chart-card,
.compare-card,
.chat-container,
.modal-card,
.filter-card,
.recurring-box,
.ocr-result-card,
.login-card,
.user-badge-btn,
.theme-btn,
.input-group-xianxia input,
.input-group-xianxia select {
  transition: background 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease, box-shadow 0.3s ease;
}

.theme-btn {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 7px 15px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-body);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  box-shadow: var(--glass-shadow);
  cursor: var(--cursor-pointer);
}
.theme-btn:hover {
  border-color: var(--gold-glow);
  transform: translateY(-2px);
  box-shadow: var(--shadow-gold);
}
.login-theme-toggle {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}

button, a, select, input, textarea, label, [role="button"], .clickable-brand, .user-badge-btn, .tab-btn, .btn-jade, .btn-jade-sm, .ocr-dropzone {
  cursor: var(--cursor-pointer) !important;
}

/* ─── SCROLLBAR ────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(238, 244, 248, 0.5); }
::-webkit-scrollbar-thumb { background: rgba(79, 168, 160, 0.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--jade-glow); }

/* ─── PERSISTENT XIANXIA BACKDROP ───────── */
.xianxia-backdrop {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.sun-aura-glow {
  position: absolute;
  top: -100px;
  left: 50%;
  transform: translateX(-50%);
  width: 1100px;
  height: 650px;
  background: radial-gradient(ellipse at center, rgba(255, 248, 220, 0.65) 0%, rgba(232, 200, 116, 0.3) 35%, rgba(143, 184, 217, 0.12) 65%, transparent 80%);
  filter: blur(25px);
  animation: auraPulse 10s ease-in-out infinite alternate;
}

@keyframes auraPulse {
  0% { opacity: 0.7; transform: translateX(-50%) scale(0.95); }
  100% { opacity: 1; transform: translateX(-50%) scale(1.05); }
}

.mountain-layer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  width: 100%;
  pointer-events: none;
}

.far-mountains { height: 280px; z-index: 1; opacity: 0.55; }
.mid-mountains { height: 240px; z-index: 2; opacity: 0.75; }
.near-mountains { height: 190px; z-index: 3; opacity: 0.92; }

.mountain-layer svg {
  width: 100%;
  height: 100%;
  display: block;
}

/* Sea of Clouds (Biển Mây) */
.sea-of-clouds-wrapper {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 180px;
  z-index: 4;
  overflow: hidden;
  pointer-events: none;
}

.sea-of-clouds {
  position: absolute;
  bottom: 0;
  width: 200%;
  height: 100%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0) 0%, rgba(238, 244, 248, 0.8) 45%, rgba(255, 255, 255, 0.98) 100%);
  mask-image: radial-gradient(ellipse 100% 100% at 50% 100%, black 65%, transparent 100%);
}

.sea-of-clouds.wave-1 {
  animation: seaCloudsScroll 75s linear infinite;
  opacity: 0.85;
}
.sea-of-clouds.wave-2 {
  animation: seaCloudsScroll 110s linear infinite reverse;
  opacity: 0.6;
  bottom: -20px;
}

@keyframes seaCloudsScroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

/* Floating Clouds */
.floating-clouds {
  position: absolute;
  top: 0;
  inset-inline: 0;
  height: 50vh;
  z-index: 2;
  pointer-events: none;
}

.cloud-cluster {
  position: absolute;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.7) 0%, rgba(238, 244, 248, 0.35) 60%, transparent 80%);
  border-radius: 50%;
  filter: blur(16px);
}

.cloud-1 {
  width: 340px; height: 130px; top: 8%; left: -120px;
  animation: floatCloudLeftToRight 85s linear infinite;
  opacity: 0.6;
}
.cloud-2 {
  width: 480px; height: 170px; top: 22%; left: -220px;
  animation: floatCloudLeftToRight 125s linear infinite 18s;
  opacity: 0.45;
}
.cloud-3 {
  width: 290px; height: 110px; top: 4%; left: -160px;
  animation: floatCloudLeftToRight 68s linear infinite 35s;
  opacity: 0.65;
}

@keyframes floatCloudLeftToRight {
  0% { transform: translateX(0); }
  100% { transform: translateX(calc(100vw + 550px)); }
}

/* Spirit Particles */
.spirit-particle-field {
  position: absolute;
  inset: 0;
  z-index: 3;
  pointer-events: none;
}

.spirit-particle {
  position: absolute;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 0 8px #e8c874, 0 0 16px #ffffff;
  animation: spiritFloatUp 9s ease-in-out infinite;
  opacity: 0;
}

@keyframes spiritFloatUp {
  0% { opacity: 0; transform: translateY(100vh) scale(0.4) translateX(0); }
  30% { opacity: 0.85; }
  75% { opacity: 0.95; }
  100% { opacity: 0; transform: translateY(-50px) scale(1.3) translateX(var(--sway, 30px)); }
}

.p-1  { left: 5%;  animation-duration: 9s;  animation-delay: 0s;   --sway: 25px; }
.p-2  { left: 12%; animation-duration: 12s; animation-delay: 1.5s; --sway: -30px; background: #e8c874; }
.p-3  { left: 18%; animation-duration: 7s;  animation-delay: 3s;   --sway: 15px; }
.p-4  { left: 24%; animation-duration: 11s; animation-delay: 0.8s; --sway: -20px; }
.p-5  { left: 30%; animation-duration: 8.5s;animation-delay: 4s;   --sway: 35px; background: #e8c874; }
.p-6  { left: 37%; animation-duration: 10s; animation-delay: 2s;   --sway: -15px; }
.p-7  { left: 43%; animation-duration: 13s; animation-delay: 5s;   --sway: 40px; }
.p-8  { left: 49%; animation-duration: 7.5s;animation-delay: 1s;   --sway: -25px; background: #e8c874; }
.p-9  { left: 55%; animation-duration: 9.5s;animation-delay: 3.5s; --sway: 20px; }
.p-10 { left: 62%; animation-duration: 11.5s;animation-delay: 0.5s;--sway: -35px; }
.p-11 { left: 68%; animation-duration: 8s;  animation-delay: 2.5s; --sway: 30px; background: #e8c874; }
.p-12 { left: 74%; animation-duration: 10.5s;animation-delay: 4.5s;--sway: -18px; }
.p-13 { left: 80%; animation-duration: 12.5s;animation-delay: 1.8s;--sway: 22px; }
.p-14 { left: 86%; animation-duration: 9s;  animation-delay: 3.2s; --sway: -28px; background: #e8c874; }
.p-15 { left: 92%; animation-duration: 7.8s;animation-delay: 0.2s; --sway: 16px; }
.p-16 { left: 8%;  animation-duration: 11s; animation-delay: 5.5s; --sway: -32px; }
.p-17 { left: 21%; animation-duration: 9.8s;animation-delay: 2.2s; --sway: 28px; background: #e8c874; }
.p-18 { left: 35%; animation-duration: 13.5s;animation-delay: 4.2s;--sway: -22px; }
.p-19 { left: 47%; animation-duration: 8.2s;animation-delay: 1.2s; --sway: 18px; }
.p-20 { left: 59%; animation-duration: 10.2s;animation-delay: 3.8s;--sway: -26px; background: #e8c874; }
.p-21 { left: 71%; animation-duration: 7.2s;animation-delay: 0.9s; --sway: 34px; }
.p-22 { left: 83%; animation-duration: 12s; animation-delay: 5.1s; --sway: -14px; }
.p-23 { left: 95%; animation-duration: 9.2s;animation-delay: 2.7s; --sway: 24px; background: #e8c874; }
.p-24 { left: 15%; animation-duration: 10.8s;animation-delay: 4.8s;--sway: -38px; }
.p-25 { left: 65%; animation-duration: 8.8s;animation-delay: 1.6s; --sway: 20px; }

/* ─── ANIMATIONS ───────────────────────── */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInScale {
  from { opacity: 0; transform: scale(0.97) translateY(8px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 15px rgba(232, 200, 116, 0.2); }
  50% { box-shadow: 0 0 30px rgba(232, 200, 116, 0.45), 0 0 50px rgba(79, 168, 160, 0.2); }
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
@keyframes rotateSymbol {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes typingPulse {
  0%, 100% { opacity: 0.3; transform: scale(0.85); }
  50% { opacity: 1; transform: scale(1.05); }
}
@keyframes slideInRight {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

/* ─── LOGIN REALM ──────────────────────── */
.login-realm {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 24px;
}

.login-card {
  position: relative;
  z-index: 10;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(232, 200, 116, 0.6);
  border-radius: var(--radius-lg);
  padding: 48px 40px;
  width: 100%;
  max-width: 460px;
  animation: fadeIn 0.8s ease-out, glowPulse 5s ease-in-out infinite;
  backdrop-filter: blur(16px);
  box-shadow: 0 20px 50px rgba(26, 58, 92, 0.15), 0 0 30px rgba(232, 200, 116, 0.25);
}

.login-header { text-align: center; margin-bottom: 36px; }

.dao-symbol {
  font-size: 56px;
  display: inline-block;
  animation: rotateSymbol 25s linear infinite;
  filter: drop-shadow(0 0 12px rgba(232, 200, 116, 0.8));
  margin-bottom: 16px;
}

.title-calligraphy {
  font-family: var(--font-calligraphy);
  font-size: 28px;
  font-weight: 700;
  color: #1a3a5c;
  letter-spacing: 1.5px;
}

.subtitle-glow {
  color: var(--text-secondary);
  font-size: 13px;
  margin-top: 8px;
  letter-spacing: 0.5px;
}

.form-title {
  font-family: var(--font-calligraphy);
  color: var(--gold);
  font-size: 19px;
  margin-bottom: 24px;
  text-align: center;
}

.input-group-xianxia {
  margin-bottom: 18px;
}
.input-group-xianxia label {
  display: block;
  font-size: 13px;
  color: var(--text-primary);
  margin-bottom: 6px;
  font-weight: 600;
}
.input-group-xianxia input,
.input-group-xianxia select {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  font-family: var(--font-body);
  transition: all 0.3s ease;
  outline: none;
}
.input-group-xianxia input:focus,
.input-group-xianxia select:focus {
  border-color: var(--jade-glow);
  box-shadow: 0 0 0 3px rgba(79, 168, 160, 0.25);
  background: #ffffff;
}
.input-group-xianxia input::placeholder {
  color: var(--text-dim);
}

.btn-jade {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #e8c874 0%, #d99b26 100%);
  color: #1a3a5c;
  border: 1px solid #f3d994;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 700;
  transition: all 0.3s ease;
  font-family: var(--font-body);
  letter-spacing: 0.5px;
  box-shadow: 0 4px 15px rgba(232, 200, 116, 0.35);
}
.btn-jade:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(232, 200, 116, 0.55), 0 0 15px rgba(79, 168, 160, 0.3);
}
.btn-jade:disabled {
  opacity: 0.65;
}

.auth-switch {
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: var(--text-secondary);
}
.auth-switch span {
  color: var(--gold);
  font-weight: 700;
}
.auth-switch span:hover { text-decoration: underline; }

.error-banner {
  margin-top: 16px;
  padding: 12px;
  background: rgba(192, 57, 43, 0.12);
  border: 1px solid rgba(192, 57, 43, 0.4);
  border-radius: 8px;
  color: var(--crimson);
  text-align: center;
  font-size: 13px;
  font-weight: 600;
}

/* ─── MAIN APP REALM ───────────────────── */
.app-realm {
  min-height: 100vh;
  position: relative;
}

/* ─── HEADER ───────────────────────────── */
.realm-header {
  background: rgba(255, 255, 255, 0.82);
  border-bottom: 2px solid rgba(232, 200, 116, 0.5);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(16px);
  box-shadow: 0 4px 20px rgba(26, 58, 92, 0.06);
}
.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.clickable-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  border-radius: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
}
.clickable-brand:hover {
  background: rgba(232, 200, 116, 0.2);
  transform: translateY(-2px) scale(1.01);
}

.header-symbol {
  font-size: 28px;
  animation: rotateSymbol 30s linear infinite;
  filter: drop-shadow(0 0 10px rgba(232, 200, 116, 0.6));
}
.header-title {
  font-family: var(--font-calligraphy);
  font-size: 22px;
  font-weight: 700;
  color: #1a3a5c;
}
.version-badge {
  font-size: 10px;
  padding: 2px 8px;
  background: linear-gradient(135deg, #4fa8a0, #2b8a82);
  color: white;
  border-radius: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-badge-btn {
  font-size: 14px;
  color: #1a3a5c;
  padding: 7px 16px;
  background: rgba(232, 200, 116, 0.2);
  border-radius: 20px;
  border: 1px solid rgba(232, 200, 116, 0.7);
  font-family: var(--font-body);
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(232, 200, 116, 0.2);
}
.user-badge-btn:hover {
  background: rgba(232, 200, 116, 0.4);
  box-shadow: var(--shadow-gold);
  transform: translateY(-2px);
}

.btn-logout {
  padding: 7px 16px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid var(--crimson);
  color: var(--crimson);
  border-radius: 8px;
  font-size: 13px;
  font-family: var(--font-body);
  font-weight: 600;
  transition: all 0.3s;
}
.btn-logout:hover {
  background: rgba(192, 57, 43, 0.12);
}

/* ─── TAB NAV ──────────────────────────── */
.tab-nav {
  background: rgba(255, 255, 255, 0.85);
  border-bottom: 1px solid rgba(232, 200, 116, 0.4);
  position: sticky;
  top: 68px;
  z-index: 99;
  backdrop-filter: blur(14px);
  user-select: none;
}
body[data-theme='modern'] .tab-nav {
  background: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid var(--border);
}

.tab-nav-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  display: flex;
  align-items: center;
}

/* Left & Right Edge Fade Mask Indicators */
.tab-nav::before,
.tab-nav::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  width: 42px;
  pointer-events: none;
  z-index: 5;
  opacity: 0;
  transition: opacity 0.25s ease;
}
.tab-nav::before {
  left: 0;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0) 100%);
}
.tab-nav::after {
  right: 0;
  background: linear-gradient(270deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0) 100%);
}
body[data-theme='modern'] .tab-nav::before {
  background: linear-gradient(90deg, #ffffff 0%, rgba(255, 255, 255, 0) 100%);
}
body[data-theme='modern'] .tab-nav::after {
  background: linear-gradient(270deg, #ffffff 0%, rgba(255, 255, 255, 0) 100%);
}
.tab-nav.has-overflow-left::before {
  opacity: 1;
}
.tab-nav.has-overflow-right::after {
  opacity: 1;
}

.tab-nav-inner {
  width: 100%;
  padding: 0 18px;
  display: flex;
  gap: 4px;
  overflow-x: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(232, 200, 116, 0.4) transparent;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}
.tab-nav-inner::-webkit-scrollbar {
  height: 3px;
}
.tab-nav-inner::-webkit-scrollbar-track {
  background: transparent;
}
.tab-nav-inner::-webkit-scrollbar-thumb {
  background: rgba(232, 200, 116, 0.35);
  border-radius: 3px;
}
.tab-nav-inner::-webkit-scrollbar-thumb:hover {
  background: var(--gold);
}
body[data-theme='modern'] .tab-nav-inner {
  scrollbar-color: rgba(37, 99, 235, 0.3) transparent;
}
body[data-theme='modern'] .tab-nav-inner::-webkit-scrollbar-thumb {
  background: rgba(37, 99, 235, 0.25);
}

.tab-scroll-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(232, 200, 116, 0.7);
  color: var(--text-primary);
  font-size: 13px;
  font-weight: bold;
  cursor: var(--cursor-pointer);
  box-shadow: 0 4px 12px rgba(26, 58, 92, 0.12);
  transition: all 0.2s ease;
}
.tab-scroll-btn:hover {
  background: #ffffff;
  border-color: var(--gold-glow);
  color: var(--gold);
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 16px rgba(232, 200, 116, 0.35);
}
.tab-scroll-btn.left {
  left: 6px;
}
.tab-scroll-btn.right {
  right: 6px;
}
body[data-theme='modern'] .tab-scroll-btn {
  background: #ffffff;
  border: 1px solid var(--border);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
body[data-theme='modern'] .tab-scroll-btn:hover {
  border-color: #2563EB;
  color: #2563EB;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 13px 16px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 13.5px;
  font-weight: 500;
  white-space: nowrap;
  border-bottom: 3px solid transparent;
  transition: all 0.25s ease;
  font-family: var(--font-body);
  flex-shrink: 0;
  border-radius: 6px 6px 0 0;
}
.tab-btn:hover {
  color: var(--gold);
  background: rgba(232, 200, 116, 0.15);
}
.tab-btn.active {
  color: #1a3a5c;
  font-weight: 700;
  border-bottom-color: var(--gold);
  background: linear-gradient(180deg, rgba(232, 200, 116, 0.25) 0%, rgba(232, 200, 116, 0.05) 100%);
}
.tab-icon { font-size: 15px; flex-shrink: 0; }
.tab-label { font-size: 13.5px; white-space: nowrap; }

/* ─── CONTENT ──────────────────────────── */
.realm-content {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  padding: 112px 24px 100px;
}

.tab-panel {
  animation: fadeInScale 0.4s ease-out;
}

.section-title {
  font-family: var(--font-calligraphy);
  font-size: 25px;
  font-weight: 700;
  color: #1a3a5c;
  margin-bottom: 28px;
  letter-spacing: 1px;
  text-shadow: 0 2px 10px rgba(232, 200, 116, 0.3);
}

.sub-title {
  font-family: var(--font-calligraphy);
  font-size: 18px;
  color: #1a3a5c;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(232, 200, 116, 0.4);
}

/* ─── METRICS ──────────────────────────── */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-bottom: 36px;
}

.metric-card {
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 18px;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}
.metric-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  border-radius: var(--radius) var(--radius) 0 0;
}
.metric-card.jade::before { background: linear-gradient(90deg, var(--jade), var(--jade-glow)); }
.metric-card.crimson::before { background: linear-gradient(90deg, var(--crimson), var(--crimson-glow)); }
.metric-card.gold::before { background: linear-gradient(90deg, var(--gold), var(--gold-glow)); }
.metric-card.purple::before { background: linear-gradient(90deg, var(--purple), var(--purple-glow)); }

.metric-card:hover {
  transform: translateY(-4px);
  border-color: #e8c874;
  box-shadow: 0 12px 30px rgba(232, 200, 116, 0.35);
}

.metric-icon {
  font-size: 36px;
  animation: float 3s ease-in-out infinite;
}
.metric-card:nth-child(2) .metric-icon { animation-delay: 0.5s; }
.metric-card:nth-child(3) .metric-icon { animation-delay: 1s; }
.metric-card:nth-child(4) .metric-icon { animation-delay: 1.5s; }

.metric-info { display: flex; flex-direction: column; gap: 6px; }
.metric-label { font-size: 13px; color: var(--text-secondary); font-weight: 600; }
.metric-value {
  font-size: 22px;
  font-weight: 700;
  font-family: var(--font-calligraphy);
  color: #1a3a5c;
}
.metric-value.positive, .positive { color: var(--jade); }
.metric-value.negative, .negative { color: var(--crimson); }

/* ─── ALERTS ───────────────────────────── */
.alerts-section { margin-bottom: 32px; }
.alert-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-radius: 10px;
  margin-bottom: 8px;
  animation: fadeIn 0.5s ease-out;
}
.alert-card.danger {
  background: rgba(192, 57, 43, 0.12);
  border: 1px solid rgba(192, 57, 43, 0.35);
}
.alert-card.warning {
  background: rgba(232, 200, 116, 0.2);
  border: 1px solid rgba(232, 200, 116, 0.6);
}
.alert-icon { font-size: 20px; }
.alert-msg { flex: 1; font-size: 14px; color: var(--text-primary); font-weight: 500; }
.alert-pct { font-weight: 700; font-size: 15px; color: var(--crimson); }

/* ─── DASHBOARD CHARTS ROW ─────────────── */
.dashboard-charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 36px;
}
.chart-card {
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 24px;
  transition: all 0.3s;
  animation: fadeInScale 0.5s ease-out;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}
.chart-card:hover {
  border-color: #e8c874;
  box-shadow: 0 12px 30px rgba(232, 200, 116, 0.3);
}

/* ─── SAVING TIPS ──────────────────────── */
.saving-tips-section {
  margin-bottom: 36px;
}
.saving-tips-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.saving-tips-header .sub-title {
  margin-bottom: 0;
  border-bottom: none;
  padding-bottom: 0;
}
.saving-tips-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(232, 200, 116, 0.6);
  border-radius: var(--radius);
  padding: 28px;
  animation: fadeInScale 0.5s ease-out;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.08);
}
.tips-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  font-size: 13px;
  color: var(--text-secondary);
}
.tips-content {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-primary);
}

/* ─── TABLE ────────────────────────────── */
.table-scroll { overflow-x: auto; }

.xianxia-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(12px);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}
.xianxia-table thead th {
  text-align: left;
  padding: 14px 18px;
  background: rgba(232, 200, 116, 0.2);
  color: #1a3a5c;
  font-family: var(--font-calligraphy);
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(232, 200, 116, 0.5);
  white-space: nowrap;
}
.xianxia-table tbody td {
  padding: 14px 18px;
  border-bottom: 1px solid rgba(232, 200, 116, 0.25);
  color: var(--text-primary);
  vertical-align: middle;
}
.xianxia-table tbody tr {
  transition: background 0.2s;
}
.xianxia-table tbody tr:hover {
  background: rgba(232, 200, 116, 0.15);
}

.cat-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(232, 200, 116, 0.15);
  border: 1px solid rgba(232, 200, 116, 0.4);
  border-radius: 6px;
  font-size: 13px;
  color: #1a3a5c;
  white-space: nowrap;
}

.amt-income { color: var(--jade); font-weight: 700; white-space: nowrap; }
.amt-expense { color: var(--crimson); font-weight: 700; white-space: nowrap; }
.empty-row { text-align: center; color: var(--text-dim); font-style: italic; }

/* ─── CATEGORY BREAKDOWN ──────────────── */
.category-breakdown { margin-top: 32px; }
.cat-bars { display: flex; flex-direction: column; gap: 12px; }
.cat-bar-row {
  display: flex;
  align-items: center;
  gap: 14px;
}
.cat-bar-label {
  min-width: 180px;
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
  white-space: nowrap;
}
.cat-bar-track {
  flex: 1;
  height: 10px;
  background: rgba(232, 200, 116, 0.2);
  border-radius: 5px;
  overflow: hidden;
}
.cat-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--jade), var(--jade-glow));
  border-radius: 5px;
}
.cat-bar-value {
  min-width: 120px;
  text-align: right;
  font-size: 13px;
  font-weight: 600;
  color: #1a3a5c;
  white-space: nowrap;
}

/* ─── FORM CARD ────────────────────────── */
.form-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 28px;
  margin-bottom: 24px;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

/* ─── WALLET TRANSFER ──────────────────── */
.transfer-card {
  border-color: rgba(232, 200, 116, 0.6);
  position: relative;
}
.transfer-arrow-col {
  display: flex;
  align-items: center;
  justify-content: center;
}
.transfer-arrow {
  font-size: 24px;
  color: var(--gold);
  animation: glowPulse 2s ease-in-out infinite;
  margin-top: 20px;
}

/* ─── WALLET CARDS ─────────────────────── */
.wallet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 28px;
}
.wallet-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 24px;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}
.wallet-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(232, 200, 116, 0.35);
  border-color: #e8c874;
}
.wallet-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.wallet-type-icon { font-size: 28px; }
.wallet-name {
  font-family: var(--font-calligraphy);
  font-size: 17px;
  color: #1a3a5c;
  margin-bottom: 8px;
}
.wallet-balance {
  font-size: 24px;
  font-weight: 700;
  color: var(--jade);
  font-family: var(--font-calligraphy);
  margin-bottom: 4px;
}
.wallet-type-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* ─── CATEGORIES ───────────────────────── */
.categories-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 28px;
}
.cat-col { display: flex; flex-direction: column; gap: 8px; }
.cat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(232, 200, 116, 0.4);
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.3s;
}
.cat-item:hover { border-color: #e8c874; }
.cat-item.income { border-color: rgba(43, 138, 130, 0.5); }
.cat-item.expense { border-color: rgba(192, 57, 43, 0.5); }

/* ─── BUTTONS SMALL ────────────────────── */
.btn-sm-danger {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(192, 57, 43, 0.1);
  border: 1px solid rgba(192, 57, 43, 0.3);
  border-radius: 6px;
  color: var(--crimson);
  font-size: 14px;
  transition: all 0.3s;
}
.btn-sm-danger:hover {
  background: rgba(192, 57, 43, 0.25);
  border-color: var(--crimson);
}

/* ─── OCR UPLOAD ───────────────────────── */
.hint-text {
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 16px;
}
.upload-zone {
  border: 2px dashed rgba(232, 200, 116, 0.7);
  border-radius: var(--radius);
  padding: 48px 24px;
  text-align: center;
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.75);
}
.upload-zone:hover {
  border-color: var(--gold);
  background: rgba(232, 200, 116, 0.15);
}
.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--text-secondary);
}
.upload-icon { font-size: 40px; }
.ocr-preview-img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  object-fit: contain;
}

.ocr-result-card {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid #e8c874;
  border-radius: var(--radius);
  padding: 28px;
  margin-top: 24px;
  animation: fadeIn 0.5s ease-out;
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.08);
}
.ocr-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}
.ocr-info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.ocr-info-item label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}
.ocr-info-item span {
  font-size: 16px;
  color: var(--text-primary);
  font-weight: 600;
}
.ocr-total {
  color: var(--jade) !important;
  font-family: var(--font-calligraphy);
  font-size: 22px !important;
}
.ocr-items { margin-top: 16px; }
.ocr-items h4 { margin-bottom: 12px; color: var(--text-primary); font-size: 14px; }
.ocr-raw { margin-top: 16px; }
.ocr-raw h4 { margin-bottom: 8px; color: var(--text-secondary); font-size: 13px; }
.ocr-raw pre {
  background: rgba(238, 244, 248, 0.8);
  padding: 16px;
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-primary);
  overflow-x: auto;
  white-space: pre-wrap;
  border: 1px solid rgba(232, 200, 116, 0.3);
}

/* ─── BUDGETS ──────────────────────────── */
.budget-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 16px;
  margin-top: 24px;
}
.budget-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 20px;
  transition: all 0.3s;
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}
.budget-card:hover { border-color: #e8c874; box-shadow: 0 12px 30px rgba(232, 200, 116, 0.3); }
.budget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 600;
  color: #1a3a5c;
}
.budget-amounts {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 10px;
}
.progress-track {
  height: 12px;
  background: rgba(232, 200, 116, 0.2);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 8px;
}
.progress-fill {
  height: 100%;
  border-radius: 6px;
}
.progress-fill.safe { background: linear-gradient(90deg, var(--jade), var(--jade-glow)); }
.progress-fill.warning { background: linear-gradient(90deg, var(--gold), var(--gold-glow)); }
.progress-fill.danger {
  background: linear-gradient(90deg, var(--crimson), var(--crimson-glow));
  animation: glowPulse 1.5s ease-in-out infinite;
}
.budget-pct { font-size: 13px; font-weight: 600; }
.pct-safe { color: var(--jade); }
.pct-warning { color: var(--gold); }
.pct-danger { color: var(--crimson); }

/* ─── STATISTICS TAB ───────────────────── */
.stats-chart-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 28px;
  margin-bottom: 28px;
  animation: fadeInScale 0.5s ease-out;
  transition: all 0.3s;
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}
.stats-chart-card:hover {
  border-color: #e8c874;
  box-shadow: 0 12px 30px rgba(232, 200, 116, 0.3);
}

/* ─── COMPARE SECTION ──────────────────── */
.compare-section {
  margin-top: 8px;
}
.compare-controls {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 24px;
}
.compare-vs {
  font-size: 20px;
  font-weight: 700;
  color: var(--gold);
  font-family: var(--font-calligraphy);
  padding-bottom: 16px;
}
.compare-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 20px;
  align-items: stretch;
}
.compare-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 24px;
  animation: slideInRight 0.5s ease-out;
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}
.compare-card h4 {
  font-family: var(--font-calligraphy);
  color: #1a3a5c;
  margin-bottom: 16px;
  font-size: 16px;
}
.compare-stat {
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 14px;
  color: var(--text-secondary);
}
.compare-stat strong {
  font-size: 16px;
  color: var(--text-primary);
}
.compare-delta {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
}
.delta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}
.delta-up {
  background: rgba(43, 138, 130, 0.12);
  color: var(--jade);
  border: 1px solid rgba(43, 138, 130, 0.3);
}
.delta-down {
  background: rgba(192, 57, 43, 0.12);
  color: var(--crimson);
  border: 1px solid rgba(192, 57, 43, 0.3);
}
.delta-arrow {
  font-size: 14px;
}

/* ─── AI CHAT ──────────────────────────── */
.chat-container {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(232, 200, 116, 0.6);
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 280px);
  min-height: 500px;
  backdrop-filter: blur(14px);
  box-shadow: 0 12px 35px rgba(26, 58, 92, 0.08);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-welcome {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 20px;
  background: rgba(232, 200, 116, 0.15);
  border: 1px solid rgba(232, 200, 116, 0.4);
  border-radius: var(--radius);
  margin-bottom: 8px;
}
.chat-ai-avatar {
  font-size: 36px;
  animation: float 3s ease-in-out infinite;
}
.chat-welcome p {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.7;
}

.chat-bubble {
  display: flex;
  gap: 12px;
  max-width: 85%;
  animation: fadeIn 0.3s ease-out;
}
.user-bubble { align-self: flex-end; flex-direction: row-reverse; }
.ai-bubble { align-self: flex-start; }

.bubble-avatar { font-size: 24px; flex-shrink: 0; }
.bubble-content {
  padding: 14px 18px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.7;
}
.user-bubble .bubble-content {
  background: linear-gradient(135deg, #e8c874, #d99b26);
  color: #1a3a5c;
  font-weight: 500;
  border-bottom-right-radius: 4px;
  box-shadow: 0 4px 12px rgba(232, 200, 116, 0.3);
}
.ai-bubble .bubble-content {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(232, 200, 116, 0.4);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}

.typing-indicator {
  display: flex;
  gap: 6px;
  padding: 8px 12px !important;
}
.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--gold);
  border-radius: 50%;
  animation: typingPulse 1.2s infinite ease-in-out;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

.chat-input-area {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid rgba(232, 200, 116, 0.4);
  background: rgba(238, 244, 248, 0.6);
}
.chat-input-area input {
  flex: 1;
  padding: 12px 16px;
  background: #ffffff;
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  font-family: var(--font-body);
  transition: border-color 0.3s;
}
.chat-input-area input:focus {
  border-color: var(--jade-glow);
  box-shadow: 0 0 0 3px rgba(79, 168, 160, 0.2);
}

.btn-jade-sm {
  padding: 12px 24px;
  background: linear-gradient(135deg, #e8c874, #d99b26);
  color: #1a3a5c;
  border: 1px solid #f3d994;
  border-radius: 10px;
  font-weight: 700;
  font-family: var(--font-body);
  font-size: 14px;
  transition: all 0.3s;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(232, 200, 116, 0.3);
}
.btn-jade-sm:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(232, 200, 116, 0.5);
}
.btn-jade-sm:disabled { opacity: 0.5; }

/* ─── MODAL ACCOUNT MANAGEMENT ────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(26, 58, 92, 0.4);
  backdrop-filter: blur(8px);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: fadeIn 0.3s ease-out;
}
.modal-card {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid #e8c874;
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 440px;
  padding: 28px;
  box-shadow: 0 20px 50px rgba(26, 58, 92, 0.2), 0 0 30px rgba(232, 200, 116, 0.3);
  animation: fadeInScale 0.3s ease-out;
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.modal-title {
  font-family: var(--font-calligraphy);
  font-size: 19px;
  color: #1a3a5c;
  font-weight: 700;
}
.modal-close {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 20px;
  transition: color 0.2s;
}
.modal-close:hover { color: var(--crimson); }
.disabled-input {
  opacity: 0.7;
  background: rgba(238, 244, 248, 0.8) !important;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
.btn-secondary {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid rgba(232, 200, 116, 0.6);
  color: var(--text-primary);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}
.btn-secondary:hover { background: rgba(232, 200, 116, 0.15); }

/* ─── TOAST ────────────────────────────── */
.toast-notification {
  position: fixed;
  bottom: 30px;
  right: 30px;
  padding: 14px 24px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  z-index: 9999;
  animation: fadeIn 0.3s ease-out;
  max-width: 400px;
  backdrop-filter: blur(8px);
}
.toast-notification.success {
  background: rgba(43, 138, 130, 0.95);
  color: white;
  border: 1px solid var(--jade-glow);
  box-shadow: 0 8px 30px rgba(43, 138, 130, 0.4);
}
.toast-notification.error {
  background: rgba(192, 57, 43, 0.95);
  color: white;
  border: 1px solid var(--crimson-glow);
  box-shadow: 0 8px 30px rgba(192, 57, 43, 0.4);
}

/* ─── AUTH LINKS & DEV NOTICE ──────────── */
.auth-links {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 14px;
}
.dev-token-notice {
  background: rgba(232, 200, 116, 0.2);
  border: 1px solid var(--gold);
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 13px;
  color: #1a3a5c;
  margin-bottom: 14px;
  text-align: center;
}

/* ─── SECTION HEADER & ACTION BUTTONS ──── */
.section-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
}
.section-header-flex .section-title {
  margin-bottom: 0;
}
.action-btn-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.btn-action-gold {
  padding: 8px 16px;
  background: linear-gradient(135deg, #e8c874, #d99b26);
  color: #1a3a5c;
  border: 1px solid #f3d994;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(232, 200, 116, 0.3);
}
.btn-action-gold:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(232, 200, 116, 0.5);
}
.btn-action-jade {
  padding: 8px 16px;
  background: linear-gradient(135deg, #2b8a82, #1e5a55);
  color: #ffffff;
  border: 1px solid var(--jade-glow);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(43, 138, 130, 0.3);
}
.btn-action-jade:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(43, 138, 130, 0.5);
}
.btn-action-secondary {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.85);
  color: #1a3a5c;
  border: 1px solid rgba(232, 200, 116, 0.6);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s;
}
.btn-action-secondary:hover {
  background: rgba(232, 200, 116, 0.2);
  transform: translateY(-2px);
}

/* ─── RECURRING SECTION ────────────────── */
.recurring-box {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid #e8c874;
  border-radius: var(--radius);
  padding: 24px;
  margin-bottom: 28px;
  animation: fadeInScale 0.3s ease-out;
  box-shadow: 0 10px 30px rgba(232, 200, 116, 0.2);
}
.recurring-header {
  margin-bottom: 16px;
}
.btn-status-active {
  padding: 4px 10px;
  background: rgba(43, 138, 130, 0.15);
  border: 1px solid var(--jade);
  color: var(--jade);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s;
}
.btn-status-inactive {
  padding: 4px 10px;
  background: rgba(192, 57, 43, 0.15);
  border: 1px solid var(--crimson);
  color: var(--crimson);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s;
}

/* ─── EDIT & ACTION BUTTONS ────────────── */
.btn-sm-edit {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(232, 200, 116, 0.2);
  border: 1px solid var(--gold);
  border-radius: 6px;
  color: #1a3a5c;
  font-size: 13px;
  transition: all 0.2s;
}
.btn-sm-edit:hover {
  background: rgba(232, 200, 116, 0.4);
  transform: translateY(-1px);
}
.action-cell, .card-action-btns, .cat-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ─── FILTER & SEARCH CARD ─────────────── */
.filter-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 20px 24px;
  margin-bottom: 24px;
  box-shadow: 0 6px 20px rgba(26, 58, 92, 0.05);
}
.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.filter-title {
  font-family: var(--font-calligraphy);
  font-size: 16px;
  color: #1a3a5c;
  font-weight: 700;
}
.btn-link {
  background: transparent;
  border: none;
  color: var(--jade);
  font-size: 13px;
  font-weight: 600;
  text-decoration: underline;
  transition: color 0.2s;
}
.btn-link:hover { color: var(--gold); }
.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 12px;
}
.filter-grid .input-group-xianxia {
  margin-bottom: 0;
}

/* ─── PAGINATION ───────────────────────── */
.table-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}
.pagination-controls, .pagination-footer {
  display: flex;
  align-items: center;
  gap: 10px;
}
.pagination-footer {
  justify-content: center;
  margin-top: 18px;
}
.btn-page {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(232, 200, 116, 0.6);
  border-radius: 6px;
  color: #1a3a5c;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s;
}
.btn-page:hover:not(:disabled) {
  background: rgba(232, 200, 116, 0.25);
  border-color: #e8c874;
}
.btn-page:disabled {
  opacity: 0.4;
}
.page-info {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* ─── EMPTY STATE ──────────────────────── */
.empty-state {
  text-align: center;
  padding: 32px;
  color: var(--text-secondary);
  font-size: 14px;
  font-style: italic;
}

/* ─── DEBT BADGES & STYLES ───────────────── */
.badge-debt-type {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
}
.badge-debt-type.borrow {
  background: rgba(220, 38, 38, 0.15);
  color: var(--crimson);
  border: 1px solid rgba(220, 38, 38, 0.35);
}
.badge-debt-type.lend {
  background: rgba(43, 138, 130, 0.15);
  color: var(--jade);
  border: 1px solid rgba(43, 138, 130, 0.35);
}
.debt-status-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}
.debt-status-tag.badge-settled {
  background: rgba(43, 138, 130, 0.15);
  color: var(--jade);
}
.debt-status-tag.badge-overdue {
  background: rgba(220, 38, 38, 0.15);
  color: var(--crimson);
}
.debt-status-tag.badge-due-today {
  background: rgba(217, 119, 6, 0.18);
  color: var(--gold);
}
.debt-status-tag.badge-pending {
  background: rgba(100, 116, 139, 0.15);
  color: var(--text-secondary);
}
.debt-status-tag.badge-no-due {
  color: var(--text-dim);
}
.row-settled {
  opacity: 0.65;
}
.btn-sm-settle {
  padding: 4px 8px;
  background: rgba(43, 138, 130, 0.15);
  border: 1px solid var(--jade-glow);
  border-radius: 6px;
  cursor: var(--cursor-pointer);
  transition: all 0.2s;
}
.btn-sm-settle:hover {
  background: var(--jade-glow);
  color: white;
  transform: scale(1.1);
}
.person-cell {
  color: var(--text-primary);
}

/* ─── SAVING GOALS STYLES ───────────────── */
.goals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-top: 16px;
}
.goal-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--glass-shadow);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.goal-card:hover {
  border-color: var(--border-glow);
  transform: translateY(-2px);
  box-shadow: var(--shadow-gold);
}
.goal-card.goal-completed {
  border-color: var(--jade-glow);
  background: linear-gradient(135deg, var(--bg-card) 0%, rgba(43, 138, 130, 0.08) 100%);
}
.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}
.goal-icon-name {
  display: flex;
  align-items: center;
  gap: 10px;
}
.goal-icon {
  font-size: 28px;
}
.goal-name {
  font-family: var(--font-calligraphy);
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}
.goal-date {
  font-size: 12px;
  color: var(--text-secondary);
  display: block;
  margin-top: 2px;
}
.goal-badge {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
}
.goal-badge.completed {
  background: rgba(43, 138, 130, 0.18);
  color: var(--jade);
  border: 1px solid var(--jade-glow);
}
.goal-badge.in-progress {
  background: rgba(232, 200, 116, 0.2);
  color: var(--gold);
  border: 1px solid var(--gold-glow);
}
.goal-progress-wrap {
  margin: 14px 0;
}
.goal-amounts {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 6px;
}
.goal-current {
  font-size: 18px;
  font-weight: 700;
  color: var(--jade);
}
.goal-target {
  font-size: 13px;
  color: var(--text-dim);
}
.goal-progress-bar {
  height: 10px;
  background: rgba(0, 0, 0, 0.06);
  border-radius: 6px;
  overflow: hidden;
  position: relative;
}
.goal-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--jade) 0%, var(--jade-glow) 100%);
  border-radius: 6px;
  transition: width 0.6s ease;
}
.goal-completed .goal-progress-fill {
  background: linear-gradient(90deg, #d99b26 0%, #e8c874 100%);
}
.goal-progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 6px;
}
.goal-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 14px;
  flex-wrap: wrap;
}

/* ─── ADMIN STYLES ──────────────────────── */
.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
}
.role-badge.admin {
  background: rgba(217, 119, 6, 0.2);
  color: var(--gold);
  border: 1px solid var(--gold-glow);
}
.role-badge.user {
  background: rgba(43, 138, 130, 0.15);
  color: var(--jade);
  border: 1px solid rgba(43, 138, 130, 0.35);
}
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
}
.status-badge.active {
  background: rgba(43, 138, 130, 0.15);
  color: var(--jade);
}
.status-badge.locked {
  background: rgba(220, 38, 38, 0.2);
  color: var(--crimson);
  border: 1px solid rgba(220, 38, 38, 0.4);
}
.row-locked {
  opacity: 0.6;
  background: rgba(220, 38, 38, 0.05);
}
.admin-tab-btn {
  border-color: rgba(217, 119, 6, 0.4) !important;
}
.admin-tab-btn.active {
  box-shadow: 0 0 12px rgba(217, 119, 6, 0.4);
}
.actions-cell {
  display: flex;
  gap: 6px;
  align-items: center;
}
.btn-sm-secondary {
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 12px;
  cursor: var(--cursor-pointer);
  transition: all 0.2s;
}
.btn-sm-secondary:hover {
  background: var(--bg-hover);
  border-color: var(--border-glow);
}

/* ─── RESPONSIVE ───────────────────────── */
/* ─── RESPONSIVE ───────────────────────── */
@media (max-width: 1024px) {
  .tab-btn { padding: 11px 13px; font-size: 13px; gap: 5px; }
  .tab-label { font-size: 13px; }
}

@media (max-width: 768px) {
  .header-title { font-size: 17px; }
  .version-badge { display: none; }
  .realm-content { padding: 112px 16px 80px; }
  .metrics-grid { grid-template-columns: 1fr; }
  .categories-split { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
  .wallet-grid { grid-template-columns: 1fr; }
  .budget-list { grid-template-columns: 1fr; }
  .tab-btn { padding: 10px 11px; font-size: 12.5px; gap: 5px; }
  .tab-label { font-size: 12.5px; }
  .tab-icon { font-size: 14px; }
  .tab-scroll-btn { width: 26px; height: 26px; font-size: 11px; }
  .login-card { margin: 16px; padding: 32px 24px; }
  .chat-container { height: calc(100vh - 240px); min-height: 400px; }
  .user-badge-btn { padding: 6px 10px; font-size: 12px; }
  .dashboard-charts-row { grid-template-columns: 1fr; }
  .compare-grid { grid-template-columns: 1fr; }
  .compare-delta { flex-direction: row; flex-wrap: wrap; justify-content: center; }
  .compare-controls { flex-direction: column; }
  .compare-vs { padding-bottom: 0; }
  .transfer-arrow-col { display: none; }

  /* Mobile backdrop optimization */
  .far-mountains { height: 180px; }
  .mid-mountains { height: 150px; }
  .near-mountains { height: 120px; }
  .floating-clouds { display: none; }
  .spirit-particle-field .spirit-particle:nth-child(n+13) { display: none; }
}

@media (max-width: 480px) {
  .tab-btn { padding: 8px 9px; font-size: 12px; gap: 4px; }
  .tab-label { font-size: 12px; }
  .tab-icon { font-size: 13px; }
  .metric-value { font-size: 19px; }
  .section-title { font-size: 21px; }
  .cat-bar-label { min-width: 120px; font-size: 12px; }
  .cat-bar-value { min-width: 90px; font-size: 12px; }
  .saving-tips-header { flex-direction: column; gap: 12px; align-items: flex-start; }
}

.suggested-questions-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px 15px;
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
  align-items: center;
}
.suggested-chip {
  background: rgba(14, 165, 233, 0.1);
  color: var(--primary-color);
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid rgba(14, 165, 233, 0.2);
}
.suggested-chip:hover {
  background: var(--primary-color);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(14, 165, 233, 0.3);
}

/* VueDatePicker Customization — Celestial Treasury System */
.dp--theme-dark,
.dp__theme_dark {
  --dp-background-color: #131b2e;
  --dp-text-color: #dae2fd;
  --dp-hover-color: rgba(125, 214, 204, 0.15);
  --dp-hover-text-color: #ffffff;
  --dp-hover-icon-color: #7dd6cc;
  --dp-primary-color: #7dd6cc;
  --dp-primary-disabled-color: rgba(125, 214, 204, 0.3);
  --dp-primary-text-color: #003733;
  --dp-secondary-color: #1b2337;
  --dp-border-color: rgba(125, 214, 204, 0.25);
  --dp-menu-border-color: rgba(125, 214, 204, 0.25);
  --dp-border-color-hover: #7dd6cc;
  --dp-border-color-focus: #7dd6cc;
  --dp-disabled-color: rgba(255, 255, 255, 0.08);
  --dp-disabled-color-text: rgba(255, 255, 255, 0.3);
  --dp-scroll-bar-background: #0b1326;
  --dp-scroll-bar-color: #7dd6cc;
  --dp-success-color: #7dd6cc;
  --dp-icon-color: #7dd6cc;
  --dp-danger-color: #ffb4ab;
  --dp-range-between-dates-background-color: rgba(125, 214, 204, 0.18);
  --dp-range-between-dates-text-color: #ffffff;
  --dp-range-between-border-color: rgba(125, 214, 204, 0.35);
}

body[data-theme='modern'] .dp--theme-light,
body[data-theme='modern'] .dp__theme_light,
.dp--theme-light,
.dp__theme_light {
  --dp-background-color: #ffffff;
  --dp-text-color: #0F172A;
  --dp-hover-color: #F1F5F9;
  --dp-hover-text-color: #0F172A;
  --dp-hover-icon-color: #2563EB;
  --dp-primary-color: #2563EB;
  --dp-primary-disabled-color: #93C5FD;
  --dp-primary-text-color: #ffffff;
  --dp-secondary-color: #F8FAFC;
  --dp-border-color: #CBD5E1;
  --dp-menu-border-color: #E2E8F0;
  --dp-border-color-hover: #3B82F6;
  --dp-border-color-focus: #2563EB;
  --dp-disabled-color: #F1F5F9;
  --dp-disabled-color-text: #94A3B8;
  --dp-scroll-bar-background: #F8FAFC;
  --dp-scroll-bar-color: #CBD5E1;
  --dp-success-color: #10B981;
  --dp-icon-color: #64748B;
  --dp-danger-color: #EF4444;
  --dp-range-between-dates-background-color: #EFF6FF;
  --dp-range-between-dates-text-color: #1E40AF;
  --dp-range-between-border-color: #BFDBFE;
}

.dp__menu {
  background: #131b2e !important;
  border: 1px solid rgba(125, 214, 204, 0.3) !important;
  border-radius: 14px !important;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7), 0 0 20px rgba(125, 214, 204, 0.12) !important;
  backdrop-filter: blur(16px) !important;
  overflow: hidden;
}
body[data-theme='modern'] .dp__menu {
  background: #ffffff !important;
  border: 1px solid #E2E8F0 !important;
  box-shadow: 0 12px 36px rgba(15, 23, 42, 0.15) !important;
}
.dp__input {
  border-radius: 10px !important;
  font-size: 13px !important;
}

/* Ensure dropdown is above everything */
.dp__outer_menu_wrap {
  z-index: 9999 !important;
}

/* Mobile responsive fix for datepicker */
@media (max-width: 768px) {
  .stats-datepicker-wrapper {
    width: 100% !important;
  }
}

/* ─── AI CHAT (RESTORED LARGE TEXT UI) ─── */
.chat-container {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(232, 200, 116, 0.6);
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 280px);
  min-height: 500px;
  backdrop-filter: blur(14px);
  box-shadow: 0 12px 35px rgba(26, 58, 92, 0.08);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-welcome {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 20px;
  background: rgba(232, 200, 116, 0.15);
  border: 1px solid rgba(232, 200, 116, 0.4);
  border-radius: var(--radius);
  margin-bottom: 8px;
}
.chat-ai-avatar {
  font-size: 36px;
  animation: float 3s ease-in-out infinite;
}
.chat-welcome p {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.7;
}

.chat-bubble {
  display: flex;
  gap: 12px;
  max-width: 85%;
  animation: fadeIn 0.3s ease-out;
}
.user-bubble { align-self: flex-end; flex-direction: row-reverse; }
.ai-bubble { align-self: flex-start; }

.bubble-avatar { font-size: 24px; flex-shrink: 0; }
.bubble-content {
  padding: 14px 18px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.7;
}
.user-bubble .bubble-content {
  background: linear-gradient(135deg, #e8c874, #d99b26);
  color: #1a3a5c;
  font-weight: 500;
  border-bottom-right-radius: 4px;
  box-shadow: 0 4px 12px rgba(232, 200, 116, 0.3);
}
.ai-bubble .bubble-content {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(232, 200, 116, 0.4);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}

.typing-indicator {
  display: flex;
  gap: 6px;
  padding: 8px 12px !important;
}
.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--gold);
  border-radius: 50%;
  animation: typingPulse 1.2s infinite ease-in-out;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

.suggested-questions-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px 15px;
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
  align-items: center;
}
.suggested-chip {
  background: rgba(14, 165, 233, 0.1);
  color: var(--primary-color);
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid rgba(14, 165, 233, 0.2);
}
.suggested-chip:hover {
  background: var(--primary-color);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(14, 165, 233, 0.3);
}

.chat-input-area {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid rgba(232, 200, 116, 0.4);
  background: rgba(238, 244, 248, 0.6);
}
.chat-input-area input {
  flex: 1;
  padding: 12px 16px;
  background: #ffffff;
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  font-family: var(--font-body);
  transition: border-color 0.3s;
}
.chat-input-area input:focus {
  border-color: var(--jade-glow);
  box-shadow: 0 0 0 3px rgba(79, 168, 160, 0.2);
}

.btn-jade-sm {
  padding: 12px 24px;
  background: linear-gradient(135deg, #e8c874, #d99b26);
  color: #1a3a5c;
  border: 1px solid #f3d994;
  border-radius: 10px;
  font-weight: 700;
  font-family: var(--font-body);
  font-size: 14px;
  transition: all 0.3s;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(232, 200, 116, 0.3);
}
.btn-jade-sm:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(232, 200, 116, 0.5);
}
.btn-jade-sm:disabled { opacity: 0.5; }

@media (max-width: 768px) {
  .chat-container { height: calc(100vh - 240px); min-height: 400px; }
}
</style>
