# QUẢN TRỊ TÔNG MÔN (PHÂN QUYỀN CHƯỞNG MÔN CÁC)

## 1. Mục Đích & Khái Niệm
Quản Trị Tông Môn (Chưởng Môn Các) là bảng điều khiển quản trị hệ thống (Admin Portal) của Càn Khôn Linh Thạch Các.
Phân hệ này chỉ hiển thị và cho phép truy cập đối với những tài khoản có vai trò tối cao: `admin` (Chưởng Môn). Người dùng thông thường (`user`) hoàn toàn không nhìn thấy tab này và không thể gọi các API quản trị.

## 2. Các Quyền Năng Khả Dụng Trong Chưởng Môn Các
1. **Thống kê toàn bộ Tông Môn**:
   - Tổng số lượng đạo hữu (tài khoản đã đăng ký).
   - Số tài khoản đang hoạt động bình thường (`active`).
   - Số tài khoản đang bị phong tỏa / khóa (`locked`).
2. **Quản lý danh sách thành viên**:
   - Tra cứu danh sách người dùng theo tên đạo hiệu, email hoặc trạng thái.
   - Xem thời điểm đăng ký và vai trò hiện tại.
3. **Phân quyền vai trò (Role-Based Access Control - RBAC)**:
   - Thăng cấp một người dùng từ `user` lên `admin` (Chưởng Môn).
   - Hạ cấp từ `admin` xuống `user`.
4. **Kiểm soát trạng thái tài khoản (Account Status Control)**:
   - Khóa tài khoản (`lock`): Vô hiệu hóa quyền đăng nhập của tài khoản vi phạm quy chế.
   - Mở khóa tài khoản (`unlock`): Khôi phục trạng thái hoạt động bình thường.

## 3. Vị Trí Trên Giao Diện (UI Location)
- Tab **Phân Quyền** (Tab 11, `activeTab === 'admin'`).
- Tab này chỉ tự động xuất hiện trên thanh điều hướng khi tài khoản đăng nhập có `userRole === 'admin'`.

## 4. Ranh Giới Quyền Hạn
- **Người dùng thông thường (`role === 'user'`)**: Không có quyền truy cập tab 11; nếu cố tình gửi request sẽ bị từ chối bằng mã lỗi HTTP 403 Forbidden.
- **Khí Linh AI Lớn**: Có thể giải thích cơ chế phân quyền RBAC và vai trò của Chưởng Môn Các; nhưng **TUYỆT ĐỐI KHÔNG CÓ QUYỀN tự ý thăng chức, hạ chức hay khóa tài khoản** của bất kỳ ai.
