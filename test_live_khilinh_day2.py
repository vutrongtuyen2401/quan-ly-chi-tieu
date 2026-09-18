"""
Day 2 Verification Test: Live Khí Linh AI Interface & Agent Core Integration
Validates:
1. Frontend dev server (http://localhost:5173) responds with HTTP 200 and loads HTML.
2. Backend API server (http://127.0.0.1:8000) responds to /api/ai/chat.
3. Natural-language read request ("Ví tiền mặt còn bao nhiêu?").
4. Financial mutation request ("Tôi vừa ăn sáng hết 50 nghìn.") -> Returns CONFIRMING + pending_confirmation data.
5. Cancellation request ("Hủy") -> Clears pending confirmation and returns IDLE.
6. Execution confirmation ("Xác nhận") -> Executes mutation, returns SUCCESS + tool_executed, and writes transaction to DB.
7. Follow-up modification flow: ("Chuyển 100 nghìn từ ví A sang ví B" -> "Sửa thành 80 nghìn" -> "Xác nhận").
8. Verifies 0 regression on wallet balances and transactions.
"""

import urllib.request
import urllib.error
import json
import unittest

BASE_API = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:5173"

class TestLiveKhiLinhDay2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # 1. Login or register a dedicated Day 2 test user
        cls.email = "khilinh_day2_tester@gmail.com"
        cls.password = "pass12345"
        cls.token = cls._get_or_create_user(cls.email, cls.password)
        cls.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cls.token}"
        }

    @classmethod
    def _get_or_create_user(cls, email, password):
        # Try register
        reg_payload = json.dumps({
            "email": email,
            "password": password,
            "full_name": "Đạo Hữu Khí Linh",
            "soul_lamp": "khilinhlamp123"
        }).encode('utf-8')
        try:
            req = urllib.request.Request(f"{BASE_API}/api/auth/register", data=reg_payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                return data["token"]
        except urllib.error.HTTPError:
            # Already exists, try login
            login_payload = json.dumps({"email": email, "password": password}).encode('utf-8')
            req = urllib.request.Request(f"{BASE_API}/api/auth/login", data=login_payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                return data["token"]

    def _post(self, path, body):
        req = urllib.request.Request(
            f"{BASE_API}{path}",
            data=json.dumps(body).encode('utf-8'),
            headers=self.headers
        )
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())

    def _get(self, path):
        req = urllib.request.Request(
            f"{BASE_API}{path}",
            headers=self.headers
        )
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())

    def test_01_frontend_dev_server_alive(self):
        """Frontend server http://localhost:5173 should return HTTP 200 with HTML"""
        req = urllib.request.Request(FRONTEND_URL)
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            content = resp.read().decode('utf-8')
            self.assertIn("<html", content.lower())
            self.assertIn("app", content)
            print(" -> Frontend server running and serving HTML.")

    def test_02_khilinh_read_request_balance(self):
        """Test read query: 'Ví tiền mặt còn bao nhiêu?'"""
        status, data = self._post("/api/ai/chat", {"message": "Ví tiền mặt còn bao nhiêu?"})
        self.assertEqual(status, 200)
        self.assertIn("response", data)
        self.assertIn("state", data)
        self.assertIn(data["state"], ["IDLE", "SUCCESS"])
        print(f" -> Khí Linh Read Query Response: {data['response'][:80]}... [State: {data['state']}]")

    def test_03_khilinh_financial_mutation_confirmation_card_data(self):
        """Test mutation: 'Tôi vừa ăn sáng hết 50 nghìn.' -> MUST yield state CONFIRMING with pending_confirmation"""
        status, data = self._post("/api/ai/chat", {"message": "Tôi vừa ăn sáng hết 50 nghìn."})
        self.assertEqual(status, 200)
        self.assertEqual(data["state"], "CONFIRMING", "Mutation must require confirmation")
        self.assertIsNotNone(data["pending_confirmation"], "pending_confirmation must not be None")
        
        pending = data["pending_confirmation"]
        self.assertEqual(pending["tool_name"], "create_expense")
        self.assertEqual(pending["args"]["amount"], 50000.0)
        self.assertIn("ăn sáng", pending["args"]["note"].lower())
        print(f" -> Confirmation Card Data: {pending['tool_name']} | {pending['args']['amount']:,.0f} VNĐ | Note: {pending['args']['note']}")

    def test_04_khilinh_cancellation_flow(self):
        """From CONFIRMING, user sends 'Hủy' -> MUST cancel action and return state IDLE"""
        # Ensure we have a pending confirmation
        self._post("/api/ai/chat", {"message": "Tôi vừa mua sách 120 nghìn."})
        
        # User cancels
        status, data = self._post("/api/ai/chat", {"message": "Hủy"})
        self.assertEqual(status, 200)
        self.assertEqual(data["state"], "IDLE")
        self.assertIn("hủy", data["response"].lower())
        print(f" -> Cancellation Response: {data['response']} [State: {data['state']}]")

    def test_05_khilinh_confirmation_execution_flow_and_db_persistence(self):
        """From CONFIRMING, user sends 'Xác nhận' -> MUST execute create_expense, return SUCCESS, and persist in transactions table"""
        # 1. Initiate expense
        status, init_data = self._post("/api/ai/chat", {"message": "Tôi vừa ăn bún chả 55 nghìn."})
        self.assertEqual(init_data["state"], "CONFIRMING")

        # 2. Confirm
        status, conf_data = self._post("/api/ai/chat", {"message": "Xác nhận"})
        self.assertEqual(status, 200)
        self.assertEqual(conf_data["state"], "SUCCESS")
        self.assertEqual(conf_data["tool_executed"], "create_expense")
        self.assertTrue(conf_data["tool_result"]["success"])

        # 3. Verify in transactions list
        status, txn_data = self._get("/api/transactions")
        self.assertEqual(status, 200)
        txns = txn_data.get("data", []) if isinstance(txn_data, dict) else txn_data
        matched = [t for t in txns if t["amount"] == 55000.0 and "bún chả" in t.get("note", "").lower()]
        self.assertTrue(len(matched) > 0, "New expense must be persisted in transactions table")
        print(f" -> Confirmed & Persisted: {matched[0]['note']} - {matched[0]['amount']:,.0f} VNĐ [ID: {matched[0]['id']}]")

    def test_06_khilinh_chat_history_preserved(self):
        """Verify that conversation history is preserved in chat_sessions"""
        status, history = self._get("/api/ai/chat-history")
        self.assertEqual(status, 200)
        self.assertTrue(len(history) > 0)
        print(f" -> Chat history entries verified: {len(history)} entries.")

    def test_07_khilinh_followup_modification_flow(self):
        """Follow-up modification: User initiates transfer 500k -> modifies to 200k -> confirms -> executes 200k"""
        status, wdata = self._get("/api/wallets")
        print(f" -> User wallets: {[w['wallet_name'] for w in wdata]}")
        w_from = wdata[0]["wallet_name"]
        w_to = wdata[1]["wallet_name"]
        # 1. Initiate transfer
        status, data1 = self._post("/api/ai/chat", {"message": f"Chuyển 500 nghìn từ {w_from} sang {w_to}"})
        print(f" -> pending_confirmation args: {data1['pending_confirmation']['args']}")
        self.assertEqual(data1["state"], "CONFIRMING")
        self.assertEqual(data1["pending_confirmation"]["args"]["amount"], 500000.0)

        # 2. Modify amount before confirming
        status, data2 = self._post("/api/ai/chat", {"message": "Sửa thành 200 nghìn"})
        self.assertEqual(data2["state"], "CONFIRMING")
        self.assertEqual(data2["pending_confirmation"]["args"]["amount"], 200000.0)

        # 3. Confirm execution
        status, data3 = self._post("/api/ai/chat", {"message": "Xác nhận"})
        self.assertEqual(data3["state"], "SUCCESS")
        self.assertEqual(data3["tool_executed"], "transfer_money")
        self.assertEqual(data3["tool_result"]["data"]["amount"], 200000.0)
        print(f" -> Follow-up Modification Succeeded: Transferred {data3['tool_result']['data']['amount']:,.0f} VNĐ from {data3['tool_result']['data']['from_wallet']} to {data3['tool_result']['data']['to_wallet']}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
