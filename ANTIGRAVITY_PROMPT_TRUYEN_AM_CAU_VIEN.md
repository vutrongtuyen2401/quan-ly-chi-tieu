# Kế hoạch & Prompt Antigravity — Chức năng "Truyền Âm Cầu Viện"

> **Góp ý của giảng viên:** khi người dùng sắp hết tiền thì hiện một danh sách gợi ý số điện thoại. Ví dụ: sinh viên tới cuối tháng có dấu hiệu sắp hết tiền thì gọi về cho phụ huynh xin thêm tiền tiêu.
>
> File này gồm 4 phần:
> - **Phần 1**: định hình chức năng (để bạn hiểu và trình bày với giảng viên)
> - **Phần 2**: kế hoạch triển khai theo giai đoạn
> - **Phần 3**: các prompt dán cho Antigravity, **mỗi lần một prompt**
> - **Phần 4**: kịch bản demo và checklist nghiệm thu

---

## PHẦN 1 — ĐỊNH HÌNH CHỨC NĂNG

### 1.1. Tên gọi (theo chủ đề tu tiên của app)

| Thành phần | Tên trong app | Nghĩa dễ hiểu |
|---|---|---|
| Cả chức năng | **Truyền Âm Cầu Viện** | Gọi người thân hỗ trợ khi sắp hết tiền |
| Danh bạ | **Danh Bạ Hộ Đạo** | Danh sách số điện thoại người thân/người hỗ trợ |
| Cảnh báo | **Linh Thạch Sắp Cạn** | Banner cảnh báo sắp hết tiền |
| Mức WARNING | *Linh thạch hao hụt* | Có dấu hiệu không đủ tiền tới kỳ nhận tiền |
| Mức CRITICAL | *Linh thạch cạn kiệt* | Gần hết hoặc đã hết tiền |

Trong giao diện luôn kèm chữ thường dễ hiểu (ví dụ: "Danh Bạ Hộ Đạo — người thân có thể hỗ trợ bạn"), để giảng viên đọc là hiểu ngay.

### 1.2. User story

> Là một sinh viên, tôi lưu sẵn số điện thoại của bố, mẹ và người thân. Khi số dư của tôi không đủ chi tiêu tới ngày được gửi tiền tiếp theo, app tự cảnh báo, cho biết tôi còn bao nhiêu tiền, đủ tiêu thêm mấy ngày, thiếu khoảng bao nhiêu, và hiện danh sách người thân để tôi bấm **Gọi** hoặc **Nhắn tin** (tin nhắn soạn sẵn) xin thêm tiền.

### 1.3. Luồng hoạt động

```
[Hồ sơ] Thêm người thân (tên, quan hệ, SĐT, thứ tự ưu tiên)
        + Cài đặt: ngưỡng cảnh báo, ngày nhận tiền hằng tháng
                        │
                        ▼
[Backend] Mỗi lần tải dữ liệu / thêm-sửa-xóa giao dịch / đổi ví
          → tính "Chỉ số sắp cạn" (số dư, tốc độ chi, số ngày còn lại, khoản cố định sắp tới)
                        │
          SAFE ─────────┼──────── WARNING / CRITICAL
          (không hiện)  │
                        ▼
[Tổng Quan] Banner "Linh Thạch Sắp Cạn": lý do bằng số liệu + số tiền gợi ý xin
            + danh sách người thân: 📞 Gọi  💬 Nhắn tin  📋 Sao chép số
            + "Để sau" (ẩn tới hết ngày)  + nếu chưa có ai: "Thêm người thân"
                        │
                        ▼
(Tùy chọn) Nhận tiền → nút "Ghi khoản thu" → mở tab Giao Dịch → banner tự biến mất
(Tùy chọn) Hỏi Khí Linh "sắp hết tiền thì gọi ai?" → trả lời bằng cùng số liệu
```

### 1.4. Quy tắc tính "sắp hết tiền" (xác định, không dùng AI đoán)

Tất cả tính ở backend, chung một hàm, để Dashboard và Khí Linh trả cùng một kết quả.

| Đại lượng | Cách tính |
|---|---|
| `total_balance` | Tổng `balance` tất cả ví của người dùng |
| `next_allowance_date` | Ngày nhận tiền kế tiếp **sau hôm nay** theo `allowance_day` (mặc định 1 = đầu tháng). Ví dụ hôm nay 09/10, `allowance_day = 1` → 01/11; `allowance_day = 15` → 15/10 |
| `days_left` | `next_allowance_date − hôm nay` (tính cả hôm nay). Ví dụ 09/10 → 01/11 = 23 ngày |
| `avg_daily_expense` | Nếu từ đầu tháng tới nay ≥ 7 ngày và đã có chi: tổng chi tháng này ÷ số ngày đã qua. Ngược lại: tổng chi 30 ngày gần nhất ÷ 30. Không có chi → 0 |
| `upcoming_fixed` | Tổng (a) giao dịch định kỳ **EXPENSE đang bật** có lần chạy rơi vào [hôm nay, `next_allowance_date`) — định kỳ hằng tuần có thể tính nhiều lần — và (b) khoản **nợ BORROW chưa trả** có `due_date` trong khoảng đó |
| `projected_need` | `avg_daily_expense × days_left + upcoming_fixed` |
| `runway_days` | `total_balance ÷ avg_daily_expense` (null nếu `avg_daily_expense = 0`) |
| `shortfall` | `max(0, projected_need − total_balance)` |
| `suggested_amount` | `max(shortfall, threshold − total_balance)` làm tròn **lên** bội số 50.000 ₫; không âm |

**Phân mức:**

- **CRITICAL** nếu một trong các điều kiện: `total_balance ≤ 0`; hoặc `runway_days < days_left × 0.5`; hoặc `total_balance < threshold × 0.5`.
- **WARNING** nếu không CRITICAL và: `total_balance < threshold`; hoặc `shortfall > 0`.
- **SAFE** trong các trường hợp còn lại.
- **NO_DATA** nếu người dùng chưa có ví nào (xét trước tất cả các mức trên). Banner không hiện.

Mỗi mức kèm danh sách `reasons` viết bằng tiếng Việt có số liệu, ví dụ:
- "Số dư 420.000 ₫ thấp hơn ngưỡng cảnh báo 500.000 ₫."
- "Với mức chi trung bình 85.000 ₫/ngày, số dư chỉ đủ khoảng 5 ngày, trong khi còn 23 ngày nữa mới tới ngày nhận tiền (01/11)."
- "Có 2 khoản cố định sắp tới hạn, tổng 1.200.000 ₫."

> Đây là **ước tính gần đúng** (giống cách tính "runway" của các app tài chính). Khi trình bày với giảng viên, nói rõ công thức này, không nói là "AI dự đoán".

### 1.5. Dữ liệu cần lưu

**Bảng mới `support_contacts`** (Danh Bạ Hộ Đạo):

| Cột | Kiểu | Ghi chú |
|---|---|---|
| id | INTEGER PK | |
| user_id | INTEGER NOT NULL FK users | Chỉ chủ sở hữu được xem/sửa |
| contact_name | TEXT NOT NULL | 1–50 ký tự |
| relationship | TEXT CHECK IN ('FATHER','MOTHER','SIBLING','RELATIVE','FRIEND','OTHER') | Hiển thị: Bố, Mẹ, Anh/Chị/Em, Họ hàng, Bạn bè, Khác |
| phone | TEXT NOT NULL | Lưu dạng chuẩn hóa `0xxxxxxxxx` |
| priority | INTEGER DEFAULT 1 | Số nhỏ hiện trước |
| note | TEXT DEFAULT '' | Ví dụ: "Gọi sau 19h" |
| is_active | INTEGER DEFAULT 1 | Tắt tạm thời không xóa |
| created_at | TEXT | |

Ràng buộc: tối đa **10** người/tài khoản; không trùng số trong cùng tài khoản; chỉ số di động VN: sau khi bỏ khoảng trắng, dấu chấm, gạch ngang thì khớp `^(0|\+84|84)(3|5|7|8|9)\d{8}$`, rồi chuẩn hóa về `0xxxxxxxxx`.

**Bảng mới `support_settings`** (1 dòng/người dùng, tạo mặc định khi đọc lần đầu):

| Cột | Mặc định | Ghi chú |
|---|---|---|
| user_id | PK, FK users | |
| enabled | 1 | Tắt thì không hiện banner |
| low_balance_threshold | 500000 | 0 – 1.000.000.000 |
| allowance_day | 1 | 1–28 (ngày nhận tiền hằng tháng) |
| message_template | '' | Rỗng = dùng mẫu mặc định |
| updated_at | | |

Chỉ **thêm bảng mới bằng `CREATE TABLE IF NOT EXISTS`**, không sửa bảng cũ → dữ liệu cũ an toàn.

**Mẫu tin nhắn mặc định** (placeholder do backend thay):

> `{xung_ho} ơi, tháng này con chi tiêu hơi quá tay, hiện chỉ còn {so_du}, mà còn {so_ngay} ngày nữa mới tới ngày nhận tiền. {xung_ho} cho con xin thêm khoảng {so_tien} được không ạ? Con cảm ơn {xung_ho} ạ!`

`{xung_ho}` lấy theo quan hệ: FATHER → "Bố", MOTHER → "Mẹ", các quan hệ khác → tên người đó.

### 1.6. Giao diện

1. **Hồ sơ (modal và tab Hồ sơ)**: thêm khối **"Danh Bạ Hộ Đạo"** ngay dưới khối Bản Mệnh Hồn Đăng:
   - Danh sách dạng **dòng** (không lưới card): quan hệ · tên · SĐT · ghi chú · nút Sửa / Xóa / bật-tắt.
   - Nút "+ Thêm người thân" mở form gọn (tên, quan hệ, SĐT, ưu tiên, ghi chú).
   - Phần **Cài đặt cảnh báo**: bật/tắt, ngưỡng cảnh báo, ngày nhận tiền hằng tháng, mẫu tin nhắn (có nút "Dùng mẫu mặc định").
2. **Tổng Quan**: banner **"Linh Thạch Sắp Cạn"** ở đầu trang, chỉ hiện khi WARNING/CRITICAL và `enabled`:
   - Một dải duy nhất, viền trái vàng (WARNING) hoặc đỏ (CRITICAL), **không phải card lồng card**.
   - Dòng chính: "Còn 420.000 ₫ · đủ khoảng 5 ngày · còn 23 ngày tới 01/11 · nên xin thêm khoảng 1.550.000 ₫".
   - Danh sách lý do (`reasons`).
   - Danh sách người thân theo ưu tiên, mỗi dòng: tên + quan hệ + SĐT + **📞 Gọi** (`tel:`) + **💬 Nhắn tin** (`sms:` kèm nội dung soạn sẵn) + **📋 Sao chép** (sao chép SĐT; có thêm nút sao chép nội dung tin nhắn).
   - Chưa có người thân nào → hiện "Bạn chưa lưu số người thân nào" + nút **Thêm người thân** (mở modal Hồ sơ).
   - Nút **"Để sau"**: ẩn tới hết ngày (localStorage, bọc try/catch). Nếu mức tăng từ WARNING lên CRITICAL thì hiện lại.
3. Trên máy tính, `tel:`/`sms:` có thể không mở được ứng dụng gọi → luôn hiện số rõ ràng và có nút Sao chép. Trên điện thoại bấm Gọi là mở trình gọi ngay.

**Phong cách:** giữ nguyên giao diện Celestial Treasury hiện có (màu, font Inter, icon Material Symbols, thuật ngữ tu tiên), theo nguyên tắc "ít card" trong `STITCH_PROMPT_THIET_KE_LAI.md`. **Không thêm tab thứ 12**, không thiết kế lại trang khác.

### 1.7. Ngoài phạm vi (nói rõ với giảng viên nếu được hỏi)

- App **không tự gọi điện hay tự gửi SMS** (web app không có quyền đó, và không nên gửi thay người dùng). App chỉ mở trình gọi/nhắn tin của điện thoại với số và nội dung soạn sẵn; người dùng tự bấm gọi/gửi.
- Không gửi thông báo đẩy khi đóng app (có thể là hướng phát triển sau).
- Không chia sẻ danh bạ cho admin; trang Phân Quyền không thấy số điện thoại người thân.

---

## PHẦN 2 — KẾ HOẠCH TRIỂN KHAI

| Giai đoạn | Nội dung | File chính | Kết quả kiểm tra |
|---|---|---|---|
| **1. Backend** | 2 bảng mới, CRUD danh bạ, cài đặt, hàm tính `compute_low_funds_status`, endpoint trạng thái | `main.py` | Test mới `test_support_contacts.py` pass |
| **2. Frontend — Danh bạ** | Component `SupportContactsCard.vue` gắn vào `ProfileView.vue`; state + API trong `App.vue` | `components/support/`, `ProfileView.vue`, `App.vue` | `npm run build` sạch |
| **3. Frontend — Banner** | Component `LowFundsAlert.vue` đặt trên `DashboardView` trong `App.vue`; tải lại trạng thái mỗi khi dữ liệu tài chính đổi | `components/support/`, `App.vue` | Build sạch; banner đúng mức với dữ liệu test |
| **4. (Tùy chọn) Khí Linh** | Tool READ `low_funds_support` dùng chung hàm tính; câu hỏi "sắp hết tiền", "gọi ai xin tiền" | `ai_agent/tools.py`, `ai_agent/core.py` | Test agent pass, tool không có quyền ghi |
| **5. (Tùy chọn) Khép vòng** | Nút "Đã nhận tiền → Ghi khoản thu" chuyển sang tab Giao Dịch | `LowFundsAlert.vue`, `App.vue` | Thêm thu nhập → banner biến mất |
| **6. Kiểm thử tổng** | Chạy lại test cũ, build, test API sống, kiểm tra 11 trang không vỡ | — | Báo cáo trung thực |

API mới:

| Method | Path | Mô tả |
|---|---|---|
| GET | `/api/support-contacts` | Danh sách người thân của tôi (sắp theo priority, id) |
| POST | `/api/support-contacts` | Thêm (validate, chuẩn hóa SĐT, tối đa 10, không trùng) |
| PUT | `/api/support-contacts/{id}` | Sửa (chỉ của mình; người khác → 404) |
| DELETE | `/api/support-contacts/{id}` | Xóa (chỉ của mình; người khác → 404) |
| GET | `/api/support-settings` | Lấy cài đặt (chưa có → trả mặc định) |
| PUT | `/api/support-settings` | Cập nhật cài đặt (validate khoảng giá trị) |
| GET | `/api/support/low-funds-status` | Trạng thái sắp cạn + người thân đang bật + tin nhắn soạn sẵn từng người |

Dạng response `GET /api/support/low-funds-status`:

```json
{
  "enabled": true,
  "level": "CRITICAL",
  "total_balance": 420000,
  "avg_daily_expense": 85000,
  "days_left": 23,
  "next_allowance_date": "2026-11-01",
  "runway_days": 4.9,
  "upcoming_fixed": 0,
  "projected_need": 1955000,
  "shortfall": 1535000,
  "suggested_amount": 1550000,
  "threshold": 500000,
  "reasons": ["Số dư 420.000 ₫ thấp hơn ngưỡng cảnh báo 500.000 ₫.", "..."],
  "contacts": [
    {"id": 1, "contact_name": "Nguyễn Văn A", "relationship": "FATHER", "relationship_label": "Bố",
     "phone": "0912345678", "priority": 1, "note": "", "message": "Bố ơi, tháng này con ..."}
  ]
}
```

---

## PHẦN 3 — PROMPT CHO ANTIGRAVITY

### Cách dùng

1. Dán **Prompt 0** trước (bối cảnh chung), rồi lần lượt **Prompt 1 → 2 → 3**. Mỗi prompt xong, đọc báo cáo của Antigravity, tự chạy thử, rồi mới dán prompt tiếp theo.
2. Prompt 4 (Khí Linh) và Prompt 5 (khép vòng) là **tùy chọn**, làm nếu còn thời gian.
3. Cuối cùng dán **Prompt 6** để kiểm thử tổng.
4. Đính kèm file này (`ANTIGRAVITY_PROMPT_TRUYEN_AM_CAU_VIEN.md`) cho Antigravity đọc ở Prompt 0. Các prompt dưới đây nói "xem Phần 1" là phần trong file này.

---

### PROMPT 0 — Bối cảnh chung (dán đầu tiên)

```
Bạn đang làm việc trên dự án "Càn Khôn Linh Thạch Các" (web quản lý chi tiêu cá nhân, chủ đề tu tiên, toàn bộ tiếng Việt).
Stack: backend FastAPI + SQLite một file `main.py` (DB `app.db`, bảng tạo trong `init_db()`), AI agent ở `ai_agent/` (tools.py có ToolRegistry), frontend Vue 3 + Vite ở `frontend/`. `frontend/src/App.vue` (~5000 dòng) giữ toàn bộ state và mọi lời gọi API (axios instance `api`); các component trong `frontend/src/components/**` chỉ nhận props và emit sự kiện, không tự gọi API.

TRƯỚC KHI LÀM, BẮT BUỘC đọc: `AGENTS.md`, `.agents/rules/*.md`, `.agents/skills/feature-development/SKILL.md`, `.agents/skills/database-change/SKILL.md`, và file `ANTIGRAVITY_PROMPT_TRUYEN_AM_CAU_VIEN.md` (bản đặc tả chức năng tôi đính kèm).

NHIỆM VỤ TỔNG: xây chức năng "Truyền Âm Cầu Viện" theo góp ý của giảng viên: khi người dùng có dấu hiệu sắp hết tiền (ví dụ sinh viên cuối tháng), app hiện danh sách số điện thoại người thân đã lưu (bố, mẹ...) để gọi/nhắn tin xin thêm tiền. Đặc tả chi tiết nằm ở Phần 1 và Phần 2 của file trên. Làm đúng đặc tả, không tự thêm tính năng ngoài đặc tả.

QUY TẮC CỨNG:
1. KHÔNG `git push`, KHÔNG commit trừ khi tôi yêu cầu. Working tree đang có thay đổi chưa commit ở nhiều component (DashboardView, BudgetsView, CategoriesView, DebtsView, SavingGoalsView, StatisticsView, AdminStatsRow) — đó là việc khác đang làm dở, KHÔNG được revert, format lại, hay sửa các file đó (trừ khi prompt bảo rõ).
2. Database: chỉ THÊM bảng mới bằng `CREATE TABLE IF NOT EXISTS` trong `init_db()`. Không DROP, không sửa/xóa cột bảng cũ, không reset `app.db`. Trước khi đụng DB thật, sao lưu `app.db` thành `app.db.before_support_contacts.bak`.
3. Không tạo dữ liệu tài chính giả hay số điện thoại giả trong `app.db`. Dữ liệu mẫu chỉ được dùng trong DB tạm của test.
4. Bảo mật: mọi endpoint mới dùng `Depends(get_current_user)`; mọi truy vấn lọc theo `user_id`; truy cập bản ghi của người khác trả 404. Không log số điện thoại. Admin endpoints không trả danh bạ.
5. Mọi tính toán tiền là xác định (deterministic), không gọi Gemini/AI để tính.
6. Giao diện: giữ nguyên phong cách Celestial Treasury hiện có (dùng biến CSS trong `frontend/src/assets/styles/tokens.css`, font Inter, Material Symbols Outlined), nguyên tắc "ít card": không card lồng card, danh sách hiển thị dạng dòng. KHÔNG thêm tab mới, KHÔNG thiết kế lại trang khác.
7. Vue: mọi biến/state dùng trong template phải được khai báo và khởi tạo giá trị mặc định hợp lệ ngay trong cùng lần sửa; state mới trong `App.vue` phải được thêm vào object `return` của `setup()`. Form phải khởi tạo đủ mọi field.
8. Sau mỗi bước: chạy test liên quan + `npm run build` (trong `frontend/`), báo cáo trung thực bằng output thật (pass/fail, lỗi nếu có). Nếu phát hiện lỗi ngoài phạm vi thì báo cho tôi, không tự sửa lớn.

Bây giờ CHỈ đọc tài liệu và code liên quan (main.py: init_db, các endpoint wallets/transactions/recurring/debts, get_current_user; App.vue: loadAllData, checkBudgetAlerts và những chỗ gọi nó, khối return của setup; ProfileView.vue; tokens.css). Sau đó tóm tắt lại cho tôi: (a) bạn hiểu chức năng thế nào, (b) danh sách file sẽ sửa/tạo, (c) các điểm trong đặc tả còn mơ hồ. CHƯA sửa code.
```

---

### PROMPT 1 — Backend: bảng, API danh bạ, cài đặt, chỉ số sắp cạn

```
Làm GIAI ĐOẠN 1 (Backend) theo Phần 1.4, 1.5 và bảng API ở Phần 2 của ANTIGRAVITY_PROMPT_TRUYEN_AM_CAU_VIEN.md.

1. Sao lưu app.db → app.db.before_support_contacts.bak.
2. Trong `init_db()` của main.py thêm 2 bảng `support_contacts` và `support_settings` đúng đặc tả (CREATE TABLE IF NOT EXISTS, FOREIGN KEY tới users). Thêm index `idx_support_contacts_user` trên (user_id). Không đụng bảng cũ.
3. Pydantic models: SupportContactBody, SupportContactUpdateBody (mọi field Optional), SupportSettingsBody. Đặt cạnh các model khác.
4. Hàm tiện ích:
   - `normalize_vn_phone(raw: str) -> str`: bỏ khoảng trắng, '.', '-', '(', ')'; chấp nhận tiền tố 0 / +84 / 84; đầu số di động 3|5|7|8|9; trả về dạng 0xxxxxxxxx; sai → HTTPException 400 với thông báo tiếng Việt.
   - `get_or_create_support_settings(conn, user_id) -> dict`.
   - `compute_low_funds_status(conn, user_id, today: datetime.date | None = None) -> dict`: hàm THUẦN tính toán theo đúng bảng công thức + quy tắc phân mức ở Phần 1.4, tham số `today` để test cố định ngày. Trả dict đúng dạng JSON ở Phần 2 (kể cả `contacts` chỉ gồm người is_active=1, sắp theo priority rồi id, mỗi người có `relationship_label` và `message` đã thay placeholder {xung_ho},{so_du},{so_ngay},{so_tien}; tiền định dạng kiểu "1.550.000 ₫"). Làm tròn runway_days 1 chữ số thập phân. Lưu ý next_allowance_date khi allowance_day > số ngày của tháng (không xảy ra vì giới hạn 1–28, nhưng vẫn dùng calendar cho an toàn). Nhớ gọi `process_recurring_transactions(conn, user_id)` trước khi tính, giống `/api/reports/summary`.
5. Endpoints (đúng bảng API Phần 2). Validate: contact_name 1–50 ký tự sau strip; relationship trong enum; priority 1–99; note ≤ 200 ký tự; tối đa 10 người (400 nếu vượt); trùng SĐT trong cùng tài khoản → 400; threshold 0–1.000.000.000; allowance_day 1–28; message_template ≤ 500 ký tự. Bản ghi không phải của mình → 404.
6. Tạo `test_support_contacts.py` (unittest + fastapi.testclient.TestClient). Trong setUp: trỏ `main.DATABASE` sang file SQLite tạm (tempfile), gọi `main.init_db()`, đăng ký + đăng nhập 2 user qua API thật (xem RegisterBody/LoginBody để biết field bắt buộc, ví dụ soul_lamp). tearDown: khôi phục main.DATABASE, xóa file tạm. TUYỆT ĐỐI không ghi vào app.db thật. Test tối thiểu:
   - CRUD danh bạ đầy đủ; chuẩn hóa "+84 912.345.678" → "0912345678"; SĐT sai ("12345", "0212345678") → 400; trùng số → 400; thêm người thứ 11 → 400.
   - User B không xem/sửa/xóa được người thân của user A (404) và GET của B không thấy dữ liệu của A.
   - Không có token → 401/403.
   - Settings: GET lần đầu trả mặc định; PUT giá trị sai (allowance_day=31, threshold âm) → 400/422.
   - compute_low_funds_status với `today` cố định (ví dụ 2026-10-09), dựng dữ liệu ví/giao dịch trong DB tạm, kiểm tra đủ 3 mức SAFE / WARNING / CRITICAL, kiểm tra days_left (allowance_day=1 → 23; allowance_day=15 → 6), avg_daily_expense khi chưa đủ 7 ngày dùng 30 ngày, avg=0 → runway_days null, upcoming_fixed có tính recurring EXPENSE đang bật và nợ BORROW chưa trả trong khoảng, suggested_amount làm tròn lên bội 50.000, và `message` đã thay hết placeholder (không còn dấu "{").
7. Chạy: `python -m unittest test_support_contacts -v` và test cũ `python -m unittest test_knowledge_data_intelligence -v`. Khởi động backend (uvicorn main:app) xác nhận init_db chạy được trên app.db thật, kiểm tra bằng PRAGMA rằng 2 bảng mới tồn tại và số dòng các bảng cũ (users, wallets, transactions, ...) KHÔNG đổi so với trước.
Báo cáo: file đã sửa/tạo, output test thật, số dòng các bảng trước/sau. Chưa làm frontend.
```

---

### PROMPT 2 — Frontend: Danh Bạ Hộ Đạo trong Hồ sơ

```
Làm GIAI ĐOẠN 2 theo Phần 1.6 mục 1 của đặc tả.

1. Tạo `frontend/src/components/support/SupportContactsCard.vue` (component thuần hiển thị, KHÔNG gọi API):
   - props: contacts (Array, mặc định []), settings (Object, mặc định {enabled:true, low_balance_threshold:500000, allowance_day:1, message_template:''}), loading (Boolean), formatVND (Function).
   - emits: 'create-contact', 'update-contact' ({id, ...fields}), 'delete-contact' (id), 'toggle-contact' ({id, is_active}), 'save-settings' (settings).
   - Danh sách dạng dòng: nhãn quan hệ tiếng Việt (Bố, Mẹ, Anh/Chị/Em, Họ hàng, Bạn bè, Khác), tên, SĐT hiển thị dạng "0912 345 678", ghi chú, nút Sửa / Xóa (có confirm) / công tắc bật-tắt.
   - Nút "+ Thêm người thân" bật form: tên, quan hệ (select), SĐT (inputmode="tel"), ưu tiên, ghi chú. Form khởi tạo đủ field; kiểm tra phía client (bắt buộc tên & SĐT, regex như backend) nhưng vẫn hiển thị lỗi backend trả về. Đủ 10 người → ẩn nút thêm và ghi "Tối đa 10 người".
   - Mục "Cài đặt cảnh báo": bật/tắt, ngưỡng cảnh báo (VND), ngày nhận tiền hằng tháng (1–28), textarea mẫu tin nhắn có liệt kê placeholder {xung_ho} {so_du} {so_ngay} {so_tien} và nút "Dùng mẫu mặc định" (đặt về rỗng).
   - Trạng thái rỗng: "Chưa có người thân nào. Thêm số bố mẹ hoặc người thân để được gợi ý gọi khi sắp hết tiền."
   - Tiêu đề: "Danh Bạ Hộ Đạo" + một dòng mô tả "Người thân có thể hỗ trợ khi linh thạch sắp cạn". Style dùng biến trong tokens.css, giống SoulLampCard/PasswordChangeCard đang có (đọc 2 file đó để bắt chước), responsive 1 cột trên mobile.
2. Gắn vào `ProfileView.vue` ngay dưới SoulLampCard; thêm props/emit tương ứng và chuyển tiếp sự kiện lên App.vue. ProfileView được dùng ở 2 chỗ trong App.vue (tab 'profile' và modal showProfileModal) → truyền props/sự kiện cho CẢ HAI.
3. Trong `App.vue`: thêm state `supportContacts` (ref([])), `supportSettings` (ref với đủ field mặc định), `loadingSupport` (ref(false)); hàm `loadSupportContacts`, `loadSupportSettings`, `createSupportContact`, `updateSupportContact`, `deleteSupportContact`, `saveSupportSettings` dùng axios `api` và cách báo lỗi/thành công giống các hàm hiện có (tìm cách App.vue đang hiện toast/thông báo và dùng lại). Gọi load khi đăng nhập xong (trong loadAllData). Thêm tất cả vào `return` của setup().
4. Grep toàn bộ frontend để chắc chắn không trùng tên biến/hàm có sẵn.
5. `npm run build` phải sạch. Báo cáo file sửa, output build thật. Nếu tôi cho phép dùng browser: mở Hồ sơ, thêm/sửa/xóa 1 người thân với số "0912 345 678", kiểm tra Console không có lỗi.
```

---

### PROMPT 3 — Frontend: Banner "Linh Thạch Sắp Cạn" ở Tổng Quan

```
Làm GIAI ĐOẠN 3 theo Phần 1.6 mục 2–3 của đặc tả.

0. SỬA NHỎ BACKEND TRƯỚC (lỗi phát hiện khi review Giai đoạn 1): tài khoản mới chưa tạo ví nào hiện bị `compute_low_funds_status` xếp CRITICAL "Số dư hiện tại đã cạn kiệt (0 ₫)", nên vừa đăng ký xong đã thấy banner đỏ. Sửa: nếu user KHÔNG có ví nào thì trả `level = "NO_DATA"`, `reasons = ["Chưa có ví nào nên chưa thể đánh giá. Hãy tạo ví trong Túi Càn Khôn."]`, các trường số vẫn đủ như cũ, và `contacts` vẫn trả bình thường. Người có ví (kể cả ví số dư 0) giữ nguyên logic hiện tại. Thêm test cho trường hợp này vào `test_support_contacts.py` và chạy lại toàn bộ file test.

1. Tạo `frontend/src/components/support/LowFundsAlert.vue` (thuần hiển thị):
   - props: status (Object | null, mặc định null), formatVND (Function).
   - emits: 'open-contacts' (mở modal Hồ sơ để thêm người thân), 'dismiss'.
   - Không render gì nếu status null, !status.enabled hoặc level là 'SAFE' hay 'NO_DATA'.
   - Một dải duy nhất (không card lồng card): viền trái vàng (#e3c370 / biến tương ứng trong tokens.css) cho WARNING, đỏ cho CRITICAL; icon Material Symbols; tiêu đề "Linh Thạch Sắp Cạn" (WARNING: "Linh thạch hao hụt", CRITICAL: "Linh thạch cạn kiệt" làm phụ đề).
   - Dòng tóm tắt số liệu: "Còn {total_balance} · đủ khoảng {runway_days} ngày · còn {days_left} ngày tới {next_allowance_date dd/mm} · nên xin thêm khoảng {suggested_amount}". Ẩn phần runway nếu null.
   - Danh sách `reasons`.
   - Danh sách contacts, mỗi dòng: tên, nhãn quan hệ, SĐT; nút "Gọi" là thẻ <a :href="'tel:' + phone">; nút "Nhắn tin" là <a :href="'sms:' + phone + '?body=' + encodeURIComponent(message)">; nút "Sao chép số" và "Sao chép lời nhắn" dùng navigator.clipboard.writeText trong try/catch, có phản hồi "Đã sao chép". Có thể mở rộng để xem trước nội dung tin nhắn.
   - contacts rỗng → "Bạn chưa lưu số người thân nào" + nút "Thêm người thân" (emit open-contacts).
   - Nút "Để sau" (emit dismiss).
   - Có aria-live="polite", nút đủ lớn để bấm trên điện thoại (≥ 44px), responsive.
2. Trong `App.vue`:
   - State `lowFundsStatus` (ref(null)), hàm `loadLowFundsStatus()` gọi GET /api/support/low-funds-status (lỗi thì giữ null, không làm sập trang).
   - Gọi `loadLowFundsStatus()` trong loadAllData VÀ ở mọi chỗ đang gọi `checkBudgetAlerts()` (grep để tìm đủ: sau thêm/sửa/xóa giao dịch, chuyển tiền...), cũng như sau khi lưu settings/danh bạ ở Prompt 2. Grep thêm các hàm tạo/sửa/xóa ví và nợ, gọi lại nếu chúng làm đổi số dư.
   - "Để sau": lưu `lowFundsSnooze = { date: 'YYYY-MM-DD', level }` vào localStorage (bọc try/catch). Computed `showLowFundsAlert`: ẩn nếu đã snooze trong ngày hôm nay với cùng level; nếu level tăng từ WARNING lên CRITICAL thì hiện lại.
   - Đặt `<LowFundsAlert>` trong `<section v-if="activeTab === 'dashboard'">` NGAY TRÊN `<DashboardView>`. KHÔNG sửa DashboardView.vue.
   - open-contacts → `showProfileModal = true` (dùng lại cơ chế có sẵn).
   - Thêm mọi state/hàm mới vào return của setup().
3. `npm run build` sạch. Báo cáo output thật.
4. Nếu tôi cho phép dùng browser: với một tài khoản test, đặt ngưỡng cảnh báo cao hơn số dư hiện tại để kích hoạt WARNING, chụp màn hình banner; bấm "Để sau" rồi tải lại trang → banner ẩn; trả ngưỡng về cũ. Kiểm tra Console không lỗi. Sau đó mở lần lượt đủ 11 tab (và modal Hồ sơ) để chắc không trang nào bị vỡ.
```

---

### PROMPT 4 — (Tùy chọn) Khí Linh trả lời câu hỏi "sắp hết tiền"

```
Làm GIAI ĐOẠN 4 (tùy chọn). Đọc `.agents/skills/ai-development/SKILL.md` và cách các tool READ hiện có được khai báo trong `ai_agent/tools.py` (ví dụ debt_status / budget_status: handler `import main`, ToolActionType.READ, RiskLevel.LOW, requires_confirmation=False).

1. Thêm tool READ `low_funds_support` (domain mới hoặc dùng domain phù hợp có sẵn — kiểm tra ToolRegistry xem domain có bị ràng buộc không). Handler mở `main.get_db()` và gọi đúng `main.compute_low_funds_status(conn, user_id)`, KHÔNG tính lại công thức. Trả lời tiếng Việt: mức cảnh báo, số dư, số ngày đủ tiêu, số tiền nên xin, và danh sách người thân (tên, quan hệ, SĐT) kèm gợi ý mở Tổng Quan để bấm Gọi/Nhắn tin. Không có người thân → hướng dẫn thêm trong Hồ sơ > Danh Bạ Hộ Đạo. SAFE → nói rõ hiện chưa có dấu hiệu sắp hết tiền và còn đủ khoảng bao nhiêu ngày.
2. Cho router/parser nhận diện các câu: "sắp hết tiền", "hết tiền rồi", "cuối tháng hết tiền", "xin tiền bố mẹ", "gọi ai xin tiền", "số điện thoại người thân", "danh bạ hộ đạo". Tìm đúng chỗ intent/keyword routing trong ai_agent/core.py và ai_agent/parser.py; không phá các intent đã có (ví dụ "xem nợ", "hạn mức").
3. Tool tuyệt đối read-only: không tạo/sửa/xóa gì. Agent KHÔNG tự gọi điện/gửi tin.
4. Thêm tài liệu tri thức ngắn `ai_agent/knowledge/docs/FEATURE/truyen_am_cau_vien.md` mô tả chức năng và công thức, rồi chạy builder theo đúng cách dự án đang dùng để cập nhật index (đọc ai_agent/knowledge/builder.py). Nếu capabilities.json liệt kê tính năng, bổ sung.
5. Thêm test vào `test_support_contacts.py` (hoặc file test agent riêng) dùng MockAIProvider: câu "cuối tháng sắp hết tiền thì gọi ai" → gọi đúng tool, không có tool ghi nào được gọi; user B không thấy người thân của user A.
6. Chạy lại toàn bộ: test_support_contacts, test_knowledge_data_intelligence. Báo cáo output thật.
```

---

### PROMPT 5 — (Tùy chọn) Khép vòng "đã nhận tiền"

```
Làm GIAI ĐOẠN 5 (tùy chọn).
1. Trong LowFundsAlert.vue thêm nút phụ "Đã nhận tiền → Ghi khoản thu" (emit 'record-income').
2. Trong App.vue xử lý 'record-income' bằng cách chuyển sang tab 'transactions' (dùng switchTab có sẵn) và, NẾU TransactionsView/App.vue đã có cơ chế mở form thêm giao dịch với loại INCOME thì dùng lại; nếu chưa có thì chỉ chuyển tab, KHÔNG viết lại form giao dịch. Báo cho tôi biết bạn chọn cách nào.
3. Sau khi lưu giao dịch, banner phải tự cập nhật (đã gọi loadLowFundsStatus ở Prompt 3) — kiểm tra lại điều này.
4. npm run build sạch, báo cáo.
```

---

### PROMPT 6 — Kiểm thử tổng & báo cáo

```
Kiểm thử tổng cho chức năng Truyền Âm Cầu Viện. KHÔNG commit, KHÔNG push.
1. `python -m unittest test_support_contacts -v` và `python -m unittest test_knowledge_data_intelligence -v` — dán output thật.
2. `cd frontend && npm run build` — dán output thật.
3. Chạy backend thật, dùng requests/httpx gọi lần lượt 7 endpoint mới với một tài khoản test (đăng nhập bằng tài khoản test có sẵn, không dùng tài khoản thật của tôi), xác nhận: status code, ownership (tài khoản khác → 404), dữ liệu cũ đọc vẫn bình thường (GET /api/wallets, /api/transactions, /api/reports/summary trả 200 và số liệu không đổi). Xóa dữ liệu test đã tạo trong app.db (chỉ những dòng support_contacts bạn vừa tạo), và nói rõ đã xóa gì.
4. `PRAGMA integrity_check` trên app.db; so sánh số dòng các bảng cũ trước/sau toàn bộ quá trình.
5. `git status` + `git diff --stat`: liệt kê mọi file đã đổi; xác nhận KHÔNG đụng tới các file đang có thay đổi dở của tôi (DashboardView, BudgetsView, CategoriesView, DebtsView, SavingGoalsView, StatisticsView, AdminStatsRow) ngoài phạm vi đã nêu.
6. Báo cáo cuối theo mẫu: Đã làm gì / File đổi / Kết quả test (số pass/fail) / Build / Rủi ro hoặc trường hợp hiếm chưa chắc chắn (ví dụ: sms: trên iOS cũ, tel: trên desktop, người dùng nhiều ví âm...) / Lỗi ngoài phạm vi phát hiện được.
Sau đó hỏi tôi có muốn commit không.
```

---

## PHẦN 4 — KỊCH BẢN DEMO & CHECKLIST NGHIỆM THU

### Kịch bản demo cho giảng viên (≈ 2 phút)

1. Đăng nhập tài khoản sinh viên. Mở **Hồ sơ → Danh Bạ Hộ Đạo**, thêm "Bố — 0912 345 678" và "Mẹ — 0987 654 321", ngày nhận tiền = 1.
2. Thêm vài giao dịch chi tiêu để số dư còn thấp (hoặc đặt ngưỡng cảnh báo cao hơn số dư).
3. Quay lại **Tổng Quan**: banner "Linh Thạch Sắp Cạn" hiện, nói rõ "còn X, đủ khoảng Y ngày, còn Z ngày tới 01/11, nên xin thêm khoảng W".
4. Mở trên **điện thoại** (cùng mạng LAN hoặc bản deploy): bấm **Gọi** → mở trình gọi với số của Bố; bấm **Nhắn tin** → mở SMS với lời nhắn soạn sẵn.
5. (Nếu làm Prompt 4) hỏi Khí Linh: "cuối tháng sắp hết tiền thì gọi ai?" → Khí Linh trả lời đúng số liệu và danh sách.
6. (Nếu làm Prompt 5) bấm "Đã nhận tiền → Ghi khoản thu", thêm 2.000.000 ₫ → banner biến mất.

### Checklist nghiệm thu

- [ ] Hai bảng mới tồn tại; dữ liệu cũ không đổi; có file backup `app.db.before_support_contacts.bak`
- [ ] SĐT sai bị chặn, SĐT có khoảng trắng / +84 được chuẩn hóa
- [ ] Tài khoản khác không xem/sửa/xóa được danh bạ của mình
- [ ] Banner chỉ hiện khi WARNING/CRITICAL và đang bật; lý do có số liệu cụ thể
- [ ] Gọi / Nhắn tin / Sao chép hoạt động (thử trên điện thoại thật)
- [ ] "Để sau" ẩn trong ngày, CRITICAL thì hiện lại
- [ ] Thêm/sửa/xóa giao dịch → banner cập nhật ngay
- [ ] `npm run build` sạch, test pass, 11 tab và modal Hồ sơ không vỡ, Console không lỗi
- [ ] Giao diện cùng phong cách Celestial Treasury, không thêm tab, không card lồng card
