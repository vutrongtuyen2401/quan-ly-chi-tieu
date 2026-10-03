# ☯️ CÀN KHÔN LINH THẠCH CÁC — HỆ THỐNG QUẢN LÝ CHI TIÊU AI (TU TIÊN THEME v3.0)

Dự án quản lý chi tiêu cá nhân kết hợp AI Google Gemini, xây dựng theo phong cách **Tu Tiên (Xianxia Theme)** và quản lý quy trình phát triển theo chuẩn **GitHub Spec-Kit (Spec-Driven Development)**.

---

## 🛠️ Công Nghệ Sử Dụng

- **Backend**: Python 3.10+, FastAPI, SQLite (`app.db`), JWT, Bcrypt, Google Gemini API (`google-genai`).
- **Frontend**: Vue 3, Vite, Pinia, Vue Router, Chart.js, `vue-chartjs`, Axios, Vanilla CSS (Cosmic Dark / Xianxia Theme).
- **Spec-Kit**: GitHub Spec-Kit CLI (`specify-cli`), `.specify/` specification templates & workflow, `.github/skills/` agent integrations.

---

## 🗂️ Cấu Trúc Mã Nguồn

```
main.py                    # Khởi tạo FastAPI, gắn router (chạy: python main.py)
backend/
  config.py                # Đọc cấu hình từ .env
  db.py                    # Kết nối SQLite, tạo bảng, migration không phá hủy, seed
  schemas.py               # Pydantic schemas + kiểm tra dữ liệu đầu vào
  security.py              # JWT, phân quyền, mật khẩu, giới hạn số lần thử sai
  services.py              # Nghiệp vụ dùng chung (quyền sở hữu ví/danh mục, số dư, giao dịch định kỳ)
  mailer.py                # Gửi mã reset mật khẩu qua SMTP
  gemini.py                # Gọi Google Gemini (google-genai)
  errors.py, utils.py
  routers/                 # auth, wallets, categories, transactions, budgets, reports,
                           # recurring, debts, goals, ai, users, admin
frontend/src/
  main.js                  # Tạo app, Pinia, router, guard trang admin
  App.vue                  # Khung: nền, header, thanh tab, <router-view>, modal hồ sơ, toast
  router.js                # Mỗi tab là một route (#/transactions, #/stats, ...)
  api.js                   # Axios dùng chung (gắn token, tự đăng xuất khi 401)
  stores/                  # Store Pinia theo domain: session, wallets, categories, transactions,
                           # budgets, reports, debts, goals, ai, admin
  composables/useAppBindings.js  # Gộp state/hàm của các store cho template
  views/                   # LoginView + 11 view theo tab (DashboardView, TransactionsView, ...)
  components/              # ChartComponents, XianxiaBackdrop
  utils/format.js          # Định dạng tiền, ngày theo giờ địa phương, escape HTML
  styles/app.css
test_suite.py              # python -m unittest test_suite -v
scripts/reset_sample_data.py
```

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

   *(File cơ sở dữ liệu `app.db` không được lưu trên Git. Lần chạy đầu tiên, server sẽ tự tạo `app.db` và nạp dữ liệu mẫu, kèm tài khoản admin `admin@gmail.com` với mật khẩu lấy từ `SEED_ADMIN_PASSWORD` trong `.env`; nếu để trống, mật khẩu được sinh ngẫu nhiên và in ra console).*

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

## 👤 Tài Khoản Mẫu (Seed Data)
- **Linh Bưu (Email)**: `admin@gmail.com`
- **Khẩu Quyết (Mật khẩu)** và **Bản Mệnh Hồn Đăng**: Được sinh ngẫu nhiên khi khởi tạo cơ sở dữ liệu lần đầu và in trực tiếp ra console terminal. Bạn cũng có thể thiết lập giá trị cố định qua biến `SEED_ADMIN_PASSWORD` / `SEED_ADMIN_SOUL_LAMP` trong file `.env`.
- File `app.db` không còn được đưa lên git (chứa dữ liệu và mã băm mật khẩu). Máy mới clone về sẽ tự tạo DB trống khi chạy `python main.py`.

---

## ⚙️ Biến Môi Trường (.env)
- `JWT_SECRET`: Khóa bí mật ký JWT (bắt buộc, server sẽ dừng nếu chưa cấu hình).
- `ALLOWED_ORIGINS`: Danh sách tên miền CORS được phép truy cập (mặc định: `http://localhost:5173`).
- `GEMINI_API_KEY`: Khóa API Google Gemini cho tính năng AI OCR và trợ lý Khí Linh.
- `SEED_ADMIN_PASSWORD`: (Tùy chọn) Mật khẩu cho tài khoản seed `admin@gmail.com`.
- `SEED_ADMIN_SOUL_LAMP`: (Tùy chọn) Bản Mệnh Hồn Đăng cho tài khoản seed `admin@gmail.com`.
- `DATABASE_PATH`: (Tùy chọn) Đường dẫn file SQLite (mặc định: `app.db`).
- `HOST`: (Tùy chọn) Địa chỉ lắng nghe của backend (mặc định: `127.0.0.1`; đặt `0.0.0.0` để mở cho máy khác trong mạng LAN).
- `APP_ENV`: `development` (mặc định) hoặc `production`. Ở `production`, mã reset mật khẩu **chỉ** được gửi qua email và không bao giờ trả trong API; nếu chưa cấu hình SMTP, chức năng quên mật khẩu trả lỗi 503. Ở `development` mà chưa cấu hình SMTP, mã được trả trực tiếp để test.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_SECURITY` (`starttls` | `ssl` | `none`): Cấu hình SMTP để gửi mã reset mật khẩu (ví dụ Gmail: `smtp.gmail.com`, `587`, `starttls`, dùng App Password). Khi đã đặt `SMTP_HOST` thì mã luôn được gửi qua email, kể cả ở `development`.

---

## 🧪 Kiểm Thử
```bash
python -m unittest test_suite -v
```

---

## 🔮 Các Tính Năng Nổi Bật (v3.5)
1. **📊 Đạo Đường Tổng Quan**: Thống kê Thu/Chi/Tiết kiệm, biểu đồ phân bổ chi tiêu Doughnut & Bar mini, cảnh báo hạn mức.
2. **💸 Tàng Kinh Giao Dịch**: Ghi nhận, chỉnh sửa, lọc theo ngày/danh mục/ví/từ khóa, phân trang và xuất báo cáo CSV/Excel.
3. **🔄 Giao Dịch Định Kỳ**: Tự động sinh giao dịch định kỳ (hàng tuần / hàng tháng).
4. **💳 Túi Càn Khôn & Chuyển Tiền**: Quản lý, chỉnh sửa ví và chuyển Linh Thạch trực tiếp giữa các ví.
5. **🏷️ Danh Mục Thu Chi**: Thêm, chỉnh sửa, xóa các loại danh mục với Icon đa dạng.
6. **🧾 Linh Nhãn OCR**: Quét ảnh hóa đơn bằng Google Gemini Vision API.
7. **🎯 Hạn Mức Tu Luyện**: Thiết lập ngân sách hàng tháng, tự động cảnh báo *"Tẩu Hỏa Nhập Ma"*.
8. **📈 Thiên Cơ Thống Kê**: Biểu đồ xu hướng 6 tháng, chi tiêu 4 tuần, so sánh 2 tháng side-by-side.
9. **💬 Khí Linh AI & Khai Thị Tiết Kiệm**: Trợ lý tư vấn tài chính Gemini và đề xuất 5 mẹo tiết kiệm thông minh.
10. **🛡️ An Ninh & Bảo Mật**: Rate limiting chống brute-force đăng nhập & khôi phục mật khẩu, đặt lại mật khẩu bằng mã OTP, kiểm tra quyền sở hữu dữ liệu ở mọi API, khóa tài khoản có hiệu lực ngay lập tức, CORS & JWT.

