# SỔ NỢ (QUẢN LÝ KHOẢN NỢ & CÔNG NỢ)

## 1. Mục Đích & Khái Niệm
Sổ Nợ là tính năng chuyên trách trong Càn Khôn Linh Thạch Các giúp người dùng quản lý toàn bộ các khoản nợ, ghi chép và theo dõi công nợ 2 chiều một cách rõ ràng, minh bạch:
1. **Cho Vay / Cho Mượn (`LEND`)**: Khoản tiền bạn đưa cho người khác mượn (đây là tài sản nợ cần thu hồi, người khác đang nợ bạn).
2. **Đi Vay / Đi Mượn (`BORROW`)**: Khoản tiền bạn vay mượn từ người khác (đây là nghĩa vụ công nợ phải trả, bạn đang nợ người khác).

Khi người dùng hỏi: *"Muốn quản lý khoản nợ thì dùng chức năng nào?"* -> Hãy hướng dẫn vào phân hệ **Sổ Nợ** (Tab 3, `activeTab === 'debts'`).

## 2. Các Trường Dữ Liệu Trong Một Khoản Nợ
- **Loại nợ (Debt Type)**: `LEND` (cho vay / cho mượn) hoặc `BORROW` (đi vay / mượn tiền).
- **Tên đối tác (Person Name)**: Tên người mượn hoặc người cho vay (ví dụ: "Nguyễn Văn A", "Công ty X").
- **Số tiền nợ (Amount)**: Số tiền giao ước bằng VNĐ (phải > 0).
- **Ngày hẹn trả (Due Date)**: Hạn định cam kết thanh toán (YYYY-MM-DD).
- **Trạng thái thanh toán (Is Settled)**:
  - `0`: Chưa thanh toán (khoản nợ đang mở).
  - `1`: Đã thanh toán / Đã tất toán (hoàn tất nghĩa vụ nợ).
- **Ví tiền liên kết (Wallet ID)**: Tùy chọn ví liên kết để tự động cộng/trừ tiền khi phát sinh hoặc khi quyết toán nợ.
- **Ghi chú (Note)**: Lý do vay hoặc thỏa thuận chi tiết.

## 3. Các Thao Tác Khả Dụng
- **Xem danh sách nợ**: Tổng nợ cần thu, tổng nợ phải trả, danh sách phân chia theo trạng thái (chưa thanh toán / đã thanh toán).
- **Thêm khoản nợ mới**: Chọn loại nợ (Cho vay hoặc Đi vay), nhập tên người, số tiền, ngày hẹn trả và ghi chú.
- **Chỉnh sửa khoản nợ**: Cập nhật số tiền, đối tác hoặc hạn trả khi có thay đổi.
- **Tất toán nợ / Quyết toán nợ (`/api/debts/{id}/settle`)**: Nhấn nút "Quyết Toán" khi người mượn đã trả tiền hoặc bạn đã trả xong nợ. Khoản nợ chuyển sang trạng thái đã thanh toán.
- **Xóa bản ghi nợ**: Xóa khoản nợ khi không còn nhu cầu lưu trữ.

## 4. Vị Trí Trên Giao Diện (UI Location)
- Tab **Sổ Nợ** (Tab 3, menu 'Sổ Nợ', `activeTab === 'debts'`).
- Có 2 tab nhỏ phân tách rõ: "Người Ta Nợ Mình" và "Mình Nợ Người Ta" cùng các thẻ tổng kết tổng nợ.

## 5. Ranh Giới Quyền Hạn
- **Khí Linh Nhỏ (Live Mode)**: Có quyền tra cứu (`get_debts`), tạo khoản nợ (`create_debt`), sửa nợ (`update_debt`), và quyết toán nợ (`settle_debt`) theo xác nhận của người dùng.
- **Khí Linh AI Lớn**: Có quyền **tra cứu sổ nợ chỉ đọc (Read-Only)**; **TUYỆT ĐỐI KHÔNG CÓ QUYỀN tạo, sửa, xóa hoặc quyết toán nợ**.
