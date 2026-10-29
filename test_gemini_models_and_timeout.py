# -*- coding: utf-8 -*-
import os
import unittest
from unittest.mock import patch, MagicMock
import main


class TestGeminiModelsAndTimeout(unittest.TestCase):

    def test_default_models_list(self):
        """Kiểm tra danh sách mô hình mặc định phải ưu tiên các bản lite/flash phản hồi nhanh"""
        with patch.dict(os.environ, {}, clear=False):
            if "GEMINI_MODEL" in os.environ:
                del os.environ["GEMINI_MODEL"]
            models = main.get_gemini_models_list()
            self.assertEqual(models[0], "gemini-flash-lite-latest")
            self.assertIn("gemini-3.5-flash-lite", models)
            self.assertIn("gemini-3.5-flash", models)
            # gemini-flash-latest bị treo không nên nằm trong danh sách
            self.assertNotIn("gemini-flash-latest", models)

    def test_custom_gemini_model_env(self):
        """Kiểm tra khi thiết lập GEMINI_MODEL thì mô hình đó được đặt lên đầu tiên"""
        with patch.dict(os.environ, {"GEMINI_MODEL": "gemini-custom-model"}):
            models = main.get_gemini_models_list()
            self.assertEqual(models[0], "gemini-custom-model")
            self.assertIn("gemini-flash-lite-latest", models)

    def test_timeout_fallback_and_handling(self):
        """Kiểm tra logic gọi _call_gemini_sync với timeout và fallback mô hình kế tiếp"""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key", "GEMINI_TIMEOUT": "10"}):
            with patch("google.generativeai.configure") as mock_configure:
                with patch("google.generativeai.GenerativeModel") as mock_gen_model:
                    # Mô hình đầu tiên ném ngoại lệ Timeout
                    mock_model_instance_1 = MagicMock()
                    mock_model_instance_1.generate_content.side_effect = Exception("Deadline expired")

                    # Mô hình thứ hai thành công
                    mock_model_instance_2 = MagicMock()
                    mock_resp = MagicMock()
                    mock_resp.text = "Phản hồi thành công từ Tiên Trí"
                    mock_model_instance_2.generate_content.return_value = mock_resp

                    mock_gen_model.side_effect = [mock_model_instance_1, mock_model_instance_2]

                    res = main._call_gemini_sync("Xin chào")
                    self.assertEqual(res, "Phản hồi thành công từ Tiên Trí")
                    self.assertEqual(mock_gen_model.call_count, 2)


if __name__ == "__main__":
    unittest.main()
