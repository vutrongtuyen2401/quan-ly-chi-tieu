"""Tính năng AI (Google Gemini): OCR hóa đơn, chat, cảnh báo hạn mức, gợi ý tiết kiệm."""

import datetime
import json
import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from backend import gemini
from backend.config import OCR_MAX_BYTES
from backend.db import get_db
from backend.schemas import ChatBody, _check_date
from backend.security import get_current_user

router = APIRouter()


# ──────────────────────────────────────────────
# AI ROUTES (Google Gemini)
# ──────────────────────────────────────────────
@router.post("/api/ai/scan-invoice")
async def scan_invoice(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """Linh Nhãn AI OCR — quét hóa đơn từ ảnh"""
    content_type = (file.content_type or "").lower()
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file ảnh (JPG, PNG, WEBP...).")
    contents = await file.read(OCR_MAX_BYTES + 1)
    if not contents:
        raise HTTPException(status_code=400, detail="File ảnh trống.")
    if len(contents) > OCR_MAX_BYTES:
        raise HTTPException(status_code=413, detail="Ảnh quá lớn (tối đa 8 MB). Vui lòng chọn ảnh nhỏ hơn.")

    prompt = """Bạn là trợ lý AI tài chính. Hãy phân tích hóa đơn/receipt trong ảnh này.
    Trả về JSON với format:
    {
        "store_name": "Tên cửa hàng",
        "total_amount": 0,
        "items": [{"name": "Tên sản phẩm", "price": 0, "quantity": 1}],
        "date": "YYYY-MM-DD",
        "currency": "VND"
    }
    Chỉ trả về JSON, không giải thích thêm."""

    gemini_input = [prompt, gemini.image_part(contents, content_type)]
    response_text = (await gemini.generate_text_async(gemini_input)).strip()

    try:
        # Bóc JSON khỏi khối ```json ... ``` nếu có
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        extracted = json.loads(response_text)
        if not isinstance(extracted, dict):
            raise ValueError("OCR result is not an object")
    except (ValueError, IndexError) as e:
        print(f"[OCR] Không phân tích được phản hồi Gemini: {e!r}", flush=True)
        raise HTTPException(
            status_code=422,
            detail="Linh Nhãn không đọc được hóa đơn này. Hãy thử ảnh rõ nét hơn hoặc nhập giao dịch thủ công."
        )

    # Chuẩn hóa các trường frontend dùng tới
    try:
        extracted["total_amount"] = max(round(float(extracted.get("total_amount") or 0)), 0)
    except (TypeError, ValueError):
        extracted["total_amount"] = 0
    try:
        extracted["date"] = _check_date(str(extracted.get("date") or ""))
    except ValueError:
        extracted["date"] = datetime.date.today().strftime("%Y-%m-%d")

    with get_db() as conn:
        conn.execute(
            "INSERT INTO invoice_ocr_logs (user_id, image_path, extracted_json) VALUES (?, ?, ?)",
            (user["user_id"], file.filename or "", json.dumps(extracted, ensure_ascii=False))
        )

    return {"success": True, "data": extracted}


@router.post("/api/ai/check-budget")
def check_budget(user: dict = Depends(get_current_user)):
    """Cảnh Báo Tẩu Hỏa Nhập Ma — kiểm tra ngân sách"""
    month_year = datetime.date.today().strftime("%Y-%m")
    with get_db() as conn:
        budgets = conn.execute("""
            SELECT b.*, c.category_name, c.icon,
                   COALESCE((SELECT SUM(t.amount) FROM transactions t
                             WHERE t.category_id = b.category_id
                             AND t.user_id = b.user_id
                             AND t.transaction_type = 'EXPENSE'
                             AND strftime('%Y-%m', t.transaction_date) = b.month_year), 0) as spent
            FROM budgets b
            LEFT JOIN categories c ON b.category_id = c.id
            WHERE b.user_id = ? AND b.month_year = ?
        """, (user["user_id"], month_year)).fetchall()

        alerts = []
        for b in budgets:
            b = dict(b)
            pct = (b["spent"] / b["limit_amount"] * 100) if b["limit_amount"] > 0 else 0
            if pct >= 100:
                alerts.append({
                    "category": b["category_name"],
                    "icon": b["icon"],
                    "spent": b["spent"],
                    "limit": b["limit_amount"],
                    "percent": round(pct, 1),
                    "level": "DANGER",
                    "message": f"🔥 TẨU HỎA NHẬP MA! {b['category_name']} đã vượt hạn mức ({round(pct,1)}%)"
                })
            elif pct >= 80:
                alerts.append({
                    "category": b["category_name"],
                    "icon": b["icon"],
                    "spent": b["spent"],
                    "limit": b["limit_amount"],
                    "percent": round(pct, 1),
                    "level": "WARNING",
                    "message": f"⚠️ CẢNH BÁO TÂM MA! {b['category_name']} đã dùng {round(pct,1)}% hạn mức"
                })

        return {"month_year": month_year, "alerts": alerts, "total_budgets": len(budgets)}


@router.post("/api/ai/chat")
async def ai_chat(body: ChatBody, user: dict = Depends(get_current_user)):
    """Khí Linh Tiên Trí — trợ lý AI Gemini tư vấn tài chính (bản async không block event loop)"""
    t_start = time.time()
    month_year = datetime.date.today().strftime("%Y-%m")

    with get_db() as conn:
        t_db_0 = time.time()
        summary = conn.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN transaction_type='INCOME' THEN amount ELSE 0 END), 0) as income,
                COALESCE(SUM(CASE WHEN transaction_type='EXPENSE' THEN amount ELSE 0 END), 0) as expense
            FROM transactions WHERE user_id = ? AND strftime('%Y-%m', transaction_date) = ?
        """, (user["user_id"], month_year)).fetchone()

        total_balance = conn.execute(
            "SELECT COALESCE(SUM(balance), 0) as total FROM wallets WHERE user_id = ?",
            (user["user_id"],)
        ).fetchone()["total"]

        # Lấy 3 lượt hội thoại gần nhất (6 tin nhắn) để giữ ngữ cảnh câu hỏi tiếp theo
        history_rows = conn.execute("""
            SELECT prompt_question, ai_response FROM chat_sessions
            WHERE user_id = ? ORDER BY id DESC LIMIT 3
        """, (user["user_id"],)).fetchall()
        t_db_1 = time.time()

    recent_history = ""
    if history_rows:
        history_items = list(reversed(history_rows))
        lines = []
        for r in history_items:
            lines.append(f"Đạo hữu: {r['prompt_question']}")
            lines.append(f"Tiên Trí: {r['ai_response'][:150]}...")
        recent_history = "Hội thoại gần đây:\n" + "\n".join(lines) + "\n\n"

    context = f"""Bạn là "Khí Linh Tiên Trí" — trợ lý AI tài chính phong cách tu tiên.
Hãy trả lời câu hỏi bằng giọng văn tu tiên huyền huyễn nhưng ngắn gọn, súc tích và chính xác về tài chính.

Thông tin tài chính tháng {month_year} của đạo hữu:
- Tổng thu nhập (Khai Thác Linh Mạch): {summary['income']:,.0f} VNĐ
- Tổng chi tiêu (Tiêu Hao Linh Thạch): {summary['expense']:,.0f} VNĐ
- Tiết kiệm thuần: {summary['income'] - summary['expense']:,.0f} VNĐ
- Tổng số dư tất cả ví (Túi Càn Khôn): {total_balance:,.0f} VNĐ

{recent_history}Câu hỏi mới của đạo hữu: {body.message}"""

    try:
        t_ai_0 = time.time()
        ai_answer = await gemini.generate_text_async(context)
        t_ai_1 = time.time()

        # Lưu lịch sử chat
        with get_db() as conn:
            conn.execute(
                "INSERT INTO chat_sessions (user_id, prompt_question, ai_response) VALUES (?, ?, ?)",
                (user["user_id"], body.message, ai_answer)
            )

        t_end = time.time()
        print(f"[AI Chat Metric] DB: {t_db_1 - t_db_0:.3f}s | Gemini API: {t_ai_1 - t_ai_0:.3f}s | Total: {t_end - t_start:.3f}s")
        return {"response": ai_answer}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AI Chat] Lỗi: {e!r}", flush=True)
        raise HTTPException(status_code=500, detail="Tiên Trí gặp trở ngại. Vui lòng thử lại sau.")


@router.get("/api/ai/chat-history")
def get_chat_history(user: dict = Depends(get_current_user)):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY id DESC LIMIT 30",
            (user["user_id"],)
        ).fetchall()
        return [dict(r) for r in rows]

@router.get("/api/chat/suggested-questions")
def get_suggested_questions(user: dict = Depends(get_current_user)):
    with get_db() as conn:
        # Get 5 unique most recent questions
        rows = conn.execute(
            """
            SELECT prompt_question, MAX(id) AS last_id
            FROM chat_sessions
            WHERE user_id = ?
            GROUP BY prompt_question
            ORDER BY last_id DESC
            LIMIT 5
            """,
            (user["user_id"],)
        ).fetchall()
        return [r["prompt_question"] for r in rows]



# ──────────────────────────────────────────────
# AI SAVING TIPS
# ──────────────────────────────────────────────
@router.post("/api/ai/saving-tips")
def ai_saving_tips(user: dict = Depends(get_current_user)):
    """Khai Thị Tiết Kiệm — AI phân tích và gợi ý tiết kiệm"""
    month_year = datetime.date.today().strftime("%Y-%m")

    with get_db() as conn:
        # Tổng quan tháng
        summary = conn.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN transaction_type='INCOME' THEN amount ELSE 0 END), 0) as income,
                COALESCE(SUM(CASE WHEN transaction_type='EXPENSE' THEN amount ELSE 0 END), 0) as expense
            FROM transactions WHERE user_id = ? AND strftime('%Y-%m', transaction_date) = ?
        """, (user["user_id"], month_year)).fetchone()

        # Chi tiêu theo danh mục
        by_cat = conn.execute("""
            SELECT c.category_name, SUM(t.amount) as total, COUNT(*) as count
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? AND t.transaction_type = 'EXPENSE'
            AND strftime('%Y-%m', t.transaction_date) = ?
            GROUP BY t.category_id ORDER BY total DESC
        """, (user["user_id"], month_year)).fetchall()

        # Top 5 giao dịch lớn nhất
        top_txns = conn.execute("""
            SELECT t.amount, t.note, t.transaction_date, c.category_name
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? AND t.transaction_type = 'EXPENSE'
            AND strftime('%Y-%m', t.transaction_date) = ?
            ORDER BY t.amount DESC LIMIT 5
        """, (user["user_id"], month_year)).fetchall()

    cat_breakdown = "\n".join([f"  - {c['category_name']}: {c['total']:,.0f} VNĐ ({c['count']} giao dịch)" for c in by_cat])
    top_breakdown = "\n".join([f"  - {t['category_name']}: {t['amount']:,.0f} VNĐ — {t['note'] or 'Không ghi chú'} ({t['transaction_date']})" for t in top_txns])

    prompt = f"""Bạn là "Khí Linh Tiên Trí" — trợ lý tài chính AI phong cách tu tiên.
Hãy phân tích chi tiêu tháng {month_year} của đạo hữu và đưa ra 5 lời khuyên tiết kiệm cụ thể.

📊 Tổng quan:
- Thu nhập: {summary['income']:,.0f} VNĐ
- Chi tiêu: {summary['expense']:,.0f} VNĐ
- Tiết kiệm: {summary['income'] - summary['expense']:,.0f} VNĐ
- Tỷ lệ tiết kiệm: {((summary['income'] - summary['expense']) / summary['income'] * 100) if summary['income'] > 0 else 0:.1f}%

📋 Chi tiêu theo danh mục:
{cat_breakdown or '  Chưa có dữ liệu'}

💸 Top 5 giao dịch lớn nhất:
{top_breakdown or '  Chưa có dữ liệu'}

Hãy trả lời bằng giọng văn tu tiên (Xianxia) nhưng vẫn thực tế và hữu ích.
Format: Đánh số 1-5, mỗi lời khuyên ngắn gọn 2-3 câu."""

    try:
        response_text = gemini.generate_text(prompt)
        return {
            "month_year": month_year,
            "income": summary["income"],
            "expense": summary["expense"],
            "savings_rate": round(((summary['income'] - summary['expense']) / summary['income'] * 100) if summary['income'] > 0 else 0, 1),
            "tips": response_text,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AI Saving Tips] Lỗi: {e!r}", flush=True)
        raise HTTPException(status_code=500, detail="Tiên Trí gặp trở ngại. Vui lòng thử lại sau.")
