# HƯỚNG DẪN: CÁCH THIẾT LẬP GIAO DỊCH ĐỊNH KỲ (LINH TRẬN ĐỊNH KỲ)

## 1. Mục Đích
Hướng dẫn đạo hữu cài đặt tự động hóa ghi chép cho các khoản tiền cố định phát sinh lặp đi lặp lại hàng tuần hoặc hàng tháng:
- Tiền thuê trọ/nhà, tiền điện nước, internet, truyền hình.
- Tiền học phí, tiền đóng bảo hiểm, tiền trả góp.
- Tiền lương hoặc tiền chu cấp nhận đều đặn.

## 2. Các Bước Thực Hiện Trên Giao Diện
1. **Bước 1**: Nhấp chọn Tab **Giao Dịch** (Tab 2, `activeTab === 'transactions'`).
2. **Bước 2**: Nhấp vào nút **"🔄 Linh Trận Định Kỳ"** ở phía trên danh sách giao dịch.
3. **Bước 3**: Điền thông tin vào biểu mẫu khởi tạo:
   - **Loại giao dịch**: Chọn `Chi Tiêu` (xuất tiền) hoặc `Thu Nhập` (nhận tiền).
   - **Số tiền**: Nhập số tiền định kỳ (ví dụ: 3.500.000 VNĐ).
   - **Túi Càn Khôn**: Chọn chiếc ví sẽ tự động thanh toán hoặc nhận tiền (ví dụ: MB Bank).
   - **Danh Mục**: Chọn danh mục tương ứng (Nhà Cửa, Ăn Uống, Lương...).
   - **Tần suất**: Chọn `Hàng tuần` (lặp mỗi 7 ngày) hoặc `Hàng tháng` (lặp mỗi 1 tháng).
   - **Ngày kích hoạt tiếp theo**: Chọn ngày đầu tiên bắt đầu chạy (định dạng YYYY-MM-DD).
   - **Ghi chú**: Điền mô tả (ví dụ: "Tiền thuê nhà tháng").
4. **Bước 4**: Nhấn nút **"✨ Khởi Tạo Linh Trận Định Kỳ"**.

## 3. Cơ Chế Tự Động Kích Hoạt
- Đến ngày hẹn (`next_run_date`), hệ thống sẽ tự động phát sinh một giao dịch chính thức vào sổ sách.
- Số dư ví được tự động cập nhật.
- Ngày hẹn kế tiếp sẽ tự động dời sang chu kỳ tiếp theo (sau 7 ngày hoặc sau 1 tháng).
- Người dùng có thể nhấn nút trạng thái để tạm dừng (inactive) hoặc kích hoạt lại (active) bất cứ lúc nào.

## 4. Lưu Ý Về Khí Linh AI Lớn
- Khí Linh AI Lớn (Tab 10) có thể giải thích cách thức hoạt động của giao dịch định kỳ; nhưng **KHÔNG CÓ QUYỀN** tự ý tạo, sửa hay xóa lịch định kỳ của người dùng.
