# KIẾN TRÚC KHÍ LINH AI: PHÂN BIỆT KHÍ LINH LỚN & KHÍ LINH NHỎ

## 1. Triết Lý Thiết Kế 2 Trợ Lý Khí Linh
Trong hệ sinh thái Càn Khôn Linh Thạch Các, Khí Linh AI được phân định thành 2 thực thể với vai trò và quyền hạn hoàn toàn tách biệt:

| Đặc Điểm | Khí Linh AI Lớn (Desktop Chat) | Khí Linh Nhỏ (Live System Mode) |
| :--- | :--- | :--- |
| **Vai trò (Role)** | **System Knowledge Assistant** (Trợ lý Tri Thức) | **Action / Execution Agent** (Đại lý Thực Thi) |
| **Vị trí** | Menu / Tab "Khí Linh AI" (Tab 10, màn hình chat lớn, activeTab === 'chat') | Nút nổi góc dưới phải màn hình / Khẩu quyết "Hệ thống" |
| **Phương thức** | Nhập văn bản (Text Chat), lưu lịch sử hội thoại | Giọng nói liên tục (Continuous Voice STT/TTS) |
| **Quyền thay đổi (Mutation)**| **TUYỆT ĐỐI KHÔNG (No Mutation Permission)** | **ĐẦY ĐỦ QUYỀN (Full Action Permission)** |
| **Quyền đọc (Read)** | Được đọc dữ liệu cá nhân chỉ đọc (Read-Only) | Được đọc toàn bộ dữ liệu chỉ đọc |
| **Nhiệm vụ chính** | Giải đáp tri thức hệ thống, tra cứu RAG, hướng dẫn sử dụng, phân tích tài chính chỉ đọc | Tiếp nhận lệnh tài chính, yêu cầu xác nhận, thực thi ghi chép, tạo ví, chuyển tiền |

---

## 2. Khí Linh AI Lớn: System Knowledge Assistant
- **Bản chất**: Hoạt động ở chế độ `AgentMode.KNOWLEDGE`.
- **Nguồn tri thức**: Được trang bị công nghệ **RAG (Retrieval-Augmented Generation)** đối soát trực tiếp với kho dữ liệu năng lực hệ thống (`Capability Inventory` và `Knowledge Documents`).
- **Năng lực**:
  1. Hiểu và giải thích toàn diện mọi chức năng của Càn Khôn Linh Thạch Các.
  2. Cung cấp hướng dẫn sử dụng từng bước cho người dùng.
  3. Giải thích các luồng công việc (workflows), quan hệ giữa các tính năng.
  4. Trả lời các câu hỏi về cơ chế bảo mật, phân quyền và kiến trúc hệ thống.
  5. Kết hợp tri thức hệ thống với việc tra cứu dữ liệu cá nhân chỉ đọc (ví dụ: giải thích cách dùng hạn mức và xem hạn mức hiện tại của người dùng).
  6. **Cơ chế chống bịa đặt (Anti-hallucination)**: Khi người dùng hỏi về các tính năng không có bằng chứng trong kho tri thức (như giao dịch chứng khoán tự động, tiền ảo), AI lớn sẽ nói rõ hệ thống chưa hỗ trợ thay vì tự suy diễn.
- **Ranh giới an toàn**:
  - Không có quyền gọi bất kỳ công cụ thay đổi dữ liệu nào (`create_expense`, `create_wallet`, `transfer_money`, `create_budget`, `create_debt`, v.v.).
  - Ranh giới này được bảo vệ cứng ở tầng mã nguồn (Code-level Tool Permission), ngăn chặn triệt để mọi hành vi mutation dù model có cố ý gọi tool.

---

## 3. Khí Linh Nhỏ: Action / Execution Agent
- **Bản chất**: Hoạt động ở chế độ `AgentMode.ACTION`.
- **Giao diện Live System Mode**: Chiếm ~65% giữa màn hình với nền tối mờ (Dark Overlay), phong cách bảng ngọc tiên hiệp tím huyền ảo.
- **Năng lực**:
  1. Kích hoạt từ mọi trang web thông qua nút nổi hoặc khẩu quyết **"Hệ thống"**.
  2. Hội thoại giọng nói liên tục (Continuous Voice Loop) không cần nhấn micro từng câu.
  3. **Chống chen ngang (Interrupt Protection)**: Khi AI đang phát âm giọng đọc (TTS), mọi lời nói chen ngang của người dùng đều bị bỏ qua; chỉ khi AI nói xong mới lắng nghe câu tiếp theo.
  4. Tiếp nhận lệnh biến động tài chính tự nhiên: *"Thêm ví Momo 20 triệu"*, *"Chi 50 nghìn ăn sáng"*, *"Chuyển 2 triệu từ ví A sang ví B"*.
  5. **Xác nhận đàm thoại (Conversational Confirmation)**: Hiển thị thẻ tóm tắt chi tiết thao tác và chờ người dùng nói *"Xác nhận"* hoặc *"Hủy"* trước khi thực thi vào DB.
  6. Tự động dọn sạch nội dung hiển thị sau 10 giây rảnh tay nhưng phiên lắng nghe vẫn tiếp tục duy trì.
