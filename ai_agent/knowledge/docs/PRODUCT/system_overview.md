# TỔNG QUAN HỆ THỐNG CÀN KHÔN LINH THẠCH CÁC

## 1. Giới Thiệu Chung
Càn Khôn Linh Thạch Các là hệ sinh thái quản lý tài chính cá nhân toàn diện, kết hợp phong cách tu tiên (Xianxia) độc đáo với trí tuệ nhân tạo (AI Agent) hai tầng. Hệ thống giúp người dùng (ký chủ / đạo hữu) theo dõi tài sản, quản lý đa ví nguồn tiền, ghi nhận thu chi, kiểm soát ngân sách trần, tích lũy mục tiêu, đối soát công nợ và tự động hóa với sự bảo mật và kỷ luật tài chính cao.

## 2. Bản Đồ 11 Phân Hệ Giao Diện (UI Tabs)
Giao diện chính của hệ thống bao gồm 11 tab điều hướng theo đúng thứ tự:

1. **Tab 1: Tổng Quan (Dashboard, `activeTab === 'dashboard'`)**:
   Bức tranh toàn cảnh tài chính — tổng tài sản các ví, tổng thu nhập và chi tiêu trong tháng, mức tiết kiệm thuần, biểu đồ phân bổ chi tiêu, biểu đồ 6 tháng và cảnh báo danh mục vượt hạn mức.
2. **Tab 2: Giao Dịch (Transactions, `activeTab === 'transactions'`)**:
   Ghi nhận chi tiết từng khoản thu và chi; hỗ trợ tìm kiếm, lọc theo tháng/danh mục/ví; tích hợp **Linh Trận Định Kỳ** tự động sinh giao dịch lặp lại; và xuất sao kê lịch sử ra file **Excel (.xlsx)** hoặc **CSV**.
3. **Tab 3: Sổ Nợ (Debts, `activeTab === 'debts'`)**:
   Quản lý công nợ 2 chiều: **Cho Vay (LEND)** - người khác nợ mình, và **Đi Vay (BORROW)** - mình nợ người khác. Theo dõi thời hạn, ghi chú và thực hiện **Quyết Toán** khi hoàn thành nghĩa vụ nợ.
4. **Tab 4: Mục Tiêu (Saving Goals, `activeTab === 'goals'`)**:
   Lập kế hoạch tích lũy tài chính (mua laptop, mua xe, quỹ khẩn cấp, mua nhà); nạp tiền từ ví vào quỹ tích lũy và rút tiền khi hoàn thành; theo dõi tiến độ hoàn thành (%).
5. **Tab 5: Túi Càn Khôn (Wallets, `activeTab === 'wallets'`)**:
   Quản lý **đa nguồn tiền không giới hạn** (Tiền mặt, nhiều tài khoản ngân hàng khác nhau như Vietcombank, Techcombank, MB Bank, VPBank, ACB, BIDV..., Ví điện tử Momo, ZaloPay, Thẻ tín dụng, Tài khoản đầu tư, Sổ tiết kiệm). Hỗ trợ tạo ví mới, sửa ví và **Chuyển Tiền nguyên tử 2 chiều** giữa các ví.
6. **Tab 6: Danh Mục (Categories, `activeTab === 'categories'`)**:
   Phân loại các khoản thu chi theo chủ đề (Ăn Uống, Nhà Cửa, Di Chuyển, Giải Trí, Mua Sắm, Tiền Lương, Tiền Thưởng...) với biểu tượng icon và màu sắc phong thủy.
7. **Tab 7: Linh Nhãn OCR (Invoice OCR, `activeTab === 'ocr'`)**:
   Trí tuệ nhân tạo Gemini Vision tự động quét ảnh hóa đơn/biên lai mua sắm, bóc tách tên cửa hàng, ngày, tổng tiền và các món đồ chi tiết để chuyển thành giao dịch chỉ với 1 cú nhấp.
8. **Tab 8: Hạn Mức (Budgets, `activeTab === 'budgets'`)**:
   Thiết lập trần chi tiêu tối đa theo tháng cho từng danh mục, theo dõi tỷ lệ phần trăm đã tiêu thời gian thực và tự động phát cảnh báo khi chạm ngưỡng 70% hoặc vượt 100%.
9. **Tab 9: Thống Kê (Stats & Reports, `activeTab === 'stats'`)**:
   Phân tích dữ liệu tài chính qua biểu đồ cơ cấu chi tiêu tròn, biểu đồ cột thu chi các tháng, xu hướng 6 tháng, chi tiêu theo tuần, so sánh chi tiết 2 tháng bất kỳ và xuất báo cáo Excel/CSV.
10. **Tab 10: Khí Linh AI (Desktop Chat, `activeTab === 'chat'`)**:
    Trợ lý tri thức toàn hệ thống (Knowledge Assistant) — nắm vững toàn bộ kiến trúc, chức năng, quy trình, bảo mật; tra cứu dữ liệu cá nhân chỉ đọc (Read-Only); **tuyệt đối KHÔNG có quyền thay đổi dữ liệu (No mutation)**.
11. **Tab 11: Phân Quyền (Admin / Chưởng Môn Các, `activeTab === 'admin'`)**:
    Bảng điều khiển quản trị dành riêng cho tài khoản có vai trò `admin` (Chưởng Môn). Thống kê số lượng người dùng toàn hệ thống, quản lý danh sách đạo hữu, nâng cấp/hạ vai trò và khóa/mở khóa tài khoản.

## 3. Các Tính Năng Bổ Trợ Đặc Sắc
- **Linh Trận Định Kỳ (Recurring Transactions)**: Thiết lập lịch chi tiêu/thu nhập tự động lặp lại theo tuần hoặc tháng (tiền nhà, tiền điện, lương); hệ thống tự động sinh giao dịch khi tới kỳ.
- **Khai Thị Tiết Kiệm (AI Saving Tips)**: Nút kích hoạt tại Tab 1 và Tab 9 giúp AI phân tích cơ cấu chi tiêu tháng và đưa ra 5 lời khuyên tài chính thiết thực mang phong cách tiên hiệp kết hợp quy tắc 50/30/20.
- **Bản Mệnh Hồn Đăng & Bảo Mật (Auth & Security)**: Xác thực JWT an toàn, mã hóa mật khẩu bcrypt, khôi phục tài khoản qua câu trả lời bí mật Bản Mệnh Hồn Đăng và mã OTP 6 ký tự.
- **Khí Linh Nhỏ (Live System Mode)**: Kích hoạt từ mọi trang bằng nút nổi hoặc khẩu quyết "Hệ thống", hỗ trợ hội thoại giọng nói liên tục, chống chen ngang và thực thi thao tác tài chính (Action Mode) có xác nhận an toàn.

## 4. Các Chức Năng Chưa Hỗ Trợ (PLANNED / UNSUPPORTED)
- Hệ thống hiện **CHƯA hỗ trợ** giao dịch cổ phiếu / chứng khoán tự động.
- Hệ thống hiện **CHƯA hỗ trợ** ví tiền mã hóa / blockchain / crypto / Bitcoin.
- Hệ thống hiện **CHƯA hỗ trợ** đầu tư vàng tự động hay giao dịch ngoại hối Forex.
