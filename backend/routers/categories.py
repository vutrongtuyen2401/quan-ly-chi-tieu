"""Danh mục thu / chi."""

from fastapi import APIRouter, Depends, HTTPException

from backend.db import get_db
from backend.schemas import CategoryBody, CategoryUpdateBody
from backend.security import get_current_user
from backend.services import get_owned_category

router = APIRouter()


# ──────────────────────────────────────────────
# CATEGORIES ROUTES
# ──────────────────────────────────────────────
@router.get("/api/categories")
def get_categories(user: dict = Depends(get_current_user)):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM categories WHERE user_id = ? ORDER BY id", (user["user_id"],)).fetchall()
        return [dict(r) for r in rows]


@router.post("/api/categories")
def create_category(body: CategoryBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO categories (user_id, category_name, category_type, icon) VALUES (?, ?, ?, ?)",
            (user["user_id"], body.category_name, body.category_type, body.icon)
        )
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"id": new_id, "message": "Danh mục mới đã khai mở!"}


# Change 3: Sửa danh mục
@router.put("/api/categories/{cat_id}")
def update_category(cat_id: int, body: CategoryUpdateBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cat = get_owned_category(conn, cat_id, user["user_id"])
        new_name = body.category_name if body.category_name is not None else cat["category_name"]
        new_icon = body.icon if body.icon is not None else cat["icon"]
        conn.execute("UPDATE categories SET category_name = ?, icon = ? WHERE id = ? AND user_id = ?",
                     (new_name, new_icon, cat_id, user["user_id"]))
        return {"message": "Danh mục đã được cập nhật!", "category_name": new_name, "icon": new_icon}


@router.delete("/api/categories/{cat_id}")
def delete_category(cat_id: int, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cat = get_owned_category(conn, cat_id, user["user_id"])
        txn_count = conn.execute("SELECT COUNT(*) FROM transactions WHERE category_id = ? AND user_id = ?",
                                 (cat_id, user["user_id"])).fetchone()[0]
        rec_count = conn.execute("SELECT COUNT(*) FROM recurring_transactions WHERE category_id = ? AND user_id = ?",
                                 (cat_id, user["user_id"])).fetchone()[0]
        if txn_count or rec_count:
            parts = []
            if txn_count:
                parts.append(f"{txn_count} giao dịch")
            if rec_count:
                parts.append(f"{rec_count} giao dịch định kỳ")
            raise HTTPException(
                status_code=400,
                detail=f"Không thể xóa danh mục '{cat['category_name']}' vì đang được dùng bởi {' và '.join(parts)}. "
                       f"Hãy đổi danh mục của chúng hoặc xóa chúng trước."
            )
        # Hạn mức của danh mục không còn ý nghĩa khi danh mục bị xóa
        conn.execute("DELETE FROM budgets WHERE category_id = ? AND user_id = ?", (cat_id, user["user_id"]))
        conn.execute("DELETE FROM categories WHERE id = ? AND user_id = ?", (cat_id, user["user_id"]))
        return {"message": "Danh mục đã bị hủy!"}
