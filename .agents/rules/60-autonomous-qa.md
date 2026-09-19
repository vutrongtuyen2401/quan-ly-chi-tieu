# Autonomous QA & Verification Rules

Quy tắc bắt buộc áp dụng cho mọi hoạt động kiểm thử (Autonomous QA), bug fixing, refactoring hoặc verification trong dự án **Càn Khôn Linh Thạch Các**.

> ⛔ **QUYẾT ĐỊNH KIẾN TRÚC CHÍNH THỨC (ARCHITECTURAL DECISION)**:
> **VĨNH VIỄN VÔ HIỆU HÓA BROWSER AUTOMATION / BROWSER SUBAGENT / CHROME TRONG AUTONOMOUS QA.**
> Không tự mở Chrome, không gọi Browser Subagent, không dùng `/browser`, không dùng Chrome DevTools MCP cho automated QA. Mọi kiểm thử tự động tập trung vào Backend API, Logic nghiệp vụ, Toàn vẹn tài chính, AI Agent, Database integrity và Frontend Build.

---

## 1. HARD PROHIBITION — CẤM TUYỆT ĐỐI TRONG AUTONOMOUS QA

Trong toàn bộ quá trình Autonomous QA, Agent **TUYỆT ĐỐI KHÔNG ĐƯỢC (NEVER)**:
1. **Tự ý mở trình duyệt Chrome** hoặc bất kỳ trình duyệt nào khác.
2. **Kích hoạt / gọi `browser_subagent`** hoặc route task sang Browser Subagent.
3. **Sử dụng lệnh `/browser`** hoặc các lệnh browser automation tương đương.
4. **Chờ đợi trình duyệt** (wait for browser render/elements).
5. **Duyệt/khám phá giao diện qua browser** (browser exploration / browser smoke test).
6. **Sử dụng screenshot hoặc video browser** làm điều kiện kiểm thử bắt buộc.
7. **Khóa hoặc trì hoãn (block) quy trình QA** vì lý do không có hoặc lỗi hạ tầng browser.

> 👁️ **Khi task yêu cầu kiểm tra trực quan giao diện (Visual/UI verification)**:
> - Đánh dấu trạng thái: `MANUAL_UI_VERIFICATION_REQUIRED`.
> - Bàn giao việc kiểm tra mắt cho người dùng.
> - **TUYỆT ĐỐI KHÔNG** tự mở browser.

---

## 2. PHƯƠNG THỨC THAY THẾ BROWSER QA (HEADLESS & DETERMINISTIC FIRST)

Toàn bộ các luồng ứng dụng được xác thực đầy đủ và chính xác cao thông qua:

### 2.1. Backend Verification
- **Unit & Business Logic Tests**: Kiểm thử tính đúng đắn của logic tính toán, số dư, tỷ lệ (`python test_suite.py`).
- **Integration Tests**: Kiểm thử liên kết giữa các module và service (`test_live_khilinh_day3.py`, `test_live_khilinh_day4.py`).
- **Live API Tests**: Kiểm thử HTTP endpoints đang chạy thực tế trên FastAPI server.
- **Authentication Tests**: Đăng nhập, cấp phát JWT, xác thực token, thu hồi phiên.
- **Authorization & IDOR Tests**: Kiểm tra quyền sở hữu tài nguyên (người dùng A không thể đọc/sửa/xóa ví, giao dịch của người dùng B).
- **Financial Integrity Tests**: Toàn vẹn số dư ví, nạp/rút tiết kiệm, đối soát linh thạch, tất toán sổ nợ.
- **AI Agent Tests**: Khí Linh AI chat, gọi tool, trích xuất tham số, phản hồi theo context tài chính.
- **OCR Tests**: Linh Nhãn OCR trích xuất hóa đơn, xử lý dữ liệu ảnh.
- **Recurring Transaction Tests**: Lập lịch, kích hoạt giao dịch định kỳ, cập nhật chu kỳ tiếp theo.

### 2.2. Frontend Verification (Non-Browser)
- **Production Build**: `npm --prefix frontend run build` (kiểm tra toàn bộ template syntax, Vue compiler, bundle assets, import module).
- **Syntax & Type / Static Checks**: Kiểm tra cú pháp script, cấu trúc component, tính hợp lệ của reactive state.
- **Source Inspection**: Đảm bảo tuân thủ Quy tắc 1 của `AGENTS.md` (khai báo đầy đủ biến/state trước khi dùng trong template).

### 2.3. Integration & Critical Flows (Qua API, Không Cần Chrome)
- **Login API**: `POST /api/auth/login` kiểm tra phản hồi token và payload đạo hiệu/email.
- **Authenticated API**: Các endpoint yêu cầu Bearer token.
- **AI Agent API**: `POST /api/khilinh/chat` hoặc tương đương.
- **Financial Mutation API**: Tạo/sửa/xóa giao dịch, chuyển khoản liên ví.
- **Confirmation Flow**: Xác thực hợp đồng dữ liệu qua API (yêu cầu payload xác nhận, kiểm tra từ chối khi thiếu cờ xác nhận, thực thi khi có xác nhận).
- **Transaction & Balance Persistence**: Kiểm tra dữ liệu được ghi chuẩn vào SQLite và cập nhật số dư ví tức thời.
- **Analytics API**: Báo cáo thu chi, xu hướng 6 tháng, chi tiêu theo tuần.
- **Database Integrity**: Toàn vẹn cấu trúc và khóa ngoại SQLite (`PRAGMA integrity_check;`, `PRAGMA foreign_key_check;`).

---

## 3. KIỂM SOÁT HỒI QUY FRONTEND (FRONTEND REGRESSION)

Không sử dụng Browser Subagent để kiểm tra console trình duyệt. Việc kiểm tra và phòng ngừa lỗi Vue runtime được thực hiện thông qua:
1. **Build Verification**: Chạy `npm --prefix frontend run build` sau mỗi lần can thiệp mã nguồn Vue. Mọi lỗi template hoặc import sai sẽ bị chặn đứng tại khâu build.
2. **Static & Source Inspection**:
   - Rà soát toàn bộ các biến, ref, reactive, computed và methods dùng trong `<template>` đã được khai báo ở top-level `<script setup>` hoặc return từ `setup()`.
   - Đặc biệt cẩn trọng với các object/form lồng nhau (`editForm`, `transferForm`, `soulLampForm`, `filterForm`...) — phải khởi tạo giá trị mặc định cho tất cả các field.
3. **Xử lý Vue Warning / Runtime Error từ log do người dùng cung cấp**:
   $$\text{REPRODUCE BẰNG CODE/TEST PHÙ HỢP} \longrightarrow \text{TÌM ROOT CAUSE} \longrightarrow \text{MINIMAL FIX} \longrightarrow \text{BUILD KIỂM CHỨNG} \longrightarrow \text{REGRESSION CHECK}$$

---

## 4. QUY TRÌNH QA 10 GIAI ĐOẠN (10-PHASE QA PIPELINE)

Autonomous QA bắt buộc thực thi tuần tự theo 10 Phase. Sau mỗi phase **PASS**, tự động chuyển sang phase tiếp theo. Không rerun các phase không bị ảnh hưởng.

```
PHASE 1: Environment Health (FastAPI, SQLite, Node/Vite)
   ↓
PHASE 2: Backend Tests (test_suite.py)
   ↓
PHASE 3: Authentication & Security Tests (Login, JWT, IDOR)
   ↓
PHASE 4: Financial Integrity Tests (Wallets, Transfers, Debts, Goals)
   ↓
PHASE 5: AI Agent Tests (Khi Linh Tool Execution & Reasoning)
   ↓
PHASE 6: Live API / E2E Tests (Live services, OCR, Recurring)
   ↓
PHASE 7: Frontend Build / Static Verification (Vite build, Template Audit)
   ↓
PHASE 8: Database Integrity (PRAGMA integrity_check & foreign_key_check)
   ↓
PHASE 9: Targeted Regression (Các module chịu tác động trực tiếp)
   ↓
PHASE 10: Final Regression (Kiểm thử hồi quy tổng thể)
```

- **Phase 1 (Environment Health)**: Kiểm tra server FastAPI `127.0.0.1:8000` (`GET /docs` hoặc `GET /openapi.json` trả về 200 OK), kiểm tra file DB `app.db` sẵn sàng.
- **Phase 2 (Backend Tests)**: Chạy `python test_suite.py`, 100% tests phải PASS.
- **Phase 3 (Authentication/Security)**: Kiểm tra đăng nhập, cấp token, quyền truy cập tài nguyên theo user ID, chống IDOR.
- **Phase 4 (Financial Integrity)**: Kiểm tra tính toán số dư, giao dịch chuyển khoản, tất toán sổ nợ, quỹ tiết kiệm, cảnh báo ngân sách.
- **Phase 5 (AI Agent Tests)**: Kiểm tra tương tác Khí Linh, gọi công cụ tài chính, nguồn chân lý tài chính thuộc về backend.
- **Phase 6 (Live API/E2E Tests)**: Chạy `test_live_khilinh_day3.py`, `test_live_khilinh_day4.py`, kiểm thử giao dịch định kỳ và OCR endpoint.
- **Phase 7 (Frontend Build/Static Verification)**: Chạy `npm --prefix frontend run build`, kiểm tra exit code 0.
- **Phase 8 (Database Integrity)**: Kiểm tra SQLite integrity và foreign keys.
- **Phase 9 (Targeted Regression)**: Chạy các bài test cụ thể cho những file/module vừa được sửa.
- **Phase 10 (Final Regression)**: Chạy lại bài test bao quát để xác nhận toàn bộ hệ thống ổn định.

---

## 5. CHÍNH SÁCH TỰ ĐỘNG SỬA LỖI (AUTO-FIX & REPAIR PROTOCOL)

Khi bất kỳ bài test nào trong pipeline bị thất bại (FAIL):
1. **Chu trình sửa lỗi chuẩn**:
   $$\text{REPRODUCE} \longrightarrow \text{COLLECT EVIDENCE} \longrightarrow \text{IDENTIFY ROOT CAUSE} \longrightarrow \text{MINIMAL FIX} \longrightarrow \text{RESTART SERVICE} \longrightarrow \text{RETEST} \longrightarrow \text{TARGETED REGRESSION}$$
2. **Giới hạn 3 Repair Cycles**: Mỗi cụm lỗi (failure cluster) chỉ được thử nghiệm sửa đổi tối đa **3 chu kỳ**. Nếu sau 3 lần vẫn thất bại, dừng lại và báo cáo trạng thái `BLOCKED` trung thực kèm phân tích nguyên nhân kỹ thuật.
3. **Cấm sửa code chỉ để qua mặt test (No Cheating / Weakening)**:
   - **KHÔNG ĐƯỢC** tắt authentication.
   - **KHÔNG ĐƯỢC** bỏ qua authorization hoặc kiểm tra sở hữu dữ liệu.
   - **KHÔNG ĐƯỢC** gỡ bỏ luồng xác nhận (confirmation flow) của giao dịch tài chính.
   - **KHÔNG ĐƯỢC** hạ thấp validation rules hoặc mock dữ liệu tài chính giả.
   - **KHÔNG ĐƯỢC** làm yếu các chốt chặn an ninh (security controls).

---

## 6. XỬ LÝ SỰ CỐ MÔI TRƯỜNG FRONTEND BUILD (ENVIRONMENT FAILURE)

Nếu lệnh `npm` hoặc Node.js không chạy được trong shell:
- **KHÔNG ĐƯỢC** coi đó là lỗi ứng dụng (application failure) ngay lập tức.
- Thực hiện kiểm tra:
  1. Biến môi trường Shell (Path, PATHEXT).
  2. Sự tồn tại của Node.js (`node -v`).
  3. Đường dẫn npm (`npm -v`).
  4. Cấu hình package manager.
- Phân loại rõ ràng:
  - Nếu `npm` không khả dụng do môi trường máy chủ / terminal: Đánh dấu **`ENVIRONMENT_FAILURE`**.
  - **TUYỆT ĐỐI KHÔNG** sửa đổi mã nguồn ứng dụng để giải quyết sự cố môi trường shell.

---

## 7. CỔNG NGHIỆM THU (DONE GATE)

Autonomous QA chỉ được tuyên bố **PASS** khi thỏa mãn đồng thời các điều kiện sau:
- [ ] **Backend Tests**: PASS 100% (`python test_suite.py`).
- [ ] **Security & Auth Tests**: PASS (Đăng nhập, JWT, chống IDOR).
- [ ] **Financial Integrity Tests**: PASS (Số dư, chuyển khoản, quỹ, nợ, ngân sách).
- [ ] **AI Agent Tests**: PASS (Khí Linh tool calling, financial grounding).
- [ ] **Live API Tests**: PASS (`test_live_khilinh_day3.py`, `test_live_khilinh_day4.py`...).
- [ ] **Frontend Build**: PASS (`npm --prefix frontend run build` exit code 0).
- [ ] **Database Integrity**: PASS (`PRAGMA integrity_check;` = `ok`).
- [ ] **Targeted Regression**: PASS.
- [ ] **Zero Unexplained Errors**: Không còn bất kỳ lỗi application (HTTP 500, unhandled exception) nào chưa được điều tra và khắc phục.

> 🚫 **Lưu ý**: Trình duyệt (Browser) **KHÔNG PHẢI** là điều kiện để PASS.
> Nếu giao diện cần kiểm tra hiển thị trực quan: Ghi chú rõ `MANUAL_UI_VERIFICATION_REQUIRED`, phần automated QA vẫn hoàn thành nghiệm thu độc lập.

---

## 8. CẤU TRÚC BÁO CÁO NGHIỆM THU (FINAL REPORT TEMPLATE)

Báo cáo nghiệm thu Autonomous QA bắt buộc tuân thủ mẫu chuẩn:

```markdown
# 📋 BÁO CÁO KIỂM THỬ AUTONOMOUS QA — CÀN KHÔN LINH THẠCH CÁC

Backend: [PASS / FAIL / SKIPPED] — [Chi tiết số lượng test pass]
Security: [PASS / FAIL] — [Chi tiết auth/IDOR verification]
Financial: [PASS / FAIL] — [Chi tiết kiểm tra số dư & toàn vẹn dữ liệu]
AI Agent: [PASS / FAIL] — [Chi tiết kiểm tra Khí Linh tool call]
Live API: [PASS / FAIL] — [Chi tiết test_live_khilinh]
Frontend Build: [PASS / FAIL / ENVIRONMENT_FAILURE] — [Chi tiết build assets]
Database: [PASS / FAIL] — [PRAGMA integrity_check result]
Regression: [PASS / FAIL] — [Các bài test hồi quy đã hoàn thành]
Browser Automation: DISABLED BY PROJECT POLICY
Manual UI Verification: [REQUIRED / NOT REQUIRED]

Failures:
- [Danh sách các lỗi phát hiện trong quá trình test, hoặc 'None']

Root Causes:
- [Phân tích nguyên nhân gốc rễ của từng lỗi, hoặc 'N/A']

Fixes:
- [Danh sách file và logic đã sửa đổi, hoặc 'N/A']

Remaining Risks:
- [Các rủi ro tồn đọng hoặc khía cạnh cần theo dõi, nếu có]
```
