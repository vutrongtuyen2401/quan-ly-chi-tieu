# HƯỚNG DẪN: CÁCH TẠO TÚI CÀN KHÔN (VÍ MỚI)

## 1. Cách Tạo Ví Thủ Công Trên Giao Diện (UI)
Để tạo một chiếc ví mới trong hệ thống Càn Khôn Linh Thạch Các, đạo hữu thực hiện theo các bước sau:

1. **Bước 1**: Đăng nhập vào hệ thống Càn Khôn Linh Thạch Các.
2. **Bước 2**: Trên thanh điều hướng trên cùng, nhấp chọn tab **"Túi Càn Khôn"** (Tab 5, `activeTab === 'wallets'`).
3. **Bước 3**: Tại màn hình Túi Càn Khôn, nhấp vào nút **"+ Thêm Ví Mới"**.
4. **Bước 4**: Một cửa sổ (modal) thiết lập ví sẽ xuất hiện, đạo hữu điền các thông tin:
   - **Tên ví**: Nhập tên ví dễ nhớ (ví dụ: `Momo`, `Vietcombank`, `Tiền Mặt`, `Techcombank`).
   - **Loại ví**: Chọn loại tương ứng (Tiền mặt, Ngân hàng, Ví điện tử, hoặc Tiết kiệm).
   - **Số dư ban đầu**: Nhập số tiền hiện có trong ví tại thời điểm khởi tạo (ví dụ: `5.000.000` VNĐ).
   - **Ghi chú**: (Tùy chọn) Điền mục đích sử dụng của ví.
5. **Bước 5**: Nhấp nút **"Lưu Ví"** / **"Xác Nhận"**.
6. **Bước 6**: Hệ thống sẽ hiển thị thông báo thành công và chiếc ví mới sẽ lập tức xuất hiện trong danh sách Túi Càn Khôn của đạo hữu, đồng thời số dư tổng trên màn hình Tổng Quan sẽ được cập nhật.

---

## 2. Cách Tạo Ví Bằng Giọng Nói Qua Khí Linh Nhỏ (Live System Mode)
Nếu muốn tạo ví nhanh bằng giọng nói thông qua Khí Linh nhỏ:
1. Nhấp vào biểu tượng Khí Linh nhỏ ở góc dưới bên phải màn hình hoặc đọc khẩu quyết **"Hệ thống"**.
2. Khi System Frame mở ra và chuyển sang trạng thái lắng nghe, đạo hữu nói:
   > *"Thêm một ví Momo 20 triệu"* hoặc *"Tạo ví Vietcombank số dư 15 triệu"*.
3. Khí Linh nhỏ sẽ phân tích câu nói và hiển thị thẻ **XÁC NHẬN THAO TÁC** trên System Frame.
4. Đạo hữu chỉ cần nói: **"Xác nhận"** (hoặc bấm nút Xác Nhận trên màn hình).
5. Khí Linh nhỏ sẽ gọi công cụ `create_wallet` và tạo ví thành công vào cơ sở dữ liệu.

---

## 3. Lưu Ý Về Khí Linh AI Lớn
- **Khí Linh AI Lớn (tại tab Khí Linh AI)** là trợ lý tri thức, **KHÔNG CÓ QUYỀN** tự động tạo ví cho đạo hữu.
- Nếu đạo hữu yêu cầu Khí Linh AI lớn tạo ví, nó sẽ từ chối và hướng dẫn đạo hữu thực hiện theo hướng dẫn trên hoặc triệu hồi Khí Linh nhỏ.
