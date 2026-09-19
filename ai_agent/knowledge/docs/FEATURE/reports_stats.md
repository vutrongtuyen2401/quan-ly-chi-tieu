# BÁO CÁO & THỐNG KÊ (REPORTS & ANALYTICS)

## 1. Mục Đích & Khái Niệm
Phân hệ Báo Cáo & Thống Kê là trung tâm phân tích dữ liệu tài chính của Càn Khôn Linh Thạch Các, giúp chuyển hóa các giao dịch đơn lẻ thành những hiểu biết sâu sắc (insights) về hành vi tài chính của đạo hữu.

## 2. Các Báo Cáo Chuyên Sâu Khả Dụng
1. **Biểu đồ tròn cơ cấu chi tiêu theo danh mục (Category Breakdown)**:
   - Thể hiện tỷ trọng phần trăm chi tiêu của từng danh mục (Ăn Uống, Di Chuyển, Nhà Cửa, Giải Trí...) trong tháng được chọn.
   - Giúp nhận biết ngay danh mục nào đang ngốn nhiều tiền nhất.
2. **Biểu đồ cột so sánh thu chi qua các tháng (Monthly Cashflow)**:
   - Trực quan hóa tương quan giữa dòng tiền vào (Thu Nhập) và dòng tiền ra (Chi Tiêu) qua từng tháng.
3. **Phân tích xu hướng 6 tháng gần nhất (Trend Analysis)**:
   - Theo dõi tốc độ gia tăng hoặc cắt giảm chi phí qua chu kỳ nửa năm.
4. **Báo cáo chi tiêu theo tuần trong tháng (Weekly Report)**:
   - Chia tháng thành 4-5 tuần để kiểm tra nhịp độ tiêu tiền (ví dụ tiêu nhiều vào đầu tháng hay cuối tháng).
5. **So sánh chi tiết 2 tháng bất kỳ (Month Comparison)**:
   - Chọn 2 tháng bất kỳ (ví dụ Tháng 8/2026 vs Tháng 9/2026).
   - Tính toán độ lệch chính xác: chênh lệch thu nhập ($\Delta \text{Income}$), chênh lệch chi tiêu ($\Delta \text{Expense}$), và chênh lệch mức thặng dư tiết kiệm.
6. **Xuất báo cáo & Sao kê (Export Reports)**:
   - Xuất dữ liệu giao dịch chi tiết ra tệp **Excel (.xlsx)** hoặc **CSV**.
   - Hỗ trợ kế toán cá nhân và lưu trữ ngoại tuyến an toàn.

## 3. Vị Trí Trên Giao Diện (UI Location)
- Tab **Thống Kê** (Tab 9, `activeTab === 'stats'`).
- Có bộ lọc chọn tháng và các nút xuất báo cáo trực quan.

## 4. Ranh Giới Quyền Hạn
- Toàn bộ các công cụ thống kê và xuất báo cáo (`spending_by_category`, `get_trend_report`, `get_weekly_report`, `compare_months`, `export_reports`) là các **công cụ chỉ đọc (Read-Only)**.
- Khí Linh AI Lớn và Khí Linh Nhỏ đều có quyền gọi các công cụ này để phục vụ nhu cầu phân tích của người dùng.
