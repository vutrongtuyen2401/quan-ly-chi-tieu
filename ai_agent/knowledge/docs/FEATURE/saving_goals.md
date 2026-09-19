# MỤC TIÊU TIẾT KIỆM (SAVING GOALS)

## 1. Mục Đích & Khái Niệm
Mục Tiêu Tiết Kiệm là tính năng giúp đạo hữu tích lũy từng bước để đạt được các mục đích tài chính trung và dài hạn trong cuộc sống:
- Tậu pháp bảo mới (Laptop làm việc, điện thoại, máy tính bảng...).
- Tậu linh thú / phương tiện di chuyển (Xe máy, ô tô).
- Quỹ khẩn cấp (Dự phòng rủi ro 3 - 6 tháng sinh hoạt).
- Du lịch, tu nghiệp, học tập nâng cao cảnh giới.
- Mua nhà, đặt cọc căn hộ (Động phủ).

## 2. Cơ Chế Hoạt Động Của Mục Tiêu Tiết Kiệm
1. **Khởi tạo mục tiêu**:
   - Tên mục tiêu (Target Name): ví dụ "Mua Laptop Dell XPS", "Quỹ Dự Phòng 50 Triệu".
   - Số tiền cần đạt (Target Amount): ví dụ 30.000.000 VNĐ.
   - Ngày dự kiến hoàn thành (Target Date): ví dụ 2026-12-31.
   - Số tiền ban đầu (Current Amount): mặc định là 0 VNĐ.
2. **Nạp tiền tích lũy (Deposit)**:
   - Khi có khoản tiền dư thừa, người dùng nạp tiền vào mục tiêu tiết kiệm.
   - Chọn ví trích tiền (ví dụ ví Momo hoặc Tiền Mặt).
   - Nhập số tiền nạp (ví dụ 2.000.000 VNĐ).
   - Hệ thống tự động trừ số tiền này khỏi ví nguồn và cộng vào số tiền hiện có của mục tiêu tiết kiệm.
   - Thanh tiến độ (%) tự động tăng lên tương ứng.
3. **Rút tiền từ mục tiêu (Withdraw)**:
   - Khi mục tiêu hoàn thành hoặc khi có nhu cầu cần sử dụng tiền tích lũy, người dùng có thể rút tiền từ mục tiêu về lại một ví chỉ định.
   - Số tiền rút không được vượt quá số tiền hiện đang tích lũy trong mục tiêu đó.
4. **Theo dõi tiến độ hoàn thành**:
   - Tỷ lệ % hoàn thành được tính toán liên tục:
     $$\text{Tiến Độ (\%)} = \frac{\text{Số Tiền Đã Tích Lũy}}{\text{Số Tiền Mục Tiêu}} \times 100\%$$
   - Khi đạt 100%, mục tiêu được vinh danh hoàn tất.

## 3. Vị Trí Trên Giao Diện (UI Location)
- Tab **Mục Tiêu** (Tab 4, `activeTab === 'goals'`).
- Mỗi mục tiêu được thể hiện dưới dạng thẻ linh thạch trang trọng với thanh tiến độ phát sáng.

## 4. Ranh Giới Quyền Hạn
- **Khí Linh Nhỏ (Live Mode)**: Có quyền tra cứu (`get_saving_goals`, `saving_goal_status`), tạo mục tiêu (`create_saving_goal`), nạp tiền tích lũy (`saving_goal_deposit`), rút tiền (`saving_goal_withdraw`) khi có xác nhận.
- **Khí Linh AI Lớn**: Có quyền **tra cứu tiến độ mục tiêu tiết kiệm (Read-Only)**; **tuyệt đối KHÔNG có quyền tạo, sửa, xóa mục tiêu hoặc nạp/rút tiền tích lũy**.
