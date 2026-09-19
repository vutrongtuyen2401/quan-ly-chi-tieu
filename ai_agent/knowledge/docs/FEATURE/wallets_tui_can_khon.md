# TÚI CÀN KHÔN (QUẢN LÝ VÍ & TÀI KHOẢN NGUỒN TIỀN)

## 1. Mục Đích & Khái Niệm
Túi Càn Khôn là phân hệ quản lý toàn bộ các nguồn tiền, tài khoản ngân hàng và ví tài sản của người dùng trong Càn Khôn Linh Thạch Các.
Hệ thống cho phép người dùng mở **nhiều ví và nhiều tài khoản ngân hàng không giới hạn** để phân tách rõ ràng dòng tiền:
- **Tiền mặt (cash)**: Tiền mặt chi tiêu hàng ngày trong ví vật lý.
- **Nhiều tài khoản ngân hàng (bank)**: Người dùng có thể quản lý đồng thời nhiều tài khoản ngân hàng khác nhau như Vietcombank, Techcombank, MB Bank, VPBank, ACB, BIDV, Agribank, TPBank... Mỗi ngân hàng có tên riêng, số dư ban đầu độc lập và lịch sử biến động chi tiết.
- **Ví điện tử (ewallet)**: Momo, ZaloPay, Viettel Money, VNPay, ShopeePay...
- **Tài khoản đầu tư (investment)**: Quỹ tích lũy hoặc tài khoản chứng chỉ quỹ.
- **Thẻ tín dụng (credit)**: Thẻ chi tiêu trước trả tiền sau.
- **Sổ tiết kiệm (saving)**: Tiền gửi ngân hàng có kỳ hạn hoặc không kỳ hạn.

## 2. Các Thao Tác Khả Dụng Trong Túi Càn Khôn
1. **Xem danh sách ví & số dư**: Hiển thị danh sách từng ví với icon tương ứng, loại ví, số dư hiện tại và tổng số dư tài sản toàn bộ hệ thống.
2. **Tạo ví mới không giới hạn**:
   - Tên ví (ví dụ: "MB Bank", "Vietcombank Tiết Kiệm", "Momo", "Tiền Mặt").
   - Loại ví: `cash` (Tiền Mặt), `bank` (Ngân Hàng), `ewallet` (Ví Điện Tử), `investment` (Đầu Tư), `credit` (Tín Dụng), `other` (Khác).
   - Số dư ban đầu (ví dụ: 15.000.000 VNĐ).
   - Hỗ trợ danh sách gợi ý các ngân hàng Việt Nam phổ biến (danh sách `bankList`).
3. **Chỉnh sửa ví**: Đổi tên ví và loại ví khi có nhu cầu cập nhật.
4. **Xóa ví (Bảo vệ dữ liệu)**:
   - Chỉ có thể xóa ví khi ví đó **không còn chứa bất kỳ giao dịch lịch sử nào**.
   - Nếu ví đang có giao dịch phát sinh, hệ thống sẽ ngăn chặn việc xóa để đảm bảo tính toàn vẹn và minh bạch của sổ kế toán.
5. **Chuyển tiền giữa hai ví (Luân chuyển Linh Thạch)**:
   - Cơ chế hoạt động: Khi chuyển tiền giữa 2 ví (ví dụ rút tiền từ MB Bank về Tiền Mặt, hoặc chuyển từ Vietcombank sang Momo):
     + Người dùng chọn Ví Nguồn (Ví trừ tiền), Ví Đích (Ví cộng tiền), nhập số tiền và ghi chú.
     + Hệ thống kiểm tra số dư ví nguồn phải >= số tiền chuyển.
     + Thực hiện giao dịch nguyên tử (Atomic Database Transaction): Trừ số dư ví nguồn, cộng số dư ví đích cùng lúc.
     + Tự động sinh 2 bản ghi lịch sử đối ứng: Một giao dịch Chi Tiêu (`EXPENSE`) từ ví nguồn và một giao dịch Thu Nhập (`INCOME`) vào ví đích cùng mang danh mục hệ thống "Chuyển Khoản" để lưu trữ vết luân chuyển tiền minh bạch.
     + Tổng tài sản của người dùng được giữ nguyên vẹn.

## 3. Vị Trí Trên Giao Diện (UI Location)
- Truy cập qua menu thanh điều hướng trên cùng: Tab **Túi Càn Khôn** (Tab 5, `activeTab === 'wallets'`).
- Người dùng nhấn nút **+ Thêm Ví Mới** để mở form tạo ví, hoặc nhấn nút **🔄 Chuyển Tiền** để thực hiện luân chuyển giữa hai ví.

## 4. Quyền Hạn Thực Thi (Permissions)
- **Người dùng trên UI**: Toàn quyền xem, tạo ví, sửa ví, xóa ví và chuyển tiền trên tài khoản của chính mình.
- **Khí Linh Nhỏ (Live System Mode)**: Có quyền tra cứu số dư (`get_wallets`), tạo ví mới (`create_wallet`), và chuyển tiền (`transfer_money`) sau khi được người dùng xác nhận rõ ràng.
- **Khí Linh AI Lớn (Knowledge Assistant)**: Chỉ có quyền **tra cứu số dư chỉ đọc (Read-Only)** qua công cụ `get_wallets` hoặc `wallet_status`; **TUYỆT ĐỐI KHÔNG CÓ QUYỀN** tạo ví, sửa ví, xóa ví hay chuyển tiền (bị chặn ở cấp độ Code-Level `PERMISSION_DENIED`).
