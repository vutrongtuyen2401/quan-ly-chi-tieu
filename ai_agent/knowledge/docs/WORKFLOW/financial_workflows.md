# CÁC QUY TRÌNH THAO TÁC CHUẨN (WORKFLOWS)

## 1. Quy Trình Ghi Nhận Chi Tiêu Thường Nhật
1. Phát sinh chi tiêu (ví dụ: ăn trưa 45.000 VNĐ).
2. Mở Càn Khôn Linh Thạch Các:
   - **Cách 1 (UI)**: Vào Tab 2 (Giao Dịch) -> Bấm "Ghi Nhận Thu Chi" -> Chọn loại "Chi Tiêu", nhập 45.000 VNĐ, chọn danh mục "Ăn Uống", chọn ví "Tiền Mặt" -> Lưu.
   - **Cách 2 (Khí Linh Nhỏ)**: Bấm nút Khí Linh hoặc nói "Hệ thống" -> Nói: *"Chi 45 nghìn ăn trưa bằng tiền mặt"* -> Xác nhận -> Xong.
3. Số dư ví Tiền Mặt tự động giảm 45.000 VNĐ.
4. Tổng chi tiêu tháng trên màn hình Tổng Quan (Tab 1) tăng thêm 45.000 VNĐ.
5. Tiến độ hạn mức danh mục Ăn Uống được cập nhật thêm 45.000 VNĐ.

## 2. Quy Trình Thiết Lập & Kiểm Soát Hạn Mức Chi Tiêu
1. Đầu tháng, vào Tab 8 (**Hạn Mức**, `activeTab === 'budgets'`).
2. Chọn danh mục cần kiểm soát (ví dụ: "Ăn Uống") và đặt mức trần: 5.000.000 VNĐ.
3. Trong suốt tháng, mỗi khi có khoản chi thuộc danh mục Ăn Uống, thanh tiến độ sẽ dâng lên.
4. Khi chi tiêu vượt 70%, hệ thống chuyển màu vàng cảnh báo.
5. Khi vượt 100%, hệ thống phát cảnh báo đỏ tại màn hình Tổng Quan (Tab 1) để đạo hữu kịp thời thắt chặt chi tiêu.

## 3. Quy Trình Luân Chuyển Tiền Giữa Các Ví (Chuyển Khoản)
1. Khi rút tiền từ ngân hàng về ví tiền mặt hoặc nạp tiền từ ngân hàng vào ví điện tử:
2. Vào Tab 5 (**Túi Càn Khôn**, `activeTab === 'wallets'`) -> Bấm nút **"🔄 Chuyển Tiền"**.
3. Chọn Ví Nguồn (ví dụ: MB Bank), Ví Đích (ví dụ: Tiền Mặt).
4. Nhập số tiền (ví dụ: 2.000.000 VNĐ) và ghi chú luân chuyển.
5. Bấm Xác Nhận:
   - Hệ thống thực hiện giao dịch nguyên tử (Atomic Transaction): Số dư MB Bank trừ 2 triệu, Tiền Mặt cộng 2 triệu.
   - Tự động sinh 2 bản ghi lịch sử tương ứng mang danh mục "Chuyển Khoản" (1 khoản chi ở ví nguồn và 1 khoản thu ở ví đích).
   - Tổng tài sản toàn hệ thống được giữ nguyên vẹn.

## 4. Quy Trình Quyết Toán Nợ (Sổ Nợ)
1. Khi cho ai đó mượn tiền: Vào Tab 3 (**Sổ Nợ**, `activeTab === 'debts'`) -> Tạo khoản nợ Cho Vay (LEND) với tên người mượn, số tiền và ngày hẹn trả.
2. Khi người đó hoàn trả: Vào lại Tab 3 -> Tìm dòng tên người đó -> Bấm nút **"Quyết Toán"**.
3. Khoản nợ được đánh dấu đã thanh toán thành công (Is Settled = 1), hoàn tất nghĩa vụ công nợ.

## 5. Quy Trình Thiết Lập & Vận Hành Linh Trận Định Kỳ
1. Vào Tab 2 (**Giao Dịch**) -> Bấm nút **"🔄 Linh Trận Định Kỳ"**.
2. Điền thông tin giao dịch lặp lại:
   - Loại giao dịch: Chi Tiêu (tiền trọ, internet...) hoặc Thu Nhập (lương hàng tháng).
   - Số tiền định kỳ (ví dụ: 3.500.000 VNĐ).
   - Ví tiền và danh mục chi tiêu liên kết.
   - Tần suất: `Hàng tuần` hoặc `Hàng tháng`.
   - Ngày chạy tiếp theo (`next_run_date`).
3. Bấm **"Khởi Tạo Linh Trận Định Kỳ"**.
4. **Vận hành tự động**: Mỗi khi người dùng truy cập hoặc hệ thống kiểm tra, nếu ngày hiện tại >= `next_run_date`, hệ thống tự động sinh 1 bản ghi giao dịch thực tế vào bảng giao dịch, cập nhật số dư ví và tăng `next_run_date` sang chu kỳ tiếp theo (+7 ngày hoặc +1 tháng).

## 6. Quy Trình Tích Lũy & Rút Tiền Mục Tiêu Tiết Kiệm
1. Vào Tab 4 (**Mục Tiêu**, `activeTab === 'goals'`) -> Bấm "Tạo Mục Tiêu Mới" (ví dụ: Quỹ Khẩn Cấp 30 triệu).
2. Khi có tiền nhàn rỗi: Bấm nút **"Nạp Tiền"** trên thẻ mục tiêu -> Chọn ví trích tiền và số tiền nạp (ví dụ: 2 triệu) -> Số dư ví bị trừ 2 triệu và tiền trong quỹ mục tiêu tăng 2 triệu.
3. Thanh tiến độ (%) dâng lên tương ứng.
4. Khi đạt 100% hoặc khi cần tiền: Bấm nút **"Rút Tiền"** -> Chọn ví nhận tiền về và số tiền cần rút -> Tiền hoàn lại ví của người dùng.

## 7. Quy Trình Quét Hóa Đơn AI (Linh Nhãn OCR) Chuyển Thành Giao Dịch
1. Vào Tab 7 (**Linh Nhãn OCR**, `activeTab === 'ocr'`).
2. Chọn hoặc kéo thả tệp ảnh hóa đơn mua sắm (JPG, PNG, WebP, HEIC).
3. Bấm nút **"Bắt Đầu Quét"**: Gemini Vision AI bóc tách tên cửa hàng, ngày, tổng tiền và các món đồ chi tiết.
4. Kiểm tra lại thông tin, chỉnh sửa nếu cần và chọn ví thanh toán.
5. Bấm **"Lưu Thành Giao Dịch"**: Hệ thống tự động tạo giao dịch chi tiêu mới và trừ tiền ví tương ứng.

## 8. Quy Trình Xuất Sao Kê Báo Cáo Tài Chính (Excel / CSV)
1. Có 2 vị trí xuất báo cáo:
   - **Tại Tab 2 (Giao Dịch)**: Bấm nút **📥 Xuất Excel** hoặc **📄 Xuất CSV** ở ngay thanh công cụ.
   - **Tại Tab 9 (Thống Kê)**: Chọn tháng cần đối soát và bấm nút xuất báo cáo.
2. Trình duyệt tự động tải về tệp bảng tính (`.xlsx` hoặc `.csv`) với đầy đủ ngày tháng, loại thu chi, danh mục, ví và ghi chú để lưu trữ hoặc nộp kế toán.
