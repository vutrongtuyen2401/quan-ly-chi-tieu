---
name: autonomous-qa
description: "Use for autonomous QA, full-stack health verification, automated test execution, frontend build, live E2E, financial integrity, security audits, and regression verification without browser automation."
---

# Autonomous QA Skill — Càn Khôn Linh Thạch Các

Kỹ năng thực hiện kiểm thử tự động, chẩn đoán sự cố, tự động sửa lỗi và nghiệm thu chất lượng toàn diện trong dự án **Càn Khôn Linh Thạch Các** mà **KHÔNG SỬ DỤNG BROWSER AUTOMATION**.

> ⛔ **QUYẾT ĐỊNH KIẾN TRÚC CHÍNH THỨC**:
> **Autonomous QA của dự án VĨNH VIỄN KHÔNG ĐƯỢC sử dụng Browser Subagent hoặc Chrome automation.**
> Mọi kiểm thử tự động đều tập trung vào Backend API, Logic nghiệp vụ, Toàn vẹn tài chính, AI Agent, Database integrity và Frontend Build.

---

## 1. HARD PROHIBITION (CẤM TUYỆT ĐỐI)

Khi kích hoạt Autonomous QA, **NEVER**:
- Mở Chrome hoặc bất kỳ trình duyệt nào khác.
- Gọi hoặc chuyển tiếp task sang `browser_subagent`.
- Sử dụng lệnh `/browser` hoặc các công cụ Chrome DevTools MCP tự động.
- Chờ đợi browser render hoặc tìm kiếm DOM selectors.
- Khám phá hoặc kiểm tra giao diện qua browser exploration/smoke test.
- Sử dụng browser screenshot làm điều kiện bắt buộc để PASS.
- Khóa hoặc hoãn (block) quy trình QA vì lý do browser không khả dụng.

> 👁️ **Nếu task yêu cầu kiểm tra giao diện trực quan**:
> - Báo cáo: `MANUAL_UI_VERIFICATION_REQUIRED`.
> - **KHÔNG ĐƯỢC** tự mở browser. Giao việc quan sát trực quan cho người dùng sau khi phần automated QA đã hoàn thành.

---

## 2. PHƯƠNG THỨC KIỂM THỬ THAY THẾ (HEADLESS VERIFICATION)

Toàn bộ các luồng ứng dụng được xác minh độc lập, tốc độ cao và mang tính tất định cao:

### Backend
- **Unit / Business Logic Tests**: `python test_suite.py` (bao phủ Auth, Wallets, Transactions, Budgets, Debts, Saving Goals, Reports).
- **Integration Tests**: `test_live_khilinh_day3.py`, `test_live_khilinh_day4.py`.
- **Live API Tests**: Gọi trực tiếp HTTP endpoints qua Python script hoặc curl/Invoke-RestMethod.
- **Authentication Tests**: `POST /api/auth/login`, cấp phát JWT, xác thực Bearer token.
- **Authorization & IDOR Tests**: Xác thực quyền sở hữu dữ liệu (user A không truy cập được tài nguyên của user B).
- **Financial Integrity Tests**: Tính toán số dư ví, nạp/rút quỹ, tất toán sổ nợ, hạn mức chi tiêu.
- **AI Agent Tests**: Khí Linh AI chat, gọi tool, tính toán tài chính dựa trên backend là nguồn chân lý duy nhất.
- **OCR Tests**: Linh Nhãn OCR trích xuất hóa đơn, validate dữ liệu trả về.
- **Recurring Transactions**: Kích hoạt và cập nhật chu kỳ giao dịch định kỳ.

### Frontend
- **Production Build**: `npm --prefix frontend run build` (kiểm tra toàn bộ cú pháp Vue, template compilation, bundle dependencies, import modules).
- **Static & Template Audit**: Rà soát các biến ref/reactive dùng trong `<template>` đã được khai báo ở top-level `<script setup>`.
- **Object/Form Field Audit**: Đảm bảo tất cả các field của object form (`editForm`, `soulLampForm`, `filterForm`...) đều có giá trị khởi tạo mặc định.

### Integration
- Kiểm tra toàn bộ 10 Critical Journeys thông qua API và database state (Dashboard, Wallets, Transactions, Income, Transfers, Goals, Budgets, Debts, Reports, Khí Linh AI).
- **Financial Mutation Confirmation Flow**: Kiểm tra API từ chối giao dịch khi thiếu cờ xác nhận và thực thi an toàn khi có cờ xác nhận.

---

## 3. FRONTEND REGRESSION PROTOCOL

1. **Không dùng Browser Subagent để kiểm tra console**.
2. **Kiểm tra hồi quy Vue runtime**:
   - Chạy `npm --prefix frontend run build` sau mọi lần sửa code Vue.
   - Kiểm tra static analysis và source inspection.
   - Kiểm tra HTTP/API integration tests đảm bảo response format không gây crash frontend.
3. **Khi nhận được log lỗi Vue từ người dùng**:
   $$\text{REPRODUCE BẰNG TEST/CODE} \longrightarrow \text{TÌM ROOT CAUSE} \longrightarrow \text{MINIMAL FIX} \longrightarrow \text{BUILD} \longrightarrow \text{REGRESSION CHECK}$$

---

## 4. QUY TRÌNH QA 10 GIAI ĐOẠN (10-PHASE PIPELINE)

Thực hiện tuần tự 10 Phase. Sau mỗi phase **PASS**, tự động chuyển sang phase tiếp theo. Không rerun các phase không bị ảnh hưởng.

1. **PHASE 1: Environment Health**:
   - Kiểm tra uvicorn backend `http://127.0.0.1:8000/docs` hoặc `/openapi.json` trả về HTTP 200 OK.
   - Kiểm tra SQLite database `app.db` truy cập được.
2. **PHASE 2: Backend Tests**:
   - Chạy `python test_suite.py` -> Đảm bảo 100% test cases đạt `OK`.
3. **PHASE 3: Authentication & Security Tests**:
   - Kiểm tra Login API, cấp phát token JWT, quyền sở hữu tài nguyên (chống IDOR).
4. **PHASE 4: Financial Integrity Tests**:
   - Kiểm tra biến động số dư ví, nạp/rút quỹ, tất toán nợ, luồng confirmation flow qua API.
5. **PHASE 5: AI Agent Tests**:
   - Kiểm tra Khí Linh AI chat, tool calling, grounding tài chính từ backend.
6. **PHASE 6: Live API & E2E Tests**:
   - Chạy `test_live_khilinh_day3.py`, `test_live_khilinh_day4.py`, OCR và recurring transactions.
7. **PHASE 7: Frontend Build & Static Verification**:
   - Chạy `npm --prefix frontend run build` (exit code 0), rà soát template binding.
8. **PHASE 8: Database Integrity**:
   - Chạy `PRAGMA integrity_check;` (trả về `ok`) và `PRAGMA foreign_key_check;`.
9. **PHASE 9: Targeted Regression**:
   - Kiểm thử tập trung vào các module/hàm trực tiếp bị tác động bởi code mới sửa.
10. **PHASE 10: Final Regression**:
    - Kiểm thử hồi quy toàn diện hệ thống.

---

## 5. AUTO-FIX & DEFECT REPAIR PROTOCOL

Khi phát hiện lỗi hoặc test FAIL:
1. **Quy trình chuẩn**:
   $$\text{REPRODUCE} \longrightarrow \text{COLLECT EVIDENCE} \longrightarrow \text{IDENTIFY ROOT CAUSE} \longrightarrow \text{MINIMAL FIX} \longrightarrow \text{RESTART SERVICE} \longrightarrow \text{RETEST} \longrightarrow \text{TARGETED REGRESSION}$$
2. **Giới hạn 3 Chu Kỳ**: Tối đa 3 repair cycles cho một cụm lỗi. Sau 3 lần vẫn lỗi -> dừng lại và báo cáo `BLOCKED` trung thực.
3. **Tuyệt đối KHÔNG sửa code để qua mặt test**:
   - Không tắt authentication.
   - Không bỏ qua authorization hoặc kiểm tra sở hữu.
   - Không gỡ bỏ confirmation flow của giao dịch tài chính.
   - Không hạ thấp validation rules hoặc mock dữ liệu tài chính giả.
   - Không làm yếu security controls.

---

## 6. XỬ LÝ SỰ CỐ MÔI TRƯỜNG BUILD (ENVIRONMENT FAILURE)

Nếu lệnh `npm` không thể chạy trong shell:
- **KHÔNG ĐƯỢC** coi đó là lỗi của ứng dụng.
- Kiểm tra Node.js, đường dẫn npm, shell environment.
- Phân loại: **`ENVIRONMENT_FAILURE`**.
- **TUYỆT ĐỐI KHÔNG** sửa mã nguồn ứng dụng để khắc phục lỗi môi trường shell.

---

## 7. CỔNG NGHIỆM THU (DONE GATE)

Autonomous QA chỉ PASS khi thỏa mãn đồng thời:
- [ ] Backend tests PASS 100% (`python test_suite.py`).
- [ ] Security/auth tests PASS.
- [ ] Financial integrity tests PASS.
- [ ] AI Agent tests PASS.
- [ ] Live API tests PASS.
- [ ] Frontend build PASS (`npm --prefix frontend run build`).
- [ ] Database integrity PASS (`PRAGMA integrity_check;`).
- [ ] Targeted regression PASS.
- [ ] Không còn lỗi application (HTTP 500, unhandled exception) chưa giải thích.

> 🚫 **Lưu ý**: Trình duyệt (Browser) **KHÔNG PHẢI** điều kiện PASS.
> Nếu UI cần kiểm tra bằng mắt: ghi rõ `MANUAL_UI_VERIFICATION_REQUIRED`, vẫn hoàn thành phần automated QA.

---

## 8. BÁO CÁO NGHIỆM THU (FINAL REPORT FORMAT)

```markdown
# 📋 BÁO CÁO KIỂM THỬ AUTONOMOUS QA — CÀN KHÔN LINH THẠCH CÁC

Backend: [PASS / FAIL / SKIPPED] — [Chi tiết test_suite.py]
Security: [PASS / FAIL] — [Chi tiết auth/IDOR]
Financial: [PASS / FAIL] — [Chi tiết số dư & confirmation flow]
AI Agent: [PASS / FAIL] — [Chi tiết Khí Linh tool call]
Live API: [PASS / FAIL] — [Chi tiết live E2E tests]
Frontend Build: [PASS / FAIL / ENVIRONMENT_FAILURE] — [Chi tiết Vite build]
Database: [PASS / FAIL] — [PRAGMA integrity_check result]
Regression: [PASS / FAIL] — [Kết quả kiểm thử hồi quy]
Browser Automation: DISABLED BY PROJECT POLICY
Manual UI Verification: [REQUIRED / NOT REQUIRED]

Failures:
- [Danh sách lỗi phát hiện hoặc 'None']

Root Causes:
- [Phân tích nguyên nhân gốc rễ hoặc 'N/A']

Fixes:
- [Danh sách file và logic đã sửa đổi hoặc 'N/A']

Remaining Risks:
- [Các rủi ro tồn đọng hoặc khuyến nghị theo dõi]
```
