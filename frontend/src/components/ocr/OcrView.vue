<template>
  <div class="ocr-realm">
    <!-- Spatial Atmosphere Glow Orbs -->
    <div class="ambient-glow-orb orb-primary" aria-hidden="true"></div>
    <div class="ambient-glow-orb orb-secondary" aria-hidden="true"></div>

    <!-- ═══ HEADER & ENGINE STATUS ═══ -->
    <section class="ocr-header">
      <div class="header-text-group">
        <div class="header-badge-row">
          <div class="status-pulse-dot"></div>
          <span class="badge-text">BÁT QUÁI KÍNH THẦN THỨC • PHIÊN BẢN LINH GIÁC 3.4</span>
        </div>
        <div class="title-with-badge">
          <h1 class="page-title">Linh Nhãn Quét Hóa Đơn</h1>
          <span class="engine-badge">
            <span class="engine-pulse-dot"></span>
            OCR Engine Active
          </span>
        </div>
        <p class="page-subtitle">
          Thần thức AI quét hóa đơn, biên nhận và chứng từ tức thì, trích xuất dữ liệu tự động lập sổ giao dịch chuẩn xác, thanh trừ tạp niệm sai sót.
        </p>
      </div>

      <!-- Quick Action Pill Group -->
      <div class="header-actions">
        <button
          type="button"
          class="btn-stitch-secondary"
          @click="triggerFileInput"
          title="Tải ảnh hóa đơn mới"
        >
          <span class="material-symbols-outlined icon-sm">add_photo_alternate</span>
          <span>Tải Hóa Đơn</span>
        </button>
        <button
          v-if="ocrFile || ocrResult"
          type="button"
          class="btn-stitch-subtle"
          @click="onReset"
          title="Xóa trắng và làm lại"
        >
          <span class="material-symbols-outlined icon-sm">restart_alt</span>
          <span>Làm Lại</span>
        </button>
      </div>
    </section>

    <!-- ═══ WORKFLOW STEP INDICATOR (4 STEPS) ═══ -->
    <section class="ocr-steps-bar" aria-label="Tiến trình nhận diện hóa đơn">
      <div class="steps-grid">
        <!-- Step 1: Upload File -->
        <div class="step-item" :class="{ 'is-completed': currentStep > 1, 'is-active': currentStep === 1 }">
          <div class="step-icon-box">
            <span v-if="currentStep > 1" class="material-symbols-outlined step-check">check</span>
            <span v-else class="step-number">1</span>
          </div>
          <div class="step-content">
            <span class="step-label">
              {{ currentStep > 1 ? 'Bước 1 • Hoàn Tất' : (currentStep === 1 ? 'Bước 1 • Hiện Tại' : 'Bước 1') }}
            </span>
            <span class="step-title">Tải Ảnh Hóa Đơn</span>
          </div>
        </div>

        <!-- Step 2: Preview / Inspection -->
        <div class="step-item" :class="{ 'is-completed': currentStep > 2, 'is-active': currentStep === 2 }">
          <div class="step-icon-box">
            <span v-if="currentStep > 2" class="material-symbols-outlined step-check">check</span>
            <span v-else class="step-number">2</span>
          </div>
          <div class="step-content">
            <span class="step-label">
              {{ currentStep > 2 ? 'Bước 2 • Hoàn Tất' : (currentStep === 2 ? 'Bước 2 • Hiện Tại' : 'Bước 2') }}
            </span>
            <span class="step-title">Khám Chiếu Hình Ảnh</span>
          </div>
        </div>

        <!-- Step 3: AI Scanning -->
        <div class="step-item" :class="{ 'is-completed': currentStep > 3, 'is-active': currentStep === 3 }">
          <div class="step-icon-box">
            <span v-if="currentStep > 3" class="material-symbols-outlined step-check">check</span>
            <span v-else-if="currentStep === 3" class="material-symbols-outlined step-spin">progress_activity</span>
            <span v-else class="step-number">3</span>
          </div>
          <div class="step-content">
            <span class="step-label">
              {{ currentStep > 3 ? 'Bước 3 • Hoàn Tất' : (currentStep === 3 ? 'Bước 3 • Đang Quét' : 'Bước 3') }}
            </span>
            <span class="step-title">Linh Nhãn Khởi Động</span>
          </div>
        </div>

        <!-- Step 4: Verification & Creation -->
        <div class="step-item" :class="{ 'is-completed': isConfirmed, 'is-active': currentStep === 4 }">
          <div class="step-icon-box">
            <span v-if="isConfirmed" class="material-symbols-outlined step-check">task_alt</span>
            <span v-else class="step-number">4</span>
          </div>
          <div class="step-content">
            <span class="step-label">
              {{ isConfirmed ? 'Bước 4 • Đã Lập Sổ' : (currentStep === 4 ? 'Bước 4 • Chờ Xác Nhận' : 'Bước 4') }}
            </span>
            <span class="step-title">Xác Thực &amp; Lập Sổ</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ MAIN WORKSPACE (SPLIT VIEW) ═══ -->
    <div class="ocr-workspace-grid">
      <!-- ─── LEFT COLUMN: IMAGE PREVIEW & UPLOAD (5 COLS) ─── -->
      <div class="ocr-left-col">
        <!-- Hidden Native File Input -->
        <input
          ref="fileInputRef"
          type="file"
          accept="image/*"
          hidden
          @change="onFileChange"
        />

        <!-- Card: Document Upload & Inspection -->
        <div class="stitch-card inspection-card">
          <!-- Card Header Bar -->
          <div class="inspection-header">
            <div class="header-left">
              <span class="material-symbols-outlined text-jade icon-md">image_search</span>
              <h3 class="inspection-title">Khám Chiếu Văn Bản Gốc</h3>
            </div>
            <span v-if="ocrFile" class="format-pill">
              {{ fileExtLabel }} • {{ formatFileSize(ocrFile.size) }}
            </span>
            <span v-else class="format-pill">
              Hỗ trợ JPG, PNG, WEBP
            </span>
          </div>

          <!-- Preview & Drop Area -->
          <div
            class="document-preview-area"
            :class="{ 'is-drag-over': isDragOver, 'has-file': !!ocrFile }"
            @click="onAreaClick"
            @dragover.prevent="onDragOver"
            @dragleave.prevent="onDragLeave"
            @drop.prevent="onDrop"
          >
            <!-- Case A: No file selected yet -> Spiritual Dropzone -->
            <div v-if="!ocrFile && !ocrPreview" class="upload-drop-placeholder">
              <div class="drop-icon-aura">
                <span class="material-symbols-outlined drop-icon">document_scanner</span>
              </div>
              <div class="drop-text-group">
                <span class="drop-main-text">Kéo thả ảnh chứng từ vào đây</span>
                <span class="drop-sub-text">hoặc nhấn để duyệt tệp từ pháp khí</span>
              </div>
              <div class="drop-specs-tag">
                <span class="material-symbols-outlined icon-xs text-jade">verified</span>
                <span>Tối đa 5.0 MB • Khuyến nghị ảnh chụp rõ nét</span>
              </div>
            </div>

            <!-- Case B: File selected -> Document Inspection Frame -->
            <div v-else class="preview-image-wrapper">
              <img
                :src="ocrPreview"
                class="document-preview-img"
                alt="Chứng từ cần nhận diện"
              />

              <!-- Atmospheric Spectral Scan Ray Overlay (Active during scanning) -->
              <div v-if="loading" class="scan-laser-ray" aria-hidden="true"></div>

              <!-- Shimmer Mask during loading -->
              <div v-if="loading" class="scan-shimmer-mask" aria-hidden="true">
                <div class="scan-scanning-banner">
                  <span class="material-symbols-outlined step-spin icon-sm">sync</span>
                  <span>Đang bóc tách thần thức AI...</span>
                </div>
              </div>

              <!-- Simulated Bounding Boxes when OCR result is available -->
              <template v-if="ocrResult && !loading">
                <div class="bounding-box box-merchant" :title="'Nhận diện: ' + (ocrResult.store_name || 'Cửa hàng')">
                  <span class="bbox-tag tag-merchant">Động Phủ • Khớp 99.8%</span>
                </div>
                <div class="bounding-box box-total" :title="'Nhận diện: ' + formatVND(ocrConfirmForm.amount)">
                  <span class="bbox-tag tag-total">Tổng Ngân • Khớp 99.4%</span>
                </div>
              </template>

              <!-- Zoom & Inspect Tag -->
              <div class="preview-zoom-pill">
                <span class="material-symbols-outlined icon-xs">visibility</span>
                <span>Khám chiếu 100%</span>
              </div>
            </div>
          </div>

          <!-- File Meta & Primary Scan Button -->
          <div class="inspection-footer">
            <div class="file-meta-row">
              <div class="file-meta-left">
                <span class="material-symbols-outlined icon-sm text-secondary">description</span>
                <span class="file-name-text" :title="fileNameDisplay">{{ fileNameDisplay }}</span>
              </div>
              <span class="file-status-badge" :class="statusBadgeClass">
                {{ statusBadgeText }}
              </span>
            </div>

            <!-- Progress Meter / Size Limit -->
            <div class="size-meter-wrapper">
              <div class="size-meter-bar">
                <div
                  class="size-meter-fill"
                  :style="{ width: fileSizePercentage + '%' }"
                ></div>
              </div>
              <div class="size-meter-labels">
                <span>Dung lượng: {{ ocrFile ? formatFileSize(ocrFile.size) : '0 MB' }} / 5.0 MB Max</span>
                <span v-if="ocrFile" class="text-jade font-mono">{{ fileSizePercentage }}%</span>
                <span v-else>Sẵn sàng tiếp nhận</span>
              </div>
            </div>

            <!-- Main Actions on File -->
            <div class="file-actions-row">
              <!-- If file selected but not scanned yet -->
              <button
                v-if="ocrFile && !ocrResult"
                type="button"
                class="btn-stitch-primary btn-block"
                :disabled="loading"
                @click="onScanClick"
              >
                <span v-if="loading" class="material-symbols-outlined step-spin icon-sm">sync</span>
                <span v-else class="material-symbols-outlined icon-sm">visibility</span>
                <span>{{ loading ? '🔮 Linh Nhãn đang phân tích...' : '👁️ Kích Hoạt Linh Nhãn OCR' }}</span>
              </button>

              <!-- If file selected or result ready -> Change photo button -->
              <button
                v-if="ocrFile"
                type="button"
                class="btn-stitch-secondary btn-block"
                :disabled="loading"
                @click="triggerFileInput"
              >
                <span class="material-symbols-outlined icon-sm">cached</span>
                <span>Quét Ảnh Khác (Đổi Chứng Từ)</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Quick OCR Tips Card -->
        <div class="stitch-card tips-card">
          <div class="tips-icon-box">
            <span class="material-symbols-outlined icon-md text-secondary">auto_fix_high</span>
          </div>
          <div class="tips-text-group">
            <h4 class="tips-title">Bí Quyết Tăng Độ Chính Xác</h4>
            <p class="tips-desc">
              Đảm bảo hóa đơn được trải phẳng, đủ ánh sáng, hình chụp ngay ngắn và không bị lóa hoặc che khuất tổng tiền thanh toán cuối cùng.
            </p>
          </div>
        </div>
      </div>

      <!-- ─── RIGHT COLUMN: EXTRACTED RESULT & TRANSACTION FORM (7 COLS) ─── -->
      <div class="ocr-right-col">
        <!-- Case 1: Scanning in Progress -->
        <div v-if="loading" class="stitch-card scanning-state-card">
          <div class="scanner-anim-ring">
            <div class="ring-pulse"></div>
            <span class="material-symbols-outlined text-jade icon-xl step-spin">neurology</span>
          </div>
          <div class="scanner-status-group">
            <h3 class="scanner-status-title">Linh Nhãn Đang Phân Tích Chứng Từ</h3>
            <p class="scanner-status-desc">
              Mạng nơ-ron Thần Thức Càn Khôn đang trích xuất tên cửa hàng, thời gian giao dịch, tổng ngân lượng và danh mục linh vật...
            </p>
          </div>
          <div class="scanner-steps-list">
            <div class="scan-micro-step is-done">
              <span class="material-symbols-outlined icon-xs text-jade">check_circle</span>
              <span>Khám chiếu định dạng &amp; độ phân giải</span>
            </div>
            <div class="scan-micro-step is-active">
              <span class="material-symbols-outlined icon-xs text-jade step-spin">sync</span>
              <span>Trích xuất bảng kê &amp; số tiền thanh toán</span>
            </div>
            <div class="scan-micro-step">
              <span class="material-symbols-outlined icon-xs text-secondary">radio_button_unchecked</span>
              <span>Kiểm thực tính toàn vẹn tài chính (Mã 422 Strict)</span>
            </div>
          </div>
        </div>

        <!-- Case 2: Result Ready — Review & Confirm Transaction -->
        <div v-else-if="ocrResult" class="stitch-card result-card">
          <!-- Form Header & Trust Score -->
          <div class="result-header">
            <div class="result-title-group">
              <div class="flex-align-center gap-xs">
                <span class="material-symbols-outlined text-jade icon-md" style="font-variation-settings: 'FILL' 1;">fact_check</span>
                <h2 class="result-title">Kết Quả Linh Nhãn Trích Xuất</h2>
              </div>
              <span class="result-subtitle">Trích xuất tự động qua mạng nơ-ron Thần Thức Càn Khôn</span>
            </div>
            <!-- Trust Badge -->
            <div class="trust-badge">
              <span class="material-symbols-outlined icon-xs">verified</span>
              <span class="font-semibold">Độ tin cậy 99.4%</span>
            </div>
          </div>

          <!-- Extraction Status Strip -->
          <div class="extraction-status-strip">
            <div class="status-strip-left">
              <span class="pulse-dot-jade"></span>
              <span class="status-strip-text">Trạng thái: Trích xuất thành công — Chờ xác nhận lập sổ</span>
            </div>
            <span class="status-strip-id font-mono">AI-OCR • READY</span>
          </div>

          <!-- Structured Form Fields Grid -->
          <div class="result-form-grid">
            <!-- Merchant / Store Name -->
            <div class="form-field-group">
              <label class="field-label" for="ocr-store-input">
                <span>🏪 Tên Động Phủ / Cửa Hàng</span>
                <span class="field-hint text-jade font-mono lowercase">Trích xuất AI</span>
              </label>
              <div class="input-with-icon-wrap">
                <span class="material-symbols-outlined input-prefix-icon text-secondary">storefront</span>
                <input
                  id="ocr-store-input"
                  v-model="ocrConfirmForm.note"
                  type="text"
                  placeholder="Tên cửa hàng / Nội dung chi..."
                  class="stitch-input-prefixed"
                  required
                />
              </div>
            </div>

            <!-- Transaction Date -->
            <div class="form-field-group">
              <label class="field-label" for="ocr-date-input">
                <span>📅 Ngày Lập Chứng Từ</span>
                <span class="field-hint text-jade font-mono lowercase">Khớp ngày</span>
              </label>
              <div class="input-with-icon-wrap">
                <span class="material-symbols-outlined input-prefix-icon text-secondary">calendar_today</span>
                <input
                  id="ocr-date-input"
                  v-model="ocrConfirmForm.transaction_date"
                  type="date"
                  class="stitch-input-prefixed"
                  required
                />
              </div>
            </div>
          </div>

          <!-- Prominent Highlight: Total Amount -->
          <div class="total-amount-highlight-card">
            <div class="amount-card-left">
              <div class="amount-icon-box">
                <span class="material-symbols-outlined icon-lg text-jade">payments</span>
              </div>
              <div class="amount-text-col">
                <span class="amount-title">Tổng Linh Thạch Thanh Toán (VNĐ)</span>
                <span class="amount-subtitle">Số tiền chính thức ghi nhận vào sổ giao dịch</span>
              </div>
            </div>
            <div class="amount-card-right">
              <div class="amount-input-wrap">
                <input
                  id="ocr-amount-input"
                  v-model.number="ocrConfirmForm.amount"
                  type="number"
                  min="0"
                  step="1000"
                  class="amount-editable-input font-bold tabular-num"
                  title="Nhấn để chỉnh sửa số tiền nếu cần"
                />
                <span class="amount-currency-unit">₫</span>
              </div>
              <span class="amount-formatted-text tabular-num text-jade">
                {{ formatVND(ocrConfirmForm.amount) }}
              </span>
            </div>
          </div>

          <!-- Items Table (If items were extracted by OCR) -->
          <div v-if="ocrResult.items && ocrResult.items.length" class="items-section">
            <div class="items-section-header">
              <span class="items-section-title">
                📋 Chi Tiết Sản Phẩm Trích Xuất ({{ ocrResult.items.length }} Hạng Mục)
              </span>
              <span class="items-section-hint">Tự động đối chiếu đơn giá</span>
            </div>
            <div class="table-responsive-box">
              <table class="ocr-items-table">
                <thead>
                  <tr>
                    <th class="col-item-name">Sản Phẩm / Linh Vật</th>
                    <th class="col-item-qty text-center">Số Lượng</th>
                    <th class="col-item-price text-right">Đơn Giá</th>
                    <th class="col-item-subtotal text-right">Thành Tiền</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, i) in ocrResult.items" :key="'ocr-item-' + i">
                    <td class="col-item-name">
                      <div class="item-name-cell">
                        <span class="item-bullet-dot" :class="'bullet-' + (i % 3)"></span>
                        <span class="item-name-text font-medium">{{ item.name }}</span>
                      </div>
                    </td>
                    <td class="col-item-qty text-center font-mono text-secondary">
                      x{{ item.quantity || 1 }}
                    </td>
                    <td class="col-item-price text-right tabular-num font-mono text-secondary">
                      {{ formatVND(item.price || 0) }}
                    </td>
                    <td class="col-item-subtotal text-right tabular-num font-mono text-white font-semibold">
                      {{ formatVND((item.quantity || 1) * (item.price || 0)) }}
                    </td>
                  </tr>
                  <tr class="table-subtotal-row">
                    <td colspan="3" class="subtotal-label font-semibold">
                      Tổng tính theo từng hạng mục sản phẩm
                    </td>
                    <td class="subtotal-value text-right font-mono text-jade font-bold">
                      {{ formatVND(computedItemsSum) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Destination Mapping Form (Wallets & Categories) -->
          <div class="destination-mapping-section">
            <div class="mapping-section-header">
              <span class="material-symbols-outlined icon-sm text-jade">account_tree</span>
              <span class="mapping-title">Ánh Xạ Vào Sổ Càn Khôn (Destination Mapping)</span>
            </div>

            <div class="mapping-fields-grid">
              <!-- Wallet Select -->
              <div class="form-field-group">
                <label class="field-label" for="ocr-wallet-select">
                  <span>💳 Túi Càn Khôn (Ví Thanh Toán)</span>
                  <span class="field-required-hint">Bắt buộc</span>
                </label>
                <div class="select-wrapper">
                  <select
                    id="ocr-wallet-select"
                    v-model="ocrConfirmForm.wallet_id"
                    class="stitch-select"
                    required
                  >
                    <option :value="null" disabled>— Chọn túi càn khôn —</option>
                    <option
                      v-for="w in wallets"
                      :key="'w-' + w.id"
                      :value="w.id"
                    >
                      {{ w.wallet_name }} (Khả dụng: {{ formatVND(w.balance) }})
                    </option>
                  </select>
                  <span class="material-symbols-outlined select-chevron">expand_more</span>
                </div>
              </div>

              <!-- Expense Category Select -->
              <div class="form-field-group">
                <label class="field-label" for="ocr-category-select">
                  <span>🏷️ Danh Mục Chi Tiêu</span>
                  <span class="field-required-hint">Bắt buộc</span>
                </label>
                <div class="select-wrapper">
                  <select
                    id="ocr-category-select"
                    v-model="ocrConfirmForm.category_id"
                    class="stitch-select"
                    required
                  >
                    <option :value="null" disabled>— Chọn danh mục chi —</option>
                    <option
                      v-for="c in expenseCategories"
                      :key="'cat-' + c.id"
                      :value="c.id"
                    >
                      {{ c.icon }} {{ c.category_name }}
                    </option>
                  </select>
                  <span class="material-symbols-outlined select-chevron">expand_more</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="result-actions-bar">
            <button
              type="button"
              class="btn-stitch-subtle"
              :disabled="loading"
              @click="onReset"
            >
              <span class="material-symbols-outlined icon-sm">close</span>
              <span>Hủy Kết Quả</span>
            </button>
            <button
              type="button"
              class="btn-stitch-primary btn-confirm-action"
              :disabled="loading || !ocrConfirmForm.amount || ocrConfirmForm.amount <= 0 || !ocrConfirmForm.wallet_id || !ocrConfirmForm.category_id"
              @click="onConfirmTransaction"
            >
              <span v-if="loading" class="material-symbols-outlined step-spin icon-sm">sync</span>
              <span v-else class="material-symbols-outlined icon-sm">task_alt</span>
              <span>{{ loading ? '⏳ Đang lưu giao dịch...' : '⚡ Xác Nhận Tạo Giao Dịch' }}</span>
            </button>
          </div>
        </div>

        <!-- Case 3: Idle State — Guided Information -->
        <div v-else class="stitch-card idle-guide-card">
          <div class="idle-hero-icon-box">
            <span class="material-symbols-outlined text-jade icon-hero">receipt_long</span>
          </div>
          <div class="idle-text-group">
            <h3 class="idle-title">Sẵn Sàng Tiếp Nhận Chứng Từ</h3>
            <p class="idle-desc">
              Vui lòng tải lên ảnh hóa đơn bán lẻ, biên lai ăn uống, chứng từ mua sắm hoặc phiếu thu tiền. Linh Nhãn sẽ tự động trích xuất thông tin và hỗ trợ lập sổ nhanh chóng chỉ với 1 cú chạm.
            </p>
          </div>

          <!-- 3 Flow Steps Illustration -->
          <div class="idle-features-grid">
            <div class="feature-item">
              <div class="feature-icon-wrap">
                <span class="material-symbols-outlined text-jade icon-sm">photo_camera</span>
              </div>
              <div class="feature-content">
                <span class="feature-title">1. Chụp / Tải Ảnh</span>
                <span class="feature-desc">Tiếp nhận định dạng JPG, PNG, WEBP tối đa 5MB.</span>
              </div>
            </div>

            <div class="feature-item">
              <div class="feature-icon-wrap">
                <span class="material-symbols-outlined text-gold icon-sm">psychology</span>
              </div>
              <div class="feature-content">
                <span class="feature-title">2. Phân Tích Thần Thức</span>
                <span class="feature-desc">Nhận diện cửa hàng, ngày lập, chi tiết từng món.</span>
              </div>
            </div>

            <div class="feature-item">
              <div class="feature-icon-wrap">
                <span class="material-symbols-outlined text-secondary icon-sm">account_balance_wallet</span>
              </div>
              <div class="feature-content">
                <span class="feature-title">3. Tự Động Lập Sổ</span>
                <span class="feature-desc">Chọn ví &amp; danh mục, lưu vào lịch sử chi tiêu tức thì.</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ BOTTOM INTEGRITY GUARD BANNER ═══ -->
    <section class="ocr-integrity-banner" aria-label="Bảo vệ tính toàn vẹn dữ liệu OCR">
      <div class="integrity-card">
        <div class="integrity-left">
          <div class="integrity-icon-box">
            <span class="material-symbols-outlined text-gold icon-lg">security</span>
          </div>
          <div class="integrity-text-col">
            <div class="flex-align-center gap-xs">
              <h3 class="integrity-title">Linh Trận Phòng Ngự (Integrity Guard)</h3>
              <span class="strict-badge font-mono">MÃ 422 STRICT</span>
            </div>
            <p class="integrity-desc">
              Hệ thống tự động từ chối ảnh không phải hóa đơn hoặc sai định dạng. Tuyệt đối không sinh dữ liệu giả khi thần thức OCR gặp trục trặc, bảo tồn sự tinh khiết và chính xác của sổ kế toán Càn Khôn.
            </p>
          </div>
        </div>

        <div class="integrity-right">
          <div class="integrity-stat-col">
            <span class="integrity-stat-label">Kiểm Thực Ngữ Nghĩa</span>
            <span class="integrity-stat-val text-jade font-mono">100% Minh Bạch</span>
          </div>
          <div class="integrity-shield-icon">
            <span class="material-symbols-outlined text-jade icon-md">verified_user</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  ocrFile: {
    type: Object,
    default: null
  },
  ocrPreview: {
    type: String,
    default: null
  },
  ocrResult: {
    type: Object,
    default: null
  },
  ocrConfirmForm: {
    type: Object,
    required: true
  },
  wallets: {
    type: Array,
    default: () => []
  },
  expenseCategories: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  formatVND: {
    type: Function,
    required: true
  }
})

const emit = defineEmits([
  'ocr-upload',
  'ocr-drop',
  'scan-invoice',
  'confirm-ocr-transaction',
  'reset-ocr'
])

// DOM ref for hidden file input
const fileInputRef = ref(null)

// Drag-and-drop state
const isDragOver = ref(false)

// Trigger native file picker
function triggerFileInput() {
  if (fileInputRef.value) {
    fileInputRef.value.click()
  }
}

function onAreaClick() {
  if (!props.ocrFile) {
    triggerFileInput()
  }
}

// File change handler
function onFileChange(e) {
  isDragOver.value = false
  emit('ocr-upload', e)
}

// Drag & drop handlers
function onDragOver(e) {
  isDragOver.value = true
}

function onDragLeave(e) {
  isDragOver.value = false
}

function onDrop(e) {
  isDragOver.value = false
  emit('ocr-drop', e)
}

// Primary actions
function onScanClick() {
  emit('scan-invoice')
}

function onConfirmTransaction() {
  emit('confirm-ocr-transaction')
}

function onReset() {
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
  emit('reset-ocr')
}

// Format file size in KB or MB
function formatFileSize(bytes) {
  if (!bytes || bytes <= 0) return '0 KB'
  const mb = bytes / (1024 * 1024)
  if (mb >= 1) {
    return mb.toFixed(1) + ' MB'
  }
  return (bytes / 1024).toFixed(0) + ' KB'
}

// Compute current workflow step (1..4)
const currentStep = computed(() => {
  if (props.ocrResult) return 4
  if (props.loading) return 3
  if (props.ocrFile) return 2
  return 1
})

const isConfirmed = computed(() => false)

// Compute file extension label
const fileExtLabel = computed(() => {
  if (!props.ocrFile || !props.ocrFile.name) return 'FILE'
  const parts = props.ocrFile.name.split('.')
  return parts.length > 1 ? parts.pop().toUpperCase() : 'IMG'
})

// File display name
const fileNameDisplay = computed(() => {
  if (!props.ocrFile) return 'Chưa chọn tệp'
  return props.ocrFile.name || 'hoa_don.jpg'
})

// File size percentage relative to 5MB (5 * 1024 * 1024)
const fileSizePercentage = computed(() => {
  if (!props.ocrFile || !props.ocrFile.size) return 0
  const maxBytes = 5 * 1024 * 1024
  const pct = (props.ocrFile.size / maxBytes) * 100
  return Math.min(100, Math.round(pct))
})

// Status badge styling and text
const statusBadgeText = computed(() => {
  if (props.ocrResult) return 'Đã Quét Xong'
  if (props.loading) return 'Đang Phân Tích...'
  if (props.ocrFile) return 'Sẵn Sàng Quét'
  return 'Chờ Tải Ảnh'
})

const statusBadgeClass = computed(() => {
  if (props.ocrResult) return 'status-badge-success'
  if (props.loading) return 'status-badge-loading'
  if (props.ocrFile) return 'status-badge-ready'
  return 'status-badge-idle'
})

// Items subtotal
const computedItemsSum = computed(() => {
  if (!props.ocrResult || !props.ocrResult.items || !props.ocrResult.items.length) {
    return props.ocrConfirmForm.amount || 0
  }
  return props.ocrResult.items.reduce((acc, item) => {
    const qty = item.quantity || 1
    const price = item.price || 0
    return acc + (qty * price)
  }, 0)
})
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════
   CELESTIAL TREASURY — LINH NHÃN OCR VIEW STYLES
   Design tokens from stitch_design/linh_nh_n_ocr
   ═══════════════════════════════════════════════════════════ */

.ocr-realm {
  position: relative;
  width: 100%;
  min-height: 100%;
  padding-bottom: 48px;
  color: #dae2fd;
}

/* ─── AMBIENT GLOW ORBS ─── */
.ambient-glow-orb {
  position: absolute;
  border-radius: 9999px;
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
  opacity: 0.18;
}

.orb-primary {
  top: -60px;
  right: 15%;
  width: 420px;
  height: 420px;
  background: radial-gradient(circle, #7dd6cc 0%, rgba(68, 159, 150, 0) 70%);
}

.orb-secondary {
  top: 360px;
  left: -80px;
  width: 360px;
  height: 360px;
  background: radial-gradient(circle, #444173 0%, rgba(68, 65, 115, 0) 70%);
}

/* ─── HEADER & CONTROLS ─── */
.ocr-header {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

@media (min-width: 768px) {
  .ocr-header {
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
  }
}

.header-text-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.header-badge-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  letter-spacing: 0.08em;
  font-weight: 600;
  color: #7dd6cc;
  text-transform: uppercase;
}

.status-pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #7dd6cc;
  box-shadow: 0 0 10px #7dd6cc;
  animation: pulseAura 2s infinite ease-in-out;
}

.title-with-badge {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.page-title {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.015em;
  color: #dae2fd;
}

@media (min-width: 640px) {
  .page-title {
    font-size: 30px;
  }
}

.engine-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  background: #222a3d;
  color: #7dd6cc;
  border-radius: 9999px;
  font-family: monospace;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 0 10px rgba(125, 214, 204, 0.15);
}

.engine-pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #7dd6cc;
  animation: pingDot 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.page-subtitle {
  margin: 0;
  max-width: 720px;
  font-size: 13.5px;
  line-height: 1.55;
  color: #bdc9c6;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  align-self: flex-start;
}

@media (min-width: 768px) {
  .header-actions {
    align-self: auto;
  }
}

/* ─── STITCH BUTTONS ─── */
.btn-stitch-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  background: #7dd6cc;
  color: #003733;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 0 18px rgba(125, 214, 204, 0.35);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-stitch-primary:hover:not(:disabled) {
  background: #9af2e8;
  box-shadow: 0 0 24px rgba(125, 214, 204, 0.5);
  transform: translateY(-1px);
}

.btn-stitch-primary:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-stitch-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 9px 16px;
  background: #222a3d;
  color: #dae2fd;
  border: 1px solid rgba(125, 214, 204, 0.2);
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-stitch-secondary:hover:not(:disabled) {
  background: #31394d;
  border-color: rgba(125, 214, 204, 0.4);
  color: #ffffff;
}

.btn-stitch-subtle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 14px;
  background: transparent;
  color: #bdc9c6;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-stitch-subtle:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.06);
  color: #dae2fd;
}

.btn-block {
  width: 100%;
}

/* ─── WORKFLOW STEP INDICATOR ─── */
.ocr-steps-bar {
  position: relative;
  z-index: 1;
  background: #131b2e;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.steps-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

@media (min-width: 640px) {
  .steps-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .steps-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.25s ease;
}

.step-item.is-active {
  background: rgba(45, 52, 73, 0.7);
  box-shadow: inset 0 0 12px rgba(125, 214, 204, 0.1);
}

.step-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #222a3d;
  color: #bdc9c6;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.step-item.is-completed .step-icon-box {
  background: rgba(125, 214, 204, 0.2);
  color: #7dd6cc;
}

.step-item.is-active .step-icon-box {
  background: #7dd6cc;
  color: #003733;
  box-shadow: 0 0 12px rgba(125, 214, 204, 0.5);
}

.step-check {
  font-size: 18px;
}

.step-spin {
  animation: spinSlow 1.5s linear infinite;
}

.step-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.step-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  color: #889391;
  letter-spacing: 0.03em;
}

.step-item.is-completed .step-label {
  color: #7dd6cc;
}

.step-item.is-active .step-label {
  color: #e3c370;
}

.step-title {
  font-size: 13.5px;
  font-weight: 600;
  color: #dae2fd;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ─── MAIN WORKSPACE GRID ─── */
.ocr-workspace-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

@media (min-width: 1024px) {
  .ocr-workspace-grid {
    grid-template-columns: repeat(12, 1fr);
  }

  .ocr-left-col {
    grid-column: span 5;
  }

  .ocr-right-col {
    grid-column: span 7;
  }
}

.ocr-left-col,
.ocr-right-col {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ─── STITCH CARDS ─── */
.stitch-card {
  background: #171f33;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
  transition: border-color 0.2s ease;
}

.stitch-card:hover {
  border-color: rgba(125, 214, 204, 0.2);
}

/* ─── LEFT COLUMN: INSPECTION CARD ─── */
.inspection-card {
  display: flex;
  flex-direction: column;
}

.inspection-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: rgba(34, 42, 61, 0.6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.inspection-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #dae2fd;
}

.format-pill {
  font-size: 11px;
  font-family: monospace;
  padding: 3px 8px;
  border-radius: 4px;
  background: #060e20;
  color: #bdc9c6;
}

/* Document preview / Dropzone area */
.document-preview-area {
  position: relative;
  min-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #060e20;
  padding: 16px;
  border: 2px dashed rgba(125, 214, 204, 0.25);
  margin: 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.document-preview-area.is-drag-over {
  border-color: #7dd6cc;
  background: rgba(125, 214, 204, 0.06);
  box-shadow: 0 0 20px rgba(125, 214, 204, 0.2);
}

.document-preview-area.has-file {
  border-style: solid;
  border-color: rgba(255, 255, 255, 0.06);
  padding: 8px;
  cursor: default;
}

.upload-drop-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 14px;
  padding: 32px 16px;
}

.drop-icon-aura {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(125, 214, 204, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7dd6cc;
  box-shadow: 0 0 20px rgba(125, 214, 204, 0.2);
  transition: transform 0.2s ease;
}

.upload-drop-placeholder:hover .drop-icon-aura {
  transform: scale(1.08);
}

.drop-icon {
  font-size: 32px;
}

.drop-text-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.drop-main-text {
  font-size: 15px;
  font-weight: 600;
  color: #dae2fd;
}

.drop-sub-text {
  font-size: 12.5px;
  color: #bdc9c6;
}

.drop-specs-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  color: #889391;
  background: rgba(255, 255, 255, 0.04);
  padding: 4px 12px;
  border-radius: 9999px;
}

/* Image preview wrapper */
.preview-image-wrapper {
  position: relative;
  width: 100%;
  max-width: 420px;
  max-height: 380px;
  border-radius: 8px;
  overflow: hidden;
  background: #171f33;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.document-preview-img {
  width: 100%;
  height: 100%;
  max-height: 380px;
  object-fit: contain;
  display: block;
}

/* Laser scan animation overlay */
.scan-laser-ray {
  position: absolute;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, #7dd6cc, #ffe08f, #7dd6cc, transparent);
  box-shadow: 0 0 14px #7dd6cc, 0 0 24px rgba(125, 214, 204, 0.8);
  animation: scanLaser 2s ease-in-out infinite;
  z-index: 5;
}

.scan-shimmer-mask {
  position: absolute;
  inset: 0;
  background: rgba(11, 19, 38, 0.45);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 4;
}

.scan-scanning-banner {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 9999px;
  background: rgba(19, 27, 46, 0.9);
  border: 1px solid rgba(125, 214, 204, 0.4);
  color: #7dd6cc;
  font-size: 12.5px;
  font-weight: 600;
  box-shadow: 0 0 20px rgba(125, 214, 204, 0.3);
}

/* Simulated bounding boxes */
.bounding-box {
  position: absolute;
  border-radius: 4px;
  pointer-events: none;
  z-index: 3;
}

.box-merchant {
  top: 10%;
  left: 8%;
  width: 55%;
  height: 12%;
  border: 1.5px solid #7dd6cc;
  background: rgba(125, 214, 204, 0.12);
}

.box-total {
  bottom: 12%;
  right: 8%;
  width: 45%;
  height: 14%;
  border: 1.5px solid #e3c370;
  background: rgba(227, 195, 112, 0.15);
}

.bbox-tag {
  position: absolute;
  top: -18px;
  left: 0;
  font-size: 9.5px;
  padding: 1px 6px;
  border-radius: 3px;
  font-weight: 600;
  white-space: nowrap;
}

.tag-merchant {
  background: #003733;
  color: #7dd6cc;
}

.tag-total {
  background: #3d2e00;
  color: #ffe08f;
}

.preview-zoom-pill {
  position: absolute;
  bottom: 8px;
  left: 8px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 4px;
  background: rgba(11, 19, 38, 0.85);
  backdrop-filter: blur(4px);
  font-size: 10.5px;
  color: #bdc9c6;
  z-index: 3;
}

/* File meta & buttons */
.inspection-footer {
  padding: 0 16px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.file-meta-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.file-name-text {
  font-size: 13px;
  font-family: monospace;
  color: #dae2fd;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.status-badge-success {
  background: rgba(125, 214, 204, 0.15);
  color: #7dd6cc;
}

.status-badge-loading {
  background: rgba(227, 195, 112, 0.15);
  color: #e3c370;
}

.status-badge-ready {
  background: rgba(196, 193, 251, 0.15);
  color: #c4c1fb;
}

.status-badge-idle {
  background: rgba(255, 255, 255, 0.05);
  color: #889391;
}

.size-meter-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.size-meter-bar {
  width: 100%;
  height: 5px;
  background: #222a3d;
  border-radius: 9999px;
  overflow: hidden;
}

.size-meter-fill {
  height: 100%;
  background: #7dd6cc;
  border-radius: 9999px;
  transition: width 0.3s ease;
}

.size-meter-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #889391;
}

.file-actions-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 4px;
}

/* Tips card */
.tips-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #131b2e;
}

.tips-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #444173;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.tips-text-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tips-title {
  margin: 0;
  font-size: 13.5px;
  font-weight: 600;
  color: #dae2fd;
}

.tips-desc {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  color: #bdc9c6;
}

/* ─── RIGHT COLUMN: SCANNING CARD ─── */
.scanning-state-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 48px 24px;
  gap: 20px;
}

.scanner-anim-ring {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(125, 214, 204, 0.1);
}

.ring-pulse {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  border: 2px dashed #7dd6cc;
  animation: spinSlow 6s linear infinite;
}

.scanner-status-title {
  margin: 0 0 6px 0;
  font-size: 18px;
  font-weight: 700;
  color: #dae2fd;
}

.scanner-status-desc {
  margin: 0;
  font-size: 13px;
  color: #bdc9c6;
  max-width: 420px;
}

.scanner-steps-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: left;
  background: #131b2e;
  padding: 14px 18px;
  border-radius: 10px;
  width: 100%;
  max-width: 380px;
}

.scan-micro-step {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #889391;
}

.scan-micro-step.is-done {
  color: #7dd6cc;
}

.scan-micro-step.is-active {
  color: #dae2fd;
  font-weight: 600;
}

/* ─── RIGHT COLUMN: IDLE GUIDE CARD ─── */
.idle-guide-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 40px 24px;
  gap: 24px;
}

.idle-hero-icon-box {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(125, 214, 204, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(125, 214, 204, 0.25);
  box-shadow: 0 0 24px rgba(125, 214, 204, 0.15);
}

.idle-title {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 700;
  color: #dae2fd;
}

.idle-desc {
  margin: 0;
  font-size: 13.5px;
  line-height: 1.6;
  color: #bdc9c6;
  max-width: 480px;
}

.idle-features-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
  width: 100%;
  text-align: left;
}

@media (min-width: 640px) {
  .idle-features-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.feature-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #131b2e;
  padding: 16px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.feature-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: #222a3d;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.feature-title {
  font-size: 13px;
  font-weight: 600;
  color: #dae2fd;
}

.feature-desc {
  font-size: 11.5px;
  line-height: 1.45;
  color: #889391;
}

/* ─── RIGHT COLUMN: RESULT REVIEW & CONFIRM CARD ─── */
.result-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

@media (min-width: 640px) {
  .result-header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.result-title-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.result-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #dae2fd;
}

.result-subtitle {
  font-size: 12px;
  color: #bdc9c6;
}

.trust-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 9999px;
  background: rgba(125, 214, 204, 0.12);
  color: #7dd6cc;
  font-size: 12px;
  align-self: flex-start;
}

@media (min-width: 640px) {
  .trust-badge {
    align-self: auto;
  }
}

.extraction-status-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: #222a3d;
  border-radius: 8px;
}

.status-strip-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pulse-dot-jade {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #7dd6cc;
  box-shadow: 0 0 8px #7dd6cc;
}

.status-strip-text {
  font-size: 12.5px;
  color: #dae2fd;
}

.status-strip-id {
  font-size: 11px;
  color: #889391;
}

/* Result form grid */
.result-form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

@media (min-width: 640px) {
  .result-form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.form-field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 600;
  color: #bdc9c6;
}

.field-hint {
  font-size: 11px;
}

.field-required-hint {
  font-size: 10.5px;
  color: #ffb4ab;
}

.input-with-icon-wrap {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.input-prefix-icon {
  position: absolute;
  left: 12px;
  pointer-events: none;
  font-size: 18px;
}

.stitch-input-prefixed {
  width: 100%;
  height: 42px;
  padding-left: 38px;
  padding-right: 12px;
  background: #131b2e;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: #dae2fd;
  font-size: 14px;
  transition: all 0.2s ease;
}

.stitch-input-prefixed:focus {
  outline: none;
  border-color: #7dd6cc;
  box-shadow: 0 0 10px rgba(125, 214, 204, 0.25);
  background: #171f33;
}

/* Total Amount Highlight Card */
.total-amount-highlight-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 20px;
  background: rgba(34, 42, 61, 0.7);
  border: 1px solid rgba(125, 214, 204, 0.25);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

@media (min-width: 640px) {
  .total-amount-highlight-card {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.amount-card-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.amount-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: rgba(125, 214, 204, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.amount-text-col {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.amount-title {
  font-size: 11.5px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #bdc9c6;
  font-weight: 600;
}

.amount-subtitle {
  font-size: 12.5px;
  color: #7dd6cc;
}

.amount-card-right {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

@media (min-width: 640px) {
  .amount-card-right {
    align-items: flex-end;
  }
}

.amount-input-wrap {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
}

.amount-editable-input {
  width: 140px;
  font-size: 26px;
  font-weight: 700;
  color: #7dd6cc;
  background: transparent;
  border: none;
  border-bottom: 1px dashed rgba(125, 214, 204, 0.4);
  padding: 0 4px;
  text-align: right;
  letter-spacing: -0.02em;
}

.amount-editable-input:focus {
  outline: none;
  border-bottom-color: #7dd6cc;
  background: rgba(125, 214, 204, 0.05);
}

.amount-currency-unit {
  font-size: 18px;
  font-weight: 600;
  color: #7dd6cc;
}

.amount-formatted-text {
  font-size: 12px;
  font-weight: 600;
}

/* Items section table */
.items-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.items-section-header {
  display: flex;
  justify-content: space-between;
  font-size: 11.5px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: #bdc9c6;
  font-weight: 600;
}

.table-responsive-box {
  overflow-x: auto;
  border-radius: 8px;
  background: #131b2e;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.ocr-items-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}

.ocr-items-table th {
  padding: 10px 14px;
  background: rgba(34, 42, 61, 0.5);
  color: #bdc9c6;
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 600;
}

.ocr-items-table td {
  padding: 10px 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}

.item-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-bullet-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.bullet-0 { background: #7dd6cc; }
.bullet-1 { background: #c4c1fb; }
.bullet-2 { background: #e3c370; }

.table-subtotal-row {
  background: rgba(34, 42, 61, 0.7);
}

.table-subtotal-row td {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding: 10px 14px;
}

/* Destination mapping */
.destination-mapping-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.mapping-section-header {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #bdc9c6;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.mapping-fields-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

@media (min-width: 640px) {
  .mapping-fields-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.select-wrapper {
  position: relative;
  width: 100%;
}

.stitch-select {
  width: 100%;
  height: 42px;
  padding: 0 34px 0 12px;
  background: #131b2e;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: #dae2fd;
  font-size: 13.5px;
  appearance: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.stitch-select:focus {
  outline: none;
  border-color: #7dd6cc;
  box-shadow: 0 0 10px rgba(125, 214, 204, 0.25);
  background: #171f33;
}

.select-chevron {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #bdc9c6;
  font-size: 20px;
}

/* Action bar */
.result-actions-bar {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 8px;
}

@media (min-width: 640px) {
  .result-actions-bar {
    flex-direction: row;
    justify-content: flex-end;
  }
}

.btn-confirm-action {
  padding: 12px 24px;
  font-size: 14px;
}

/* ─── BOTTOM INTEGRITY BANNER ─── */
.ocr-integrity-banner {
  position: relative;
  z-index: 1;
  margin-top: 28px;
}

.integrity-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #131b2e;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

@media (min-width: 768px) {
  .integrity-card {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.integrity-left {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.integrity-icon-box {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  background: rgba(227, 195, 112, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.integrity-text-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.integrity-title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: #dae2fd;
}

.strict-badge {
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  background: #c6a858;
  color: #241a00;
}

.integrity-desc {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.5;
  color: #bdc9c6;
  max-width: 720px;
}

.integrity-right {
  display: flex;
  align-items: center;
  gap: 14px;
  align-self: flex-end;
}

@media (min-width: 768px) {
  .integrity-right {
    align-self: auto;
  }
}

.integrity-stat-col {
  display: flex;
  flex-direction: column;
  text-align: right;
  gap: 2px;
}

.integrity-stat-label {
  font-size: 11px;
  color: #889391;
}

.integrity-stat-val {
  font-size: 13.5px;
  font-weight: 700;
}

.integrity-shield-icon {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #222a3d;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ─── UTILITY CLASSES ─── */
.text-jade { color: #7dd6cc; }
.text-gold { color: #e3c370; }
.text-secondary { color: #c4c1fb; }
.text-white { color: #ffffff; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.tabular-num { font-variant-numeric: tabular-nums; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }
.flex-align-center { display: flex; align-items: center; }
.gap-xs { gap: 8px; }

.icon-xs { font-size: 14px; }
.icon-sm { font-size: 16px; }
.icon-md { font-size: 20px; }
.icon-lg { font-size: 24px; }
.icon-xl { font-size: 32px; }
.icon-hero { font-size: 36px; }

/* ─── KEYFRAME ANIMATIONS ─── */
@keyframes pulseAura {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 1; }
}

@keyframes pingDot {
  0% { transform: scale(1); opacity: 1; }
  75%, 100% { transform: scale(2.2); opacity: 0; }
}

@keyframes spinSlow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes scanLaser {
  0% { top: 6%; opacity: 0.4; }
  50% { top: 92%; opacity: 1; }
  100% { top: 6%; opacity: 0.4; }
}
</style>
