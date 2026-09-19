# CÁC GIỚI HẠN & TÍNH NĂNG CHƯA HỖ TRỢ (LIMITATIONS & UNSUPPORTED)

## 1. Giới Hạn Của Khí Linh AI Lớn
- **Không có quyền thay đổi dữ liệu (No Mutation Permission)**:
  - Khí Linh AI Lớn (tại tab Khí Linh AI) là Trợ lý Tri thức (Knowledge Assistant).
  - Không được phép tự ý tạo giao dịch, xóa giao dịch, thêm ví, sửa ví, tạo ngân sách, xóa ngân sách, tạo nợ hay chuyển tiền.
  - Khi người dùng yêu cầu hành động tài chính, Khí Linh AI Lớn sẽ từ chối và hướng dẫn người dùng tự thực hiện trên giao diện hoặc triệu hồi Khí Linh nhỏ (Live System Mode).
- **Chỉ truy cập dữ liệu cá nhân ở chế độ chỉ đọc (Read-Only)**:
  - Khí Linh AI Lớn chỉ có thể tra cứu số dư ví, danh sách giao dịch, tiến độ mục tiêu, trạng thái ngân sách và công nợ để trả lời thắc mắc của người dùng.

## 2. Các Tính Năng Hệ Thống Chưa Hỗ Trợ (Unsupported Features)
Để đảm bảo tính trung thực và ngăn ngừa ảo giác (Anti-hallucination), hệ thống xác định rõ các tính năng hiện **CHƯA HỖ TRỢ**:

1. **Giao dịch chứng khoán / cổ phiếu tự động**:
   - Hệ thống Càn Khôn Linh Thạch Các hiện tại **CHƯA hỗ trợ** kết nối các sàn chứng khoán (HOSE, HNX), chưa hỗ trợ đặt lệnh mua bán cổ phiếu, trái phiếu hay phái sinh tự động.
2. **Ví tiền điện tử / Blockchain / Crypto**:
   - Hệ thống hiện **CHƯA hỗ trợ** kết nối ví Web3 (Metamask, Trust Wallet) hay các đồng tiền mã hóa (Bitcoin, Ethereum, USDT).
3. **Đầu tư vàng / Ngoại hối tự động (Forex)**:
   - Hệ thống hiện **CHƯA hỗ trợ** tích hợp giao dịch vàng trực tuyến hay giao dịch ngoại tệ thời gian thực.
4. **Quét văn bản không phải hóa đơn (Non-receipt OCR)**:
   - Tiên Trí Khám Hóa Đơn chỉ xử lý biên lai, hóa đơn mua bán thanh toán hợp lệ; không hỗ trợ dịch tài liệu hay nhận diện văn bản pháp lý chung.

## 3. Quy Tắc Ứng Xử Của AI Khi Gặp Câu Hỏi Ngoài Phạm Vi
- Khi người dùng hỏi: *"Hệ thống có giao dịch cổ phiếu tự động không?"* hoặc *"Hệ thống có ví crypto không?"*:
  - Khí Linh AI Lớn bắt buộc phải trả lời: **Hệ thống chưa hỗ trợ tính năng này**.
  - Tuyệt đối không được bịa đặt rằng hệ thống đã có tính năng hoặc đang kết nối với sàn giao dịch.
