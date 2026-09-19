# HƯỚNG DẪN: CÁCH QUẢN LÝ VÀ TẤT TOÁN KHOẢN NỢ

## 1. Mục Đích
Hướng dẫn đạo hữu cách ghi chép, theo dõi và tất toán các khoản nợ vay mượn trong Càn Khôn Linh Thạch Các:
- Quản lý các khoản bạn cho bạn bè, người thân vay mượn (Khoản nợ cần thu hồi).
- Quản lý các khoản bạn đi vay từ người khác hoặc tổ chức tín dụng (Khoản nợ phải trả).

## 2. Cách Tạo Khoản Nợ Mới Trên Giao Diện
1. **Bước 1**: Nhấp chọn Tab **Sổ Nợ** (Tab 3, menu 'Sổ Nợ', `activeTab === 'debts'`).
2. **Bước 2**: Nhấp vào nút **"+ Thêm Khoản Nợ"**.
3. **Bước 3**: Điền thông tin vào biểu mẫu:
   - **Loại nợ**: Chọn **"Cho Vay"** (nếu người khác mượn tiền bạn) hoặc **"Đi Vay"** (nếu bạn mượn tiền người khác).
   - **Tên đối tác**: Tên người vay hoặc người cho vay (ví dụ: "Anh Nam", "Chị Mai").
   - **Số tiền**: Nhập số tiền nợ (VNĐ).
   - **Ngày hẹn trả**: Chọn ngày cam kết hoàn trả tiền.
   - **Ghi chú**: (Tùy chọn) Ghi lý do mượn tiền.
4. **Bước 4**: Nhấn **"Lưu Khoản Nợ"**. Khoản nợ xuất hiện ngay trong danh sách theo dõi.

## 3. Cách Tất Toán / Quyết Toán Khoản Nợ Khi Đã Hoàn Thành
1. Khi đối tác trả tiền cho bạn, hoặc bạn đã trả nợ xong cho đối tác:
2. Vào Tab **Sổ Nợ (Tab 3)**.
3. Tìm đến dòng tên người đó trong danh sách nợ đang mở (chưa thanh toán).
4. Nhấn vào nút **"Quyết Toán"** (hoặc Tất Toán).
5. Hệ thống cập nhật trạng thái khoản nợ thành **"Đã Thanh Toán"** (`is_settled = 1`), nghĩa vụ nợ được hoàn tất.

## 4. Cách Thực Hiện Qua Khí Linh Nhỏ
- Tạo nợ: Mở Khí Linh nhỏ và nói *"Cho anh Nam mượn 3 triệu hẹn ngày 30"* -> Nói *"Xác nhận"*.
- Quyết toán nợ: Nói *"Tất toán khoản nợ của anh Nam"* -> Nói *"Xác nhận"*.

## 5. Lưu Ý Về Khí Linh AI Lớn
- Khí Linh AI Lớn (Tab 10) chỉ có quyền tra cứu tình trạng nợ (`get_debts`, `debt_status`); **KHÔNG CÓ QUYỀN** tự ý tạo hoặc quyết toán nợ thay người dùng.
