# CÂU HỎI THƯỜNG GẶP (FAQ)

## 1. Hệ thống có những chức năng nào?
Càn Khôn Linh Thạch Các hỗ trợ toàn diện các phân hệ quản lý tài chính cá nhân mang phong cách tiên hiệp:
- **Tổng Quan (Dashboard)**: Theo dõi số dư tổng, thu chi tháng, tỷ lệ tiết kiệm, biểu đồ thu chi và cảnh báo hạn mức.
- **Túi Càn Khôn (Wallets)**: Quản lý đa ví không giới hạn (tiền mặt, nhiều tài khoản ngân hàng, ví điện tử, tiết kiệm) và chuyển tiền nguyên tử giữa các ví.
- **Giao Dịch (Transactions)**: Ghi chép chi tiêu và thu nhập, tìm kiếm, lọc, phân trang, tích hợp Linh Trận Định Kỳ và xuất file Excel/CSV.
- **Danh Mục (Categories)**: Phân loại khoản chi và thu với biểu tượng icon và màu sắc sinh động.
- **Hạn Mức / Ngân Sách (Budgets)**: Đặt trần chi tiêu theo tháng cho từng danh mục và theo dõi tiến độ cảnh báo vượt ngưỡng.
- **Sổ Nợ (Debts)**: Quản lý cho vay (LEND) và đi vay (BORROW), hạn trả nợ và quyết toán công nợ.
- **Mục Tiêu Tiết Kiệm (Saving Goals)**: Lập mục tiêu tích lũy, nạp/rút tiền tích lũy và theo dõi tiến độ đạt 100%.
- **Giao Dịch Định Kỳ (Recurring)**: Tự động hóa các khoản chi phí lặp lại hàng tuần hoặc hàng tháng.
- **Tiên Trí Khám Hóa Đơn (Linh Nhãn OCR)**: Trí tuệ nhân tạo Gemini Vision tự động đọc hóa đơn/biên lai và chuyển thành giao dịch.
- **Thống Kê & Báo Cáo (Reports)**: Biểu đồ tròn cơ cấu danh mục, so sánh 2 tháng, xu hướng 6 tháng và xuất dữ liệu ra Excel/CSV.
- **Khai Thị Tiết Kiệm (Saving Tips)**: AI phân tích chi tiêu tháng và tư vấn 5 lời khuyên tài chính theo quy tắc 50/30/20.
- **Bản Mệnh Hồn Đăng & Bảo Mật**: Xác thực JWT, khôi phục mật khẩu qua câu trả lời bí mật và OTP 6 ký tự.
- **Khí Linh AI Lớn & Khí Linh Nhỏ**: Trợ lý tri thức hệ thống (Knowledge RAG) và Trợ lý giọng nói thực thi hành động (Live System Mode).

## 2. Ta có thể quản lý nhiều tài khoản ngân hàng không?
**Hoàn toàn có thể**. Hệ thống Càn Khôn Linh Thạch Các cho phép đạo hữu tạo và quản lý **nhiều tài khoản ngân hàng không giới hạn** trong phân hệ Túi Càn Khôn (Tab 5).
Đạo hữu có thể tạo riêng biệt từng tài khoản như Vietcombank, Techcombank, MB Bank, BIDV, VPBank, ACB... Mỗi tài khoản ngân hàng có tên riêng, số dư ban đầu độc lập, lịch sử biến động thu/chi riêng và có thể chuyển tiền qua lại lẫn nhau an toàn.

## 3. Chuyển tiền giữa hai ví hoạt động thế nào?
Khi chuyển tiền giữa hai ví trong Túi Càn Khôn:
1. Đạo hữu chọn Ví Nguồn (ví trừ tiền), Ví Đích (ví cộng tiền) và nhập số tiền cần chuyển.
2. Hệ thống kiểm tra số dư ví nguồn có đủ tiền không.
3. Thực hiện giao dịch nguyên tử (Atomic Database Transaction): Số dư ví nguồn lập tức bị trừ và số dư ví đích lập tức được cộng thêm cùng một lúc.
4. Tự động sinh 2 bản ghi lịch sử tương ứng mang danh mục "Chuyển Khoản" (một khoản chi ở ví nguồn và một khoản thu ở ví đích) để lưu vết lịch sử minh bạch. Tổng tài sản không thay đổi.

## 4. Muốn quản lý khoản nợ thì dùng chức năng nào?
Để quản lý các khoản nợ, đạo hữu hãy sử dụng phân hệ **Sổ Nợ** (Tab 3, `activeTab === 'debts'`).
Sổ Nợ chia làm 2 mục rõ ràng:
- **Cho Vay (LEND)**: Ghi chép các khoản tiền người khác mượn của bạn (nợ cần thu).
- **Đi Vay (BORROW)**: Ghi chép các khoản tiền bạn mượn của người khác (nghĩa vụ nợ phải trả).
Khi khoản nợ đã hoàn trả xong, đạo hữu bấm nút **"Quyết Toán"** để đánh dấu đã thanh toán thành công.

## 5. Mục tiêu tiết kiệm hoạt động ra sao?
Mục Tiêu Tiết Kiệm (Tab 4, `activeTab === 'goals'`) hoạt động theo nguyên lý:
1. **Thiết lập mục tiêu**: Nhập tên mục tiêu (mua xe, mua laptop, quỹ khẩn cấp...), số tiền cần đạt và ngày đến hạn.
2. **Nạp tiền tích lũy (Deposit)**: Khi có tiền dư dả, bấm "Nạp Tiền" để trích tiền từ ví vào quỹ mục tiêu. Số dư ví giảm và số tiền tích lũy tăng lên.
3. **Theo dõi tiến độ**: Thanh tiến độ hiển thị trực quan tỷ lệ % đã đạt được.
4. **Rút tiền (Withdraw)**: Khi hoàn thành hoặc có việc đột xuất, có thể rút tiền từ mục tiêu về lại ví của mình.

## 6. Giao dịch định kỳ hoạt động thế nào?
Giao dịch định kỳ (Linh Trận Định Kỳ trong Tab 2 Giao Dịch) hoạt động tự động:
1. Đạo hữu tạo lịch định kỳ với số tiền, ví, danh mục, tần suất (`weekly` - hàng tuần hoặc `monthly` - hàng tháng) và ngày chạy kế tiếp (`next_run_date`).
2. Khi đến ngày hẹn (`next_run_date`), hệ thống tự động sinh một bản ghi giao dịch thực tế vào sổ sách, cập nhật số dư ví và dời ngày hẹn sang kỳ kế tiếp.
3. Đạo hữu có thể bật/tắt (active/inactive) lịch định kỳ bất cứ lúc nào.

## 7. Quét hóa đơn bằng AI ra sao?
Tại Tab 7 (Linh Nhãn OCR):
1. Đạo hữu tải lên hoặc chụp ảnh hóa đơn mua sắm (siêu thị, quán ăn, cà phê...).
2. Trí tuệ nhân tạo Gemini Vision tự động đọc và bóc tách: Tên cửa hàng, ngày mua, tổng số tiền và danh sách các món đồ chi tiết.
3. Đạo hữu kiểm tra lại thông tin, chọn chiếc ví đã thanh toán và bấm **"Lưu Thành Giao Dịch"** để hệ thống tự động ghi nhận vào sổ thu chi.

## 8. Khí Linh Lớn khác Khí Linh Nhỏ thế nào?
- **Khí Linh AI Lớn (Desktop Chat - Tab 10)**: Là **Trợ lý Tri thức (Knowledge Assistant)**. Chuyên giải đáp câu hỏi, hướng dẫn sử dụng toàn hệ thống, tra cứu dữ liệu cá nhân chỉ đọc (Read-Only). **TUYỆT ĐỐI KHÔNG CÓ QUYỀN** thực hiện hành động tạo, sửa, xóa dữ liệu tài chính (No mutation).
- **Khí Linh Nhỏ (Live System Mode)**: Là **Đại lý Thực thi (Action Agent)** kích hoạt từ nút nổi góc phải hoặc khẩu quyết "Hệ thống". Hỗ trợ đàm thoại giọng nói liên tục, chống chen ngang và có quyền tạo ví, ghi chép thu chi, chuyển tiền sau khi được đạo hữu nói "Xác nhận".

## 9. Khí Linh Lớn có được tự thêm ví không?
**Tuyệt đối KHÔNG**. Khí Linh AI Lớn chỉ hoạt động ở chế độ Tra cứu Tri thức (Knowledge Mode). Hệ thống đã áp dụng cơ chế bảo vệ cứng ở cấp độ mã nguồn (Code-level Tool Permission) để từ chối mọi yêu cầu thay đổi dữ liệu của AI Lớn (`PERMISSION_DENIED`).
Nếu muốn tạo ví bằng AI, đạo hữu hãy triệu hồi Khí Linh Nhỏ (Live System Mode) bằng cách bấm nút nổi góc dưới phải hoặc nói khẩu quyết "Hệ thống".

## 10. Hệ thống có giao dịch cổ phiếu tự động không?
Hiện tại, Càn Khôn Linh Thạch Các **CHƯA hỗ trợ** tính năng giao dịch chứng khoán hay cổ phiếu tự động. Hệ thống hiện tập trung tối ưu cho việc quản lý tài chính cá nhân toàn diện (thu chi, hạn mức ngân sách, sổ nợ, mục tiêu tiết kiệm, hóa đơn OCR và đa ví tài sản).

## 11. Hệ thống có ví Bitcoin không?
Hiện tại, Càn Khôn Linh Thạch Các **CHƯA hỗ trợ** tích hợp ví tiền mã hóa (crypto), bitcoin, blockchain hay Web3. Hệ thống hiện hỗ trợ các nguồn tiền truyền thống (tiền mặt, nhiều tài khoản ngân hàng, ví điện tử Momo/ZaloPay và sổ tiết kiệm).

## 12. RAG là gì?
- **Về mặt khái niệm chung trong công nghệ AI**: RAG (Retrieval-Augmented Generation) là kiến trúc kết hợp giữa việc truy xuất (Retrieval) thông tin chính xác từ một cơ sở tri thức bên ngoài và việc dùng mô hình ngôn ngữ lớn (LLM) để sinh câu trả lời (Generation), giúp câu trả lời luôn có căn cứ xác thực, hạn chế tối đa việc bịa đặt (hallucination).
- **Trong hệ thống Càn Khôn Linh Thạch Các**: Khí Linh AI Lớn sử dụng công nghệ RAG để đối soát trực tiếp câu hỏi của đạo hữu với kho tài liệu năng lực hệ thống (`Capability Inventory` và `docs/`), đảm bảo mọi câu trả lời về tính năng, quy trình và bảo mật đều bám sát 100% mã nguồn thực tế của hệ sinh thái Càn Khôn.
