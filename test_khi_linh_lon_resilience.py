import unittest
from unittest.mock import AsyncMock
from ai_agent.knowledge.rag import KnowledgeRAG

class TestKhiLinhLonResilience(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.rag = KnowledgeRAG()

    def test_synthesize_knowledge_fallback_spending_advice(self):
        """Kiểm tra fallback tự chủ khi hỏi về lời khuyên chi tiêu"""
        retrieved = self.rag.retrieve("cho tôi lời khuyên về chi tiêu")
        res = self.rag.synthesize_knowledge_fallback("cho tôi lời khuyên về chi tiêu", retrieved)
        self.assertIn("Chủ Nhân", res)
        self.assertIn("50/30/20", res)
        self.assertIn("Hạn Mức", res)
        self.assertNotIn("Đạo Hữu", res)
        self.assertNotIn("Ký Chủ", res)

    def test_synthesize_knowledge_fallback_system_features(self):
        """Kiểm tra fallback tự chủ khi hỏi về chức năng hệ thống"""
        retrieved = self.rag.retrieve("hệ thống có những chức năng gì")
        res = self.rag.synthesize_knowledge_fallback("hệ thống có những chức năng gì", retrieved)
        self.assertIn("Chủ Nhân", res)
        self.assertIn("Túi Càn Khôn", res)
        self.assertIn("Sổ Giao Dịch", res)
        self.assertIn("Linh Nhãn OCR", res)

    async def test_answer_question_with_provider_failure_graceful_fallback(self):
        """Kiểm tra quy trình RAG khi AI Provider bị lỗi/nghẽn mạng thì không bị sập mà tự chủ phản hồi"""
        mock_provider = AsyncMock()
        mock_provider.generate_response.side_effect = Exception("Deadline expired / Quota exceeded")

        ans, trace = await self.rag.answer_question("cho tôi lời khuyên về chi tiêu", mock_provider)
        self.assertTrue(len(ans) > 50)
        self.assertIn("Chủ Nhân", ans)
        self.assertIn("50/30/20", ans)
        self.assertTrue(len(trace) > 0)

    def test_prompt_addressing_and_length_optimization(self):
        """Kiểm tra prompt được tối ưu gọn gàng và xưng hô chuẩn mực Chủ Nhân"""
        retrieved = self.rag.retrieve("cho tôi lời khuyên về chi tiêu")
        prompt = self.rag.build_grounded_prompt("cho tôi lời khuyên về chi tiêu", retrieved)
        self.assertIn("Chủ Nhân", prompt)
        self.assertIn("CÂU HỎI CỦA CHỦ NHÂN:", prompt)
        self.assertNotIn("CÂU HỎI CỦA KÝ CHỦ:", prompt)
        self.assertLess(len(prompt), 4000)

if __name__ == "__main__":
    unittest.main()
