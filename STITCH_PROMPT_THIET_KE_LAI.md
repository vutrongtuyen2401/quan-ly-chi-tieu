# Prompt Stitch — Tinh gọn giao diện "Càn Khôn Linh Thạch Các"

> Góp ý của giảng viên: **giao diện cần dễ nhìn hơn, ít card hơn.**
> Mục tiêu: **tinh chỉnh** giao diện hiện tại (bản Stitch "Celestial Treasury", commit `1f1afa3`), **không** thiết kế lại thành trang web mới. Giữ nguyên toàn bộ chức năng.
>
> Danh sách "Loại bỏ" trong file này được lập sau khi chạy thử web và xem đủ 11 trang, modal hồ sơ và màn hình đăng nhập (ngày 09/10/2026). Mỗi mục bị loại bỏ đều là chữ trang trí, huy hiệu không có thật, hoặc thông tin đang hiển thị trùng ở chỗ khác. **Không mục nào là nút hay ô nhập mà chức năng của nó chỉ có ở đó.**

## Cách dùng với Stitch

1. Chụp màn hình **từng trang hiện tại** (bản đang chạy) và đính kèm vào Stitch cùng prompt của trang đó. Stitch bám theo ảnh thật thì kết quả mới giống "phiên bản gọn hơn của trang cũ", không biến thành trang mới.
2. Dán **Prompt chung (Phần A)** trước tiên, sau đó làm **mỗi lần một màn hình** với prompt ở Phần B. Không dán tất cả cùng lúc.
3. Nếu Stitch tự thêm hoặc bớt nút, ô nhập hay cột bảng, nhắc lại câu: *"Giữ đúng danh sách 'Phải giữ đủ', chỉ bỏ những gì trong danh sách 'Loại bỏ', không thêm gì mới."*
4. Khi có bản thiết kế ưng ý, chỉ áp dụng vào phần **template và CSS** của từng component Vue. Giữ nguyên `v-model`, `@click`, `emit`, `props` và tên hàm (xem Phần C).

---

## PHẦN A — PROMPT CHUNG (dán đầu tiên)

```
Bạn đang TINH CHỈNH (refine) giao diện có sẵn của web app quản lý chi tiêu cá nhân tên "Càn Khôn Linh Thạch Các", chủ đề tu tiên, toàn bộ chữ tiếng Việt. KHÔNG thiết kế lại từ đầu. Ảnh đính kèm là giao diện hiện tại; bản mới phải nhìn ra ngay là cùng một sản phẩm, chỉ gọn, giản dị và dễ đọc hơn.

GÓP Ý CẦN GIẢI QUYẾT: "Giao diện khó nhìn, quá nhiều card." 

GIỮ NGUYÊN (bản sắc hệ thống):
- Bố cục khung: header trên cùng (logo ☯ + tên "Càn Khôn Linh Thạch Các", nút đổi giao diện Sáng/Tối, khối tên người dùng + vai trò, nút "Hạ Sơn" đăng xuất) và bên dưới là thanh tab ngang gồm 11 tab theo đúng thứ tự: Tổng Quan, Giao Dịch, Sổ Nợ, Mục Tiêu, Túi Càn Khôn, Danh Mục, Linh Nhãn OCR, Hạn Mức, Thống Kê, Khí Linh AI, Phân Quyền (chỉ admin). Giữ mũi tên cuộn trái/phải khi thanh tab bị tràn (nhưng ở màn hình 1440px phải đủ chỗ cho cả 11 tab).
- Nút tròn nổi "Khí Linh" (trợ lý giọng nói) ở góc dưới bên phải mọi trang.
- Bảng màu tối "Celestial Treasury": nền #0b1326; bề mặt #131b2e / #171f33 / #222a3d; chữ chính #dae2fd, chữ phụ #bdc9c6; đường viền rgba(255,255,255,0.08).
  Ngọc bích #7dd6cc (màu chính, nút chính, thu nhập); đỏ #ef4444 (chi tiêu, nguy hiểm, xóa); vàng phù triện #e3c370 (cảnh báo, tích lũy); chàm #c4c1fb (AI / Khí Linh); xanh lá #10b981 (thành công).
- Font Inter; icon Material Symbols Outlined; emoji danh mục/mục tiêu do người dùng chọn (🍜, 🎯...) vẫn hiển thị vì đó là dữ liệu.
- Dãy núi phía sau nội dung, nhưng giảm độ đậm (opacity ~50%).
- Toàn bộ thuật ngữ tu tiên ở tiêu đề trang, tên nút, nhãn ô nhập, tên cột bảng.

NGUYÊN TẮC "ÍT CARD":
1. Mỗi trang tối đa 1 cấp khung. KHÔNG đặt card bên trong card. Khung nội dung chỉ dùng nền #131b2e, viền 1px mảnh, bo góc 12px, không glow, không gradient, không bóng đổ nặng.
2. Phần đầu trang KHÔNG đóng khung: chỉ gồm tiêu đề (24–28px), MỘT dòng mô tả ngắn và các nút hành động căn phải.
3. Hàng chỉ số (3–4 KPI) gộp thành MỘT dải duy nhất, các ô ngăn cách bằng đường kẻ dọc mảnh thay vì card riêng. Mỗi ô gồm nhãn, con số lớn, và (nếu có) một dòng chú thích CÓ SỐ LIỆU. Bỏ ô icon vuông trang trí.
4. Danh sách dữ liệu (ví, mục tiêu, hạn mức, định kỳ, danh mục, cảnh báo) hiển thị dạng DÒNG trong một khung chung, phân cách bằng đường kẻ, thay vì lưới card. Mỗi dòng vẫn giữ đủ thông tin, thanh tiến độ và nút thao tác.
5. Lời khuyên do hệ thống tự tính (Lời Khuyên Của Khí Linh, Khí Linh Khuyên Dạy...) VẪN HIỂN THỊ, nhưng là một dải ghi chú viền trái màu chàm ngay dưới khu vực liên quan, không phải card riêng.
6. Biểu mẫu tạo mới giữ nguyên cách mở/đóng hiện tại (nút bật/tắt biểu mẫu); khi mở là một khung phẳng duy nhất, nhãn nằm trên ô nhập, lưới 2–3 cột trên desktop, 1 cột trên mobile.
7. Mỗi thông tin chỉ hiển thị MỘT lần trên một khu vực. Nếu cùng một con số/trạng thái đang xuất hiện ở huy hiệu, dòng chữ và hộp cảnh báo, chỉ giữ một chỗ.

LOẠI BỎ TRÊN MỌI TRANG (chữ trang trí / thông tin trùng):
- Header: ô trạng thái "Linh Thạch Khả Dụng • Khí Vận Hanh Thông" có chấm nhấp nháy; nhãn "v3.0"; dòng phụ "Quản Lý Tài Chính & Tu Luyện Thạch" dưới tên.
- Dòng chữ in hoa nhỏ phía trên tiêu đề mỗi trang ("SỔ NHẬT KÝ NGÂN THẠCH", "TU VI TÍCH LŨY • TRÚC CƠ TRÌ", "BÁT QUÁI TÀI PHỔ • CHU KỲ GIÁP THÌN"...).
- Phần tiếng Anh/ngoặc trong tiêu đề: "(Debts & Loans)", "(Saving Goals)", "(Categories)", "(Budgets)", "(Quản Lý Ví Nguồn)".
- Câu mô tả 2 dòng dưới tiêu đề → rút còn 1 dòng ngắn.
- Dòng chú thích dưới ô chỉ số chỉ nhắc lại tên ô ("Toàn bộ ngân khố khả dụng", "Tổng thu nạp chu kỳ", "Tổng tiêu phí chu kỳ", "Dòng chân khí tích tụ ổn định", "Linh thạch kết tinh viên mãn"...). GIỮ những dòng có số liệu ("1 khế ước cần thanh toán", "Tỷ lệ giữ lại 91%", "22 ngày còn lại").
- Ô icon vuông ở góc mỗi ô chỉ số.
- Nền: hạt sáng bay, 2 lớp mây chuyển động, quầng sáng mặt trời, quả cầu phát sáng.
- Huy hiệu/phiên bản/thuật ngữ kỹ thuật không có ý nghĩa với người dùng ("OCR Engine Active", "Idempotent Guard", "MÃ 422 STRICT", "Phiên Bản 2.4.1", "Cấp Độ 4", "Bát Quái Động Phủ v4.2", "Tri Thức RAG", "Token Versioning", "Bcrypt", "ACID", "Atomic").
- Footer 2 vế → thu còn 1 dòng bản quyền nhỏ.

DỄ ĐỌC:
- Chữ nội dung tối thiểu 14px, nhãn tối thiểu 12px, độ tương phản đạt WCAG AA trên nền tối (kể cả chú thích biểu đồ).
- Số tiền dùng chữ số đều độ rộng (tabular), căn phải trong bảng; thu = ngọc bích có dấu "+", chi = đỏ có dấu "−". Ký hiệu "₫" chỉ xuất hiện MỘT lần sau số.
- Khoảng cách theo lưới 8px; khoảng cách giữa các khu vực lớn 24–32px.
- Mỗi trang chỉ một nút chính (nền ngọc bích); các nút còn lại dạng viền hoặc chữ.
- Bảng: hàng cao 48–52px, tiêu đề cột chữ nhỏ in hoa màu chữ phụ, hover đổi nền nhẹ, không viền dọc.
- Biểu đồ: chỉ MỘT chú thích (legend), không emoji trong chú thích.
- Mỗi dòng danh sách chỉ một icon (emoji danh mục), không thêm ô icon vuông lặp lại.
- Responsive: desktop 1440, laptop 1024, mobile 375 (bảng chuyển thành danh sách dòng xếp chồng, không cuộn ngang trang).

RÀNG BUỘC CHỨC NĂNG (BẮT BUỘC):
- KHÔNG xóa, gộp mất hoặc đổi tên bất kỳ thành phần nào trong mục "Phải giữ đủ" của từng trang: nút, ô nhập, lựa chọn dropdown, bộ lọc, cột bảng, phân trang, biểu đồ, modal, trạng thái rỗng, trạng thái đang tải.
- Chỉ bỏ những gì nằm trong mục "Loại bỏ".
- KHÔNG thêm chức năng mới, ô nhập mới hay trang mới.
- Chỉ thay đổi cách trình bày: bố cục, khung, khoảng cách, cỡ chữ, màu, icon trang trí.
```

---

## PHẦN B — PROMPT TỪNG MÀN HÌNH

> Mỗi prompt có **"Phải giữ đủ"** (lấy từ code hiện tại) và **"Loại bỏ"** (lấy từ lần xem trực tiếp trang web). Đây là phần quan trọng nhất để Stitch không làm mất chức năng.

### B1. Đăng nhập / Đăng ký / Quên mật khẩu / Đặt lại mật khẩu

```
Màn hình xác thực. Áp dụng Prompt chung.
Phải giữ đủ:
- Nút đổi giao diện Sáng/Tối ở góc trên.
- Logo ☯, tiêu đề "CÀN KHÔN LINH THẠCH CÁC", phụ đề "Hệ Thống Quản Lý Tài Chính & Khí Vận Tu Tiên", linh vật Khí Linh "Hộ trì tài chính".
- 4 biểu mẫu chuyển qua lại: Đăng nhập (Email, Mật khẩu có nút hiện/ẩn, nút Đăng nhập, link Quên mật khẩu, link Đăng ký); Đăng ký (Họ tên / Đạo hiệu, Email, Mật khẩu có hiện/ẩn, Bản Mệnh Hồn Đăng); Quên mật khẩu (Email, Bản Mệnh Hồn Đăng có hiện/ẩn); Đặt lại mật khẩu (Email, Mã đặt lại mật khẩu, Mật khẩu mới có hiện/ẩn). Mỗi form có vùng hiển thị lỗi, trạng thái đang xử lý và link quay lại.
- Dòng bản quyền ở chân.
Loại bỏ: dòng "Bảo mật bởi cơ chế Token Versioning & Bản Mệnh Hồn Đăng".
Cách tinh gọn: chỉ MỘT khung form ở giữa. Bỏ card lồng bên trong form, bỏ hiệu ứng glow quanh khung. (Màn hình này vốn đã khá gọn, chỉ chỉnh nhẹ.)
```

### B2. Header + thanh tab (dùng chung mọi trang)

```
Thành phần header dùng chung. Áp dụng Prompt chung.
Phải giữ đủ: logo ☯ (bấm về Tổng Quan), tên "Càn Khôn Linh Thạch Các"; nút Sáng/Tối; khối người dùng (tên, vai trò "Trưởng Lão Tông Môn"/"Động Chủ Tu Sĩ", avatar, bấm mở hồ sơ); nút "Hạ Sơn"; thanh 11 tab có icon + nhãn, tab đang chọn nổi bật, tab "Phân Quyền" có màu riêng cho admin; nút mũi tên cuộn khi tràn.
Loại bỏ: nhãn "v3.0"; dòng phụ "Quản Lý Tài Chính & Tu Luyện Thạch"; ô trạng thái "Linh Thạch Khả Dụng • Khí Vận Hanh Thông" có chấm nhấp nháy (đang chiếm chỗ khiến 11 tab không vừa ở 1440px — tab "Phân Quyền" bị che).
Cách tinh gọn: header cao tối đa 64px + thanh tab 44px, nền đặc #0b1326 có viền dưới mảnh. Tab đang chọn = chữ ngọc bích + gạch chân 2px (không dùng nền khối phát sáng). Ở 1440px cả 11 tab phải hiện đủ, không cần mũi tên.
```

### B3. Tổng Quan (Dashboard)

```
Trang Tổng Quan. Áp dụng Prompt chung.
Phải giữ đủ:
- Lời chào "Chào Đạo hữu {tên}", dòng mô tả theo tháng, nút chính "Khắc Ghi Biến Động" (chuyển sang tab Giao Dịch).
- 4 chỉ số: Tổng Linh Thạch / Số Dư; Linh Tuyền Thu Vào; Tiêu Hao Pháp Bảo; Tích Tụ Chân Nguyên (kèm trạng thái "Thặng dư tích cực"/"Thâm hụt cần chú ý").
- Biểu đồ cột "Xu Hướng Thu & Chi 6 Tháng Gần Nhất" (một chú thích Thu Nhập/Chi Tiêu, link "Xem Thống Kê Toàn Diện", trạng thái rỗng).
- "Phân Bổ Chi Tiêu": biểu đồ tròn + danh sách danh mục (chấm màu, icon, tên, thanh %, số tiền, %), trạng thái rỗng.
- "Cảnh Báo Tâm Ma Hạn Mức": số lượng, từng cảnh báo (icon + tên danh mục, %, thanh tiến độ, mức nguy cấp đỏ / cảnh báo vàng), trạng thái an toàn "Tâm cảnh an định", nút "Điều chỉnh giới luật hạn mức".
- "Khai Thị Tiết Kiệm AI": nút "Nhận Khai Thị" (có trạng thái đang tải), tháng, tỷ lệ tích lũy, nội dung lời khuyên, dòng gợi ý khi chưa có.
- "Giao Dịch Gần Đây": từng dòng (emoji danh mục, ghi chú, danh mục • ví • ngày, số tiền ±), link "Xem toàn bộ sổ cái", trạng thái rỗng.
Loại bỏ:
- Nhãn vai trò "Hộ Pháp Trưởng Lão (Admin)" cạnh lời chào (đã có trên header) và ô ngày tháng (tháng đã có trong câu mô tả).
- 2 quả cầu phát sáng trang trí; chú thích dưới 4 ô chỉ số chỉ nhắc lại tên ô.
- Chú thích thứ hai của biểu đồ cột (đang có 2 chú thích: một ở góc, một của biểu đồ có emoji 💎🔥); dòng "* Quy chuẩn: 1 Linh Ngân = 1.000 VNĐ".
- Câu cảnh báo dài trong mỗi dòng cảnh báo ("TẨU HỎA NHẬP MA! Pháp Khí Mua Sắm đã vượt hạn mức (114.8%)") vì lặp lại tên và % đã hiển thị; dòng mô tả "Theo dõi các định ngạch chi tiêu...".
- Ô vuông icon túi xách ở đầu mỗi giao dịch gần đây (giống hệt nhau, trùng với emoji danh mục); dòng "Trạng thái đồng bộ linh thạch: Viên Mãn • Sổ cái toàn vẹn".
Tùy chọn: có thể bỏ biểu đồ tròn ở trang này (giữ danh sách thanh %) vì trang Thống Kê đã có biểu đồ tròn cùng dữ liệu. Nếu chưa chắc, giữ cả hai.
Cách tinh gọn:
- Lời chào thành phần đầu trang không khung.
- 4 chỉ số thành 1 dải.
- Hàng 2: biểu đồ cột (2/3) và Phân Bổ Chi Tiêu (1/3), mỗi bên 1 khung.
- Hàng 3: Giao Dịch Gần Đây (7/12) và một cột (5/12) chứa Cảnh Báo + Khai Thị AI xếp dọc trong CÙNG một khung, ngăn bằng đường kẻ (hiện tại là card chứa 2 card con, cần bỏ lớp lồng). Mỗi cảnh báo là một dòng, không phải card.
- Tên ví trong dòng giao dịch dùng cùng font Inter cỡ nhỏ như phần chữ phụ còn lại.
```

### B4. Giao Dịch

```
Trang Giao Dịch "Sổ Giao Dịch Càn Khôn". Áp dụng Prompt chung.
Phải giữ đủ:
- Nút ở đầu trang: "Giao Dịch Định Kỳ" (kèm số "x đang chạy", bật/tắt khay định kỳ), "Thêm Giao Dịch Mới"/"Đóng Biểu Mẫu", "Excel", "CSV".
- Khay "Định Kỳ Pháp Trận": nút "Thêm Định Kỳ"/"Ẩn Biểu Mẫu"; form (Loại: Tiêu Hao/Thu Hoạch, Số Tiền, Túi Càn Khôn, Danh Mục, Tần Suất: Hàng Tháng/Hàng Tuần, Kỳ Chạy Kế Tiếp, Ghi Chú, nút "Khởi Tạo Linh Trận Định Kỳ"); danh sách định kỳ (icon, tên, số tiền • tần suất • "Kế tiếp: ngày", nút Tạm dừng/Chạy, Sửa, Xóa); trạng thái rỗng.
- Form "Ghi Nhận Giao Dịch Linh Thạch": Loại Giao Dịch, Số Linh Thạch (VNĐ), Túi Càn Khôn, Danh Mục, Ngày Giao Dịch, Ghi Chú, nút "Khắc Ghi Biến Động", nút đóng.
- Bộ lọc: Từ Ngày, Đến Ngày, Loại (Tất cả/Khoản Thu/Khoản Chi), Danh mục, Ví, ô "Tìm theo ghi chú...", nút "Làm Mới".
- Tóm tắt: Tổng hiển thị x giao dịch, Thu trang này, Chi trang này, Thặng dư trang.
- Bảng: Ngày giao dịch, Mô tả & Ghi chú, Danh mục, Ví thanh toán, Số tiền, Thao tác (nút Xóa "Xóa giao dịch & hoàn nguyên số dư"); trạng thái rỗng.
- Phân trang: "Hiển thị a - b trên tổng số n giao dịch", Trước, số trang, Sau.
Loại bỏ:
- Dòng chữ in hoa trên tiêu đề; rút câu mô tả còn 1 dòng.
- Cột "#" (số thứ tự).
- Cột "Loại" (THU/CHI) — trùng với dấu +/− và màu của cột Số tiền.
- Dòng chữ phụ dưới ghi chú đang lặp lại tên danh mục (đã có cột Danh mục).
Cách tinh gọn: bộ lọc là một hàng công cụ phẳng ngay trên bảng (không khung riêng); 4 số tóm tắt thành một dòng chữ nhỏ giữa bộ lọc và bảng; bảng nằm trong 1 khung duy nhất; khay định kỳ hiển thị dạng danh sách dòng thay vì lưới card.
```

### B5. Sổ Nợ

```
Trang "Sổ Nợ & Khế Ước". Áp dụng Prompt chung.
Phải giữ đủ:
- Nút "Tạo Khế Ước Nợ Mới"/"Đóng Biểu Mẫu" (mobile).
- 4 chỉ số: Tổng Vay Chưa Trả (+ số khế ước cần thanh toán), Tổng Cho Vay Chưa Thu (+ số đang chờ thu), Hiệu Số Nợ Ròng (+ Thặng dư phải thu/Thâm hụt phải trả), Đã Hoàn Tất Quyết Toán (+ số đã hoàn trả).
- Bộ lọc: ô tìm "Tìm theo tên đạo hữu, ghi chú khế ước...", nút "Đặt lại", lọc loại (Tất cả khế ước / Tôi Vay Nợ / Tôi Cho Vay), lọc trạng thái (Tất cả / Chưa tất toán / Đã tất toán).
- Bảng "Danh Sách Khế Ước Nợ Pháp" (đếm "x / y bản ghi"): Loại Khế Ước, Đạo Hữu / Đối Tác (avatar chữ cái, tên, ghi chú), Linh Thạch, Hạn Trả (+ nhãn "Còn x ngày"/quá hạn), Ví Liên Kết, Thao Tác (Đã Trả/Đã Thu/Hoàn Tác, Sửa, Xóa); trạng thái rỗng.
- Form "Tạo Khế Ước Mới": Loại (Tôi Cho Vay / Tôi Vay Nợ), Tên Đạo Hữu / Đối Tác, Số Linh Thạch, Ngày Hẹn Trả, Ví Nguồn Liên Kết, Ghi Chú Đạo Sự, nút "Khắc Ấn Khế Ước".
- "Lời Khuyên Của Khí Linh" (nội dung tự sinh).
Loại bỏ:
- "(Debts & Loans)" trong tiêu đề; dòng chữ in hoa trên tiêu đề.
- Huy hiệu "Ấn Ký" và câu mô tả dài dưới tiêu đề form.
- Cột "#".
- Cột "Trạng Thái" riêng ("Chưa tất toán") — trùng với nút ở cột Thao Tác. Thay bằng: khoản đã tất toán hiển thị mờ hơn và có chữ nhỏ "Đã tất toán" cạnh nút "Hoàn Tác".
Cách tinh gọn: 4 chỉ số thành 1 dải; bộ lọc thành hàng công cụ phía trên bảng (bỏ card lọc riêng); cột phải chỉ còn form trong 1 khung, lời khuyên là dải ghi chú dưới form.
```

### B6. Mục Tiêu

```
Trang "Mục Tiêu Tích Lũy". Áp dụng Prompt chung.
Phải giữ đủ:
- Nút "Khởi Tạo Mục Tiêu"/"Đóng Biểu Mẫu".
- 4 chỉ số: Tổng Linh Thạch Đã Tích (+ Mục tiêu tổng), Đang Thực Hiện, Mục Tiêu Viên Mãn, Linh Thạch Cần Thêm (+ Tiến độ đại đạo %).
- Form tạo: Tên Mục Tiêu*, Số Tiền Đích*, Số Tiền Ban Đầu, Thời Hạn Hoàn Thành, Biểu Tượng Tâm Pháp (10 lựa chọn emoji), nút "Khởi Tạo Mục Tiêu", nút đóng ✕.
- Thanh công cụ: ô "Tìm mục tiêu theo tên...", nút xóa tìm kiếm, lọc Tất Cả / Đang Tích Tụ / Viên Mãn (kèm số lượng), sắp xếp (Mặc định, Kỳ hạn gần nhất, Tiến độ cao nhất, Số tiền lớn nhất, Tên A-Z).
- Mỗi mục tiêu: icon, trạng thái (Đạt Mục Tiêu/Đang Tích Lũy), nhãn ngày ("Còn x ngày"), tên, nút Sửa, Xóa; Đã Gom Góp, Mục Tiêu Đích, Còn Thiếu/Dư; thanh "Tiến Độ Đại Đạo" %; câu khuyên ("Khuyên nạp ~x ₫/ngày"); nút "Nạp Thêm", "Rút".
- Trạng thái rỗng (nút "Khởi Tạo Mục Tiêu Đầu Tiên", "Khôi Phục Bộ Lọc").
Loại bỏ:
- "(Saving Goals)" trong tiêu đề; dòng chữ in hoa trên tiêu đề.
- Chú thích không có số liệu dưới ô chỉ số: "Dòng chân khí tích tụ ổn định", "Linh thạch kết tinh viên mãn".
- Hộp con bao quanh bộ 3 số (Đã gom góp / Mục tiêu đích / Còn thiếu) trong mỗi mục tiêu — giữ 3 số, bỏ khung lồng.
- Góc phát sáng trang trí ở mỗi thẻ.
Cách tinh gọn: lưới card mục tiêu thành danh sách dòng trong 1 khung, mỗi dòng gồm: icon + tên + trạng thái | số đã gom / đích / còn thiếu | thanh tiến độ rộng | nút Nạp / Rút / Sửa / Xóa. Câu khuyên là chữ nhỏ dưới thanh tiến độ.
```

### B7. Túi Càn Khôn (Ví)

```
Trang "Túi Càn Khôn". Áp dụng Prompt chung.
Phải giữ đủ:
- Nút "Điều Chuyển Linh Thạch" (bật/tắt khu chuyển tiền), "Khai Mở Ví Mới"/"Đóng Biểu Mẫu".
- Tổng hợp: số ví hoạt động, Tổng Số Dư Khả Dụng, thanh "Phân Bổ Dòng Chảy Linh Thạch" nhiều màu + chú thích từng ví với % (tên ví không bị cắt).
- Form khai mở ví: Tên Ví (có gợi ý danh sách ngân hàng), Số Dư Ban Đầu, Loại Ví (Tiền Mặt/Ngân Hàng/Ví Điện Tử), nút "Khai Mở Ví Mới".
- Mỗi ví: icon theo loại, tên, số dư khả dụng, nút "Chuyển", Sửa, Xóa; trạng thái rỗng + nút "Khai Mở Ví Đầu Tiên".
- Khu "Lệnh Điều Chuyển Linh Thạch": Ví Nguồn, nút "Đảo chiều ví nguồn và đích", Ví Đích, Số Tiền, 5 nút nhanh (1.000.000 ₫, 2.000.000 ₫, 5.000.000 ₫, 10.000.000 ₫, Toàn Bộ Khả Dụng), nút "Xác Nhận Thực Hiện Điều Chuyển"; khung "Mô Phỏng Dòng Chảy" (ví nguồn −, ví đích +, số dư dự kiến sau chuyển, trạng thái Sẵn Sàng/Đang Chờ).
Loại bỏ:
- "(Quản Lý Ví Nguồn)" trong tiêu đề; dòng chữ in hoa trên tiêu đề; cụm "(Atomic Two-sided Transfers)" trong câu mô tả.
- "Chu kỳ quyết toán: Nhật Triều", huy hiệu "Cân Bằng Nội Bộ", đoạn văn dưới tổng số dư ("Dòng thanh khoản linh hoạt đã kết nối qua linh thạch ấn tín...").
- Ở mỗi ví: chỉ giữ MỘT cách thể hiện loại ví (icon). Bỏ huy hiệu loại ví và dòng mô tả phụ ("Chi tiêu thường nhật tại động phủ", "Tài khoản ngân hàng & chuyển khoản", "Quét mã QR thanh toán nhanh"). Bỏ góc phát sáng.
- Trong khu chuyển tiền: phụ đề "Quy trình chuyển dịch năng lượng hai chiều đối ứng (Atomic & Two-sided)", huy hiệu "Idempotent Guard", dòng "Tỷ lệ quy đổi: 1:1 nội bộ • Miễn phí ấn chú", hộp "Bảo Toàn Chu Kỳ Nguyên Tử (ACID)", nhãn "Đối Ứng Tự Động" trên nút xác nhận.
- 3 dòng tick xanh dưới "Mô Phỏng Dòng Chảy" → thay bằng MỘT dòng ghi chú: "Chuyển nội bộ không tính vào Tổng Thu / Tổng Chi."
- Thẻ "Túi Càn Khôn Độc Lập" (lời triết lý, có con số "22%" không có thật).
Cách tinh gọn: phần tổng hợp thành 1 dải (tổng số dư + thanh phân bổ); danh sách ví thành các dòng trong 1 khung; khu chuyển tiền = 1 khung chia 2 cột (form | mô phỏng) không có card con.
```

### B8. Danh Mục

```
Trang "Danh Mục Thu Chi". Áp dụng Prompt chung.
Phải giữ đủ:
- Nút "Khai Mở Danh Mục Mới" (cuộn tới form).
- Thanh công cụ: ô "Tìm danh mục theo tên linh mục...", nút xóa tìm kiếm, lọc Tất cả / Chi Tiêu / Thu Nhập (kèm số lượng).
- 2 danh sách "Danh Mục Chi Tiêu" và "Danh Mục Thu Nhập" (đếm số mục): icon, tên, nút Sửa, Xóa; trạng thái rỗng.
- Form "Khai Mở Danh Mục Mới": Tên Danh Mục, Loại (Tiêu Hao / Thu Hoạch), lưới chọn biểu tượng emoji, nút "Làm Lại", "Khai Mở Danh Mục".
Loại bỏ:
- "(Categories)" trong tiêu đề; dòng chữ in hoa trên tiêu đề.
- Cả 3 ô chỉ số (Linh Thạch Xuất Quán / Nhập Động / Tổng Thể Phân Loại) — chỉ là số lượng danh mục, đã hiển thị trên nút lọc "Tất cả (5) / Chi Tiêu (3) / Thu Nhập (2)" và ở đầu mỗi danh sách.
- Dòng "Mã định danh linh mục: #id" (ID nội bộ).
- Nhãn "CHI"/"THU" trên từng dòng (dòng đã nằm trong danh sách Chi hoặc Thu); nhãn "Linh Thạch Tổn Hao"/"Linh Thạch Tích Tụ" ở đầu danh sách.
- Thẻ "Cơ Cấu Luân Chuyển Linh Thạch" (tỷ lệ Chi 60% / Thu 40% là tỷ lệ SỐ LƯỢNG danh mục, không phải tiền, dễ gây hiểu nhầm).
- Khung card riêng của từng danh mục bên trong danh sách.
Cách tinh gọn: hai danh sách là 2 cột trong cùng một khung (ngăn bằng đường kẻ dọc), mỗi danh mục là một dòng; form ở cột phải trong 1 khung.
```

### B9. Linh Nhãn OCR

```
Trang "Linh Nhãn Quét Hóa Đơn". Áp dụng Prompt chung.
Phải giữ đủ:
- Nút "Làm Lại" ở đầu trang.
- Thanh 4 bước: Tải Ảnh Hóa Đơn → Khám Chiếu Hình Ảnh → Linh Nhãn Khởi Động → Xác Thực & Lập Sổ (trạng thái hoàn tất/đang làm).
- Cột trái: vùng kéo-thả ảnh (bấm để chọn tệp; JPG/PNG/WEBP, tối đa 5MB — ghi MỘT lần), xem trước ảnh, tên tệp, dung lượng + thanh % (chỉ khi đã có ảnh), nút "Kích Hoạt Linh Nhãn OCR", nút "Quét Ảnh Khác", mẹo chụp ảnh (1 dòng).
- Trạng thái đang phân tích (3 dòng tiến trình).
- Kết quả: cảnh báo lệch số liệu; Tên Cửa Hàng, Ngày Lập Chứng Từ (sửa được); Tổng Linh Thạch Thanh Toán; bảng hạng mục sửa trực tiếp (Sản Phẩm, SL, Đơn Giá, Thành Tiền, nút xóa dòng), dòng tổng đối chiếu, nút "Thêm Hạng Mục"; chọn Túi Càn Khôn và Danh Mục Chi Tiêu (bắt buộc); nút "Hủy Kết Quả", "Xác Nhận Tạo Giao Dịch".
- Trạng thái chờ "Sẵn Sàng Tiếp Nhận Chứng Từ" (1 câu hướng dẫn).
Loại bỏ:
- Dòng chữ in hoa "BÁT QUÁI KÍNH THẦN THỨC • PHIÊN BẢN LINH GIÁC 3.4"; huy hiệu "OCR Engine Active".
- Nút "Tải Hóa Đơn" ở đầu trang (trùng với vùng kéo-thả ngay bên dưới, vốn cũng bấm được để chọn tệp).
- Phần "3 bước" (Chụp / Phân Tích / Lập Sổ) trong khung chờ — trùng với thanh 4 bước ở trên.
- Huy hiệu "Hỗ trợ JPG, PNG, WEBP" ở góc khung (thông tin này đang lặp 3 lần).
- Thanh "Dung lượng 0 MB / 5.0 MB" và dòng "Chưa chọn tệp / Chờ tải ảnh / Sẵn sàng tiếp nhận" khi CHƯA có ảnh.
- Các dòng "Động Phủ • Khớp 99.8%", "Tổng Ngân • Khớp 99.4%" (số không có thật); nhãn "AI-OCR • READY".
- Banner "Linh Trận Phòng Ngự (Integrity Guard) – MÃ 422 STRICT – 100% Minh Bạch" → thay bằng 1 dòng ghi chú nhỏ: "Ảnh không phải hóa đơn sẽ bị từ chối."
Cách tinh gọn: thanh bước là 1 hàng chữ + số, không card; khung làm việc chia 2 cột (ảnh | kết quả), mỗi cột 1 khung.
```

### B10. Hạn Mức

```
Trang "Hạn Mức Chi Tiêu". Áp dụng Prompt chung.
Phải giữ đủ:
- Bộ chọn tháng: nút tháng trước, nhãn tháng, nút tháng sau, nút "Hiện tại"; nút "Thiết Lập Hạn Mức Mới".
- 3 chỉ số: Tổng Hạn Mức Tháng (+ số danh mục), Đã Chi Tiêu (% + trạng thái), Hạn Mức Khả Dụng Còn Lại (hoặc "Vượt …", số ngày còn lại).
- Thanh công cụ: ô "Tìm linh mục chi tiêu...", nút xóa, lọc Tất cả / Nguy Cấp / Cảnh Báo / An Toàn (kèm số lượng).
- Mỗi hạn mức: icon, tên danh mục, "Giới hạn: …", nhãn trạng thái, số đã chi, %, chênh lệch ("Còn …"/"Vượt …"), thanh tiến độ màu theo trạng thái, nút "Điều Chỉnh Hạn Mức", nút Xóa; trạng thái rỗng (nút "Thiết Lập Hạn Mức Đầu Tiên", "Đặt Lại Bộ Lọc").
- Form: Linh Mục Chi Tiêu, Mức Giới Hạn (VNĐ), nút "Làm Lại", "Lưu Hạn Mức" (form áp dụng cho tháng đang chọn ở đầu trang — ghi rõ trong tiêu đề form, ví dụ "Thiết Lập Hạn Mức · Tháng 10/2026").
- "Khí Linh Khuyên Dạy": lời khuyên tự sinh.
Loại bỏ:
- "(Budgets)" trong tiêu đề; dòng chữ in hoa trên tiêu đề.
- Ô chỉ số thứ 4 "Trạng Thái Tổng Cương" (số Nguy Cấp / Cảnh Báo / An Toàn đã có trên các nút lọc).
- Chú thích "≥100% / ≥80% / <80%" (trùng với các nút lọc).
- Hộp cảnh báo trong mỗi hạn mức ("TẨU HỎA NHẬP MA! Đã vượt ngưỡng quy định...") — trạng thái đã được nói bằng nhãn + dòng % + màu thanh.
- Ô chỉ đọc "Chu Kỳ Áp Dụng" và huy hiệu "Tháng 10/2026" trong form (trùng với bộ chọn tháng); phụ đề "Khóa cương thổ tài chính".
- Đoạn "Quy Ước Linh Môn" → rút thành 1 dòng ghi chú nhỏ.
- Vòng tròn "106.6% Tổng Cương" trong thẻ Khí Linh (trùng với ô "Đã Chi Tiêu").
Cách tinh gọn: bộ chọn tháng nằm ở đầu trang, không khung; 3 chỉ số thành 1 dải; lưới card hạn mức thành danh sách dòng (icon+tên | đã chi / giới hạn | thanh tiến độ | % | nút); cột phải: form + lời khuyên trong 1 khung.
```

### B11. Thống Kê

```
Trang "Thống Kê Chi Tiêu & Dự Báo Tu Luyện". Áp dụng Prompt chung.
Phải giữ đủ:
- 4 nút chọn nhanh khoảng thời gian, ô chọn khoảng ngày (chỉ ngày, định dạng dd/MM/yyyy, không hiện giờ), nút "CSV", "Excel".
- 4 chỉ số: Tổng Thu Kỳ Này, Tổng Chi Kỳ Này, Thặng Dư Tích Lũy (+ tỷ lệ giữ lại %), Số Dư Khả Dụng (Ví).
- Biểu đồ "Xu Hướng Thu - Chi & Tích Lũy" (một chú thích, trạng thái rỗng).
- Biểu đồ đường "Biến Động Chi Tiêu Theo Tuần" (có tooltip số tiền từng tuần).
- "Tỷ Trọng Chi Tiêu Theo Danh Mục": biểu đồ tròn + danh sách (icon, tên, thanh %, số tiền, %).
- "So Sánh Chi Tiêu Hai Tháng": chọn Tháng 1, Tháng 2, nút "Đối Chiếu"; 3 ô Tổng Thu Nhập / Tổng Chi Tiêu / Tích Lũy Ròng (chênh lệch ▲▼ + giá trị từng tháng); bảng chi tiết (Danh Mục, Tháng 1, Tháng 2, Chênh Lệch, Đánh Giá Khí Linh).
- "Lời Khuyên Tiết Kiệm Từ Khí Linh AI": nút "Thỉnh Khai Thị Khí Linh", tháng, tỷ lệ tích lũy, nội dung.
- Trạng thái "Chưa Có Đủ Dữ Liệu Thống Kê".
Loại bỏ:
- Dòng chữ in hoa "BÁT QUÁI TÀI PHỔ • CHU KỲ GIÁP THÌN"; khung bao quanh phần đầu trang.
- Chú thích thứ hai trên mỗi biểu đồ (đang có 2 chú thích, cái của biểu đồ có emoji 💎🔥 và chữ tối khó đọc); chú thích chữ tối của biểu đồ tròn (danh sách bên cạnh đã có tên + màu).
- Dãy ô T1…T7 dưới biểu đồ tuần (lặp lại đúng dữ liệu biểu đồ); nhãn "7 Tuần Lễ", "3 Danh Mục Chi".
- Chân biểu đồ "Số chu kỳ ghi nhận: 3 Tháng / Đối chiếu tự động theo lịch sử".
- Dòng chữ in hoa "ĐỐI CHIẾU CHU KỲ", phụ đề "Tự động đối chiếu chênh lệch giữa hai tháng".
- Huy hiệu "BẬC THẦY KHÍ LINH"; câu "Phân tích chuyên sâu kết hợp vận số ngũ hành & dòng tiền tu đạo".
Cách tinh gọn: đầu trang không khung, bộ lọc thời gian là 1 hàng công cụ; 4 chỉ số thành 1 dải; 3 biểu đồ mỗi cái 1 khung (xu hướng và tuần chia đôi; danh mục rộng toàn trang); phần So Sánh là 1 khung, 3 ô so sánh thành 1 dải trong khung, bảng ngay bên dưới; lời khuyên AI là dải viền trái màu chàm.
```

### B12. Khí Linh AI (trang tra cứu)

```
Trang "Khí Linh" (chế độ Chỉ Đọc). Áp dụng Prompt chung.
Phải giữ đủ: tiêu đề "Khí Linh" + nhãn "Chỉ Đọc" + mô tả 1 dòng, nút "Làm Mới" (xóa lịch sử); lời chào của Khí Linh theo tên người dùng (kèm ảnh linh vật); dòng ngày "Hôm nay • …"; bong bóng tin nhắn người dùng (tên + avatar chữ cái) và Khí Linh (nhãn, nội dung định dạng); trạng thái "Khí Linh đang tra cứu…"; dòng "Gợi ý pháp vấn" với các chip câu hỏi; ô nhập, nút micro (đang nghe / tắt), nút "Truyền Lệnh".
Loại bỏ: huy hiệu "Bát Quái Động Phủ v4.2", "Tri Thức RAG Sẵn Sàng", "Độ Nhạy: Thần Thức Cấp 7", "Thần Thức Cấp 7" trên tin nhắn; dòng "Phản hồi từ Thần Thức Bát Quái • Tri Thức RAG" dưới mỗi câu trả lời; phần "(Chế độ Tri Thức / Read-Only)" trong mô tả.
Cách tinh gọn: giao diện chat một cột, rộng tối đa 860px; thẻ giới thiệu thành tin nhắn đầu tiên của Khí Linh thay vì card riêng; ô nhập dính ở đáy.
```

### B13. Phân Quyền (Admin)

```
Trang "Phân Quyền & Quản Lý Tu Sĩ". Áp dụng Prompt chung.
Phải giữ đủ: tiêu đề + mô tả 1 dòng; 3 chỉ số Tổng Số Đạo Hữu, Đang Hoạt Động (+%), Đang Bị Phong Ấn / Khóa; ô "Tìm kiếm theo tên đạo hiệu, thư điện tử...", nút xóa, lọc vai trò (Tất cả / Admin / User), lọc trạng thái (Tất cả / Đang Hoạt Động / Bị Phong Ấn), nút "Đặt Lại", "Làm Mới"; bảng: Tu Sĩ (avatar, tên, nhãn "Hiện Tại", "Khởi tạo: ngày", mã #id chữ nhỏ), Thư Điện Tử, Vai Trò, Trạng Thái, Thao Tác (Khóa/Mở Khóa, Nâng Lên Admin / Hạ Xuống User, dòng "Tự bảo vệ" với tài khoản hiện tại); trạng thái rỗng; phân trang "Trang x / y"; modal xác nhận đổi vai trò.
Loại bỏ: dòng chữ in hoa "KHU VỰC QUẢN TRỊ TÔNG MÔN"; thẻ "Pháp Trận Phong Ấn – Cấp Độ 4 • Bất Khả Xâm Phạm"; dòng phụ "Toàn bộ tông môn – Hệ thống Càn Khôn Các", "Vi phạm giới luật tông môn"; cột riêng "Mã / Ngày Tạo" (ngày tạo đã có dưới tên, mã #id chuyển thành chữ nhỏ cạnh tên).
Cách tinh gọn: 3 chỉ số thành 1 dải; bộ lọc là hàng công cụ phía trên bảng trong cùng một khung với bảng.
```

### B14. Hồ Sơ (modal "Quản Lý Hồ Sơ Đạo Tâm")

```
Modal hồ sơ, mở từ khối người dùng trên header. Áp dụng Prompt chung.
Phải giữ đủ: avatar, vai trò, tên, email; "Cảnh Giới Tài Chính" + tích lũy + thanh tiến độ; form Đạo Hiệu (sửa được), Email (khóa), nút "Cập Nhật Đạo Hiệu"; "Đổi Mật Khẩu" (mật khẩu hiện tại, mới, xác nhận, nút hiện/ẩn từng ô, thông báo lỗi, nút "Cập Nhật Mật Khẩu Pháp Ấn"); "Bản Mệnh Hồn Đăng" (mô tả 1 dòng, trạng thái đã thiết lập, mật khẩu hiện tại, khẩu quyết mới + nhập lại, hiện/ẩn, lỗi, nút "Khắc Ghi Hồn Đăng Mới"); nút đóng ✕.
Loại bỏ:
- Dòng chữ in hoa "THIẾT LẬP BẢN THỂ & KẾT GIỚI • THẦN THỨC CẤP 9"; ô "Trạng Thái Kết Giới: Kiên Cố • Linh Quang Hộ Thể".
- Nhãn "Đang Tu Luyện" cạnh vai trò.
- Email dưới tên (giữ email trong ô bị khóa phía dưới — hiện đang hiện 2 lần).
- Ô "Động Phủ Quản Thác: Vạn Hạc Động Phủ • Phân Khu Nhị" (chữ viết cứng, không phải dữ liệu người dùng).
- Thẻ "Đặc Quyền Chưởng Môn".
- Huy hiệu "Đang Cháy Sáng", "Phiên Bản 2.4.1"; chữ "Bcrypt", "Token Versioning" trong mô tả (giữ ý: "Đổi mật khẩu sẽ đăng xuất mọi thiết bị khác").
- Thẻ "Đăng Xuất Khỏi Pháp Trận" (trùng với nút "Hạ Sơn" trên header).
- 3 ô cuối "Bản Mệnh Hồn Đăng / Phiên Truy Cập An Toàn / Vô Hiệu Hóa Tức Thì".
Cách tinh gọn: modal 2 cột (trái: danh tính + đổi tên; phải: Bản Mệnh Hồn Đăng và Đổi Mật Khẩu xếp dọc, ngăn bằng đường kẻ, không card lồng).
```

### B15. Các modal chỉnh sửa

```
Bộ modal chỉnh sửa dùng chung một kiểu. Áp dụng Prompt chung.
Phải giữ đủ các modal và trường:
- Sửa ví: Tên Ví, Loại Ví.
- Sửa danh mục: Tên Danh Mục, Biểu Tượng.
- Sửa định kỳ: Loại, Số Tiền, Ví, Danh Mục, Tần Suất, Ngày Chạy Kế Tiếp, Ghi Chú, Trạng Thái.
- Sửa khoản nợ: Loại, Đối Tác, Số Tiền, Ngày Đến Hạn, Ví Liên Kết, Trạng Thái, Ghi Chú.
- Sửa mục tiêu: Tên, Số Tiền Đích, Số Tiền Đang Có, Thời Hạn, Biểu Tượng, Trạng Thái Hoàn Thành.
- Nạp / Rút mục tiêu: tên mục tiêu, Số Tiền, ví trừ/cộng (tùy chọn).
- Sửa hạn mức: tên danh mục + chu kỳ, Mức Giới Hạn Mới.
Mỗi modal: tiêu đề + nút đóng ✕, thân form, chân có "Hủy" và nút lưu (có trạng thái đang lưu).
Loại bỏ: emoji đầu tiêu đề modal (✏️, ➕, ➖) và trong nút lưu (💾, ✨, ⚡).
Cách tinh gọn: khung modal rộng 480–520px, nền #171f33, không glow; lưới 2 cột cho form nhiều trường; trên mobile thành bottom sheet.
```

### B16. Trợ lý nổi Khí Linh (tùy chọn — chỉ làm nếu cần)

```
Lớp phủ trợ lý giọng nói Khí Linh mở từ nút tròn góc dưới phải. Áp dụng Prompt chung.
Phải giữ đủ: nút nổi "Bấm hoặc nói 'Hệ thống'"; tiêu đề hệ thống, nút bật/tắt giọng đọc, nút đóng; nhân vật Khí Linh + trạng thái; "Bạn vừa nói"; trạng thái đang tra cứu; thẻ "Xác Nhận Thao Tác" (loại thao tác, nguồn → đích, số tiền, ghi chú, nút "Hủy Bỏ Pháp Lệnh" / "Xác Nhận Giao Dịch"); khối phản hồi (đồng hồ tự dọn); 4 câu gợi ý; dòng trạng thái; nút "Bật Mic"/"Đang Nghe".
Loại bỏ: chữ trang trí "[CAN-KHON::SYS-01]", "TÂM THỨC LIÊN KẾT: 99.87%", "Phí Pháp Lực (Tự Động) 0 Đ".
Cách tinh gọn: giảm hiệu ứng glow; giữ bố cục.
```

---

## PHẦN C — Khi áp dụng thiết kế Stitch vào code (để không mất chức năng)

- Mỗi lần chỉ áp dụng **một màn hình**: thay phần HTML/CSS trong đúng component (ví dụ `components/debts/DebtsView.vue`). Không đụng `App.vue` script, store hay backend.
- Giữ nguyên mọi `v-model`, `@click`, `$emit(...)`, `props`, `v-if`/`v-for` và tên hàm. Chỉ đổi thẻ bao, class và CSS.
- Khi bỏ một khối trong mục "Loại bỏ", chỉ xóa phần hiển thị trong template. Nếu khối đó dùng một biến hoặc hàm chỉ để hiển thị (ví dụ `companionAdviceText`), có thể để nguyên trong script, không bắt buộc xóa.
- Đối chiếu danh sách "Phải giữ đủ" ở Phần B sau khi áp dụng. Thiếu mục nào thì bổ sung lại trước khi chuyển trang khác.
- Sau mỗi trang: chạy app, thử lại thao tác của trang đó, xem Console không có lỗi đỏ hay `[Vue warn]`, rồi xem lại các trang chính (Đăng nhập, Tổng Quan, Giao Dịch, Linh Nhãn OCR, Khí Linh AI, Phân Quyền) theo AGENTS.md.

### Lỗi hiển thị cần sửa cùng lúc (phát hiện khi xem web, không phải việc của Stitch)

| Lỗi | Nơi thấy |
|---|---|
| Ký hiệu tiền bị lặp "₫₫" (ví dụ "660.000 ₫₫", "110.850.000 ₫ ₫") | Hạn Mức, Túi Càn Khôn |
| Tên ví trong "Giao Dịch Gần Đây" hiện bằng font có chân, to hơn chữ xung quanh | Tổng Quan |
| Ô chọn khoảng ngày hiện cả giờ ("09/09/2026, 10:18") | Thống Kê |
| Chú thích biểu đồ chữ tối trên nền tối, khó đọc | Tổng Quan, Thống Kê |
| 11 tab không vừa ở màn hình 1440px, tab "Phân Quyền" bị che | Header |
| Phiên đăng nhập hết hạn không tự đăng xuất: vẫn hiện Tổng Quan với số liệu 0 ₫, Console báo hàng loạt lỗi 401 | Mọi trang |
