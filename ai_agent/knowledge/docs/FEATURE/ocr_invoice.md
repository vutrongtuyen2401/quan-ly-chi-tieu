# TIÊN TRÍ KHÁM HÓA ĐƠN (LINH NHÃN OCR)

## 1. Mục Đích & Khái Niệm
Tiên Trí Khám Hóa Đơn (Linh Nhãn OCR) là công nghệ trí tuệ nhân tạo thị giác đa phương thức (Multimodal AI Vision) được tích hợp trực tiếp trong Càn Khôn Linh Thạch Các.
Tính năng này giúp người dùng quét ảnh hóa đơn thanh toán, biên lai siêu thị, phiếu thu nhà hàng... và tự động chuyển hóa thành giao dịch tài chính có cấu trúc chuẩn mà không cần gõ tay thủ công.

## 2. Quy Trình Hoạt Động (OCR Workflow)
1. **Tải lên chứng từ**: Người dùng kéo thả hoặc chọn tệp ảnh hóa đơn (hỗ trợ JPG, PNG, JPEG, WebP, HEIC) tại giao diện Tab 7 (Linh Nhãn OCR).
2. **AI Thần Thức Quét**:
   - Backend sử dụng mô hình Google Gemini Vision để phân tích nội dung hình ảnh hóa đơn.
   - Trích xuất tự động và kiểm thực schema nghiêm ngặt:
     - `store_name`: Tên cửa hàng, siêu thị, nhà hàng (ví dụ: "WinMart+", "Highlands Coffee", "Nhà sách Fahasa").
     - `date`: Ngày xuất hóa đơn (chuẩn hóa `YYYY-MM-DD`).
     - `total_amount`: Tổng số tiền thanh toán cuối cùng bằng số.
     - `category_name`: Tự động nhận diện và gán danh mục phù hợp (Ăn Uống, Mua Sắm, Di Chuyển...).
     - `items`: Danh sách chi tiết từng món đồ (tên sản phẩm, số lượng, đơn giá).
3. **Xem trước & Chỉnh sửa**: Người dùng xem lại bảng danh sách sản phẩm và các trường thông tin bóc tách. Có thể chỉnh sửa trực tiếp số tiền, ngày hoặc chọn ví thanh toán.
4. **Lưu thành giao dịch**: Nhấn nút **"Lưu Thành Giao Dịch"**, hệ thống lập tức tạo bản ghi giao dịch mới trong Tab 2 (Giao Dịch), trừ số dư ví tương ứng và cập nhật tiến độ hạn mức ngân sách.

## 3. Vị Trí Trên Giao Diện (UI Location)
- Tab **Linh Nhãn OCR** (Tab 7, menu 'Linh Nhãn OCR', `activeTab === 'ocr'`).
- Hỗ trợ xem lại lịch sử các lần quét hóa đơn trước đó (`invoice_ocr_logs`).

## 4. Giới Hạn & Kiểm Thực An Toàn
- Dung lượng tối đa: Giới hạn 10MB mỗi ảnh tải lên (chống cạn kiệt bộ nhớ máy chủ).
- Kiểm thực ngữ nghĩa: Từ chối ảnh phong cảnh, ảnh chân dung, ảnh rác không phải chứng từ thanh toán hợp lệ.
- Cần ảnh chụp rõ ràng, không bị mờ nhòe hoặc che khuất phần tổng tiền.

## 5. Ranh Giới Quyền Hạn
- **Khí Linh AI Lớn**: Có quyền giải thích chi tiết quy trình quét hóa đơn và hướng dẫn người dùng thao tác; **tuyệt đối KHÔNG có quyền tự tải ảnh hoặc tự lưu giao dịch từ hóa đơn**. Thao tác này thực hiện trực tiếp trên giao diện Tab 7.
