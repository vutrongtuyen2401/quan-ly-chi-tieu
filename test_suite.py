import os
import sys
import io
import unittest
from fastapi.testclient import TestClient

from main import app, init_db, validate_image_bytes, cleanup_corrupted_categories, SessionLocal
from models import Category

class TestCanKhonAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_01_login_default_admin(self):
        res = self.client.post("/api/auth/login", json={
            "email": "admin@gmail.com",
            "password": "123456"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("token", data)
        self.__class__.admin_token = data["token"]

    def test_02_register_new_user_and_validation(self):
        # Invalid email validation (Natural language error check)
        res = self.client.post("/api/auth/register", json={
            "email": "invalid-email",
            "password": "password123",
            "full_name": "Người Dùng Mới"
        })
        self.assertEqual(res.status_code, 422)
        err_detail = res.json().get("detail", "")
        self.assertIsInstance(err_detail, str)
        self.assertIn("email", err_detail.lower())

        # Password too short validation
        res_pw = self.client.post("/api/auth/register", json={
            "email": "valid_user_test@gmail.com",
            "password": "123",
            "full_name": "Người Dùng Mới"
        })
        self.assertEqual(res_pw.status_code, 422)
        self.assertIn("mật khẩu tối thiểu 6 kí tự", res_pw.json().get("detail", "").lower())

        # Valid register
        import time
        unique_email = f"test_{int(time.time())}@tongmon.com"
        res = self.client.post("/api/auth/register", json={
            "email": unique_email,
            "password": "password123",
            "full_name": "Người Dùng Mới"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("token", data)

    def test_03_wallets_and_transfer(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get wallets
        res = self.client.get("/api/wallets", headers=headers)
        self.assertEqual(res.status_code, 200)
        wallets = res.json()
        self.assertGreaterEqual(len(wallets), 2)
        
        w1, w2 = wallets[0], wallets[1]
        w1_init = w1["balance"]
        w2_init = w2["balance"]

        # Transfer 100,000 VND
        transfer_amount = 100000
        res = self.client.post("/api/wallets/transfer", json={
            "from_wallet_id": w1["id"],
            "to_wallet_id": w2["id"],
            "amount": transfer_amount,
            "note": "Test transfer"
        }, headers=headers)
        self.assertEqual(res.status_code, 200)

        # Check balances updated
        res = self.client.get("/api/wallets", headers=headers)
        updated_wallets = {w["id"]: w["balance"] for w in res.json()}
        self.assertEqual(updated_wallets[w1["id"]], w1_init - transfer_amount)
        self.assertEqual(updated_wallets[w2["id"]], w2_init + transfer_amount)

    def test_04_transactions_crud_and_balance(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get wallets and categories
        wallets = self.client.get("/api/wallets", headers=headers).json()
        categories = self.client.get("/api/categories", headers=headers).json()
        
        wallet = wallets[0]
        expense_cat = [c for c in categories if c["category_type"] == "EXPENSE"][0]
        income_cat = [c for c in categories if c["category_type"] == "INCOME"][0]

        # Mismatched category type check
        res = self.client.post("/api/transactions", json={
            "wallet_id": wallet["id"],
            "category_id": income_cat["id"],
            "amount": 50000,
            "transaction_type": "EXPENSE",
            "transaction_date": "2026-08-13",
            "note": "Invalid mismatch test"
        }, headers=headers)
        self.assertEqual(res.status_code, 400)

        # Valid create expense transaction
        init_balance = self.client.get("/api/wallets", headers=headers).json()[0]["balance"]
        res = self.client.post("/api/transactions", json={
            "wallet_id": wallet["id"],
            "category_id": expense_cat["id"],
            "amount": 50000,
            "transaction_type": "EXPENSE",
            "transaction_date": "2026-08-13",
            "note": "Mua đồ dùng văn phòng"
        }, headers=headers)
        self.assertEqual(res.status_code, 200)
        txn_id = res.json()["id"]

        # Verify wallet balance decreased
        new_balance = self.client.get("/api/wallets", headers=headers).json()[0]["balance"]
        self.assertEqual(new_balance, init_balance - 50000)

        # Delete transaction and check balance restored
        res = self.client.delete(f"/api/transactions/{txn_id}", headers=headers)
        self.assertEqual(res.status_code, 200)
        restored_balance = self.client.get("/api/wallets", headers=headers).json()[0]["balance"]
        self.assertEqual(restored_balance, init_balance)

    def test_05_reports_and_budget_check(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        res = self.client.get("/api/reports/summary", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn("total_income", res.json())
        self.assertIn("total_expense", res.json())

        res = self.client.get("/api/reports/trend?months=6", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn("trend", res.json())

        res = self.client.get("/api/reports/weekly?weeks=4", headers=headers)
        self.assertEqual(res.status_code, 200)

        res = self.client.post("/api/ai/check-budget", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn("alerts", res.json())

    def test_06_magic_bytes_validation(self):
        # JPEG header
        jpeg_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 20
        self.assertEqual(validate_image_bytes(jpeg_bytes), "image/jpeg")

        # PNG header
        png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
        self.assertEqual(validate_image_bytes(png_bytes), "image/png")

        # Non-image
        fake_bytes = b"<html><script>alert(1)</script></html>"
        with self.assertRaises(ValueError):
            validate_image_bytes(fake_bytes)

    def test_07_gemini_config(self):
        from main import get_gemini_api_key, get_gemini_models_list
        api_key = get_gemini_api_key()
        self.assertTrue(bool(api_key), "API Key should be detected from .env")
        models = get_gemini_models_list(vision=False)
        self.assertGreater(len(models), 0, "Candidate models list should not be empty")

    def test_08_analytics_and_forecasting(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        res = self.client.get("/api/analytics", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("today_income", data)
        self.assertIn("today_expense", data)
        self.assertIn("avg_daily_expense_7d", data)
        self.assertIn("avg_daily_expense_30d", data)
        self.assertIn("forecast_tomorrow_expense", data)
        self.assertIn("forecast_month_end_balance", data)
        self.assertIn("is_overspending", data)
        self.assertIn("forecast_message", data)

    def test_09_gemini_ai_chat_and_ocr(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}

        # 1. Test AI Chat endpoint
        res_chat = self.client.post("/api/ai/chat", json={
            "message": "Làm thế nào để tiết kiệm 20% thu nhập mỗi tháng?"
        }, headers=headers)
        self.assertEqual(res_chat.status_code, 200)
        chat_data = res_chat.json()
        self.assertIn("response", chat_data)
        self.assertIsInstance(chat_data["response"], str)
        self.assertTrue(len(chat_data["response"]) > 0)

        # 2. Test Chat history endpoint
        res_hist = self.client.get("/api/ai/chat-history", headers=headers)
        self.assertEqual(res_hist.status_code, 200)
        self.assertIsInstance(res_hist.json(), list)

        # 3. Test OCR endpoint with simulated valid image
        fake_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00" + b"\x00" * 100
        files = {"file": ("receipt.jpg", io.BytesIO(fake_jpeg), "image/jpeg")}
        res_ocr = self.client.post("/api/ocr", files=files, headers=headers)
        self.assertEqual(res_ocr.status_code, 200)
        ocr_data = res_ocr.json()
        self.assertIn("status", ocr_data)
        self.assertIn("amount", ocr_data)
        self.assertIn("date", ocr_data)

    def test_10_cleanup_categories_mojibake(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}

        # Tạo category lỗi font thử nghiệm
        db = SessionLocal()
        try:
            bad_cat = Category(Name="?? An U?ng Test", Type="EXPENSE", Icon="fas fa-test")
            db.add(bad_cat)
            db.commit()
        finally:
            db.close()

        # Gọi API dọn rác
        res = self.client.post("/api/cleanup-categories", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("cleaned_count", data)
        self.assertGreaterEqual(data["cleaned_count"], 1)

        # Kiểm tra không còn category nào chứa ký tự '?'
        res_cats = self.client.get("/api/categories", headers=headers)
        for cat in res_cats.json():
            self.assertNotIn("?", cat["category_name"])

if __name__ == "__main__":
    unittest.main()
