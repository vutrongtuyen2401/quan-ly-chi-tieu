# QUẢN LÝ GIAO DỊCH THU CHI (TRANSACTIONS)

## 1. Mục Đích & Khái Niệm
Phân hệ Giao Dịch là hạt nhân kế toán của Càn Khôn Linh Thạch Các, nơi ghi nhận chính xác từng dòng chảy tiền thạch ra vào tài sản của người dùng.
Mỗi giao dịch bao gồm 2 loại chính:
- **EXPENSE (Chi Tiêu)**: Các khoản xuất tiền chi trả cho sinh hoạt, mua sắm, ăn uống, hóa đơn, học phí... Khi ghi nhận khoản chi, số dư của ví được chọn sẽ tự động giảm trừ tương ứng.
- **INCOME (Thu Nhập)**: Các khoản nhập tiền như tiền lương, tiền thưởng, lợi nhuận kinh doanh, được tặng... Khi ghi nhận thu nhập, số dư của ví được chọn sẽ tự động tăng thêm.

## 2. Các Trường Thông Tin Trong Một Giao Dịch
1. **Số tiền (Amount)**: Giá trị bằng VNĐ (phải lớn hơn 0).
2. **Loại giao dịch (Type)**: `EXPENSE` (Chi Tiêu) hoặc `INCOME` (Thu Nhập).
3. **Danh mục (Category)**: Danh mục phân loại gắn liền (Ăn Uống, Nhà Cửa, Di Chuyển, Giải Trí...).
4. **Túi tiền / Ví (Wallet)**: Ví tiền thực hiện giao dịch (Tiền Mặt, Momo, Ngân Hàng...).
5. **Ngày giao dịch (Date)**: Định dạng YYYY-MM-DD (mặc định là ngày hiện tại).
6. **Ghi chú (Note)**: Nội dung chi tiết của khoản thu/chi (ví dụ: "Ăn phở bò sáng", "Tiền điện tháng 9").

## 3. Các Thao Tác Khả Dụng
- **Thêm giao dịch mới**: Điền form trên giao diện hoặc ra lệnh bằng giọng nói qua Khí Linh nhỏ.
- **Chỉnh sửa giao dịch**: Điều chỉnh lại số tiền, danh mục, ví hoặc ngày. Hệ thống tự động tính toán chênh lệch để cập nhật lại số dư ví chính xác.
- **Xóa giao dịch**: Xóa khoản ghi nhận nhầm. Hệ thống tự động hoàn nguyên (rollback) số dư ví: nếu xóa khoản chi thì cộng lại tiền vào ví, nếu xóa khoản thu thì trừ lại tiền khỏi ví.
- **Tìm kiếm & Bộ lọc**: Tìm kiếm nhanh theo từ khóa ghi chú, lọc theo khoảng thời gian (tháng này, tháng trước), lọc theo danh mục cụ thể và lọc theo từng ví.
- **Phân trang**: Danh sách phân trang mượt mà giúp quản lý hàng nghìn giao dịch mà không làm chậm hệ thống.
- **Linh Trận Định Kỳ**: Bấm nút **🔄 Linh Trận Định Kỳ** ngay trên thanh công cụ để mở giao diện quản lý các khoản chi tiêu/thu nhập tự động lặp lại theo tuần hoặc theo tháng.
- **Xuất dữ liệu sao kê (Export)**:
  - Bấm nút **📥 Xuất Excel** để tải về tệp `.xlsx` đầy đủ bảng tính, ngày, loại thu/chi, số tiền, danh mục, ví và ghi chú.
  - Bấm nút **📄 Xuất CSV** để xuất tệp dữ liệu phẳng chuẩn UTF-8 có BOM tương thích Excel tiếng Việt.

## 4. Vị Trí Trên Giao Diện (UI Location)
- Tab **Giao Dịch** (Tab 2, `activeTab === 'transactions'`).
- Bấm nút **+ Ghi Nhận Thu Chi** để mở modal biểu mẫu nhập liệu.
- Các nút tiện ích: **🔄 Linh Trận Định Kỳ**, **📥 Xuất Excel**, **📄 Xuất CSV** nằm ngay trên đầu danh sách giao dịch.

## 5. Ranh Giới Quyền Hạn
- **Khí Linh Nhỏ (Live Mode)**: Có quyền ghi nhận chi tiêu/thu nhập (`create_expense`, `create_income`), xóa (`delete_transaction`) và tìm kiếm giao dịch sau khi người dùng xác nhận.
- **Khí Linh AI Lớn**: Có quyền tìm kiếm và thống kê giao dịch (Read-Only qua `get_recent_transactions`, `transaction_search`). **TUYỆT ĐỐI KHÔNG CÓ QUYỀN thêm, sửa hay xóa giao dịch**.
