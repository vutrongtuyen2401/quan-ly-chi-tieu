# ☯️ CÀN KHÔN LINH THẠCH CÁC — HỆ THỐNG QUẢN LÝ CHI TIÊU AI (TU TIÊN THEME)

Dự án quản lý chi tiêu cá nhân kết hợp AI Google Gemini, xây dựng theo phong cách **Tu Tiên (Xianxia Theme)**.

---

## 🛠️ Công Nghệ Sử Dụng

- **Backend**: Python 3.10+, FastAPI, SQLite (`app.db`), JWT, Bcrypt, Google Gemini API (`google-generativeai`).
- **Frontend**: Vue 3, Vite, Axios, Vanilla CSS (Cosmic Dark / Xianxia Theme).

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

## 🔮 Các Tính Năng Chính
1. **📊 Đạo Đường Tổng Quan**: Thống kê Thu/Chi/Tiết kiệm, cảnh báo hạn mức, biểu đồ phân bổ chi tiêu.
2. **💸 Tàng Kinh Giao Dịch**: Ghi nhận, chỉnh sửa, xóa giao dịch thu/chi.
3. **💳 Túi Càn Khôn**: Quản lý nhiều loại ví (Tiền mặt, Ngân hàng, Ví điện tử).
4. **🏷️ Danh Mục Thu Chi**: Thêm/xóa các loại danh mục với Icon đa dạng.
5. **🧾 Linh Nhãn OCR**: Quét ảnh hóa đơn bằng Google Gemini Vision API.
6. **🎯 Hạn Mức Tu Luyện**: Thiết lập ngân sách hàng tháng, tự động cảnh báo *"Tẩu Hỏa Nhập Ma"*.
7. **💬 Khí Linh AI**: Trợ lý tư vấn tài chính Gemini bằng giọng văn tu tiên.
