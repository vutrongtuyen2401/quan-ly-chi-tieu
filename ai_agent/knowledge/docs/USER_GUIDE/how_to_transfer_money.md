# HƯỚNG DẪN: CÁCH CHUYỂN TIỀN GIỮA HAI VÍ (LUÂN CHUYỂN LINH THẠCH)

## 1. Mục Đích
Chuyển tiền giữa hai ví được sử dụng khi đạo hữu cần luân chuyển tiền bạc giữa các tài khoản của chính mình:
- Rút tiền từ tài khoản ngân hàng (Vietcombank, MB Bank...) về ví tiền mặt để chi tiêu hàng ngày.
- Nạp tiền từ ngân hàng vào ví điện tử Momo hoặc ZaloPay.
- Trích tiền từ ví chi tiêu sang ví tích lũy hoặc sổ tiết kiệm.

## 2. Cách Thực Hiện Trên Giao Diện (UI)
1. **Bước 1**: Đăng nhập hệ thống Càn Khôn Linh Thạch Các.
2. **Bước 2**: Nhấp chọn Tab **Túi Càn Khôn** (Tab 5, `activeTab === 'wallets'`).
3. **Bước 3**: Nhấp vào nút **"🔄 Chuyển Tiền"** trên thanh công cụ.
4. **Bước 4**: Cửa sổ Chuyển Tiền xuất hiện, đạo hữu điền các thông tin:
   - **Từ Túi (Ví Nguồn)**: Chọn ví bị trừ tiền (ví dụ: MB Bank).
   - **Đến Túi (Ví Đích)**: Chọn ví được cộng tiền (ví dụ: Tiền Mặt). Hai ví này phải khác nhau.
   - **Số tiền**: Nhập số tiền cần chuyển (phải > 0 và <= số dư của ví nguồn).
   - **Ghi chú**: (Tùy chọn) Ghi lý do luân chuyển (ví dụ: "Rút tiền ATM tiêu tuần 3").
5. **Bước 5**: Nhấp nút **"Xác Nhận Chuyển Tiền"**.
6. **Bước 6**: Hệ thống thực hiện chuyển tiền nguyên tử:
   - Số dư ví nguồn lập tức bị trừ đúng số tiền chuyển.
   - Số dư ví đích lập tức được cộng thêm đúng số tiền chuyển.
   - Tự động ghi nhận 2 bản ghi lịch sử tương ứng vào Tab Giao Dịch: một giao dịch chi ở ví nguồn và một giao dịch thu ở ví đích cùng mang danh mục "Chuyển Khoản".
   - Tổng tài sản không thay đổi.

## 3. Cách Chuyển Tiền Bằng Giọng Nói Qua Khí Linh Nhỏ
1. Mở Khí Linh nhỏ (Live System Mode) bằng nút nổi góc dưới bên phải hoặc nói khẩu quyết **"Hệ thống"**.
2. Nói câu lệnh luân chuyển tự nhiên:
   > *"Chuyển 2 triệu từ MB Bank sang Tiền Mặt"* hoặc *"Chuyển 500 nghìn từ Vietcombank sang ví Momo"*.
3. Khí Linh nhỏ hiển thị thẻ xác nhận với đầy đủ ví nguồn, ví đích và số tiền.
4. Đạo hữu nói **"Xác nhận"**. Hệ thống sẽ gọi công cụ `transfer_money` và thực hiện luân chuyển ngay lập tức.

## 4. Lưu Ý Quan Trọng
- **Khí Linh AI Lớn (tại Tab 10)** là trợ lý tri thức, **KHÔNG CÓ QUYỀN** tự ý chuyển tiền của đạo hữu.
- Hệ thống chỉ cho phép chuyển tiền giữa các ví thuộc quyền sở hữu của chính đạo hữu.
