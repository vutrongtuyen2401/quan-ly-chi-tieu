# DANH MỤC THU CHI (CATEGORIES)

## 1. Mục Đích & Khái Niệm
Danh Mục Thu Chi là phân hệ tổ chức và phân loại các dòng tiền thu và chi trong Càn Khôn Linh Thạch Các.
Hệ thống sử dụng danh mục để cấu trúc hóa dữ liệu kế toán, làm nền tảng cho việc thiết lập Hạn Mức Ngân Sách, lập Báo Cáo Cơ Cấu Chi Tiêu, và phân tích xu hướng tài chính.

## 2. Cấu Trúc Của Một Danh Mục
- **Tên danh mục (Name)**: Tên gọi đặc trưng (ví dụ: "Ăn Uống", "Nhà Cửa", "Di Chuyển", "Giải Trí", "Lương", "Thưởng").
- **Loại danh mục (Category Type)**:
  - `EXPENSE`: Danh mục dành cho các khoản chi tiêu xuất tiền.
  - `INCOME`: Danh mục dành cho các khoản thu nhập nhập tiền.
- **Biểu tượng (Icon)**: Các emoji trực quan sinh động (🍜, 🏠, 🚗, 🎮, 🛍️, 💵, 🎁...).
- **Mã màu sắc (Color)**: Màu sắc phong thủy hiển thị trên biểu đồ tròn và thẻ giao dịch.

## 3. Các Thao Tác Khả Dụng
1. **Xem danh sách danh mục**: Phân tách rõ ràng giữa tab Danh Mục Chi Tiêu và Danh Mục Thu Nhập.
2. **Thêm danh mục tùy biến**: Người dùng có thể tự do tạo thêm danh mục theo thói quen sinh hoạt cá nhân.
3. **Chỉnh sửa danh mục**: Đổi tên, icon hoặc màu sắc hiển thị.
4. **Xóa danh mục**:
   - **Quy tắc bảo vệ dữ liệu**: Chỉ cho phép xóa danh mục khi **chưa có bất kỳ giao dịch hoặc ngân sách nào gắn liền**.
   - Nếu danh mục đang được sử dụng trong các giao dịch lịch sử, hệ thống sẽ từ chối xóa để tránh gây mồ côi dữ liệu kế toán.

## 4. Vị Trí Trên Giao Diện (UI Location)
- Tab **Danh Mục** (Tab 6, menu 'Danh Mục', `activeTab === 'categories'`).

## 5. Ranh Giới Quyền Hạn
- **Khí Linh Nhỏ (Live Mode)**: Có quyền tra cứu (`get_categories`), tạo danh mục mới (`create_category`) theo lệnh giọng nói có xác nhận.
- **Khí Linh AI Lớn (Knowledge Assistant)**: Chỉ có quyền **tra cứu danh sách danh mục (Read-Only)**; **TUYỆT ĐỐI KHÔNG CÓ QUYỀN tạo, sửa hoặc xóa danh mục**.
