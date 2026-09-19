"""
Test Suite Live E2E Day 3: Voice UX + Financial Analytics Tools + Context Follow-Up
Càn Khôn Linh Thạch Các — Khí Linh AI Agent
"""

import unittest
import urllib.request
import urllib.error
import json
import sqlite3
import datetime

BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:5173"


class TestLiveKhiLinhDay3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.email = "day3_khilinh_user@gmail.com"
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
            "full_name": "Đạo Hữu Day 3",
            "soul_lamp": "day3soul123"
        }).encode('utf-8')
        try:
            req = urllib.request.Request(f"{BASE_URL}/api/auth/register", data=reg_payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return data["token"]
        except urllib.error.HTTPError:
            login_payload = json.dumps({"email": email, "password": password}).encode('utf-8')
            req = urllib.request.Request(f"{BASE_URL}/api/auth/login", data=login_payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return data["token"]

    @classmethod
    def _setup_test_data(cls):
        """Khởi tạo dữ liệu mẫu cho user Day 3 (ví, danh mục, ngân sách, mục tiêu, sổ nợ, giao dịch)"""
        headers = {
            "Authorization": f"Bearer {cls.token}",
            "Content-Type": "application/json"
        }
        # 1. Tạo ví
        wallets_req = urllib.request.Request(f"{BASE_URL}/api/wallets", headers=headers)
        with urllib.request.urlopen(wallets_req) as resp:
            existing_wallets = json.loads(resp.read().decode('utf-8'))

        if not existing_wallets:
            w_create = urllib.request.Request(
                f"{BASE_URL}/api/wallets",
                data=json.dumps({"wallet_name": "Linh Thạch Tiền Mặt", "wallet_type": "CASH", "balance": 10000000}).encode('utf-8'),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(w_create) as resp:
                w1 = json.loads(resp.read().decode('utf-8'))
                w1_id = w1["id"]
        else:
            w1_id = existing_wallets[0]["id"]

        cls.wallet_id = w1_id

        # 2. Lấy danh mục
        cat_req = urllib.request.Request(f"{BASE_URL}/api/categories", headers=headers)
        with urllib.request.urlopen(cat_req) as resp:
            cats = json.loads(resp.read().decode('utf-8'))
            eat_cat = next((c for c in cats if "ăn" in c["category_name"].lower()), cats[0])
            cls.eat_cat_id = eat_cat["id"]

        # 3. Tạo ngân sách tháng này
        month_now = datetime.date.today().strftime("%Y-%m")
        try:
            b_req = urllib.request.Request(
                f"{BASE_URL}/api/budgets",
                data=json.dumps({"category_id": cls.eat_cat_id, "limit_amount": 3000000, "month_year": month_now}).encode('utf-8'),
                headers=headers,
                method="POST"
            )
            urllib.request.urlopen(b_req)
        except Exception:
            pass

        # 4. Tạo mục tiêu tiết kiệm
        try:
            g_req = urllib.request.Request(
                f"{BASE_URL}/api/saving-goals",
                data=json.dumps({"target_name": "Mua laptop mới", "target_amount": 25000000, "target_date": "2026-12-31"}).encode('utf-8'),
                headers=headers,
                method="POST"
            )
            urllib.request.urlopen(g_req)
        except Exception:
            pass

        # 5. Tạo sổ nợ
        try:
            d_req = urllib.request.Request(
                f"{BASE_URL}/api/debts",
                data=json.dumps({"person_name": "Trần Bằng Hữu", "amount": 1500000, "debt_type": "BORROW", "due_date": "2026-10-15"}).encode('utf-8'),
                headers=headers,
                method="POST"
            )
            urllib.request.urlopen(d_req)
        except Exception:
            pass

        # 6. Tạo vài giao dịch mẫu
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        try:
            tx1 = urllib.request.Request(
                f"{BASE_URL}/api/transactions",
                data=json.dumps({
                    "wallet_id": cls.wallet_id,
                    "category_id": cls.eat_cat_id,
                    "amount": 75000,
                    "transaction_type": "EXPENSE",
                    "note": "Ăn trưa cơm văn phòng",
                    "transaction_date": today_str
                }).encode('utf-8'),
                headers=headers,
                method="POST"
            )
            urllib.request.urlopen(tx1)
        except Exception:
            pass

    def _chat(self, msg: str):
        req = urllib.request.Request(
            f"{BASE_URL}/api/ai/chat",
            data=json.dumps({"message": msg}).encode('utf-8'),
            headers=self.headers,
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))

    def test_01_financial_overview_tool(self):
        """Tool 1: financial_overview lấy dữ liệu tài chính thực tế (thu, chi, số dư, tiết kiệm)"""
        data = self._chat("Tình hình tài chính của ta hôm nay thế nào?")
        self.assertEqual(data["state"], "SUCCESS")
        self.assertIn(data["tool_executed"], ("financial_overview", "get_financial_overview"))
        self.assertIn("total_balance", data["tool_result"]["data"])
        self.assertIn("income", data["tool_result"]["data"])
        self.assertIn("expense", data["tool_result"]["data"])
        self.assertGreaterEqual(data["tool_result"]["data"]["total_balance"], 0)
        print(f" -> Financial Overview verified: {data['response']}")

    def test_02_spending_summary_tool(self):
        """Tool 2: spending_summary tổng hợp chi tiêu thực tế (tổng chi, số lượng giao dịch, trung bình ngày)"""
        data = self._chat("Tháng này ta tiêu bao nhiêu?")
        self.assertEqual(data["state"], "SUCCESS")
        self.assertIn(data["tool_executed"], ("spending_summary", "get_financial_overview"))
        self.assertIn("response", data)
        print(f" -> Spending Summary verified: {data['response']}")

    def test_03_spending_by_category_tool(self):
        """Tool 3: spending_by_category breakdown chi tiêu theo danh mục thực tế"""
        # Query 3a: Khoản chi lớn nhất / tiêu nhiều nhất
        data1 = self._chat("Tháng này ta tiêu nhiều nhất vào đâu?")
        self.assertEqual(data1["state"], "SUCCESS")
        self.assertEqual(data1["tool_executed"], "spending_by_category")
        self.assertIn("categories", data1["tool_result"]["data"])
        print(f" -> Spending By Category breakdown verified: {data1['response']}")

        # Query 3b: Chi tiêu danh mục cụ thể
        data2 = self._chat("Ta tiêu ăn uống bao nhiêu?")
        self.assertEqual(data2["state"], "SUCCESS")
        self.assertEqual(data2["tool_executed"], "spending_by_category")
        self.assertIn("total_spent", data2["tool_result"]["data"])
        print(f" -> Specific Category Spending verified: {data2['response']}")

    def test_04_transaction_search_tool(self):
        """Tool 4: transaction_search tìm kiếm giao dịch với các bộ lọc thực tế"""
        data = self._chat("Tìm các khoản ăn uống tuần này")
        self.assertEqual(data["state"], "SUCCESS")
        self.assertIn(data["tool_executed"], ("transaction_search", "search_transactions"))
        self.assertIn("results", data["tool_result"]["data"])
        print(f" -> Transaction Search verified: {data['response']}")

    def test_05_budget_status_tool(self):
        """Tool 5: budget_status kiểm tra tiến độ hạn mức ngân sách thực tế"""
        data = self._chat("Ngân sách tháng này còn bao nhiêu?")
        self.assertEqual(data["state"], "SUCCESS")
        self.assertIn(data["tool_executed"], ("budget_status", "get_budget_status"))
        self.assertIn("budgets", data["tool_result"]["data"])
        print(f" -> Budget Status verified: {data['response']}")

    def test_06_saving_goal_status_tool(self):
        """Tool 6: saving_goal_status kiểm tra tiến độ mục tiêu tiết kiệm thực tế"""
        data = self._chat("Mục tiêu mua laptop tiến triển thế nào?")
        self.assertEqual(data["state"], "SUCCESS")
        self.assertIn(data["tool_executed"], ("saving_goal_status", "get_saving_goals"))
        self.assertIn("saving_goals", data["tool_result"]["data"])
        print(f" -> Saving Goal Status verified: {data['response']}")

    def test_07_debt_status_tool(self):
        """Tool 7: debt_status kiểm tra sổ nợ thực tế (nợ phải trả, nợ thu hồi)"""
        data = self._chat("Ta còn nợ bao nhiêu?")
        self.assertEqual(data["state"], "SUCCESS")
        self.assertIn(data["tool_executed"], ("debt_status", "get_debts"))
        self.assertIn("total_borrowing", data["tool_result"]["data"])
        self.assertIn("total_lending", data["tool_result"]["data"])
        print(f" -> Debt Status verified: {data['response']}")

    def test_08_followup_context_period(self):
        """Follow-up Context 1: Người dùng hỏi 'Tháng này ta tiêu bao nhiêu?' -> hỏi tiếp 'Còn tháng trước?'"""
        # Bước 1: Hỏi tháng này
        res1 = self._chat("Tháng này ta tiêu bao nhiêu?")
        self.assertEqual(res1["state"], "SUCCESS")

        # Bước 2: Follow-up thay đổi chu kỳ
        res2 = self._chat("Còn tháng trước?")
        self.assertEqual(res2["state"], "SUCCESS")
        self.assertIn(res2["tool_executed"], ("spending_summary", "get_financial_overview", "financial_overview"))
        self.assertIn("tháng trước", res2["response"].lower())
        print(f" -> Follow-up Period verified: {res2['response']}")

    def test_09_followup_context_search(self):
        """Follow-up Context 2: Người dùng tìm giao dịch -> điều chỉnh bộ lọc 'Chỉ lấy tuần này'"""
        # Bước 1: Tìm kiếm giao dịch
        res1 = self._chat("Tìm các khoản ăn uống")
        self.assertEqual(res1["state"], "SUCCESS")

        # Bước 2: Follow-up lọc tuần này
        res2 = self._chat("Chỉ lấy tuần này")
        self.assertEqual(res2["state"], "SUCCESS")
        self.assertIn(res2["tool_executed"], ("transaction_search", "search_transactions"))
        print(f" -> Follow-up Filter Adjustment verified: {res2['response']}")

    def test_10_financial_mutation_safety_preserved(self):
        """Bảo toàn luồng xác nhận tài chính: Khí Linh không tự ý ghi DB nếu chưa xác nhận"""
        # 1. Gửi lệnh ghi nhận chi tiêu
        res1 = self._chat("Tôi vừa ăn trưa 45 nghìn")
        self.assertEqual(res1["state"], "CONFIRMING")
        self.assertIsNotNone(res1.get("pending_confirmation"))
        self.assertEqual(res1["pending_confirmation"]["args"]["amount"], 45000)

        # 2. Người dùng bấm Hủy
        res_cancel = self._chat("Hủy")
        self.assertEqual(res_cancel["state"], "IDLE")
        self.assertIn("hủy", res_cancel["response"].lower())

        # 3. Gửi lại và Xác nhận
        res2 = self._chat("Tôi vừa ăn trưa 45 nghìn")
        self.assertEqual(res2["state"], "CONFIRMING")
        res_confirm = self._chat("Xác nhận")
        self.assertEqual(res_confirm["state"], "SUCCESS")
        self.assertEqual(res_confirm["tool_executed"], "create_expense")
        print(" -> Financial Safety & Single Execution Verified.")

    def test_11_frontend_voice_and_quick_action_chips(self):
        """Kiểm tra giao diện frontend có đầy đủ các nút Voice STT, TTS và Quick Action Chips"""
        req = urllib.request.Request(f"{FRONTEND_URL}/")
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8')

        # Frontend source checks
        with open("frontend/src/components/KhiLinhAssistant.vue", "r", encoding="utf-8") as f:
            comp_content = f.read()

        # Voice STT button
        self.assertIn('id="btn-khilinh-mic"', comp_content)
        # Send button
        self.assertIn('id="btn-khilinh-send"', comp_content)
        # TTS toggle button
        self.assertIn('toggleTTS', comp_content)
        # Quick Action Chips
        self.assertIn('quickActionChips', comp_content)
        self.assertIn('💰 Số dư', comp_content)
        self.assertIn('📊 Tổng quan', comp_content)
        self.assertIn('📅 Tháng này', comp_content)
        self.assertIn('🏷️ Chi theo mục', comp_content)
        self.assertIn('🎯 Mục tiêu', comp_content)
        self.assertIn('📜 Sổ nợ', comp_content)
        # Duplicate submission guard
        self.assertIn('hasSubmittedUtterance', comp_content)
        # Safe TTS normalization
        self.assertIn('lastSpokenText', comp_content)
        print(" -> Frontend Voice & Analytics Quick Actions verified in code & components.")

    def test_12_query_highest_balance_wallet(self):
        """Kiểm tra câu hỏi ví có nhiều tiền nhất: 'Ví nào đang còn nhiều tiền nhất?'"""
        data = self._chat("Ví nào đang còn nhiều tiền nhất?")
        self.assertEqual(data["state"], "SUCCESS")
        self.assertEqual(data["tool_executed"], "get_wallets")
        self.assertIn("top_wallet", data["tool_result"]["data"])
        self.assertIn("dồi dào nhất", data["response"])
        print(f" -> Richest Wallet Query verified: {data['response']}")

    def test_13_query_general_saving_goals(self):
        """Kiểm tra câu hỏi tổng thể tiến độ mục tiêu: 'Mục tiêu tiết kiệm của ta thế nào?'"""
        data = self._chat("Mục tiêu tiết kiệm của ta thế nào?")
        self.assertEqual(data["state"], "SUCCESS")
        self.assertIn(data["tool_executed"], ("saving_goal_status", "get_saving_goals"))
        self.assertIn("saving_goals", data["tool_result"]["data"])
        print(f" -> General Saving Goals Query verified: {data['response']}")

    def test_14_search_transaction_by_wallet(self):
        """Kiểm tra tìm kiếm giao dịch theo ví và tuần: 'Tìm giao dịch Vietcombank tuần này.'"""
        data = self._chat("Tìm giao dịch Vietcombank tuần này.")
        self.assertEqual(data["state"], "SUCCESS")
        self.assertIn(data["tool_executed"], ("transaction_search", "search_transactions"))
        self.assertIn("results", data["tool_result"]["data"])
        print(f" -> Wallet Transaction Search verified: {data['response']}")

    def test_15_frontend_processing_state_and_debounce(self):
        """Kiểm tra frontend có cờ isSubmitting và hỗ trợ state PROCESSING toàn diện"""
        with open("frontend/src/components/KhiLinhAssistant.vue", "r", encoding="utf-8") as f:
            comp_content = f.read()

        # isSubmitting lock
        self.assertIn('isSubmitting', comp_content)
        # PROCESSING state
        self.assertIn("'PROCESSING'", comp_content)
        self.assertIn("'Đang xử lý'", comp_content)
        # Cancel synth on send
        self.assertIn('synth.cancel()', comp_content)
        print(" -> Frontend PROCESSING state machine & debounce guards verified.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
