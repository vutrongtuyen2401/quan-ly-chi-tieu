# BẢO MẬT & PHÂN QUYỀN HỆ THỐNG (SECURITY & PERMISSIONS)

## 1. Cơ Chế Xác Thực & Phân Quyền (Authentication & RBAC)
1. **JSON Web Token (JWT)**:
   - Sử dụng thuật toán ký `HS256`.
   - Mỗi token chứa `user_id`, `email`, `role`, và `token_version`.
   - Thời hạn hiệu lực an toàn; khi hết hạn người dùng cần đăng nhập lại.
2. **Mã Hóa Mật Khẩu (Password Hashing)**:
   - Mật khẩu được mã hóa an toàn bằng thư viện `bcrypt` với muối ngẫu nhiên (salt). Tuyệt đối không lưu mật khẩu dạng bản rõ (plaintext).
3. **Phân Quyền Vai Trò (Role-Based Access Control - RBAC)**:
   - `user`: Vai trò người dùng thông thường. Chỉ có quyền truy cập, xem và quản lý dữ liệu tài chính của chính mình.
   - `admin` (Chưởng Môn): Có thêm quyền truy cập phân hệ Quản Trị Tông Môn (Tab Chưởng Môn Các), xem thống kê tài khoản toàn hệ thống, quản lý người dùng, thay đổi vai trò hoặc khóa/mở khóa tài khoản.

---

## 2. Bản Mệnh Hồn Đăng (Soul Lamp) & Khôi Phục Tài Khoản
- **Đèn Mệnh (Soul Lamp)**: Là lớp bảo vệ thứ hai cho tài khoản đạo hữu, được băm mật mã riêng biệt để bảo vệ các thao tác trọng yếu.
- **Khôi phục mật khẩu (Forgot/Reset Password)**:
  - Khi quên mật khẩu, người dùng nhập email để hệ thống sinh mã OTP ngẫu nhiên 6 ký tự gồm chữ và số (`secrets.choice`).
  - Mã OTP có hiệu lực trong 15 phút.
  - Người dùng nhập mã OTP cùng mật khẩu mới để hoàn tất đặt lại mật khẩu.
- **Hủy bỏ toàn bộ phiên đăng nhập cũ (Token Versioning)**:
  - Khi người dùng đổi mật khẩu hoặc đặt lại mật khẩu, trường `token_version` trong cơ sở dữ liệu sẽ tự động tăng thêm 1 đơn vị.
  - Toàn bộ các JWT token cũ đang tồn tại trên các thiết bị khác sẽ lập tức bị vô hiệu hóa, bảo vệ tuyệt đối tài khoản trước nguy cơ bị chiếm đoạt phiên đăng nhập.

---

## 3. Cách Ly Dữ Liệu & Ranh Giới AI (AI Permission Boundary)
- **Cách ly dữ liệu cấp người dùng**: Mọi truy vấn cơ sở dữ liệu (Database queries) đều bắt buộc lọc qua mệnh đề `WHERE user_id = ?`. Người dùng A tuyệt đối không thể xem hay sửa dữ liệu của người dùng B (ngăn chặn IDOR).
- **Ranh giới công cụ AI (Tool Permission Boundary)**:
  - Chế độ `KNOWLEDGE` (Khí Linh AI Lớn): Chỉ cho phép các công cụ có `operation_type == OperationType.READ`. Mọi công cụ ghi chép (`WRITE`), xóa (`DELETE`) hay hệ thống (`SYSTEM`) đều bị từ chối ở tầng mã nguồn (Code-level Tool Registry Enforcement).
  - Chế độ `ACTION` (Khí Linh Nhỏ): Được phép gọi công cụ thay đổi dữ liệu nhưng bắt buộc phải đi qua quy trình xác nhận của người dùng (Conversational Confirmation).
