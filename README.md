# ☯️ CÀN KHÔN LINH THẠCH CÁC — HỆ THỐNG QUẢN LÝ CHI TIÊU AI (TU TIÊN THEME v3.0)

Dự án quản lý chi tiêu cá nhân kết hợp AI Google Gemini, xây dựng theo phong cách **Tu Tiên (Xianxia Theme)** và quản lý quy trình phát triển theo chuẩn **GitHub Spec-Kit (Spec-Driven Development)**.

---

## 🛠️ Công Nghệ Sử Dụng

- **Backend**: Python 3.10+, FastAPI, SQLite (`app.db`), JWT, Bcrypt, Google Gemini API (`google-generativeai`).
- **Frontend**: Vue 3, Vite, Chart.js, `vue-chartjs`, Axios, Vanilla CSS (Cosmic Dark / Xianxia Theme).
- **Spec-Kit**: GitHub Spec-Kit CLI (`specify-cli`), `.specify/` specification templates & workflow, `.github/skills/` agent integrations.

---

## 📐 GitHub Spec-Kit (Spec-Driven Development)

Dự án đã tích hợp thành công **GitHub Spec-Kit**:

- **Cấu trúc `.specify/`**:
  - `memory/constitution.md`: Nguyên tắc tối cao và quy chuẩn thiết kế của dự án.
  - `templates/`: Mẫu Specification, Technical Plan, Task Breakdown.
  - `workflows/`: Quy trình thực thi từ ý tưởng đến kiểm thử.
- **Lệnh Spec-Kit Skills**:
  - `/speckit-constitution`: Thiết lập nguyên tắc cốt lõi của dự án.
  - `/speckit-specify`: Khai mở yêu cầu tính năng (Specification).
  - `/speckit-plan`: Lập kế hoạch kiến trúc kỹ thuật.
  - `/speckit-tasks`: Phân rã công việc thực thi.
  - `/speckit-implement`: Triển khai mã nguồn và nghiệm thu.

---

## 🚀 Hướng Dẫn Chạy Trên Máy Tính Mới / Tài Khoản Mới

### Bước 1: Sao chép dự án
- Cách 1: Push mã nguồn lên **GitHub / GitLab** và clone về máy mới.
- Cách 2: Nén thư mục dự án (bỏ thư mục `node_modules` và `__pycache__`) rồi copy sang máy mới.

### Bước 2: Cài đặt Backend (Python)
1. Mở terminal tại thư mục gốc `quan-ly-chi-tieu`:
   ```bash
   pip install -r requirements.txt
   ```
2. Tạo file `.env` từ file mẫu `.env.example`:
   ```bash
   cp .env.example .env
   ```
   *(Thêm `GEMINI_API_KEY` của bạn vào file `.env` nếu muốn dùng tính năng AI OCR hóa đơn và Chat trợ lý).*

3. Khởi chạy Backend FastAPI:
   ```bash
   python main.py
   ```
   Backend sẽ chạy tại: `http://localhost:8000` (API Docs: `http://localhost:8000/docs`).

### Bước 3: Cài đặt Frontend (Vue 3)
1. Mở terminal mới, di chuyển vào thư mục `frontend`:
   ```bash
   cd frontend
   ```
2. Cài đặt các gói phụ thuộc (Node.js):
   ```bash
   npm install
   ```
3. Khởi chạy Frontend Vite:
   ```bash
   npm run dev
   ```
   Frontend sẽ chạy tại: `http://localhost:5173`.

---

## 👤 Tài Khoản Mẫu Mặc Định (Đã Seed Dữ Liệu)
- **Linh Bưu (Email)**: `admin@gmail.com`
- **Khẩu Quyết (Mật khẩu)**: `123456`

---

## 🔮 Các Tính Năng Chính (v3.0)
1. **📊 Đạo Đường Tổng Quan**: Thống kê Thu/Chi/Tiết kiệm, biểu đồ phân bổ chi tiêu Doughnut & Bar mini, cảnh báo hạn mức.
2. **💸 Tàng Kinh Giao Dịch**: Ghi nhận, chỉnh sửa, xóa giao dịch thu/chi.
3. **💳 Túi Càn Khôn & Chuyển Tiền**: Quản lý nhiều loại ví và chuyển Linh Thạch trực tiếp giữa các ví.
4. **🏷️ Danh Mục Thu Chi**: Thêm/xóa các loại danh mục với Icon đa dạng.
5. **🧾 Linh Nhãn OCR**: Quét ảnh hóa đơn bằng Google Gemini Vision API.
6. **🎯 Hạn Mức Tu Luyện**: Thiết lập ngân sách hàng tháng, tự động cảnh báo *"Tẩu Hỏa Nhập Ma"*.
7. **📈 Thiên Cơ Thống Kê (Mới)**: Biểu đồ xu hướng 6 tháng, chi tiêu 4 tuần, so sánh 2 tháng side-by-side.
8. **💬 Khí Linh AI & Khai Thị Tiết Kiệm**: Trợ lý tư vấn tài chính Gemini và đề xuất 5 mẹo tiết kiệm thông minh.

