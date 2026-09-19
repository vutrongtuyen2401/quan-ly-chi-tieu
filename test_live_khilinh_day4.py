"""
Test Suite Live E2E Day 4: Full AI Financial Journey Integration + Hardening Sprint
Càn Khôn Linh Thạch Các — Khí Linh AI Agent
"""

import unittest
import urllib.request
import urllib.error
import json
import sqlite3
import datetime
import re
import asyncio


BASE_URL = "http://127.0.0.1:8000"


class TestLiveKhiLinhDay4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.email = "day4_khilinh_user@gmail.com"
        cls.password = "password123"
        cls.token = cls._get_or_create_user(cls.email, cls.password)
        cls.headers = {
            "Authorization": f"Bearer {cls.token}",
            "Content-Type": "application/json"
        }
        cls._setup_test_data()

    @classmethod
    def _get_or_create_user(cls, email, password):
        reg_payload = json.dumps({
            "email": email,
            "password": password,
            "full_name": "Đạo Hữu Day 4",
            "soul_lamp": "day4soul123"
        }).encode('utf-8')
        try:
            req = urllib.request.Request(
                f"{BASE_URL}/api/auth/register",
                data=reg_payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return data["token"]
        except urllib.error.HTTPError:
            login_payload = json.dumps({"email": email, "password": password}).encode('utf-8')
            req = urllib.request.Request(
                f"{BASE_URL}/api/auth/login",
                data=login_payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return data["token"]

    @classmethod
    def _setup_test_data(cls):
        """Khởi tạo 2 ví mẫu, 1 ngân sách, 1 mục tiêu tiết kiệm, 1 sổ nợ cho user Day 4"""
        headers = {
            "Authorization": f"Bearer {cls.token}",
            "Content-Type": "application/json"
        }

        # 1. Lấy hoặc tạo ví
        wallets_req = urllib.request.Request(f"{BASE_URL}/api/wallets", headers=headers)
        with urllib.request.urlopen(wallets_req) as resp:
            existing_wallets = json.loads(resp.read().decode('utf-8'))

        w1 = next((w for w in existing_wallets if "Tiền Mặt" in w["wallet_name"]), None)
        if not w1:
            w1_req = urllib.request.Request(
                f"{BASE_URL}/api/wallets",
                data=json.dumps({"wallet_name": "Linh Thạch Tiền Mặt", "wallet_type": "CASH", "balance": 15000000}).encode('utf-8'),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(w1_req) as resp:
                w1 = json.loads(resp.read().decode('utf-8'))

        w2 = next((w for w in existing_wallets if "Vietcombank" in w["wallet_name"]), None)
        if not w2:
            w2_req = urllib.request.Request(
                f"{BASE_URL}/api/wallets",
                data=json.dumps({"wallet_name": "Linh Mạch Vietcombank", "wallet_type": "BANK", "balance": 5000000}).encode('utf-8'),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(w2_req) as resp:
                w2 = json.loads(resp.read().decode('utf-8'))

        cls.wallet_cash = w1
        cls.wallet_vcb = w2

        # 2. Danh mục Ăn Uống
        cat_req = urllib.request.Request(f"{BASE_URL}/api/categories", headers=headers)
        with urllib.request.urlopen(cat_req) as resp:
            cats = json.loads(resp.read().decode('utf-8'))
            eat_cat = next((c for c in cats if "ăn" in c["category_name"].lower()), cats[0])
            cls.eat_cat_id = eat_cat["id"]

        # 3. Ngân sách tháng này
        month_now = datetime.date.today().strftime("%Y-%m")
        try:
            b_req = urllib.request.Request(
                f"{BASE_URL}/api/budgets",
                data=json.dumps({"category_id": cls.eat_cat_id, "limit_amount": 4000000, "month_year": month_now}).encode('utf-8'),
                headers=headers,
                method="POST"
            )
            urllib.request.urlopen(b_req)
        except Exception:
            pass

        # 4. Mục tiêu tiết kiệm: Tái sử dụng nếu đã tồn tại
        g_list_req = urllib.request.Request(f"{BASE_URL}/api/saving-goals", headers=headers)
        with urllib.request.urlopen(g_list_req) as resp:
            goals_resp = json.loads(resp.read().decode('utf-8'))
            goals = goals_resp.get("goals", []) if isinstance(goals_resp, dict) else goals_resp
            cls.goal = next((g for g in goals if "laptop" in g.get("target_name", "").lower()), None)

        if not cls.goal:
            try:
                g_req = urllib.request.Request(
                    f"{BASE_URL}/api/saving-goals",
                    data=json.dumps({"target_name": "Mua laptop mới", "target_amount": 25000000, "target_date": "2026-12-31"}).encode('utf-8'),
                    headers=headers,
                    method="POST"
                )
                with urllib.request.urlopen(g_req) as resp:
                    cls.goal = json.loads(resp.read().decode('utf-8'))
            except Exception:
                pass

        # 5. Sổ nợ
        try:
            d_req = urllib.request.Request(
                f"{BASE_URL}/api/debts",
                data=json.dumps({
                    "debt_type": "BORROW",
                    "person_name": "Đạo Hữu Tiêu Dao",
                    "amount": 1000000,
                    "due_date": "2026-11-30",
                    "note": "Mượn linh thạch mua đan dược"
                }).encode('utf-8'),
                headers=headers,
                method="POST"
            )
            urllib.request.urlopen(d_req)
        except Exception:
            pass

    def _chat(self, message: str) -> dict:
        """Gửi lệnh đến /api/ai/chat qua HTTP"""
        payload = json.dumps({"message": message}).encode('utf-8')
        req = urllib.request.Request(f"{BASE_URL}/api/ai/chat", data=payload, headers=self.headers)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))

    def _get_wallet_balance(self, wallet_id: int) -> float:
        req = urllib.request.Request(f"{BASE_URL}/api/wallets", headers=self.headers)
        with urllib.request.urlopen(req) as resp:
            wallets = json.loads(resp.read().decode('utf-8'))
            w = next((w for w in wallets if w["id"] == wallet_id), None)
            return w["balance"] if w else 0.0

    # ─── P0: JOURNEY 1 — EXPENSE ──────────────────────────────────────────
    def test_01_journey_expense(self):
        """Journey 1: Ghi nhận chi tiêu qua STT/Text -> Xác nhận -> Database cập nhật"""
        bal_before = self._get_wallet_balance(self.wallet_cash["id"])

        # 1. Gửi lệnh
        data1 = self._chat("Tôi vừa ăn sáng hết 50 nghìn.")
        self.assertEqual(data1["state"], "CONFIRMING")
        self.assertIsNotNone(data1["pending_confirmation"])
        self.assertEqual(data1["pending_confirmation"]["tool_name"], "create_expense")
        self.assertEqual(data1["pending_confirmation"]["args"]["amount"], 50000.0)
        self.assertIn("operation_id", data1["pending_confirmation"]["args"])

        # 2. Xác nhận
        data2 = self._chat("Xác nhận")
        self.assertEqual(data2["state"], "SUCCESS")
        self.assertEqual(data2["tool_executed"], "create_expense")
        self.assertTrue(data2["tool_result"]["success"])

        # 3. Kiểm tra số dư và giao dịch thực tế
        bal_after = self._get_wallet_balance(self.wallet_cash["id"])
        self.assertEqual(bal_before - bal_after, 50000.0)
        print(" -> Journey 1 (Expense) verified: 50,000 VND recorded and deducted.")

    # ─── P0: JOURNEY 2 — INCOME ───────────────────────────────────────────
    def test_02_journey_income(self):
        """Journey 2: Ghi nhận thu nhập -> Xác nhận -> Số dư tăng, bản ghi INCOME"""
        bal_before = self._get_wallet_balance(self.wallet_cash["id"])

        # 1. Gửi lệnh thu nhập
        data1 = self._chat("Ta vừa nhận 5 triệu tiền lương.")
        self.assertEqual(data1["state"], "CONFIRMING")
        self.assertIsNotNone(data1["pending_confirmation"])
        self.assertEqual(data1["pending_confirmation"]["tool_name"], "create_income")
        self.assertEqual(data1["pending_confirmation"]["args"]["amount"], 5000000.0)
        self.assertIn("operation_id", data1["pending_confirmation"]["args"])

        # 2. Xác nhận
        data2 = self._chat("Xác nhận")
        self.assertEqual(data2["state"], "SUCCESS")
        self.assertEqual(data2["tool_executed"], "create_income")
        self.assertTrue(data2["tool_result"]["success"])

        # 3. Kiểm tra số dư tăng
        bal_after = self._get_wallet_balance(self.wallet_cash["id"])
        self.assertEqual(bal_after - bal_before, 5000000.0)
        print(" -> Journey 2 (Income) verified: 5,000,000 VND income credited.")

    # ─── P0: JOURNEY 3 — TRANSFER ─────────────────────────────────────────
    def test_03_journey_transfer_explicit_and_idempotency(self):
        """Journey 3: Chuyển tiền từ ví nguồn sang ví đích với operation_id và 2 bản ghi bù trừ"""
        bal_cash_before = self._get_wallet_balance(self.wallet_cash["id"])
        bal_vcb_before = self._get_wallet_balance(self.wallet_vcb["id"])

        # 1. Lệnh chuyển
        data1 = self._chat("Chuyển 500 nghìn từ Linh Thạch Tiền Mặt sang Linh Mạch Vietcombank.")
        self.assertEqual(data1["state"], "CONFIRMING")
        self.assertIsNotNone(data1["pending_confirmation"])
        self.assertEqual(data1["pending_confirmation"]["tool_name"], "transfer_money")
        self.assertEqual(data1["pending_confirmation"]["args"]["amount"], 500000.0)
        op_id = data1["pending_confirmation"]["args"]["operation_id"]
        self.assertTrue(bool(op_id))

        # 2. Xác nhận
        data2 = self._chat("Xác nhận")
        self.assertEqual(data2["state"], "SUCCESS")
        self.assertEqual(data2["tool_executed"], "transfer_money")
        self.assertTrue(data2["tool_result"]["success"])

        # 3. Số dư 2 ví
        bal_cash_after = self._get_wallet_balance(self.wallet_cash["id"])
        bal_vcb_after = self._get_wallet_balance(self.wallet_vcb["id"])
        self.assertEqual(bal_cash_before - bal_cash_after, 500000.0)
        self.assertEqual(bal_vcb_after - bal_vcb_before, 500000.0)

        # 4. Kiểm tra database có 2 bản ghi bù trừ cùng operation_id
        con = sqlite3.connect("app.db")
        con.row_factory = sqlite3.Row
        txns = con.execute("SELECT * FROM transactions WHERE operation_id = ?", (op_id,)).fetchall()
        self.assertEqual(len(txns), 2)
        types = {t["transaction_type"] for t in txns}
        self.assertEqual(types, {"EXPENSE", "INCOME"})
        con.close()
        print(" -> Journey 3 (Transfer & Dual Records) verified successfully.")

    def test_04_journey_transfer_destination_only(self):
        """Journey 3b: Chuyển tiền chỉ nêu ví đích: 'Chuyển 300 nghìn cho ví Vietcombank'"""
        data1 = self._chat("Chuyển 300 nghìn cho ví Vietcombank.")
        self.assertEqual(data1["state"], "CONFIRMING")
        self.assertIsNotNone(data1["pending_confirmation"])
        self.assertIn("Vietcombank", data1["pending_confirmation"]["args"].get("to_wallet_name", ""))
        self.assertEqual(data1["pending_confirmation"]["args"]["amount"], 300000.0)

        # Hủy để không ảnh hưởng số dư kiểm thử khác
        data2 = self._chat("Hủy")
        self.assertEqual(data2["state"], "IDLE")
        print(" -> Journey 3b (Single Destination Wallet Resolution) verified.")

    # ─── P0: JOURNEY 4 — SAVING GOAL ──────────────────────────────────────
    def test_05_journey_saving_goal(self):
        """Journey 4: Tích lũy mục tiêu tiết kiệm: 'Đưa 200 nghìn vào mục tiêu mua laptop.'"""
        data1 = self._chat("Đưa 200 nghìn vào mục tiêu mua laptop.")
        self.assertEqual(data1["state"], "CONFIRMING")
        self.assertIsNotNone(data1["pending_confirmation"])
        self.assertEqual(data1["pending_confirmation"]["tool_name"], "saving_goal_deposit")
        self.assertEqual(data1["pending_confirmation"]["args"]["amount"], 200000.0)

        data2 = self._chat("Xác nhận")
        self.assertEqual(data2["state"], "SUCCESS")
        self.assertEqual(data2["tool_executed"], "saving_goal_deposit")
        self.assertTrue(data2["tool_result"]["success"])

        # Kiểm tra mục tiêu trong DB
        con = sqlite3.connect("app.db")
        con.row_factory = sqlite3.Row
        target_id = data2["tool_result"]["data"]["goal_id"]
        g = con.execute("SELECT current_amount FROM saving_goals WHERE id = ?", (target_id,)).fetchone()
        self.assertGreaterEqual(g["current_amount"], 200000.0)
        con.close()
        print(" -> Journey 4 (Saving Goal Deposit) verified.")

    # ─── P0: JOURNEY 5 — ANALYTICS TOOLS FACTUALITY ───────────────────────
    def test_06_journey_analytics_factual_results(self):
        """Journey 5: Kiểm tra 7 công cụ đọc tài chính thực tế, số liệu xuất phát từ backend DB"""
        queries = [
            ("Tháng này ta tiêu bao nhiêu?", ("spending_summary", "get_financial_overview", "financial_overview")),
            ("Ta tiêu nhiều nhất vào đâu?", ("spending_by_category",)),
            ("Ví nào đang còn nhiều tiền nhất?", ("get_wallets",)),
            ("Ngân sách tháng này còn bao nhiêu?", ("budget_status", "get_budget_status")),
            ("Mục tiêu tiết kiệm của ta thế nào?", ("saving_goal_status", "get_saving_goals")),
            ("Ta còn nợ bao nhiêu?", ("debt_status", "get_debts")),
            ("Tìm giao dịch ăn sáng.", ("transaction_search", "search_transactions"))
        ]

        for q, expected_tools in queries:
            res = self._chat(q)
            self.assertEqual(res["state"], "SUCCESS", f"Query '{q}' did not return SUCCESS")
            self.assertIn(res["tool_executed"], expected_tools, f"Query '{q}' executed unexpected tool: {res['tool_executed']}")
            self.assertTrue(res["tool_result"]["success"], f"Tool result for '{q}' was not successful")
            self.assertIsNotNone(res["tool_result"]["data"], f"Tool data for '{q}' is None")
        print(" -> Journey 5 (Analytics Factuality - 7 Tools) verified.")

    # ─── P0: CROSS-FEATURE FOLLOW-UP ─────────────────────────────────────
    def test_07_followup_pending_modification(self):
        """Follow-up 1: Sửa đổi số tiền trong thao tác đang chờ -> Thực thi đúng 1 lần với số tiền mới"""
        bal_cash_before = self._get_wallet_balance(self.wallet_cash["id"])
        bal_vcb_before = self._get_wallet_balance(self.wallet_vcb["id"])

        # 1. Bắt đầu chuyển 500k
        res1 = self._chat("Chuyển 500 nghìn từ Linh Thạch Tiền Mặt sang Linh Mạch Vietcombank.")
        self.assertEqual(res1["state"], "CONFIRMING")
        self.assertEqual(res1["pending_confirmation"]["args"]["amount"], 500000.0)

        # 2. Sửa thành 200 nghìn
        res2 = self._chat("Sửa thành 200 nghìn.")
        self.assertEqual(res2["state"], "CONFIRMING")
        self.assertEqual(res2["pending_confirmation"]["args"]["amount"], 200000.0)
        self.assertIn("200,000", res2["response"])

        # 3. Xác nhận
        res3 = self._chat("Xác nhận")
        self.assertEqual(res3["state"], "SUCCESS")

        # 4. Kiểm tra số dư chỉ chuyển đúng 200,000 VND
        bal_cash_after = self._get_wallet_balance(self.wallet_cash["id"])
        bal_vcb_after = self._get_wallet_balance(self.wallet_vcb["id"])
        self.assertEqual(bal_cash_before - bal_cash_after, 200000.0)
        self.assertEqual(bal_vcb_after - bal_vcb_before, 200000.0)
        print(" -> Follow-Up 1 (Pending Operation Modification) verified.")

    def test_08_followup_period_shift(self):
        """Follow-up 2: Hỏi chu kỳ tiếp nối: 'Tháng này ta tiêu bao nhiêu?' -> 'Còn tháng trước?'"""
        res1 = self._chat("Tháng này ta tiêu bao nhiêu?")
        self.assertEqual(res1["state"], "SUCCESS")
        self.assertIn(res1["tool_executed"], ("spending_summary", "financial_overview"))

        res2 = self._chat("Còn tháng trước?")
        self.assertEqual(res2["state"], "SUCCESS")
        self.assertIn(res2["tool_executed"], ("spending_summary", "financial_overview"))
        self.assertIn("tháng trước", str(res2["tool_result"]["data"].get("period")))
        print(" -> Follow-Up 2 (Period Shift) verified.")

    def test_09_followup_filter_narrowing(self):
        """Follow-up 3: Thu hẹp bộ lọc: 'Tìm giao dịch ăn uống' -> 'Chỉ lấy tuần này'"""
        res1 = self._chat("Tìm giao dịch ăn uống.")
        self.assertEqual(res1["state"], "SUCCESS")
        self.assertIn(res1["tool_executed"], ("transaction_search", "search_transactions"))

        res2 = self._chat("Chỉ lấy tuần này.")
        self.assertEqual(res2["state"], "SUCCESS")
        self.assertIn(res2["tool_executed"], ("transaction_search", "search_transactions"))
        self.assertEqual(res2["tool_result"]["data"].get("time_frame"), "this_week")
        print(" -> Follow-Up 3 (Filter Narrowing) verified.")

    # ─── P1: ERROR / EDGE CASES ──────────────────────────────────────────
    def test_10_error_insufficient_balance(self):
        """Edge Case 1: Chuyển tiền vượt quá số dư ví nguồn"""
        res1 = self._chat("Chuyển 999 triệu từ Linh Thạch Tiền Mặt sang Linh Mạch Vietcombank.")
        self.assertEqual(res1["state"], "CONFIRMING")

        res2 = self._chat("Xác nhận")
        self.assertEqual(res2["state"], "ERROR")
        self.assertIn("không đủ", res2["response"])
        print(" -> Edge Case 1 (Insufficient Balance) verified.")

    def test_11_error_cancellation_preserves_state(self):
        """Edge Case 2: Hủy bỏ xác nhận trả về IDLE và không làm biến động cơ sở dữ liệu"""
        bal_before = self._get_wallet_balance(self.wallet_cash["id"])
        res1 = self._chat("Tôi vừa chi 100k mua trà sữa")
        self.assertEqual(res1["state"], "CONFIRMING")

        res2 = self._chat("Hủy")
        self.assertEqual(res2["state"], "IDLE")
        self.assertIn("hủy bỏ", res2["response"].lower())

        bal_after = self._get_wallet_balance(self.wallet_cash["id"])
        self.assertEqual(bal_before, bal_after)
        print(" -> Edge Case 2 (Cancellation Flow) verified.")

    def test_12_error_invalid_non_positive_amount(self):
        """Edge Case 3: Số tiền không hợp lệ (<= 0) không được ghi nhận"""
        from ai_agent.tools import build_default_tool_registry
        reg = build_default_tool_registry()
        user_row = sqlite3.connect("app.db").execute("SELECT id FROM users WHERE email = ?", (self.email,)).fetchone()
        uid = user_row[0]

        res = asyncio.run(reg.execute("create_expense", user_id=uid, amount=-50000, note="tiền âm"))
        self.assertFalse(res.success)
        self.assertIn("lớn hơn 0", res.error)
        print(" -> Edge Case 3 (Invalid Negative Amount) rejected safely.")

    def test_13_error_idempotency_duplicate_prevention(self):
        """Edge Case 4: Cùng 1 operation_id không bị thực thi 2 lần"""
        from ai_agent.tools import build_default_tool_registry
        reg = build_default_tool_registry()
        user_row = sqlite3.connect("app.db").execute("SELECT id FROM users WHERE email = ?", (self.email,)).fetchone()
        uid = user_row[0]

        op_test_id = f"test_idempotency_{datetime.datetime.now().timestamp()}"
        bal_before = self._get_wallet_balance(self.wallet_cash["id"])

        # Lần 1: Thành công
        res1 = asyncio.run(reg.execute("create_expense", user_id=uid, amount=25000, note="test lặp 1", wallet_id=self.wallet_cash["id"], operation_id=op_test_id))
        self.assertTrue(res1.success)

        # Lần 2: Cùng operation_id -> Báo đã xử lý, không trừ tiền lần 2
        res2 = asyncio.run(reg.execute("create_expense", user_id=uid, amount=25000, note="test lặp 2", wallet_id=self.wallet_cash["id"], operation_id=op_test_id))
        self.assertTrue(res2.success)
        self.assertTrue(res2.data.get("already_processed"))

        bal_after = self._get_wallet_balance(self.wallet_cash["id"])
        self.assertEqual(bal_before - bal_after, 25000.0)  # Chỉ trừ đúng 1 lần 25k!
        print(" -> Edge Case 4 (Operation Idempotency) strictly enforced.")

    # ─── P2: TOOL REGISTRY & PROVIDER AUDIT ────────────────────────────────
    def test_14_tool_registry_architecture_audit(self):
        """P2 Audit: Kiểm tra toàn bộ Tool Registry tuân thủ chuẩn READ/WRITE, rủi ro, và xác nhận"""
        from ai_agent.tools import build_default_tool_registry, ToolActionType, RiskLevel
        reg = build_default_tool_registry()

        expected_reads = [
            "get_wallets", "get_recent_transactions", "financial_overview", "get_financial_overview",
            "spending_summary", "spending_by_category", "budget_status", "get_budget_status",
            "saving_goal_status", "get_saving_goals", "debt_status", "get_debts",
            "transaction_search", "search_transactions", "get_categories", "get_recurring_transactions",
            "get_system_help"
        ]
        expected_writes = [
            "create_expense", "create_income", "transfer_money", "saving_goal_deposit"
        ]

        for r_tool in expected_reads:
            tool = reg.get(r_tool)
            self.assertIsNotNone(tool, f"Missing READ tool: {r_tool}")
            self.assertEqual(tool.action_type, ToolActionType.READ)
            self.assertFalse(tool.requires_confirmation)
            self.assertEqual(tool.risk_level, RiskLevel.LOW)

        for w_tool in expected_writes:
            tool = reg.get(w_tool)
            self.assertIsNotNone(tool, f"Missing WRITE tool: {w_tool}")
            self.assertEqual(tool.action_type, ToolActionType.WRITE)
            self.assertTrue(tool.requires_confirmation)
            self.assertIn(tool.risk_level, (RiskLevel.MEDIUM, RiskLevel.HIGH))

        print(f" -> Tool Registry Architecture Audit: {len(expected_reads)} READ + {len(expected_writes)} WRITE tools verified.")

    def test_15_provider_server_side_security_audit(self):
        """P2 Audit: Gemini Provider nằm hoàn toàn ở server-side, không rò rỉ API key ra client"""
        from ai_agent.provider import GeminiProvider, MockAIProvider

        # Provider classes exist and implement generate_response
        self.assertTrue(hasattr(GeminiProvider, "generate_response"))
        self.assertTrue(hasattr(MockAIProvider, "generate_response"))

        # Check frontend code does NOT import or contain GEMINI_API_KEY
        with open("frontend/src/App.vue", "r", encoding="utf-8") as f:
            fe_app = f.read()
        self.assertNotIn("GEMINI_API_KEY", fe_app)
        self.assertNotIn("AIzaSy", fe_app)

        with open("frontend/src/components/KhiLinhAssistant.vue", "r", encoding="utf-8") as f:
            fe_kl = f.read()
        self.assertNotIn("GEMINI_API_KEY", fe_kl)
        self.assertNotIn("AIzaSy", fe_kl)

        print(" -> Provider Security Audit: Server-side isolation verified.")

    # ─── P1: FRONTEND REFRESH & DISMISS GUARDS ─────────────────────────────
    def test_16_frontend_refresh_and_state_consistency(self):
        """P1 Audit: Kiểm tra mã frontend có đầy đủ bộ xử lý đồng bộ và tự động phục hồi trạng thái"""
        with open("frontend/src/components/KhiLinhAssistant.vue", "r", encoding="utf-8") as f:
            kl_code = f.read()

        # 1. Đóng thẻ xác nhận tự động khi có lệnh mới
        self.assertIn("m.confirmation.isPending = false", kl_code)
        # 2. Tự động chuyển về IDLE sau SUCCESS và ERROR
        self.assertIn("agentState.value = 'IDLE'", kl_code)
        # 3. Phát sự kiện transactionCompleted
        self.assertIn("emit('transactionCompleted'", kl_code)

        with open("frontend/src/App.vue", "r", encoding="utf-8") as f:
            app_code = f.read()

        # 4. App.vue bắt sự kiện và gọi Promise.all tải lại toàn bộ thực thể
        self.assertIn("@transaction-completed=\"onKhiLinhTransactionCompleted\"", app_code)
        self.assertIn("loadWallets()", app_code)
        self.assertIn("loadTransactions(true)", app_code)
        self.assertIn("loadSummary()", app_code)
        self.assertIn("loadBudgets()", app_code)
        self.assertIn("loadSavingGoals()", app_code)
        self.assertIn("loadDebts()", app_code)
        self.assertIn("showToast('✨ Khí Linh đã đồng bộ thành công vào sổ sách!', 'success')", app_code)

        print(" -> Frontend Data Refresh & State Consistency verified in source.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
