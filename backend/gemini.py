"""Gọi Google Gemini qua SDK google-genai (thay cho google-generativeai đã ngừng phát triển)."""

import time

from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool

from backend.config import GEMINI_API_KEY

# Thử lần lượt các mô hình Flash (nhanh, rẻ); mô hình lỗi / quá tải thì chuyển sang mô hình kế tiếp
GEMINI_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.5-flash",
    "gemini-flash-latest",
]
REQUEST_TIMEOUT_MS = 10000  # mỗi mô hình tối đa 10 giây (Gemini API từ chối deadline < 10 giây)

_client = None
_generate_config = None


def _api_key_configured() -> bool:
    return bool(GEMINI_API_KEY) and GEMINI_API_KEY != "your_api_key_here"


def get_client():
    """Tạo client một lần rồi dùng lại (mỗi lần tạo mới sẽ mở kết nối HTTP mới)."""
    global _client
    if not _api_key_configured():
        raise HTTPException(
            status_code=503,
            detail="Chưa cấu hình GEMINI_API_KEY trong file .env. Đạo hữu hãy thêm chìa khóa API để đàm đạo cùng Khí Linh!"
        )
    if _client is None:
        from google import genai
        from google.genai import types
        _client = genai.Client(
            api_key=GEMINI_API_KEY,
            # Tắt retry nội bộ của SDK: việc thử lại do vòng lặp qua các mô hình bên dưới đảm nhiệm
            http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS, retry_options=types.HttpRetryOptions(attempts=1)),
        )
    return _client


def _get_generate_config():
    """App không dùng function calling → tắt hẳn (tránh cảnh báo AFC của SDK mỗi lần gọi)."""
    global _generate_config
    if _generate_config is None:
        from google.genai import types
        _generate_config = types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        )
    return _generate_config


def image_part(data: bytes, mime_type: str):
    """Đóng gói ảnh để gửi kèm prompt (OCR hóa đơn)."""
    from google.genai import types
    return types.Part.from_bytes(data=data, mime_type=mime_type)


def _is_invalid_key_error(exc: Exception) -> bool:
    code = getattr(exc, "code", None)
    text = str(exc)
    return code in (400, 401, 403) and ("API key" in text or "API_KEY" in text or "PERMISSION_DENIED" in text)


def generate_text(contents) -> str:
    """Gọi Gemini (đồng bộ) và trả về văn bản; thử lần lượt từng mô hình trong GEMINI_MODELS."""
    client = get_client()
    last_error = None
    for model_name in GEMINI_MODELS:
        t0 = time.time()
        try:
            print(f"[Gemini API] Thử mô hình: {model_name}", flush=True)
            response = client.models.generate_content(model=model_name, contents=contents, config=_get_generate_config())
            if response is not None and response.text:
                print(f"[Gemini API] Thành công với mô hình: {model_name} (Thời gian: {time.time() - t0:.2f}s)", flush=True)
                return response.text
        except Exception as e:
            if _is_invalid_key_error(e):
                print(f"[Gemini API] API key bị từ chối: {e!r}", flush=True)
                raise HTTPException(
                    status_code=503,
                    detail="GEMINI_API_KEY không hợp lệ hoặc đã bị thu hồi. Hãy tạo khóa mới tại Google AI Studio và cập nhật file .env."
                )
            print(f"[Gemini API] Bỏ qua mô hình {model_name} sau {time.time() - t0:.2f}s do lỗi: {e!r}", flush=True)
            last_error = e

    print(f"[Gemini API] Tất cả mô hình đều thất bại. Lỗi cuối: {last_error!r}", flush=True)
    raise HTTPException(
        status_code=504,
        detail="Tiên Trí phản hồi quá lâu hoặc đang gặp trở ngại. Vui lòng thử lại sau ít phút."
    )


async def generate_text_async(contents) -> str:
    """Gọi Gemini qua threadpool để không block event loop của FastAPI."""
    return await run_in_threadpool(generate_text, contents)
