"""
Vietnamese Financial Parser
Phân tích ngữ nghĩa tiếng Việt chuyên sâu cho các giá trị tài chính:
- Số tiền: 50k, 50 nghìn, 50 ngàn, 1tr5, 1.5 triệu, 2 tỷ...
- Ngày tháng: hôm nay, hôm qua, ngày mai, YYYY-MM-DD, DD/MM/YYYY...
- Ý định xác nhận / hủy bỏ (confirmation / cancellation)
"""

import re
import datetime
from typing import Optional, Tuple, Dict, Any


class VietnameseFinancialParser:
    """Bộ phân tích ngôn ngữ tự nhiên tài chính tiếng Việt"""

    CONFIRM_KEYWORDS = {
        "xác nhận", "xac nhan", "đồng ý", "dong y", "ok", "oke", "được", "duoc",
        "tiến hành", "tien hanh", "lưu", "luu", "chuẩn", "chuan", "chính xác", "chinh xac",
        "yes", "y", "làm đi", "lam di", "lưu đi", "luu di", "thêm đi", "them di"
    }

    CANCEL_KEYWORDS = {
        "hủy", "huy", "thôi", "thoi", "không", "khong", "dừng", "dung",
        "bỏ qua", "bo qua", "đừng", "dung", "hủy bỏ", "huy bo", "cancel", "no", "n"
    }

    @classmethod
    def is_cancellation(cls, text: str) -> bool:
        """Kiểm tra người dùng có đang phát biểu ý định HỦY BỎ hay không"""
        clean = text.lower().strip()
        clean = re.sub(r"[.!?,]+$", "", clean).strip()
        if clean in cls.CANCEL_KEYWORDS:
            return True
        for kw in cls.CANCEL_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", clean):
                return True
        return False

    @classmethod
    def is_confirmation(cls, text: str) -> bool:
        """Kiểm tra người dùng có đang phát biểu ý định XÁC NHẬN hay không"""
        clean = text.lower().strip()
        clean = re.sub(r"[.!?,]+$", "", clean).strip()
        # Nếu có từ khóa hủy bỏ hoặc phủ định, chắc chắn không phải xác nhận
        if cls.is_cancellation(clean):
            return False
        if clean in cls.CONFIRM_KEYWORDS:
            return True
        for kw in cls.CONFIRM_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", clean):
                return True
        return False

    @classmethod
    def parse_amount(cls, text: str) -> Optional[float]:
        """Trích xuất số tiền từ văn bản tiếng Việt
        Hỗ trợ:
        - 50k, 50 k -> 50,000
        - 50 nghìn, 50 ngàn -> 50,000
        - 1tr, 1 tr, 1 triệu, 1 trieu -> 1,000,000
        - 1tr5, 1 tr 5 -> 1,500,000
        - 1.5 triệu, 1,5 triệu -> 1,500,000
        - 2 tỷ, 2 ty -> 2,000,000,000
        - 150.000, 150,000, 150000 -> 150,000
        """
        raw = text.lower().strip()

        # 1. Pattern: 1tr5, 2tr8, 1 triệu 5, 2 triệu 8
        m_combo = re.search(r"(\d+)\s*(?:tr|triệu|trieu)\s*(\d+)(?!\d)", raw)
        if m_combo:
            base = int(m_combo.group(1)) * 1_000_000
            dec = m_combo.group(2)
            if len(dec) == 1:
                val = base + int(dec) * 100_000
            else:
                val = base + int(dec) * (10 ** (6 - len(dec)))
            return float(val)

        # 2. Pattern: Số thập phân hoặc nguyên + tỷ
        m_ty = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:tỷ|ty)\b", raw)
        if m_ty:
            num = float(m_ty.group(1).replace(",", "."))
            return num * 1_000_000_000

        # 3. Pattern: Số thập phân hoặc nguyên + triệu / tr
        m_tr = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:triệu|trieu|tr)\b", raw)
        if m_tr:
            num = float(m_tr.group(1).replace(",", "."))
            return num * 1_000_000

        # 4. Pattern: Số + k, nghìn, ngàn, củ (tiếng lóng triệu: 1 củ = 1 triệu)
        m_cu = re.search(r"(\d+(?:[.,]\d+)?)\s*củ\b", raw)
        if m_cu:
            num = float(m_cu.group(1).replace(",", "."))
            return num * 1_000_000

        m_k = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:k|nghìn|nghin|ngàn|ngan)\b", raw)
        if m_k:
            num = float(m_k.group(1).replace(",", "."))
            return num * 1_000

        # 5. Pattern: Định dạng số tiêu chuẩn có chấm/phẩy phân cách (ví dụ: 150.000 hoặc 150,000)
        m_std = re.search(r"(?<!\d)(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?)(?!\d)", raw)
        if m_std:
            s = m_std.group(1)
            # Kiểm tra xem là phân cách hàng nghìn bằng dấu chấm hay phẩy
            if "." in s and "," not in s:
                clean_s = s.replace(".", "")
            elif "," in s and "." not in s:
                clean_s = s.replace(",", "")
            else:
                clean_s = s.replace(".", "").replace(",", ".")
            try:
                return float(clean_s)
            except ValueError:
                pass

        # 6. Pattern: Số nguyên đơn thuần (ít nhất 3 chữ số nếu đứng độc lập hoặc có từ chỉ tiền)
        m_plain = re.search(r"(?:hết|tiền|chi|thu|số tiền|giá)?\s*(\d{4,})(?!\d)", raw)
        if m_plain:
            return float(m_plain.group(1))

        return None

    @classmethod
    def parse_date(cls, text: str) -> str:
        """Trích xuất ngày từ văn bản, mặc định là ngày hôm nay YYYY-MM-DD"""
        raw = text.lower()
        today = datetime.date.today()

        if "hôm qua" in raw or "hom qua" in raw:
            return (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        if "hôm kia" in raw or "hom kia" in raw:
            return (today - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        if "ngày mai" in raw or "ngay mai" in raw:
            return (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        # DD/MM/YYYY
        m_dmy = re.search(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})\b", raw)
        if m_dmy:
            d, m, y = int(m_dmy.group(1)), int(m_dmy.group(2)), int(m_dmy.group(3))
            try:
                return datetime.date(y, m, d).strftime("%Y-%m-%d")
            except ValueError:
                pass

        # YYYY-MM-DD
        m_ymd = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", raw)
        if m_ymd:
            try:
                datetime.date.fromisoformat(m_ymd.group(0))
                return m_ymd.group(0)
            except ValueError:
                pass

        return today.strftime("%Y-%m-%d")

    @classmethod
    def extract_transfer_wallets(cls, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Trích xuất tên ví nguồn và ví đích từ câu chuyển tiền.
        Ví dụ: 'Chuyển 500 nghìn từ ví A sang ví B' -> ('ví A', 'ví B')
        """
        raw = text.strip()
        # Pattern 1: từ [ví] X sang/đến/qua [ví] Y
        m = re.search(r"(?:từ|tu)\s+([^,\n]+?)\s+(?:sang|đến|qua|den|vao|vào)\s+([^,.\n;]+)", raw, re.IGNORECASE)
        if m:
            w_from = m.group(1).strip()
            w_to = m.group(2).strip()
            return w_from, w_to
        return None, None

    @classmethod
    def extract_goal_name(cls, text: str) -> Optional[str]:
        """Trích xuất tên mục tiêu tiết kiệm.
        Ví dụ: 'Đưa 1 triệu vào mục tiêu mua laptop' -> 'mua laptop'
        """
        m = re.search(r"(?:mục tiêu|tiết kiệm cho|quỹ|muc tieu)\s+(?:là\s+|để\s+)?([^,.\n;]+)", text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        return None

    @classmethod
    def guess_category(cls, text: str) -> Optional[str]:
        """Dự đoán danh mục thu/chi từ ngữ cảnh câu nói"""
        raw = text.lower()
        if any(k in raw for k in ["ăn", "uống", "cơm", "phở", "bún", "bánh mì", "trà sữa", "cafe", "cà phê", "nhậu", "tiệc", "sáng", "trưa", "tối"]):
            return "Ăn Uống"
        if any(k in raw for k in ["xăng", "đổ xăng", "xe", "grab", "be", "taxi", "gửi xe", "vé xe", "sửa xe"]):
            return "Đi Lại"
        if any(k in raw for k in ["điện", "nước", "internet", "wifi", "tiền nhà", "phòng trọ", "hóa đơn", "chung cư"]):
            return "Hóa Đơn"
        if any(k in raw for k in ["mua", "quần áo", "giày", "dép", "shopee", "lazada", "tiki", "sách"]):
            return "Mua Sắm"
        if any(k in raw for k in ["thuốc", "bệnh viện", "khám", "bác sĩ", "y tế"]):
            return "Y Tế"
        if any(k in raw for k in ["lương", "thưởng", "bonus", "hoa hồng"]):
            return "Tiền Lương"
        return None
