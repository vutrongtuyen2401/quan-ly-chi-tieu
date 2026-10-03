<template>
  <!-- ═══════ TAB 5: OCR INVOICE ═══════ -->
  <section class="tab-panel">
    <h2 class="section-title">🧾 Linh Nhãn Tầm Bảo — Quét Hóa Đơn AI</h2>

    <div class="form-card">
      <h3 class="sub-title">📸 Tải Lên Hóa Đơn</h3>
      <p class="hint-text">Linh Nhãn AI sẽ tự động trích xuất thông tin từ ảnh hóa đơn / receipt</p>
      <div class="upload-zone" @click="$refs.ocrInput.click()"
           @dragover.prevent @drop.prevent="handleOCRDrop">
        <input ref="ocrInput" type="file" accept="image/*" @change="handleOCRUpload" hidden />
        <div v-if="!ocrPreview" class="upload-placeholder">
          <span class="upload-icon">📷</span>
          <span>Kéo thả hoặc nhấn để chọn ảnh hóa đơn</span>
        </div>
        <img v-else :src="ocrPreview" class="ocr-preview-img" alt="Preview" />
      </div>
      <button class="btn-jade" @click="scanInvoice" :disabled="loading || !ocrFile" style="margin-top: 16px;">
        {{ loading ? '🔮 Linh Nhãn đang phân tích...' : '👁️ Kích Hoạt Linh Nhãn OCR' }}
      </button>
    </div>

    <div v-if="ocrResult" class="ocr-result-card">
      <h3 class="sub-title">✅ Kết Quả Linh Nhãn — Xác Nhận Giao Dịch</h3>
      <p class="hint-text" style="margin-bottom: 16px;">Vui lòng kiểm tra và chỉnh sửa thông tin nếu cần trước khi thêm vào lịch sử thu chi:</p>

      <div class="form-grid">
        <div class="input-group-xianxia">
          <label>🏪 Cửa Hàng / Nội Dung Giao Dịch</label>
          <input v-model="ocrConfirmForm.note" type="text" placeholder="Tên cửa hàng..." />
        </div>
        <div class="input-group-xianxia">
          <label>💰 Số Tiền (VNĐ)</label>
          <input v-model.number="ocrConfirmForm.amount" type="number" placeholder="0" />
        </div>
        <div class="input-group-xianxia">
          <label>📅 Ngày Giao Dịch</label>
          <input v-model="ocrConfirmForm.transaction_date" type="date" />
        </div>
        <div class="input-group-xianxia">
          <label>💳 Túi Càn Khôn (Ví)</label>
          <select v-model="ocrConfirmForm.wallet_id">
            <option v-for="w in wallets" :key="w.id" :value="w.id">{{ w.wallet_name }} ({{ formatVND(w.balance) }})</option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>🏷️ Danh Mục Chi</label>
          <select v-model="ocrConfirmForm.category_id">
            <option v-for="c in expenseCategories" :key="c.id" :value="c.id">{{ c.icon }} {{ c.category_name }}</option>
          </select>
        </div>
      </div>

      <div v-if="ocrResult.items && ocrResult.items.length" class="ocr-items" style="margin-top: 16px;">
        <h4>📋 Chi Tiết Sản Phẩm Trích Xuất</h4>
        <table class="xianxia-table">
          <thead><tr><th>Sản Phẩm</th><th>SL</th><th>Đơn Giá</th></tr></thead>
          <tbody>
            <tr v-for="(item, i) in ocrResult.items" :key="i">
              <td>{{ item.name }}</td>
              <td>{{ item.quantity || 1 }}</td>
              <td>{{ formatVND(item.price || 0) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <button class="btn-jade" @click="confirmOCRTransaction" :disabled="loading" style="margin-top: 20px;">
        {{ loading ? '⏳ Đang lưu giao dịch...' : '⚡ Xác Nhận & Thêm Vào Lịch Sử Giao Dịch' }}
      </button>
    </div>
  </section>
</template>

<script>
import { useAppBindings } from '../composables/useAppBindings'

export default {
  name: 'OcrView',
  setup() {
    return useAppBindings()
  },
}
</script>
