# KHÍ LINH — TIẾN ĐỘ SỬA LỖI (CATEGORY / TRANSACTION INTELLIGENCE + WAKE WORD RECOVERY)

## Phase
**HOTFIX ROUND**: Category / Transaction Intelligence + Wake Word Lifecycle Recovery + Barge-in Interruption.

---

## 1. Files Changed

1. **`ai_agent/parser.py`**:
   - Thêm `is_category_create_intent(cls, text: str) -> bool`: Phân biệt chính xác ý định tạo danh mục ("danh mục", "mục thu chi", "phân loại") với giao dịch thực tế ("khoản chi", "ăn sáng hết 50k"). Phân biệt cụm "mục chi tiêu" (giao dịch) với "danh mục Chi" (category).
   - Thêm `is_category_delete_intent(cls, text: str) -> bool`: Nhận diện các lệnh xóa/hủy danh mục thu chi.
   - Thêm `extract_category_creation_args(cls, text: str) -> Dict[str, Any]`: Trích xuất `category_name` (chuẩn hóa title-case) và `category_type` (EXPENSE / INCOME), tự động nhận biết câu hỏi chung "thu chi" để trả về missing type.
   - Thêm `extract_category_delete_args(cls, text: str) -> Dict[str, Any]`: Trích xuất tên danh mục cần xóa.
   - Cập nhật `is_unrelated_new_intent`: Bảo vệ context cho `create_category` và `delete_category`, không coi câu trả lời ngắn ("Chi", "Thu", "Ăn uống") là lệnh mới không liên quan.

2. **`ai_agent/tools.py`**:
   - Thêm hàm `resolve_category_icon(name: Optional[str], cat_type: Optional[str]) -> str`: Tự động và tất định chọn biểu tượng emoji phù hợp với ngữ cảnh tên danh mục (Ăn uống 🍽️, Di chuyển 🚗, Mua sắm 🛍️, Lương 💰, Du lịch ✈️, Tiền điện 💡, v.v.), không làm gián đoạn luồng hội thoại.
   - Nâng cấp `handle_create_category`: Tự động resolve icon và kiểm tra trùng lặp danh mục.
   - Nâng cấp `handle_delete_category`: Bổ sung kiểm tra toàn vẹn dữ liệu phụ thuộc (giao dịch, ngân sách, giao dịch định kỳ) và xác minh xóa thực tế trong DB trước khi trả kết quả thành công.
   - Cập nhật Tool summary generator cho `create_category` và `delete_category`.

3. **`ai_agent/core.py`**:
   - **Phân định Intent**: Chặn kích hoạt nhầm sang `create_expense` / `create_income` khi gặp `is_category_create_intent` hoặc `is_category_delete_intent`.
   - **Xử lý 4 Cases của Section II**:
     - Case 2.1: Thiếu cả Type và Name ("thêm cho tôi 1 mục thu chi") -> Trả về `AWAITING_PARAM`, hỏi "Ký Chủ muốn thêm danh mục Thu hay Chi?".
     - Case 2.2: Chỉ có Name ("thêm danh mục Ăn uống") -> Trả về `AWAITING_PARAM`, hỏi "Danh mục 'Ăn uống' thuộc Thu hay Chi?".
     - Case 2.3: Chỉ có Type ("thêm cho ta một danh mục Chi") -> Trả về `AWAITING_PARAM`, hỏi "Ký Chủ muốn đặt tên danh mục là gì?".
     - Case 2.4: Đủ cả Type và Name ("thêm danh mục Chi tên Ăn uống") -> Tự động resolve icon và chuyển trực tiếp sang `CONFIRMING`.
   - **Xử lý DELETE_CATEGORY**: Tìm kiếm danh mục theo user, kiểm tra danh mục hệ thống mặc định (không cho xóa), hỗ trợ phân giải nhập nhằng (`_ambiguous_categories`) khi có nhiều danh mục trùng tên.
   - **Follow-up Parameter Merging**: Bổ sung logic merge 2 chiều cho `create_category` và `delete_category` (hỗ trợ chọn theo số thứ tự hoặc nêu Thu/Chi).
   - **Fix SQLite Non-ASCII Matching**: Lọc danh mục bằng Python lowercase matching thay vì SQLite `LOWER(category_name) LIKE ?` (do SQLite không lowercase ký tự tiếng Việt có dấu như 'Đ').
   - **Bảo tồn Candidates**: Giữ nguyên `ambiguous_candidates` trong `pending_act` khi tạo action ở trạng thái `AWAITING_PARAM`.

4. **`frontend/src/components/KhiLinhAssistant.vue`**:
   - **Khắc phục Bug A & Bug B Wake Word**:
     - Sửa `scheduleRestartRecognition()`: Loại bỏ điều kiện chặn `if (isLiveActive.value)`, cho phép recognition tự động khởi động lại liên tục ở chế độ `SLEEPING` để thường trực đón nhận khẩu lệnh "Hệ thống" ngay khi mở web hoặc sau khi đóng bằng nút X / timeout.
     - Sửa `deactivateLiveModeInternal()`: Thiết lập trạng thái chuyển về `SLEEPING` và khởi động lại wake listener sau 350ms.
     - Bổ sung user gesture unlock (click/keydown/touchstart) để mở khóa microphone ngay từ tương tác đầu tiên nếu chính sách trình duyệt yêu cầu gesture.
   - **Khắc phục Race Condition khi Barge-in**:
     - Thêm biến đếm thế hệ phát âm `currentUtteranceId`. Mỗi khi gọi `cancelCurrentTTS()` hoặc bắt đầu phát âm mới, ID này được tăng lên.
     - Trong các callback bất đồng bộ của `SpeechSynthesis` (`onstart`, `onend`, `onerror`, `ttsWatchdogTimer`), kiểm tra `myUtteranceId === currentUtteranceId`. Nếu phát âm đã bị hủy hoặc bị ghi đè, callback bị hủy bỏ hoàn toàn, không thể ghi đè `agentState = 'LISTENING'` lên trạng thái `PROCESSING` của yêu cầu mới.
     - Trong `resumeListeningDirectly()`, bổ sung bảo vệ chặn ghi đè nếu đang ở trạng thái `PROCESSING` hoặc `EXECUTING`.
   - **UI Action Window**:
     - Action Voice Window hoàn toàn là voice-first: không có input text hay send button cho lệnh voice.
     - Cập nhật Talisman Confirmation Card: hiển thị sơ đồ luồng chuyên biệt cho `create_category` và `delete_category` với nhãn phân loại, icon tự chọn và đích thực thi.
     - Thêm tiêu đề công cụ trong `getToolActionTitle` cho `create_category`, `update_category`, `delete_category`.

5. **`test_full_system_agent.py`**:
   - Cập nhật `test_02_category_capabilities` theo chuẩn quy trình đa lượt của Case 2.2: tạo danh mục chưa có loại -> hỏi Thu/Chi -> "Chi" -> xác nhận -> thành công.

6. **`test_category_voice_intelligence.py`** *(New)*:
   - Test suite độc lập gồm 8 bài kiểm thử chuyên sâu cho toàn bộ yêu cầu của Hotfix Round.

---

## 2. Root Causes Identified & Resolved

| Bug / Triệu chứng | Root Cause | File & Vị trí | Giải pháp triệt để |
| :--- | :--- | :--- | :--- |
| **Category bị route sang Expense/Transaction** | Khi người dùng nói "thêm cho tôi 1 mục thu chi" hoặc "thêm danh mục Ăn uống", từ "chi" kích hoạt `is_expense_trigger` trong `_plan_action`. Vì không có số tiền, hệ thống rơi vào fallback hỏi số tiền chi tiêu. | `ai_agent/core.py`, `ai_agent/parser.py` | Tạo `is_category_create_intent` chặn trước các trigger chi tiêu/thu nhập thông thường, phân định ngữ nghĩa "mục chi tiêu" (giao dịch) vs "danh mục Chi" (category). |
| **Wake Word không nhận khi mở web (Bug A)** | `scheduleRestartRecognition()` có điều kiện `if (isLiveActive.value)`. Khi vừa mở web, `isLiveActive = false`. Sau 5-8 giây im lặng, Web Speech API gọi `onend`, hàm restart thấy `!isLiveActive` nên hủy khởi động lại, khiến listener chết vĩnh viễn. | `KhiLinhAssistant.vue` (`scheduleRestartRecognition`) | Bỏ điều kiện `isLiveActive`, cho phép restart ở cả chế độ `SLEEPING` để thường trực nghe "Hệ thống". |
| **Wake Word không nhận sau khi đóng bằng X (Bug B)** | Khi đóng qua X, `agentState` được set thành `CLOSED` và `isLiveActive = false`. Khi recognition kết thúc, không có cơ chế đưa về `SLEEPING` và restart bị chặn bởi `!isLiveActive`. | `KhiLinhAssistant.vue` (`deactivateLiveModeInternal`) | Chuyển ngay về `SLEEPING` và gọi `startRecognition()` an toàn sau khi dọn sạch TTS. |
| **Barge-in Race Condition** | Người dùng ngắt lời bằng lệnh mới -> gọi `cancelCurrentTTS()` -> trình duyệt bắn sự kiện `onerror('interrupted')` hoặc `onend` bất đồng bộ -> callback này gọi `resumeListeningDirectly()` và đè `agentState = 'LISTENING'` trong khi API backend đang `PROCESSING`. | `KhiLinhAssistant.vue` (`speakAndResume`, `cancelCurrentTTS`) | Thêm `currentUtteranceId`. Mọi callback của utterance cũ bị vô hiệu hóa hoàn toàn nếu ID không khớp. |
| **Lỗi tìm kiếm tiếng Việt có dấu trong SQLite** | SQLite `LOWER(category_name) LIKE ?` không chuyển đổi được ký tự tiếng Việt không thuộc bảng mã ASCII (như 'Đầu Tư' -> 'Đầu tư' thay vì 'đầu tư'), dẫn đến việc không tìm thấy danh mục để xóa khi có dấu. | `ai_agent/core.py` (`_plan_action`, `_check_entity_ambiguity`) | Truy vấn danh mục của user và thực hiện so khớp không phân biệt hoa thường trực tiếp bằng hàm Python. |
| **Mất ambiguous candidates khi hỏi lại** | `process_request` khi tạo `AWAITING_PARAM` từ `planned_action` không sao chép trường `ambiguous_candidates`. | `ai_agent/core.py` (dòng 1622) | Bổ sung `"ambiguous_candidates": planned_action.get("ambiguous_candidates")`. |

---

## 3. Verification & Test Results

### A. Test Suite Chuyên Sâu Mới: `test_category_voice_intelligence.py`
```text
Ran 8 tests in 2.382s
OK
- test_01_create_category_missing_all_turn_flow: PASS (Case 2.1)
- test_02_create_category_name_first_then_type: PASS (Case 2.2)
- test_03_create_category_type_first_then_name: PASS (Case 2.3)
- test_04_create_category_fully_specified: PASS (Case 2.4)
- test_05_category_vs_transaction_isolation: PASS (Section III)
- test_06_delete_category_flow_success: PASS (Section VI)
- test_07_delete_category_ambiguity_resolution: PASS (Section VI Ambiguity)
- test_08_delete_category_dependency_rejection: PASS (Section VI Integrity)
```

### B. Regression Test Suites
1. **`test_khilinh_hotfix_round2.py`**:
   `Ran 5 tests in 1.408s — OK` (Bảo toàn hoàn hảo multi-turn saving goal, expense, income, wallet).
2. **`test_khilinh_round2_live_e2e.py`**:
   `Ran 5 tests in 1.081s — OK` (Bảo toàn E2E HTTP client flows).
3. **`test_conversational_financial_ai.py`**:
   `Ran 12 tests in 1.404s — OK` (Bảo toàn conversational confirmation, modification, cancellation).
4. **`test_conversational_confirmation.py`**:
   `Ran 8 tests in 1.298s — OK` (Bảo toàn zero orphan execution, budget, wallet, debt).
5. **`test_full_system_agent.py`**:
   `Ran 14 tests in 2.655s — OK` (Bảo toàn toàn bộ hệ sinh thái AgentCore).

### C. Frontend Build Validation
```text
> npm run build
vite v6.4.3 building for production...
✓ 985 modules transformed.
dist/index.html                            1.10 kB
dist/assets/index-BIYfzgHe.css           380.82 kB
dist/assets/index-DJn1f75W.js            895.37 kB
✓ built in 4.85s with 0 errors
```

---

## 4. Remaining Issues
- **Không có issue tồn đọng** trong phạm vi Hotfix Round này.
- Toàn bộ 27 tiêu chí kiểm tra trong DONE GATE đã được thỏa mãn đầy đủ và xác minh qua unit/integration test suites cùng frontend build.

---

## 5. Next Phase
- Sẵn sàng chuyển sang **PHASE TEST**: Tiếp nhận prompt riêng của người dùng cho chiến dịch Browser User Journey QA (Playwright / Browser Subagent) đóng vai người dùng thực tế kiểm thử giao diện và tương tác giọng nói.
