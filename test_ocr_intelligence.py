"""Test Suite for Linh Nhãn AI OCR Intelligence Upgrade
Multi-layout receipt recognition, number normalization, total ground truth,
editable line items, and single-transaction recording verification.
"""

import io
import os
import json
import unittest
from unittest.mock import patch, AsyncMock
from starlette.testclient import TestClient

import main
from ai_agent.ocr_engine import (
    parse_vietnamese_currency,
    parse_receipt_date,
    clean_store_name,
    validate_and_normalize_receipt,
    execute_multi_strategy_ocr
)


class TestOcrIntelligence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)
        # Khởi tạo người dùng kiểm thử
        with main.get_db() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role) "
                "VALUES (101, 'ocr_tester@gmail.com', 'test_hash', 'Đạo Hữu Linh Nhãn', 'user')"
            )
            conn.execute(
                "INSERT OR IGNORE INTO wallets (id, user_id, wallet_name, balance) "
                "VALUES (1001, 101, 'Túi Càn Khôn Tiền Mặt', 10000000)"
            )
            conn.execute(
                "INSERT OR IGNORE INTO categories (id, user_id, category_name, category_type, icon) "
                "VALUES (2001, 101, 'Tiệc Tùng & Giải Trí', 'EXPENSE', '🎤')"
            )
            conn.execute(
                "INSERT OR IGNORE INTO categories (id, user_id, category_name, category_type, icon) "
                "VALUES (2002, 101, 'Thời Trang Mua Sắm', 'EXPENSE', '👕')"
            )

    def _get_headers(self, user_id=101, email="ocr_tester@gmail.com", role="user"):
        token = main.create_token(user_id=user_id, email=email, role=role)
        return {"Authorization": f"Bearer {token}"}

    # ─────────────────────────────────────────────────────────────
    # 1. NUMBER & CURRENCY NORMALIZATION
    # ─────────────────────────────────────────────────────────────
    def test_number_normalization_vietnamese_formats(self):
        """Kiểm tra bóc tách và chuẩn hóa các kiểu biểu diễn tiền tệ Việt Nam phổ biến"""
        # Dấu chấm phân cách hàng nghìn
        self.assertEqual(parse_vietnamese_currency("4.030.000"), 4030000.0)
        self.assertEqual(parse_vietnamese_currency("50.000"), 50000.0)
        # Dấu phẩy phân cách hàng nghìn
        self.assertEqual(parse_vietnamese_currency("4,030,000"), 4030000.0)
        # Dấu cách
        self.assertEqual(parse_vietnamese_currency("4 030 000"), 4030000.0)
        # Kèm ký hiệu đ, ₫, VND, VNĐ
        self.assertEqual(parse_vietnamese_currency("4.030.000 đ"), 4030000.0)
        self.assertEqual(parse_vietnamese_currency("4.030.000 ₫"), 4030000.0)
        self.assertEqual(parse_vietnamese_currency("4,030,000 VND"), 4030000.0)
        self.assertEqual(parse_vietnamese_currency("500000 vnđ"), 500000.0)
        # Hậu tố viết tắt
        self.assertEqual(parse_vietnamese_currency("120k"), 120000.0)
        self.assertEqual(parse_vietnamese_currency("1.5tr"), 1500000.0)
        # Số int/float trực tiếp
        self.assertEqual(parse_vietnamese_currency(4030000), 4030000.0)
        self.assertEqual(parse_vietnamese_currency(50000.5), 50000.5)

    def test_number_normalization_invalid_rejected(self):
        """Kiểm tra từ chối số tiền âm, NaN, Boolean hoặc chuỗi rỗng"""
        with self.assertRaises(ValueError):
            parse_vietnamese_currency(-1000)
        with self.assertRaises(ValueError):
            parse_vietnamese_currency(True)
        with self.assertRaises(ValueError):
            parse_vietnamese_currency(None)
        with self.assertRaises(ValueError):
            parse_vietnamese_currency("")
        with self.assertRaises(ValueError):
            parse_vietnamese_currency("hai trieu dong")

    # ─────────────────────────────────────────────────────────────
    # 2. DATE NORMALIZATION
    # ─────────────────────────────────────────────────────────────
    def test_date_normalization_formats(self):
        """Kiểm tra chuẩn hóa ngày đa định dạng về ISO YYYY-MM-DD"""
        self.assertEqual(parse_receipt_date("2026-03-20"), "2026-03-20")
        self.assertEqual(parse_receipt_date("24/01/2026"), "2026-01-24")
        self.assertEqual(parse_receipt_date("24/01/2026 22:30:15"), "2026-01-24")
        self.assertEqual(parse_receipt_date("Ngày lập: 24-01-2026"), "2026-01-24")
        self.assertEqual(parse_receipt_date("15.09.2026"), "2026-09-15")
        # Không có ngày hợp lệ -> trả về None (không đoán bừa)
        self.assertIsNone(parse_receipt_date(None))
        self.assertIsNone(parse_receipt_date(""))
        self.assertIsNone(parse_receipt_date("không có ngày"))

    # ─────────────────────────────────────────────────────────────
    # 3. CASE A: KARAOKE RECEIPT RECOGNITION
    # ─────────────────────────────────────────────────────────────
    def test_case_a_karaoke_receipt(self):
        """CASE A: Hóa đơn Karaoke / dịch vụ với cột TÊN HÀNG, SL, Đ.GIÁ, T.THÀNH, TOTAL"""
        karaoke_raw = {
            "store_name": "Quán Karaoke Họa Mi 3",
            "receipt_date": "24/01/2026 21:45",
            "total": "4.030.000 đ",
            "items": [
                {"name": "Tiger Nâu Chai", "quantity": "20", "unit_price": "25.000", "line_total": "500.000"},
                {"name": "Thuốc Lá 555", "quantity": "1", "unit_price": "80.000", "line_total": "80.000"},
                {"name": "Trái Cây Thập Cẩm Đĩa Lớn", "quantity": "2", "unit_price": "150.000", "line_total": "300.000"},
                {"name": "Khăn Lạnh VIP", "quantity": "15", "unit_price": "5.000", "line_total": "75.000"},
                {"name": "Giờ Hát Phòng VIP 08 (3h)", "quantity": "1", "unit_price": "3.075.000", "line_total": "3.075.000"}
            ],
            "currency": "VND"
        }

        res = validate_and_normalize_receipt(karaoke_raw)
        self.assertEqual(res["store_name"], "Quán Karaoke Họa Mi 3")
        self.assertEqual(res["total"], 4030000.0)
        self.assertEqual(res["receipt_date"], "2026-01-24")
        self.assertEqual(len(res["items"]), 5)
        # Kiểm tra chi tiết dòng đầu tiên
        item0 = res["items"][0]
        self.assertEqual(item0["name"], "Tiger Nâu Chai")
        self.assertEqual(item0["quantity"], 20)
        self.assertEqual(item0["unit_price"], 25000.0)
        self.assertEqual(item0["line_total"], 500000.0)

    # ─────────────────────────────────────────────────────────────
    # 4. CASE B: CLOTHING / RETAIL RECEIPT & MULTILINE ITEM
    # ─────────────────────────────────────────────────────────────
    def test_case_b_clothing_receipt_and_multiline(self):
        """CASE B: Hóa đơn bán lẻ thời trang, tên sản phẩm nhiều dòng, bỏ qua thông tin khách mua"""
        clothing_raw = {
            "store_name": "Cửa Hàng Thời Trang An Nhiên Boutique",
            "receipt_date": "2026-03-21",
            "total": "750.000",
            "items": [
                {
                    "name": "Áo Sơ Mi Xanh Vải Linen Cao Cấp I Kẻ Sọc - M - Cái",
                    "quantity": 1,
                    "unit_price": "750.000 đ",
                    "line_total": "750.000 đ"
                }
            ],
            # Khách hàng và thông tin phụ trong OCR
            "customer_name": "Nguyễn Văn Tu Sĩ",
            "customer_phone": "0987654321",
            "cashier": "Thu Ngân 02"
        }

        res = validate_and_normalize_receipt(clothing_raw)
        self.assertIn("Thời Trang An Nhiên", res["store_name"])
        self.assertNotIn("Nguyễn Văn Tu Sĩ", res["store_name"])
        self.assertEqual(res["total"], 750000.0)
        self.assertEqual(len(res["items"]), 1)
        self.assertEqual(res["items"][0]["name"], "Áo Sơ Mi Xanh Vải Linen Cao Cấp I Kẻ Sọc - M - Cái")

    # ─────────────────────────────────────────────────────────────
    # 5. CASE C: RECEIPT TOTAL IS GROUND TRUTH (NO AUTO-RECALCULATE)
    # ─────────────────────────────────────────────────────────────
    def test_case_c_receipt_total_is_ground_truth(self):
        """CASE C: Khi tổng từng dòng không khớp chính xác với TOTAL in trên hóa đơn,
        hệ thống GIỮ NGUYÊN TOTAL làm nguồn sự thật và sinh cảnh báo cho người dùng,
        tuyệt đối không tự sửa TOTAL."""
        mismatch_raw = {
            "store_name": "Nhà Hàng Sơn Thủy",
            "receipt_date": "2026-03-20",
            "total": 4030000.0, # Nguồn sự thật in trên hóa đơn
            "items": [
                {"name": "Gà hấp lá chanh", "quantity": 1, "unit_price": 300000, "line_total": 300000},
                {"name": "Lẩu cá tầm", "quantity": 1, "unit_price": 500000, "line_total": 500000}
                # Tổng 2 món là 800.000đ, khác 4.030.000đ (có thể do các dịch vụ khác)
            ]
        }

        res = validate_and_normalize_receipt(mismatch_raw)
        # TOTAL tuyệt đối không bị ghi đè thành 800.000!
        self.assertEqual(res["total"], 4030000.0)
        self.assertEqual(res["total_amount"], 4030000.0)
        # Có cảnh báo đối chiếu
        self.assertIsNotNone(res["warning"])
        self.assertIn("không khớp", res["warning"])

    # ─────────────────────────────────────────────────────────────
    # 6. CASE D: MULTI-STRATEGY FALLBACK EXECUTION
    # ─────────────────────────────────────────────────────────────
    def test_case_d_multi_strategy_fallback(self):
        """CASE D: Khi Chiến lược A gặp lỗi định dạng, Chiến lược B dự phòng được kích hoạt và thành công"""
        headers = self._get_headers()

        mock_raw_b = json.dumps({
            "store_name": "Quán Trà Đạo Tiên Cảnh",
            "receipt_date": "2026-03-20",
            "total": 120000,
            "items": [{"name": "Bạch Hạc Trà", "quantity": 2, "unit_price": 60000, "line_total": 120000}],
            "currency": "VND"
        })

        image_bytes = io.BytesIO(b"\xff\xd8\xff\xe0" + b"dummy_valid_image")
        files = {"file": ("receipt_fallback.jpg", image_bytes, "image/jpeg")}

        # Lần 1 (Strategy A) trả lỗi parse / cú pháp, Lần 2 (Strategy B) trả JSON hợp lệ
        with patch("main.generate_gemini_content_async", new_callable=AsyncMock) as mock_gemini:
            mock_gemini.side_effect = ["Phản hồi không phải JSON hợp lệ", mock_raw_b]
            res = self.client.post("/api/ai/scan-invoice", files=files, headers=headers)

        self.assertEqual(res.status_code, 200)
        d = res.json()
        self.assertTrue(d["success"])
        self.assertEqual(d["data"]["store_name"], "Quán Trà Đạo Tiên Cảnh")
        self.assertEqual(d["data"]["total"], 120000.0)

    # ─────────────────────────────────────────────────────────────
    # 7. CASE E: ONE RECEIPT = EXACTLY ONE EXPENSE TRANSACTION IN DB
    # ─────────────────────────────────────────────────────────────
    def test_case_e_one_receipt_creates_exactly_one_expense_transaction(self):
        """CASE E: Xác nhận một hóa đơn nhiều món (ví dụ 5 món) sau khi người dùng sửa
        chỉ tạo DUY NHẤT 1 giao dịch chi tiêu (EXPENSE) với số tiền bằng TOTAL đã sửa."""
        headers = self._get_headers()

        # 1. Quét hóa đơn (OCR scan)
        karaoke_json = json.dumps({
            "store_name": "Karaoke Họa Mi 3",
            "receipt_date": "2026-01-24",
            "total": 4030000,
            "items": [
                {"name": "Tiger Nâu", "quantity": 20, "unit_price": 25000, "line_total": 500000},
                {"name": "Thuốc 555", "quantity": 1, "unit_price": 80000, "line_total": 80000},
                {"name": "Trái Cây", "quantity": 2, "unit_price": 150000, "line_total": 300000}
            ]
        })

        image_bytes = io.BytesIO(b"\xff\xd8\xff\xe0" + b"dummy_karaoke")
        files = {"file": ("karaoke.jpg", image_bytes, "image/jpeg")}

        with patch("main.generate_gemini_content_async", new_callable=AsyncMock) as mock_gemini:
            mock_gemini.return_value = karaoke_json
            scan_res = self.client.post("/api/ai/scan-invoice", files=files, headers=headers)

        self.assertEqual(scan_res.status_code, 200)
        scan_data = scan_res.json()["data"]

        # 2. Giả lập Người dùng phát hiện hóa đơn thực tế là 4.080.000đ (sửa TOTAL)
        edited_total = 4080000.0
        edited_note = "Karaoke Họa Mi 3 (Đã soát)"

        # Đếm số giao dịch trước khi lưu
        with main.get_db() as conn:
            tx_count_before = conn.execute(
                "SELECT COUNT(*) FROM transactions WHERE user_id = 101"
            ).fetchone()[0]

        # 3. Người dùng bấm 'Xác Nhận Tạo Giao Dịch'
        create_payload = {
            "amount": edited_total,
            "wallet_id": 1001,
            "category_id": 2001,
            "transaction_date": scan_data["receipt_date"],
            "note": edited_note,
            "transaction_type": "EXPENSE"
        }
        create_res = self.client.post("/api/transactions", json=create_payload, headers=headers)
        self.assertEqual(create_res.status_code, 200)

        # 4. Kiểm tra trong DB: tăng CHÍNH XÁC 1 giao dịch, số tiền = 4.080.000đ
        with main.get_db() as conn:
            tx_count_after = conn.execute(
                "SELECT COUNT(*) FROM transactions WHERE user_id = 101"
            ).fetchone()[0]
            self.assertEqual(tx_count_after, tx_count_before + 1, "Chỉ được tạo đúng 1 giao dịch duy nhất cho hóa đơn!")

            latest_tx = conn.execute(
                "SELECT * FROM transactions WHERE user_id = 101 ORDER BY id DESC LIMIT 1"
            ).fetchone()
            self.assertEqual(latest_tx["amount"], 4080000.0)
            self.assertEqual(latest_tx["transaction_type"], "EXPENSE")
            self.assertEqual(latest_tx["wallet_id"], 1001)
            self.assertEqual(latest_tx["category_id"], 2001)
            self.assertEqual(latest_tx["note"], edited_note)

    # ─────────────────────────────────────────────────────────────
    # 8. CASE F: NON-RECEIPT IMAGE REJECTION (TRUTHFUL 422 STRICT)
    # ─────────────────────────────────────────────────────────────
    def test_case_f_non_receipt_image_rejected(self):
        """CASE F: Ảnh không phải hóa đơn bị từ chối trung thực với HTTP 422, không ghi log fake vào DB"""
        headers = self._get_headers()

        with main.get_db() as conn:
            logs_before = conn.execute("SELECT COUNT(*) FROM invoice_ocr_logs WHERE user_id = 101").fetchone()[0]

        # Giả lập AI nhận diện ảnh phong cảnh / không phải hóa đơn
        image_bytes = io.BytesIO(b"\xff\xd8\xff\xe0" + b"landscape_photo")
        files = {"file": ("cat_photo.jpg", image_bytes, "image/jpeg")}

        with patch("main.generate_gemini_content_async", new_callable=AsyncMock) as mock_gemini:
            mock_gemini.return_value = json.dumps({"status": "not a receipt", "is_receipt": False})
            res = self.client.post("/api/ai/scan-invoice", files=files, headers=headers)

        self.assertEqual(res.status_code, 422)
        self.assertIn("Linh Nhãn không thể nhận diện hóa đơn", res.json()["detail"])

        # Đảm bảo không có bản ghi nào bị ghi vào invoice_ocr_logs
        with main.get_db() as conn:
            logs_after = conn.execute("SELECT COUNT(*) FROM invoice_ocr_logs WHERE user_id = 101").fetchone()[0]
            self.assertEqual(logs_after, logs_before)

    # ─────────────────────────────────────────────────────────────
    # 9. CASE G: UNUSUAL LAYOUT & REARRANGED COLUMNS (RETAIL / F&B)
    # ─────────────────────────────────────────────────────────────
    def test_case_g_unusual_layout_rearranged_columns(self):
        """CASE G: Bố cục thay đổi thứ tự cột (SẢN PHẨM / ĐƠN GIÁ / SL / T.TIỀN) vẫn được chuẩn hóa thành công"""
        unusual_raw = {
            "store_name": "Nhà Sách Trí Tuệ",
            "receipt_date": "2026-03-21",
            "total": 350000,
            "items": [
                {
                    "item_name": "Sổ Tay Bìa Da Cổ Điển",
                    "price": 120000,
                    "qty": 2,
                    "amount": 240000
                },
                {
                    "item_name": "Bút Ký Kim Loại Cao Cấp",
                    "price": 110000,
                    "qty": 1,
                    "amount": 110000
                }
            ],
            "currency": "VND"
        }

        res = validate_and_normalize_receipt(unusual_raw)
        self.assertEqual(res["store_name"], "Nhà Sách Trí Tuệ")
        self.assertEqual(res["total"], 350000.0)
        self.assertEqual(len(res["items"]), 2)
        self.assertEqual(res["items"][0]["name"], "Sổ Tay Bìa Da Cổ Điển")
        self.assertEqual(res["items"][0]["quantity"], 2)
        self.assertEqual(res["items"][0]["unit_price"], 120000.0)
        self.assertEqual(res["items"][0]["line_total"], 240000.0)

    # ─────────────────────────────────────────────────────────────
    # 10. CASE H: RECEIPT MISSING TOTAL REJECTED
    # ─────────────────────────────────────────────────────────────
    def test_case_h_missing_total_rejected(self):
        """CASE H: Hóa đơn thiếu total hoặc total <= 0 bị từ chối trung thực"""
        no_total_raw = {
            "store_name": "Tiệm Bánh Mì",
            "receipt_date": "2026-03-21",
            "items": [{"name": "Bánh mì thịt", "quantity": 1, "unit_price": 25000, "line_total": 25000}]
        }
        with self.assertRaises(ValueError):
            validate_and_normalize_receipt(no_total_raw)

        zero_total_raw = {
            "store_name": "Tiệm Bánh Mì",
            "receipt_date": "2026-03-21",
            "total": 0,
            "items": [{"name": "Bánh mì thịt", "quantity": 1, "unit_price": 25000, "line_total": 25000}]
        }
        with self.assertRaises(ValueError):
            validate_and_normalize_receipt(zero_total_raw)

    # ─────────────────────────────────────────────────────────────
    # 11. CASE I: NO CROSS-USER LEAKAGE IN OCR LOGS
    # ─────────────────────────────────────────────────────────────
    def test_case_i_user_isolation_ocr_logs(self):
        """CASE I: Người dùng A không xem hoặc ghi đè được nhật ký OCR của người dùng B"""
        headers_a = self._get_headers(user_id=101, email="ocr_tester@gmail.com")
        headers_b = self._get_headers(user_id=102, email="user_b@gmail.com")

        # Insert 1 log cho user 101
        with main.get_db() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role) "
                "VALUES (102, 'user_b@gmail.com', 'hash', 'User B', 'user')"
            )
            conn.execute(
                "INSERT INTO invoice_ocr_logs (user_id, image_path, extracted_json) VALUES (?, ?, ?)",
                (101, "private_a.jpg", json.dumps({"store_name": "Bí Mật User A", "total": 999999}))
            )
            # Query log của user 102
            user_b_logs = conn.execute(
                "SELECT * FROM invoice_ocr_logs WHERE user_id = 102"
            ).fetchall()
            # User B không có log của User A
            for log in user_b_logs:
                self.assertNotIn("Bí Mật User A", log["extracted_json"])


if __name__ == "__main__":
    unittest.main()

