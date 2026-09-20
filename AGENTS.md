# Quy Tắc Dành Cho AI Assistant (Agent Rules)

## ⛔ Quy Tắc Git & Push Code lên GitHub
- **TUYỆT ĐỐI KHÔNG** tự ý thực hiện lệnh `git push` mã nguồn lên GitHub (hoặc bất kỳ remote repository nào) trừ khi người dùng đưa ra yêu cầu/lệnh rõ ràng và trực tiếp.
- Chỉ chỉnh sửa, chạy thử và kiểm thử mã nguồn ở môi trường cục bộ (Local).
- Khi sửa code xong, chỉ thông báo kết quả kiểm thử local và hỏi ý kiến người dùng nếu họ muốn push code lên GitHub.

## 🌐 QUY TẮC KIỂM THỬ & BROWSER AUTOMATION
- **Cho phép sử dụng Browser Automation** (Playwright, Chrome, Browser subagents/tools) khi người dùng yêu cầu (ví dụ qua lệnh `/browser`, kiểm tra luồng giao diện UI/E2E).
- Khi kiểm thử browser: thực hiện theo đúng các bước người dùng chỉ định, quan sát DOM/Console và báo cáo trung thực kết quả từng bước.
- Đối với các tác vụ phát triển thông thường không có yêu cầu browser trực tiếp, ưu tiên kiểm thử nhanh và ổn định bằng:
  1. Backend tests (`python -m unittest ...`, `pytest`, v.v.)
  2. Unit / Integration tests
  3. API / Live HTTP tests (dùng `FastAPI TestClient`, `urllib`, `requests`, `httpx`...)
  4. Database verification (kiểm tra trạng thái SQLite `app.db`, integrity, records)
  5. Frontend build validation (`npm run build`)
- **Trọng tâm phát triển:** Agent Core, Tool Registry, Natural-language argument resolution, Actual tool execution và UI/E2E verification khi được yêu cầu.

## 📌 6 NGUYÊN TẮC BẮT BUỘC KHI PHÁT TRIỂN & SỬA CODE

### 1. KHAI BÁO ĐẦY ĐỦ TRƯỚC KHI DÙNG
- Bất kỳ biến/state nào được dùng trong template (Vue) hoặc JSX, phải được khai báo VÀ khởi tạo giá trị mặc định hợp lệ (không để undefined) NGAY TRONG CÙNG 1 lần sửa — không được thêm vào template trước rồi "khai báo sau".
- Với object/form phức tạp (ví dụ `soulLampForm`, `editForm`...), khởi tạo đầy đủ TẤT CẢ các field mà template sẽ dùng tới, kể cả field chưa dùng ngay nhưng đã được tham chiếu ở đâu đó trong file.
- Nếu dùng Options API/Composition mixin, kiểm tra biến mới đã được thêm vào đúng chỗ (data(), computed, methods) và có `return` đầy đủ nếu dùng `setup()`. Nếu dùng `<script setup>`, kiểm tra biến được khai báo ở top-level của block, không lồng trong hàm khác khiến template không truy cập được.

### 2. KHÔNG SỬA/THÊM TRỰC TIẾP VÀO FILE DÙNG CHUNG QUÁ LỚN MÀ KHÔNG KIỂM TRA TOÀN DIỆN
- Dự án đang dùng file `App.vue` rất lớn chứa toàn bộ các trang. Bất kỳ lỗi nhỏ nào ở 1 phần cũng có thể làm sập toàn bộ ứng dụng (kể cả các phần không liên quan).
- Sau khi sửa xong 1 phần, PHẢI kiểm tra lại toàn bộ các trang khác trong web (không chỉ phần vừa sửa) để đảm bảo không có phần nào bị ảnh hưởng dây chuyền.
- Nếu tính năng mới đủ lớn (có form, modal, hoặc logic phức tạp riêng), cân nhắc tách thành 1 component Vue riêng (file `.vue` độc lập) thay vì nhồi thêm vào `App.vue`, để giảm rủi ro và dễ kiểm tra hơn.

### 3. KIỂM THỬ BUILD & GIAO DIỆN SẠCH
- Kiểm tra kết quả qua frontend `npm run build` không có lỗi bundling.
- Kiểm tra cú pháp template, biến định nghĩa đầy đủ.
- Khi có yêu cầu kiểm thử giao diện/browser, kiểm tra log Console và đảm bảo không có uncaught exception.

### 4. KIỂM THỬ LUỒNG CHỨC NĂNG BẰNG TEST SUITE & HTTP/E2E TESTS
- Chạy test suite tương ứng (`test_full_system_agent.py`, `test_conversational_financial_ai.py`, `test_conversational_confirmation.py`, `test_suite.py`...).
- Khi kiểm thử UI/E2E với Browser Automation theo yêu cầu, ghi nhận chi tiết trạng thái từng bước và console.
- Liệt kê rõ trong báo cáo: đã test những gì, kết quả cụ thể ra sao bằng output kiểm thử thực tế (pass/fail, execution time, assertions).

### 5. THẬN TRỌNG VỚI CÁC THAY ĐỔI ẢNH HƯỞNG DIỆN RỘNG
- Với các thay đổi liên quan tới: cấu trúc database (thêm/sửa cột, bảng), biến toàn cục dùng ở nhiều trang, hoặc theme/CSS variables dùng chung — PHẢI đặc biệt cẩn trọng vì phạm vi ảnh hưởng rộng hơn bình thường.
- Với thay đổi database: luôn viết dưới dạng migration không phá hủy dữ liệu cũ (dùng ALTER TABLE thêm cột thay vì xóa/tạo lại bảng), và kiểm tra dữ liệu cũ vẫn đọc được bình thường sau khi thêm cột mới.
- Nếu không chắc chắn 1 thay đổi có ảnh hưởng tới phần nào khác của code hay không, hãy tìm kiếm (grep/search) toàn bộ dự án xem biến/hàm/API đó được dùng ở những đâu trước khi sửa, thay vì chỉ sửa đúng 1 chỗ đang nhìn thấy.

### 6. BÁO CÁO RÕ RÀNG, TRUNG THỰC
- Nếu trong quá trình sửa phát hiện thêm lỗi khác không thuộc phạm vi yêu cầu ban đầu, phải báo cáo rõ cho người dùng biết (không tự ý sửa luôn nếu thay đổi lớn, hoặc sửa xong thì phải liệt kê rõ đã sửa thêm gì ngoài yêu cầu).
- Nếu có phần nào chưa chắc chắn đã sửa triệt để, hoặc còn nghi ngờ có thể phát sinh lỗi trong 1 số trường hợp hiếm, phải nói rõ điều đó thay vì báo "hoàn thành" một cách tuyệt đối.


