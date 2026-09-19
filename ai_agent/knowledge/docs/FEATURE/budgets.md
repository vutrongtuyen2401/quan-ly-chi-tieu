# HẠN MỨC & NGÂN SÁCH (BUDGETS)

## 1. Mục Đích & Khái Niệm
Hạn Mức (Ngân Sách) là công cụ kiểm soát kỷ luật tài chính trong Càn Khôn Linh Thạch Các.
Tính năng này cho phép đạo hữu đặt ra một mức trần chi tiêu tối đa trong một tháng cụ thể cho từng danh mục chi tiêu (hoặc cho toàn bộ chi tiêu chung), nhằm ngăn chặn việc vung tay quá trán và duy trì dòng tiền lành mạnh.

## 2. Cơ Chế Hoạt Động Của Hạn Mức
1. **Thiết lập hạn mức**:
   - Chọn danh mục chi tiêu (ví dụ: "Ăn Uống", "Mua Sắm", "Giải Trí", "Di Chuyển").
   - Nhập số tiền tối đa được phép chi trong tháng (ví dụ: 4.000.000 VNĐ cho Ăn Uống).
   - Chu kỳ áp dụng: Tính theo tháng (định dạng `YYYY-MM`, ví dụ `2026-09`).
2. **Theo dõi tiến độ thời gian thực**:
   - Khi có bất kỳ giao dịch chi tiêu (`EXPENSE`) nào phát sinh thuộc danh mục đó trong tháng, hệ thống tự động cộng dồn và tính toán tỷ lệ phần trăm đã sử dụng:
     $$\text{Tỷ Lệ Đã Chi (\%)} = \frac{\text{Tổng Đã Chi Trong Tháng}}{\text{Hạn Mức Đặt Ra}} \times 100\%$$
   - Hiển thị số tiền còn lại được phép chi tiêu trước khi chạm trần.
3. **Mức độ cảnh báo trực quan**:
   - **Xanh lá (< 70%)**: Mức an toàn, chi tiêu trong tầm kiểm soát.
   - **Vàng cam (70% - 99%)**: Cảnh báo sắp chạm ngưỡng ngân sách.
   - **Đỏ rực (>= 100%)**: Báo động đã bội chi / vượt quá hạn mức cho phép. Thẻ cảnh báo sẽ xuất hiện nổi bật tại màn hình Tổng Quan (Dashboard).

## 3. Các Thao Tác Khả Dụng
- Xem bảng trạng thái hạn mức các danh mục trong tháng hiện tại hoặc các tháng trước.
- Đặt hạn mức mới cho một danh mục.
- Điều chỉnh / sửa đổi số tiền hạn mức khi kế hoạch chi tiêu thay đổi.
- Hủy bỏ / xóa hạn mức đã đặt.

## 4. Vị Trí Trên Giao Diện (UI Location)
- Tab **Hạn Mức** (Tab 8, `activeTab === 'budgets'`).
- Ngoài ra, các cảnh báo vượt hạn mức tự động xuất hiện ở phần đầu trang **Tổng Quan** (Tab 1, `activeTab === 'dashboard'`).

## 5. Ranh Giới Quyền Hạn
- **Khí Linh Nhỏ (Live Mode)**: Có quyền tạo, sửa, xóa hạn mức sau khi người dùng xác nhận lệnh.
- **Khí Linh AI Lớn**: Có quyền **tra cứu trạng thái hạn mức (`budget_status`, `get_budget_status`)** của người dùng và giải thích cơ chế ngân sách; **tuyệt đối KHÔNG có quyền tạo, sửa hoặc xóa hạn mức**.
