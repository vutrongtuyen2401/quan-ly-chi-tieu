# TRUYỀN ÂM CẦU VIỆN & DANH BẠ HỘ ĐẠO (LOW FUNDS SUPPORT)

## 1. Mục Đích & Khái Niệm
"Truyền Âm Cầu Viện" là cơ chế hỗ trợ khẩn cấp thông minh của Càn Khôn Linh Thạch Các khi ngân khố cá nhân của tu sĩ có dấu hiệu sắp cạn kiệt trước kỳ nhận trợ cấp/lương kế tiếp.
Tính năng này tự động đánh giá dòng tiền dựa trên tốc độ tiêu xài thực tế (`daily_burn_rate`), số dư khả dụng (`total_balance`) và số ngày còn lại tới kỳ trợ cấp (`days_left`), từ đó đưa ra cảnh báo sớm và cung cấp danh bạ người thân (phụ huynh, gia đình, đạo hữu bảo hộ) để tu sĩ kịp thời liên hệ xin cứu viện linh thạch.

## 2. Công Thức & Cơ Chế Đánh Giá
Hệ thống sử dụng các chỉ số tài chính xác thực từ cơ sở dữ liệu:
1. **Ngày nhận trợ cấp tiếp theo (`next_allowance_date`) và Số ngày còn lại (`days_left`)**:
   - Tu sĩ cài đặt ngày nhận chu cấp cố định hàng tháng (`allowance_day`, từ ngày 1 đến 28).
   - $days\_left = \text{số ngày từ hôm nay tới ngày nhận trợ cấp tiếp theo}$.
2. **Tốc độ tiêu tiền trung bình ngày (`daily_burn_rate`)**:
   - Tính từ tổng chi tiêu thực tế từ ngày nhận trợ cấp gần nhất đến hôm nay chia cho số ngày đã qua:
     $$\text{daily\_burn\_rate} = \frac{\text{Tổng chi tiêu}}{\text{Số ngày đã hoạt động}}$$
3. **Số ngày còn đủ tiêu (`runway_days`)**:
   - Thể hiện số dư hiện tại còn đủ duy trì chi tiêu trong bao lâu nếu giữ nguyên tốc độ tiêu:
     $$\text{runway\_days} = \left\lfloor \frac{\text{total\_balance}}{\text{daily\_burn\_rate}} \right\rfloor$$
4. **Dự phóng chi phí cần thiết (`projected_cost`)**:
     $$\text{projected\_cost} = \text{daily\_burn\_rate} \times \text{days\_left}$$
5. **Số tiền nên xin hỗ trợ (`suggested_amount`)**:
   - Nếu $total\_balance < projected\_cost$, hệ thống gợi ý khoản tiền cần xin thêm để bù đắp thâm hụt:
     $$\text{suggested\_amount} = \text{projected\_cost} - \text{total\_balance}$$
6. **Bốn phân cấp cảnh báo (`level`)**:
   - **`NO_DATA`**: Tu sĩ chưa tạo bất kỳ ví nào trong Túi Càn Khôn.
   - **`CRITICAL` (Đỏ - Cạn kiệt)**: $total\_balance \le 0$, hoặc $runway\_days \le 2$ (khi $days\_left > 2$), hoặc $total\_balance < 0.3 \times projected\_cost$.
   - **`WARNING` (Vàng - Hao hụt)**: $total\_balance \le low\_balance\_threshold$, hoặc $runway\_days < days\_left$, hoặc $total\_balance < projected\_cost$.
   - **`SAFE` (Xanh - An toàn)**: Số dư đảm bảo đủ tiêu đến kỳ tiếp theo và trên ngưỡng cảnh báo.

## 3. Danh Bạ Hộ Đạo & Thao Tác Nhanh
- **Danh Bạ Hộ Đạo**: Lưu trữ tối đa 10 liên hệ người thân (tên, nhãn quan hệ như Phụ Thân, Mẫu Thân, Huynh Đệ, số điện thoại VN chuẩn hóa 10 số, ghi chú, trạng thái kích hoạt).
- **Lời nhắn soạn sẵn**: Tự động chèn số tiền cần xin vào mẫu tin nhắn để tu sĩ gửi nhanh.
- **Hành động 1 chạm**: Trên banner cảnh báo tại màn hình Tổng Quan có các nút gọi trực tiếp (`tel:`), nhắn tin (`sms:`), sao chép số và sao chép lời nhắn.
- **Tính năng Để sau (Snooze)**: Tu sĩ có thể tạm ẩn cảnh báo trong ngày hôm nay. Nếu mức độ tăng từ WARNING lên CRITICAL thì cảnh báo sẽ tự động kích hoạt lại.

## 4. Vị Trí Trên Giao Diện (UI Location)
- **Banner cảnh báo (`LowFundsAlert`)**: Xuất hiện ở đầu trang **Tổng Quan** (Tab 1, `activeTab === 'dashboard'`) ngay trên các thẻ thống kê khi rơi vào trạng thái `WARNING` hoặc `CRITICAL`.
- **Quản lý danh bạ & Cài đặt (`SupportContactsCard`)**: Nằm trong modal **Hồ Sơ Tu Sĩ** > tab **Danh Bạ Hộ Đạo** (mở từ thanh tiêu đề hoặc bấm nút "Quản lý danh bạ").

## 5. Ranh Giới Quyền Hạn Của Khí Linh AI
- **Khí Linh AI Lớn & Nhỏ**:
  - Hỗ trợ công cụ **`low_funds_support` (READ)** để tra cứu mức độ cảnh báo, số dư, số ngày đủ tiêu, số tiền nên xin hỗ trợ và danh sách người thân.
  - **Tuyệt đối READ-ONLY**: Khí Linh AI KHÔNG tự ý thực hiện cuộc gọi, KHÔNG tự gửi tin nhắn SMS và KHÔNG tự ý thêm/sửa/xóa liên hệ hay thay đổi cài đặt người thân.
