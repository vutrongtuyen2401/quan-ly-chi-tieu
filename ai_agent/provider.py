"""
AI Provider Layer
Trừu tượng hóa nhà cung cấp mô hình trí tuệ nhân tạo (AI Provider).
Agent Core phụ thuộc vào AIProvider thay vì phụ thuộc cứng vào Gemini.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List


class AIProvider(ABC):
    """Lớp cơ sở trừu tượng cho tất cả AI Providers"""

    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Sinh phản hồi văn bản từ prompt"""
        pass

    @abstractmethod
    async def parse_structured_intent(self, prompt: str, schema: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Phân tích ý định người dùng và sinh cấu trúc JSON"""
        pass


class GeminiProvider(AIProvider):
    """Triển khai AIProvider sử dụng Google Gemini Flash (tái sử dụng cấu hình hiện có của dự án)"""

    def __init__(self, gemini_caller=None):
        self._caller = gemini_caller

    def _get_caller(self):
        if self._caller:
            return self._caller
        # Tránh circular import bằng cách import tại runtime
        import main
        return main.generate_gemini_content_async

    async def generate_response(self, prompt: str, **kwargs) -> str:
        caller = self._get_caller()
        raw = await caller(prompt, vision=False)
        return (raw or "").strip()

    async def parse_structured_intent(self, prompt: str, schema: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        import json
        structured_prompt = f"""{prompt}
Chỉ trả về JSON thuần túy (không kèm giải thích hay markdown code block thừa). Định dạng:
{json.dumps(schema or {}, ensure_ascii=False, indent=2)}
"""
        caller = self._get_caller()
        raw_text = await caller(structured_prompt, vision=False)
        clean_text = (raw_text or "").strip()
        if clean_text.startswith("```"):
            parts = clean_text.split("```")
            if len(parts) > 1:
                clean_text = parts[1]
                if clean_text.startswith("json"):
                    clean_text = clean_text[4:]
            clean_text = clean_text.strip()
        try:
            return json.loads(clean_text)
        except Exception:
            return {"error": "JSON parse error", "raw": raw_text}


class MockAIProvider(AIProvider):
    """Mock AI Provider phục vụ deterministic test, không gọi ra ngoài mạng internet"""

    def __init__(self, default_response: str = "Tiên Trí đã lắng nghe đạo hữu.", canned_intents: Optional[Dict[str, Any]] = None):
        self.default_response = default_response
        self.canned_intents = canned_intents or {}
        self.history: List[str] = []

    async def generate_response(self, prompt: str, **kwargs) -> str:
        self.history.append(prompt)
        return self.default_response

    async def parse_structured_intent(self, prompt: str, schema: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        self.history.append(prompt)
        for key, value in self.canned_intents.items():
            if key in prompt:
                return value
        return {"tool": None, "arguments": {}}
