# GIAO DỊCH ĐỊNH KỲ (LINH TRẬN ĐỊNH KỲ)

## 1. Mục Đích & Khái Niệm
Giao Dịch Định Kỳ (Linh Trận Định Kỳ) là tính năng tự động hóa ghi chép tài chính trong Càn Khôn Linh Thạch Các.
Tính năng này giải phóng người dùng khỏi việc phải nhập tay lặp đi lặp lại các khoản chi phí cố định phát sinh đều đặn theo chu kỳ:
- **Chi tiêu định kỳ**: Tiền thuê nhà/động phủ, tiền mạng internet, tiền điện nước, gói cước điện thoại, phí dịch vụ chung cư, trả góp định kỳ...
- **Thu nhập định kỳ**: Tiền lương hàng tháng, tiền lãi ngân hàng, thu nhập thụ động...

## 2. Cơ Chế Hoạt Động Của Giao Dịch Định Kỳ
Khi người dùng hỏi: *"Giao dịch định kỳ hoạt động thế nào?"* hoặc *"Linh trận định kỳ vận hành ra sao?"*, câu trả lời bám sát các nguyên lý sau:
1. **Thiết lập thông số linh trận**:
   - Loại giao dịch: `EXPENSE` (Chi Tiêu) hoặc `INCOME` (Thu Nhập).
   - Số tiền định kỳ (Amount > 0).
   - Túi Càn Khôn liên kết (Wallet ID): Ví sẽ tự động bị trừ tiền hoặc được cộng tiền.
   - Danh mục thu/chi (Category ID).
   - Tần suất lặp lại (`frequency`):
     + `weekly`: Hàng tuần (chu kỳ 7 ngày).
     + `monthly`: Hàng tháng (chu kỳ 1 tháng, cùng ngày của tháng tiếp theo).
   - Ngày chạy tiếp theo (`next_run_date`): Ngày dự kiến sinh giao dịch thực tế kế tiếp (định dạng `YYYY-MM-DD`).
   - Ghi chú: Mô tả chi tiết khoản định kỳ.
   - Trạng thái hoạt động (`is_active`): `1` là đang kích hoạt, `0` là tạm ngưng linh trận.
2. **Cơ chế tự động sinh giao dịch thực tế (Scheduler & Auto-generation)**:
   - Hệ thống kiểm tra tự động (`process_recurring_transactions`) mỗi khi người dùng truy cập hoặc tương tác với giao dịch.
   - Nếu ngày hiện tại >= `next_run_date` và `is_active == 1`:
     + Hệ thống tự động tạo một bản ghi giao dịch mới trong bảng `transactions`.
     + Cập nhật số dư của ví liên kết (trừ tiền nếu là chi, cộng tiền nếu là thu).
     + Tự động tính toán và cập nhật `next_run_date` mới: cộng thêm 7 ngày (nếu là weekly) hoặc cộng thêm 1 tháng (nếu là monthly).
     + Người dùng không cần phải nhớ hay thao tác nhập liệu thủ công mỗi khi đến kỳ thanh toán.

## 3. Các Thao Tác Khả Dụng
- **Xem danh sách**: Xem toàn bộ các linh trận định kỳ, tần suất, số tiền và ngày chạy kế tiếp.
- **Tạo mới**: Điền form và bấm **"Khởi Tạo Linh Trận Định Kỳ"**.
- **Bật / Tắt trạng thái**: Bấm nút chuyển trạng thái để tạm dừng hoặc kích hoạt lại linh trận mà không cần xóa đi.
- **Chỉnh sửa**: Cập nhật lại số tiền, ví, danh mục hoặc ngày hẹn chạy.
- **Xóa**: Hủy bỏ vĩnh viễn linh trận định kỳ.

## 4. Vị Trí Trên Giao Diện (UI Location)
- Nằm trong **Tab 2 (Giao Dịch, `activeTab === 'transactions'`)**.
- Nhấn vào nút toggle **"🔄 Linh Trận Định Kỳ"** ở phía trên danh sách giao dịch để mở bảng điều khiển định kỳ.

## 5. Ranh Giới Quyền Hạn
- **Khí Linh Nhỏ (Live Mode)**: Có quyền tra cứu danh sách định kỳ (`get_recurring_transactions`), tạo mới (`create_recurring_transaction`), sửa hoặc xóa sau khi người dùng xác nhận.
- **Khí Linh AI Lớn (Knowledge Assistant)**: Có quyền **tra cứu danh sách định kỳ chỉ đọc (Read-Only)**; **TUYỆT ĐỐI KHÔNG CÓ QUYỀN tạo, sửa, xóa hoặc kích hoạt linh trận định kỳ**.
