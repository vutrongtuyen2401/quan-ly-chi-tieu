# Quy Tắc Dành Cho AI Assistant (Agent Rules)

## ⛔ Quy Tắc Git & Push Code lên GitHub
- **TUYỆT ĐỐI KHÔNG** tự ý thực hiện lệnh `git push` mã nguồn lên GitHub (hoặc bất kỳ remote repository nào) trừ khi người dùng đưa ra yêu cầu/lệnh rõ ràng và trực tiếp.
- Chỉ chỉnh sửa, chạy thử và kiểm thử mã nguồn ở môi trường cục bộ (Local).
- Khi sửa code xong, chỉ thông báo kết quả kiểm thử local và hỏi ý kiến người dùng nếu họ muốn push code lên GitHub.

## 📌 6 NGUYÊN TẮC BẮT BUỘC KHI PHÁT TRIỂN & SỬA CODE

### 1. KHAI BÁO ĐẦY ĐỦ TRƯỚC KHI DÙNG
- Bất kỳ biến/state nào được dùng trong template (Vue) hoặc JSX, phải được khai báo VÀ khởi tạo giá trị mặc định hợp lệ (không để undefined) NGAY TRONG CÙNG 1 lần sửa — không được thêm vào template trước rồi "khai báo sau".
- Với object/form phức tạp (ví dụ `soulLampForm`, `editForm`...), khởi tạo đầy đủ TẤT CẢ các field mà template sẽ dùng tới, kể cả field chưa dùng ngay nhưng đã được tham chiếu ở đâu đó trong file.
- Nếu dùng Options API/Composition mixin, kiểm tra biến mới đã được thêm vào đúng chỗ (data(), computed, methods) và có `return` đầy đủ nếu dùng `setup()`. Nếu dùng `<script setup>`, kiểm tra biến được khai báo ở top-level của block, không lồng trong hàm khác khiến template không truy cập được.

### 2. KHÔNG SỬA/THÊM TRỰC TIẾP VÀO FILE DÙNG CHUNG QUÁ LỚN MÀ KHÔNG KIỂM TRA TOÀN DIỆN
- Dự án đang dùng file `App.vue` rất lớn chứa toàn bộ các trang. Bất kỳ lỗi nhỏ nào ở 1 phần cũng có thể làm sập toàn bộ ứng dụng (kể cả các phần không liên quan).
- Sau khi sửa xong 1 phần, PHẢI kiểm tra lại toàn bộ các trang khác trong web (không chỉ phần vừa sửa) để đảm bảo không có phần nào bị ảnh hưởng dây chuyền.
- Nếu tính năng mới đủ lớn (có form, modal, hoặc logic phức tạp riêng), cân nhắc tách thành 1 component Vue riêng (file `.vue` độc lập) thay vì nhồi thêm vào `App.vue`, để giảm rủi ro và dễ kiểm tra hơn.

### 3. KIỂM TRA CONSOLE TRƯỚC KHI BÁO ĐÃ XONG
- Sau MỌI lần sửa code, bắt buộc phải mở trình duyệt, tải lại toàn bộ ứng dụng, và kiểm tra tab Console.
- Nếu có BẤT KỲ dòng lỗi đỏ (Uncaught, TypeError, ReferenceError...) hoặc cảnh báo vàng dạng `[Vue warn]: Property ... was accessed but is not defined` xuất hiện — dù không liên quan trực tiếp tới phần vừa sửa — PHẢI dừng lại và sửa hết trước khi báo cáo hoàn thành, KHÔNG được bỏ qua với lý do "không liên quan tới yêu cầu hiện tại".
- Việc kiểm tra Console không chỉ ở trang vừa sửa, mà phải thử qua ít nhất các trang chính: Đăng nhập, Tổng Quan, Giao Dịch, Linh Nhãn OCR, Khí Linh AI, Quản Lý Tài Khoản.

### 4. KIỂM THỬ LUỒNG CHỨC NĂNG LIÊN QUAN, KHÔNG CHỈ PHẦN VỪA SỬA
- Trước khi báo "đã hoàn thành", phải tự kiểm thử thực tế bằng cách thao tác trực tiếp trên giao diện (không chỉ đọc code rồi suy đoán là đúng): đăng nhập thử, bấm nút thử, nhập dữ liệu thử.
- Liệt kê rõ trong báo cáo: đã test những gì, kết quả cụ thể ra sao — không được chỉ nói chung chung "đã hoạt động tốt" mà không có bằng chứng cụ thể (ví dụ log Console sạch, ảnh chụp, hoặc mô tả hành vi quan sát được).

### 5. THẬN TRỌNG VỚI CÁC THAY ĐỔI ẢNH HƯỞNG DIỆN RỘNG
- Với các thay đổi liên quan tới: cấu trúc database (thêm/sửa cột, bảng), biến toàn cục dùng ở nhiều trang, hoặc theme/CSS variables dùng chung — PHẢI đặc biệt cẩn trọng vì phạm vi ảnh hưởng rộng hơn bình thường.
- Với thay đổi database: luôn viết dưới dạng migration không phá hủy dữ liệu cũ (dùng ALTER TABLE thêm cột thay vì xóa/tạo lại bảng), và kiểm tra dữ liệu cũ vẫn đọc được bình thường sau khi thêm cột mới.
- Nếu không chắc chắn 1 thay đổi có ảnh hưởng tới phần nào khác của code hay không, hãy tìm kiếm (grep/search) toàn bộ dự án xem biến/hàm/API đó được dùng ở những đâu trước khi sửa, thay vì chỉ sửa đúng 1 chỗ đang nhìn thấy.

### 6. BÁO CÁO RÕ RÀNG, TRUNG THỰC
- Nếu trong quá trình sửa phát hiện thêm lỗi khác không thuộc phạm vi yêu cầu ban đầu, phải báo cáo rõ cho người dùng biết (không tự ý sửa luôn nếu thay đổi lớn, hoặc sửa xong thì phải liệt kê rõ đã sửa thêm gì ngoài yêu cầu).
- Nếu có phần nào chưa chắc chắn đã sửa triệt để, hoặc còn nghi ngờ có thể phát sinh lỗi trong 1 số trường hợp hiếm, phải nói rõ điều đó thay vì báo "hoàn thành" một cách tuyệt đối.

