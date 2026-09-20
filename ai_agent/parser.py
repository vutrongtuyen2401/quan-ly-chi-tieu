"""
Vietnamese Financial Parser
Phân tích ngữ nghĩa tiếng Việt chuyên sâu cho các giá trị tài chính:
- Số tiền: 50k, 50 nghìn, 50 ngàn, 1tr5, 1.5 triệu, 2 tỷ...
- Ngày tháng: hôm nay, hôm qua, ngày mai, YYYY-MM-DD, DD/MM/YYYY...
- Ý định xác nhận / hủy bỏ (confirmation / cancellation)
"""

import re
import datetime
from enum import Enum
from typing import Optional, Tuple, Dict, Any, List
from .knowledge.builder import remove_accents


class MessageIntent(str, Enum):
    """Phân loại 4 tầng ý định người dùng đối với Khí Linh AI Agent"""
    CONFIRMATION = "CONFIRMATION"
    CANCELLATION = "CANCELLATION"
    MODIFICATION = "MODIFICATION"
    GENERAL_CONVERSATION = "GENERAL_CONVERSATION"
    FINANCIAL_ADVICE = "FINANCIAL_ADVICE"
    FINANCIAL_READ = "FINANCIAL_READ"
    FINANCIAL_WRITE = "FINANCIAL_WRITE"



class VietnameseFinancialParser:
    """Bộ phân tích ngôn ngữ tự nhiên tài chính tiếng Việt"""

    CONFIRM_KEYWORDS = {
        # Xác nhận / xác thực
        "xác nhận", "xac nhan", "xác thực", "xac thuc", "confirm", "confirmed",
        # Đồng ý / tán thành
        "đồng ý", "dong y", "tán thành", "tan thanh", "nhất trí", "nhat tri", "chấp nhận", "chap nhan",
        # Được
        "được", "duoc", "được rồi", "duoc roi", "được đấy", "duoc day", "được chứ", "duoc chu",
        "được nhé", "duoc nhe", "được nha", "duoc nha", "được đó", "duoc do", "được nè", "duoc ne",
        # Làm / tiến hành / triển khai
        "làm đi", "lam di", "làm luôn", "lam luon", "làm luôn đi", "lam luon di", "làm giúp", "lam giup",
        "cứ làm", "cu lam", "cứ làm đi", "cu lam di", "cứ thế làm", "cu the lam", "cứ thế", "cu the",
        "tiến hành", "tien hanh", "tiến hành đi", "tien hanh di", "thực hiện", "thuc hien", "thực hiện đi", "thuc hien di",
        "triển", "trien", "triển đi", "trien di", "triển luôn", "trien luon", "triển khai", "trien khai", "triển khai đi", "trien khai di",
        # Lưu / ghi nhận
        "lưu", "luu", "lưu lại", "luu lai", "lưu đi", "luu di", "lưu nhé", "luu nhe", "lưu nha", "luu nha", "lưu giúp", "luu giup", "lưu giùm", "luu gium",
        "ghi nhận", "ghi nhan", "ghi nhận đi", "ghi nhan di", "ghi lại", "ghi lai", "ghi đi", "ghi di",
        "ghi vào", "ghi vao", "lưu vào", "luu vao",
        # Thêm / tạo
        "thêm", "them", "thêm đi", "them di", "thêm vào", "them vao", "thêm giúp", "them giup", "tạo đi", "tao di",
        # OK / Yes
        "ok", "oke", "oki", "okey", "okay", "okie", "ok nha", "ok nhé", "ok luôn", "ok rồi",
        "uk", "uh", "ừ", "ừm", "ờ", "uhm", "um", "yes", "yep", "yeah", "y", "sure",
        # Chuẩn / chính xác / đúng
        "chuẩn", "chuan", "chuẩn rồi", "chuan roi", "chuẩn đấy", "chuan day",
        "chính xác", "chinh xac", "đúng rồi", "dung roi", "đúng thế", "dung the", "đúng vậy", "dung vay", "chính nó", "chinh no",
        # Duyệt / hợp lý
        "duyệt", "duyet", "duyệt đi", "duyet di", "duyệt luôn", "duyet luon", "duyệt nhé", "duyet nhe",
        "hợp lý", "hop ly", "hợp lý đấy", "hop ly day"
    }

    CANCEL_KEYWORDS = {
        # Hủy
        "hủy", "huy", "hủy bỏ", "huy bo", "hủy đi", "huy di", "hủy thao tác", "huy thao tac",
        "hủy lệnh", "huy lenh", "hủy giao dịch", "huy giao dich", "cancel", "canceled", "cancelled",
        # Thôi
        "thôi", "thoi", "thôi khỏi", "thoi khoi", "thôi đừng", "thoi dung", "thôi bỏ", "thoi bo",
        "thôi bỏ đi", "thoi bo di", "thôi không", "thoi khong", "thôi không làm", "thoi khong lam",
        "thôi không cần", "thoi khong can", "thôi không lưu", "thoi khong luu",
        # Không
        "không", "khong", "không cần", "khong can", "không làm", "khong lam", "không làm nữa", "khong lam nua",
        "không lưu", "khong luu", "không thêm", "khong them", "không tạo", "khong tao", "không ghi", "khong ghi",
        "không đồng ý", "khong dong y", "không xác nhận", "khong xac nhan", "không phải", "khong phai",
        # Đừng / dừng
        "đừng", "dung", "đừng làm", "dung lam", "đừng lưu", "dung luu", "đừng ghi", "dung ghi",
        "dừng", "dung", "dừng lại", "dung lai", "dừng thao tác", "dung thao tac",
        # Bỏ / khỏi
        "bỏ qua", "bo qua", "bỏ đi", "bo di", "bỏ", "bo", "khỏi", "khoi", "khỏi cần", "khoi can", "khỏi làm", "khoi lam", "khỏi lưu", "khoi luu",
        # Tiếng Anh
        "stop", "abort", "no", "nope", "nevermind", "n"
    }

    @classmethod
    def is_cancellation(cls, text: str) -> bool:
        """Kiểm tra người dùng có đang phát biểu ý định HỦY BỎ hay không"""
        clean = text.lower().strip()
        clean = re.sub(r"[.!?,:;]+$", "", clean).strip()
        clean_punct = re.sub(r"[,;!?]+", " ", clean)

        # 1. Các cụm từ hủy dứt khoát — luôn là cancellation
        explicit_cancels = [
            "thôi không làm", "thoi khong lam", "không làm nữa", "khong lam nua",
            "thôi không", "thoi khong", "thôi khỏi", "thoi khoi", "thôi bỏ", "thoi bo",
            "thôi đừng", "thoi dung", "không cần", "khong can", "không làm", "khong lam",
            "hủy", "huy", "hủy bỏ", "huy bo", "hủy đi", "huy di", "hủy thao tác",
            "đừng làm", "dung lam", "đừng lưu", "dung luu", "dừng lại", "dung lai",
            "không đồng ý", "khong dong y", "không xác nhận", "khong xac nhan",
            "khỏi cần", "khoi can", "khỏi làm", "khoi lam", "bỏ qua", "bo qua",
            "cancel", "abort", "stop", "nevermind"
        ]
        for ec in explicit_cancels:
            if re.search(rf"\b{re.escape(ec)}\b", clean_punct):
                return True

        # 1.1. Nếu câu chứa thực thể tài chính rõ ràng kết hợp với từ ngữ cảnh (khoản vừa ghi, giao dịch vừa rồi, ví đó...)
        # thì đây là hành động trên thực thể (ví dụ xóa/bỏ giao dịch), KHÔNG PHẢI hủy xác nhận confirmation!
        if any(e in clean for e in ["khoản", "khoan", "giao dịch", "giao dich", "ví", "vi", "mục tiêu", "muc tieu", "ngân sách", "ngan sach", "sổ nợ", "so no"]):
            if any(ctx in clean for ctx in ["vừa", "vua", "đó", "do", "này", "nay", "hôm nay", "hom nay", "gần nhất", "gan nhat", "ghi", "tạo"]):
                return False

        # 2. Nếu có số tiền mới (như '80k thôi', 'đổi thành 70 nghìn') -> không phải cancellation mà là modification
        amt = cls.parse_amount(clean)
        if amt and amt > 0:
            return False

        # 3. Các từ khóa hủy đơn lẻ
        if clean in cls.CANCEL_KEYWORDS:
            return True
        words = clean.split()
        if len(words) <= 3:
            for kw in cls.CANCEL_KEYWORDS:
                if re.search(rf"\b{re.escape(kw)}\b", clean_punct):
                    return True

        return False

    @classmethod
    def is_modification(cls, text: str) -> bool:
        """Kiểm tra xem người dùng có đang muốn sửa đổi tham số thao tác đang chờ hay không"""
        clean = text.lower().strip()
        clean = re.sub(r"[.!?,:;]+$", "", clean).strip()

        # Nếu là lệnh hủy dứt khoát -> không phải modification
        if cls.is_cancellation(clean):
            return False

        # 0. Lệnh đảo ngược chiều (swap) chuyển tiền hoặc từ chối sửa thông tin: "ngược lại", "đảo lại", "nhầm, từ X sang Y"
        if any(kw in clean for kw in ["ngược lại", "nguoc lai", "đảo lại", "dao lai"]):
            return True
        if ("từ " in clean or "tu " in clean) and (" sang " in clean or " qua " in clean):
            return True

        # 0.1. Lệnh đính chính / từ chối thông tin cũ: "không phải", "nhầm", "lộn", "chứ không phải"
        if any(kw in clean for kw in ["không phải", "khong phai", "nhầm", "nham", "lộn", "lon"]):
            return True

        # 1. Có số tiền mới và từ khóa sửa đổi
        amt = cls.parse_amount(clean)
        mod_keywords = [
            "sửa", "sua", "đổi", "doi", "thành", "thanh", "chỉnh", "chinh",
            "thay", "thay đổi", "thay doi", "tính lại", "tinh lai", "lấy", "lay",
            "chỉ", "chi", "không phải", "khong phai", "nhầm", "nham", "tăng", "tang", "giảm", "giam",
            "thôi", "thoi", "không", "khong", "k", "lộn", "lon", "chứ", "chu", "là", "la"
        ]
        if amt and amt > 0:
            if any(kw in clean for kw in mod_keywords) or clean.endswith("thôi") or clean.endswith("thoi"):
                return True
            # Nếu chuỗi bắt đầu bằng 'đổi' hoặc 'sửa'
            if clean.startswith("đổi") or clean.startswith("doi") or clean.startswith("sửa") or clean.startswith("sua"):
                return True
            # Nếu câu ngắn chủ yếu là số tiền mới (ví dụ '80k', '70000', '70 nghìn')
            words = clean.split()
            if len(words) <= 3 and not any(w in clean for w in ["ăn", "uống", "mua", "chi", "lương", "thu", "vay", "nợ", "xăng", "hôm nay", "hôm qua"]):
                return True
            return False

        # 2. Sửa danh mục, ví hoặc thời gian
        if any(kw in clean for kw in [
            "đổi sang ví", "doi sang vi", "sửa ví", "sua vi", "dùng ví", "dung vi",
            "đổi danh mục", "doi danh muc", "sửa danh mục", "sua danh muc", "đổi sang", "doi sang",
            "đổi ví", "doi vi", "ví khác", "vi khac", "đổi tháng", "doi thang", "sửa tháng", "sua thang",
            "đổi kỳ", "doi ky", "tháng trước", "thang truoc", "tuần trước", "tuan truoc"
        ]):
            return True

        return False

    @classmethod
    def is_confirmation(cls, text: str) -> bool:
        """Kiểm tra người dùng có đang phát biểu ý định XÁC NHẬN hay không"""
        clean = text.lower().strip()
        clean = re.sub(r"[.!?,:;]+$", "", clean).strip()
        clean_punct = re.sub(r"[,;!?]+", " ", clean)

        # 1. Nếu có từ khóa hủy bỏ hoặc phủ định -> không phải xác nhận
        if cls.is_cancellation(clean):
            return False

        # 2. Nếu là câu sửa đổi tham số (ví dụ: 'đổi thành 70 nghìn') -> không phải xác nhận
        if cls.is_modification(clean):
            return False

        # 3. Nếu câu chứa số tiền VÀ có từ khóa tạo giao dịch mới (như 'nhận được', 'ăn hết', 'chi tiêu', 'chuyển') -> không phải xác nhận
        amt = cls.parse_amount(clean)
        if amt and amt > 0:
            if any(kw in clean for kw in ["nhận", "nhan", "lương", "luong", "thưởng", "thuong", "chi", "tiêu", "tieu", "hết", "het", "chuyển", "chuyen", "ăn", "an", "mua"]):
                return False

        # 4. Khớp chính xác cụm từ xác nhận trong từ điển
        if clean in cls.CONFIRM_KEYWORDS:
            return True

        # 5. Khớp từ khóa xác nhận mạnh dứt khoát
        strong_confirms = [
            "xác nhận", "xac nhan", "xác thực", "xac thuc", "confirm",
            "đồng ý", "dong y", "tán thành", "tan thanh", "nhất trí", "nhat tri",
            "làm đi", "lam di", "làm luôn", "lam luon", "cứ làm", "cu lam",
            "tiến hành đi", "tien hanh di", "thực hiện đi", "thuc hien di",
            "triển đi", "trien di", "triển luôn", "trien luon", "triển khai đi",
            "lưu đi", "luu di", "lưu lại", "luu lai", "ghi nhận đi", "ghi nhan di",
            "đúng rồi", "dung roi", "chính xác", "chinh xac", "chuẩn rồi", "chuan roi",
            "chuẩn đấy", "chuan day", "duyệt đi", "duyet di", "duyệt luôn", "duyet luon"
        ]
        for sc in strong_confirms:
            if re.search(rf"\b{re.escape(sc)}\b", clean_punct):
                return True

        # 6. Các từ đơn đa nghĩa (được, ok, ừ, lưu, thêm) chỉ khớp nếu câu ngắn (<= 4 từ) và không chứa từ phủ định
        words = clean.split()
        if len(words) <= 4:
            ambiguous_confirms = [
                "ok", "oke", "oki", "okey", "okay", "okie", "uk", "uh", "ừ", "ừm", "ờ", "yes", "yep", "yeah", "sure",
                "được", "duoc", "lưu", "luu", "thêm", "them", "duyệt", "duyet", "chuẩn", "chuan"
            ]
            for ac in ambiguous_confirms:
                if re.search(rf"\b{re.escape(ac)}\b", clean_punct):
                    if not any(stop in clean for stop in ["không", "khong", "chưa", "chua", "đừng", "dung", "tìm", "tim"]):
                        return True

        return False

    @classmethod
    def is_financial_advice_or_hypothetical(cls, text: str) -> bool:
        """Kiểm tra câu nói có phải là câu hỏi tư vấn, xin lời khuyên, gợi ý hoặc kịch bản giả định hay không.
        Ví dụ:
        - 'Gợi ý chi tiêu tháng sau cho tôi'
        - 'Tháng sau tôi nên chi tiêu thế nào?'
        - 'Nếu tôi muốn tiết kiệm thêm 2 triệu thì nên làm gì?'
        - 'Có nên mua xe lúc này không?'
        - 'Làm sao để tiết kiệm 5 triệu mỗi tháng?'
        """
        clean = text.lower().strip()
        clean = re.sub(r"[.!?,:;]+$", "", clean).strip()

        # 0. Tra cứu trạng thái hạn mức / ngân sách / sổ nợ / số dư / mục tiêu (READ) không phải là advice
        status_read_keywords = [
            "hạn mức chi tiêu thế nào", "hạn mức thế nào", "ngân sách thế nào", "ngân sách ra sao",
            "tiến độ mục tiêu", "tiến độ tiết kiệm", "mục tiêu của ta thế nào", "mục tiêu của tôi thế nào",
            "mục tiêu tiết kiệm của ta thế nào", "mục tiêu tiết kiệm của tôi thế nào", "mục tiêu tiết kiệm thế nào",
            "sổ nợ thế nào", "số dư thế nào"
        ]
        if any(kw in clean for kw in status_read_keywords) and not any(adv in clean for adv in ["gợi ý", "tư vấn", "lời khuyên", "chiến lược", "kế hoạch"]):
            return False

        # 1. Các cụm từ xin gợi ý, tư vấn, lời khuyên, kế hoạch
        advice_phrases = [
            "gợi ý", "goi y", "tư vấn", "tu van", "lời khuyên", "loi khuyen",
            "khuyên tôi", "khuyên ta", "khuyên em", "khuyên mình", "cho lời khuyên", "cho xin lời khuyên",
            "chiến lược", "chien luoc", "kế hoạch chi tiêu", "kế hoạch tài chính", "ke hoach chi tieu",
            "phương án", "phuong an", "bí quyết", "bi quyet", "kinh nghiệm", "kinh nghiem",
            "lên kế hoạch", "len ke hoach", "định hướng", "dinh huong"
        ]
        for p in advice_phrases:
            if re.search(rf"\b{re.escape(p)}\b", clean):
                return True

        # 2. Câu hỏi điều kiện / giả định (Nếu... thì... / Giả sử... / Liệu...)
        if (clean.startswith("nếu ") or clean.startswith("neu ") or " nếu " in clean or " neu " in clean or 
            clean.startswith("giả sử") or clean.startswith("gia su") or " giả sử " in clean or " gia su " in clean or
            clean.startswith("liệu ") or clean.startswith("lieu ") or " liệu " in clean or " lieu " in clean or
            clean.startswith("ví dụ") or clean.startswith("vi du")):
            # Trừ trường hợp người dùng ra lệnh ghi chép dứt khoát
            explicit_writes = ["ghi lại", "ghi lai", "lưu lại", "luu lai", "thêm vào", "them vao", "tạo giao dịch", "tao giao dich", "đặt ngân sách", "dat ngan sach"]
            if not any(ew in clean for ew in explicit_writes):
                return True

        # 3. Mẫu câu hỏi phương hướng: nên làm gì, nên chi tiêu thế nào, làm sao để...
        direction_patterns = [
            "nên làm gì", "nen lam gi", "nên làm sao", "nen lam sao",
            "nên chi tiêu thế nào", "nên tiêu thế nào", "nên chi thế nào",
            "nên chi tiêu ra sao", "nên tiêu ra sao", "nên chi ra sao",
            "nên chi tiêu sao", "nên tiêu sao", "nên chi sao",
            "có nên", "co nen", "làm sao để", "lam sao de",
            "làm thế nào để", "lam the nao de", "cách nào để", "cach nao de",
            "thế nào thì tốt", "thế nào thì hợp lý", "ra sao thì tốt", "ra sao thì hợp lý"
        ]
        for dp in direction_patterns:
            if re.search(rf"\b{re.escape(dp)}\b", clean):
                return True

        # 4. Câu hỏi đánh giá / tham vấn ý kiến kết thúc bằng các mẫu nghi vấn
        eval_questions = [
            "có ổn không", "co on khong", "ổn không", "on khong",
            "có hợp lý không", "co hop ly khong", "hợp lý không", "hop ly khong",
            "có nên không", "co nen khong", "được không", "duoc khong",
            "thì sao", "thi sao", "thế nào nhỉ", "ra sao nhỉ", "được chăng", "duoc chang"
        ]
        if any(clean.endswith(eq) or f"{eq}?" in text.lower() for eq in eval_questions):
            return True

        # 5. Câu hỏi kết thúc bằng nghi vấn về phương hướng hoặc lời khuyên
        question_ends = [
            "thế nào", "the nao", "ra sao", "làm gì", "lam gi", "làm sao", "lam sao", "sao cho hợp lý"
        ]
        if any(clean.endswith(qe) for qe in question_ends) and any(w in clean for w in ["nên", "phân bổ", "đầu tư", "tiết kiệm"]) and not any(r in clean for r in ["hạn mức", "tiến độ", "mục tiêu", "muc tieu"]):
            return True

        return False

    @classmethod
    def is_general_conversation(cls, text: str) -> bool:
        """Kiểm tra câu nói có phải là đối thoại tự nhiên thông thường (chào hỏi, triết lý, phi tài chính)."""
        clean = text.lower().strip()
        clean = re.sub(r"[.!?,:;]+$", "", clean).strip()

        # Nếu là câu truy vấn tiếp nối follow-up -> KHÔNG phải đối thoại phiếm
        if cls.is_followup_query(clean):
            return False

        # Từ khóa tài chính cá nhân cốt lõi - nếu có thì KHÔNG phải general conversation
        fin_terms = [
            "chi tiêu", "chi tieu", "thu nhập", "thu nhap", "số dư", "so du", "ví", "vi",
            "danh mục", "danh muc", "mục", "khoản", "khoan",
            "ngân sách", "ngan sach", "hạn mức", "han muc", "mục tiêu tiết kiệm", "tiết kiệm", "tiet kiem",
            "tích lũy", "tich luy", "sổ nợ", "so no", "nợ", "no", "vay mượn", "cho vay", "đi vay", "lương", "luong",
            "thưởng", "thuong", "giao dịch", "giao dich", "tiền", "tien", "linh thạch", "linh thach",
            "ăn sáng", "an sang", "ăn trưa", "an trua", "ăn tối", "an toi", "đổ xăng", "do xang",
            "hóa đơn", "hoa don", "chuyển tiền", "chuyen tien", "báo cáo", "bao cao",
            "mua", "bán", "đóng tiền", "trả tiền", "định kỳ", "dinh ky",
            "ngân khố", "ngan kho", "khố phòng", "kho phong", "tán tài", "tan tai", "nạp tài", "nap tai",
            "tụ linh trận", "tu linh tran", "trái chủ", "trai chu", "lỡ tiêu", "lo tieu", "quá tay", "qua tay",
            "bất thường", "bat thuong", "tiêu bao nhiêu", "chi bao nhiêu", "còn bao nhiêu"
        ]
        if any(re.search(rf"\b{re.escape(ft)}\b", clean) for ft in fin_terms):
            return False

        # Nếu có từ chỉ hành động hệ thống (thêm, tạo, xóa, sửa, đổi, đặt, chuyển, xem, kiểm tra...) -> không phải general conversation
        action_verbs = ["thêm", "them", "tạo", "tao", "xóa", "xoa", "sửa", "sua", "hủy", "huy", "đổi", "doi", "đặt", "dat", "cài", "cai", "chuyển", "chuyen", "xem", "kiểm tra", "kiem tra", "tra cứu", "tra cuu", "tìm", "tim"]
        if any(re.search(rf"\b{re.escape(av)}\b", clean) for av in action_verbs):
            return False

        # Nếu có số tiền được parse -> không phải general conversation
        amt = cls.parse_amount(clean)
        if amt and amt > 0:
            return False

        # Các chủ đề đối thoại phiếm / tu tiên / chào hỏi
        general_patterns = [
            "xin chào", "xin chao", "chào bạn", "chao ban", "chào khí linh", "chao khi linh",
            "chào tiên trí", "chao tien tri", "hello", "hi", "hey", "chào", "chao",
            "bạn là ai", "ban la ai", "ngươi là ai", "nguoi la ai", "bạn tên gì", "nguoi ten gi",
            "khí linh là gì", "khi linh la gi", "tiên trí là gì",
            "tu tiên", "tu tien", "đạo pháp", "dao phap", "tu vi", "cảnh giới", "canh gioi",
            "pháp bảo", "phap bao", "tông môn", "tong mon", "linh khí", "linh khi",
            "kể chuyện", "ke chuyen", "kể chuyện cười", "ke chuyen cuoi", "hài hước",
            "thời tiết", "thoi tiet", "hôm nay trời đẹp", "trời đẹp nhỉ",
            "bạn khỏe không", "ngươi khỏe không", "khỏe không", "có khỏe không",
            "tạm biệt", "tam biet", "bye", "goodbye", "hẹn gặp lại",
            "chúc mừng", "chuc mung", "cảm ơn", "cam on", "thanks", "thank you"
        ]
        for gp in general_patterns:
            if re.search(rf"\b{re.escape(gp)}\b", clean):
                return True

        # Nếu câu rất ngắn không chứa thuật ngữ tài chính (ví dụ 'alô', 'ngươi đó hả', 'ở đây không')
        if len(clean.split()) <= 5 and not any(w in clean for w in ["chi", "thu", "tiêu", "nợ", "ví", "mua", "danh mục", "mục", "khoản", "giao dịch", "thêm", "tạo", "xóa", "sửa", "đổi", "đặt", "ngân sách", "hạn mức", "tiết kiệm", "định kỳ", "xem"]):
            return True

        return False

    @classmethod
    def is_budget_intent(cls, text: str) -> bool:
        """Kiểm tra câu nói có liên quan đến hạn mức / ngân sách / giới hạn chi tiêu hay không"""
        raw = text.lower().strip()
        budget_kws = [
            "hạn mức", "han muc", "ngân sách", "ngan sach",
            "giới hạn chi tiêu", "gioi han chi tieu", "mức chi tiêu", "muc chi tieu"
        ]
        return any(kw in raw for kw in budget_kws) or ("tối đa" in raw and cls.guess_category(text) is not None)

    @classmethod
    def is_budget_create_intent(cls, text: str) -> bool:
        """Kiểm tra ý định tạo/thêm/thiết lập hạn mức ngân sách mới.
        Hỗ trợ cả trường hợp chưa cung cấp số tiền hoặc danh mục (để chuyển sang luồng hỏi thiếu tham số).
        """
        raw = text.lower().strip()
        # Loại trừ xóa/hủy
        if any(neg in raw for neg in ["xóa", "xoa", "hủy", "huy", "gỡ", "go", "bỏ", "bo"]):
            return False
        # Loại trừ sửa đổi/cập nhật
        if any(kw in raw for kw in ["đổi", "doi", "sửa", "sua", "thay", "cập nhật", "cap nhat", "chỉnh", "chinh"]):
            return False
        # Loại trừ các câu hỏi tra cứu
        if any(q in raw for q in ["thế nào", "the nao", "bao nhiêu", "bao nhieu", "còn", "con", "vượt", "vuot", "tra cứu", "xem danh sách"]):
            return False

        create_triggers = [
            "thêm hạn mức", "them han muc", "tạo hạn mức", "tao han muc", "đặt hạn mức", "dat han muc",
            "cài hạn mức", "cai han muc", "thiết lập hạn mức", "thiet lap han muc",
            "thêm ngân sách", "them ngan sach", "tạo ngân sách", "tao ngan sach", "đặt ngân sách", "dat ngan sach",
            "cài ngân sách", "cai ngan sach", "thiết lập ngân sách", "thiet lap ngan sach", "lập ngân sách", "lap ngan sach",
            "đặt giới hạn chi tiêu", "dat gioi han chi tieu", "tạo giới hạn", "tao gioi han",
            "đặt giới hạn", "dat gioi han", "cài giới hạn", "cai gioi han",
            "cho tôi một ngân sách", "cho tôi 1 ngân sách", "cho tôi ngân sách mới",
            "cho tôi một hạn mức", "cho tôi 1 hạn mức", "cho tôi hạn mức mới",
            "cho tôi giới hạn chi tiêu", "cho toi gioi han chi tieu",
            "hạn mức mới", "han muc moi", "ngân sách mới", "ngan sach moi"
        ]
        if any(trig in raw for trig in create_triggers):
            return True

        if re.search(r"\b(?:thêm|tạo|đặt|cài|thiết lập|lập)\s+(?:cho\s+(?:tôi|ta|mình)\s+)?(?:một\s+|1\s+)?(?:khoản\s+)?(?:hạn mức|ngân sách|giới hạn chi tiêu|mức chi tiêu)\b", raw, re.IGNORECASE):
            return True

        if re.search(r"\b(?:cho\s+(?:tôi|ta|mình)\s+)?(?:một\s+|1\s+)?(?:khoản\s+)?(?:giới hạn chi tiêu|hạn mức mới|ngân sách mới)\b", raw, re.IGNORECASE):
            return True

        # Ví dụ: 'tháng này cho ăn uống tối đa 2 triệu'
        if re.search(r"\b(?:tối đa|toi da)\b", raw) and cls.guess_category(text) and cls.parse_amount(text):
            return True

        return False

    @classmethod
    def is_budget_delete_intent(cls, text: str) -> bool:
        """Kiểm tra ý định xóa/hủy hạn mức ngân sách"""
        raw = text.lower().strip()
        if not cls.is_budget_intent(text):
            return False
        return any(kw in raw for kw in ["xóa", "xoa", "hủy", "huy", "gỡ", "go", "bỏ", "bo"])

    @classmethod
    def is_budget_update_intent(cls, text: str) -> bool:
        """Kiểm tra ý định sửa/cập nhật hạn mức ngân sách"""
        raw = text.lower().strip()
        if not cls.is_budget_intent(text):
            return False
        if any(neg in raw for neg in ["xóa", "xoa", "hủy", "huy"]):
            return False
        return any(kw in raw for kw in ["đổi", "doi", "sửa", "sua", "thay", "cập nhật", "cap nhat", "chỉnh", "chinh", "tăng", "tang", "giảm", "giam"])

    @classmethod
    def is_budget_read_intent(cls, text: str) -> bool:
        """Kiểm tra ý định tra cứu tình trạng hạn mức ngân sách"""
        raw = text.lower().strip()
        if not cls.is_budget_intent(text):
            return False
        if cls.is_budget_create_intent(text) or cls.is_budget_delete_intent(text) or cls.is_budget_update_intent(text):
            return False
        return True

    @classmethod
    def is_budget_write(cls, text: str) -> bool:
        """Alias tương thích ngược cho is_budget_create_intent"""
        return cls.is_budget_create_intent(text)


    @classmethod
    def parse_amount(cls, text: str) -> Optional[int]:
        """Trích xuất số tiền chuẩn từ văn bản tiếng Việt.
        Đại diện chuẩn nội bộ: integer VND (không để mất số 0 hoặc biến dấu chấm phân cách hàng nghìn thành số thập phân).
        
        Hỗ trợ:
        - 50.000đ, 50.000 VNĐ, 50.000 vnđ, 50.000 đồng -> 50000
        - 50,000đ, 50,000 VNĐ -> 50000
        - 50k, 50 k -> 50000
        - 50 nghìn, 50 ngàn -> 50000
        - 2 triệu, 20 triệu, 1,5 triệu, 1.5 triệu -> 2000000, 20000000, 1500000
        - 1tr5, 1 tr 5 -> 1500000
        - một triệu, hai triệu, năm trăm nghìn, nửa triệu, một triệu rưỡi -> 1000000, 2000000, 500000, 500000, 1500000
        - 2 củ -> 2000000
        - 2 tỷ, 1.5 tỷ -> 2000000000, 1500000000
        - 150.000, 150,000, 50.000 -> 150000, 150000, 50000
        - 50000 -> 50000
        """
        raw = text.lower().strip()

        # -1. Kiểm tra mệnh đề đính chính trước (ví dụ: 'không phải 1 triệu, 2 triệu' -> lấy 2 triệu)
        m_corr = re.search(r"(?:không phải|khong phai|chứ không phải)\s+[^,;]+?(?:[,;]|mà là|ma la|mà|ma)\s*(.+)$", raw)
        if m_corr:
            sub_res = cls.parse_amount(m_corr.group(1))
            if sub_res is not None:
                return sub_res

        m_nham = re.search(r"(?:nhầm|lộn|nham|lon)(?:\s+rồi|\s+roi)?[,;]?\s*(.+)$", raw)
        if m_nham:
            sub_res = cls.parse_amount(m_nham.group(1))
            if sub_res is not None:
                return sub_res

        # 0. Textual Vietnamese Numbers (Hỗ trợ số bằng chữ từ STT giọng nói)
        text_num_map = {
            "nửa": 0.5, "mot": 1, "một": 1, "mốt": 1, "hai": 2, "ba": 3, "bốn": 4, "bon": 4, "tư": 4, "tu": 4,
            "năm": 5, "nam": 5, "lăm": 5, "sáu": 6, "sau": 6, "bảy": 7, "bay": 7, "bẩy": 7,
            "tám": 8, "tam": 8, "chín": 9, "chin": 9, "mười": 10, "muoi": 10
        }

        # 0.1: [nửa / một / hai... / 1..9] (triệu / tr / củ / tỷ) rưỡi
        m_tr_ruoi = re.search(r"(?:(?:(\d+(?:[.,]\d+)?)|(nửa|một|hai|ba|bốn|tư|năm|sáu|bảy|bẩy|tám|chín|mười))\s*(?:triệu|trieu|tr|củ|cu|tỷ|ty))\s*rưỡi\b", raw)
        if m_tr_ruoi:
            digit_val = m_tr_ruoi.group(1)
            word_val = m_tr_ruoi.group(2)
            base_n = float(digit_val.replace(",", ".")) if digit_val else text_num_map.get(word_val, 1)
            if any(u in raw for u in ["tỷ", "ty"]):
                return int(round((base_n + 0.5) * 1_000_000_000))
            return int(round((base_n + 0.5) * 1_000_000))

        # 0.1b: Nửa tỷ / nửa củ / nửa lít
        if re.search(r"\bnửa\s+(?:tỷ|ty)\b", raw):
            return 500_000_000
        if re.search(r"\bnửa\s+(?:củ|cu)\b", raw):
            return 500_000
        if re.search(r"\bnửa\s+(?:lít|lit)\b", raw):
            return 50_000

        # 0.1c: Tiếng lóng "năm chục", "hai chục", "ba chục" (50k, 20k, 30k)
        m_chuc_slang = re.search(r"\b(nửa|một|hai|ba|bốn|tư|năm|sáu|bảy|bẩy|tám|chín)\s*chục(?:\s*(?:nghìn|nghin|ngàn|ngan|k))?\b", raw)
        if m_chuc_slang:
            val = text_num_map.get(m_chuc_slang.group(1), 1) * 10_000
            return int(val)

        # 0.2: [mười lăm triệu, hai mươi triệu, hai mươi lăm triệu, một..mười triệu]
        m_phrase_tr = re.search(r"\b(mười\s*(?:một|hai|ba|bốn|tư|lăm|năm|sáu|bảy|bẩy|tám|chín)?|(?:hai|ba|bốn|tư|năm|sáu|bảy|bẩy|tám|chín)\s*mươi(?:\s*(?:mốt|hai|ba|bốn|tư|lăm|năm|sáu|bảy|bẩy|tám|chín))?|nửa|một|hai|ba|bốn|tư|năm|sáu|bảy|bẩy|tám|chín|mười)\s*(?:triệu|trieu|tr|củ|cu)\b", raw)
        if m_phrase_tr:
            phrase = m_phrase_tr.group(1).strip()
            if phrase in text_num_map:
                base = text_num_map[phrase]
            elif phrase.startswith("mười"):
                parts = phrase.split()
                base = 10 if len(parts) == 1 else 10 + text_num_map.get(parts[1], 0)
            else:
                parts = phrase.split()
                tens = text_num_map.get(parts[0], 1) * 10
                unit = text_num_map.get(parts[2], 0) if len(parts) >= 3 else 0
                base = tens + unit
            return int(round(base * 1_000_000))

        # 0.3: [một..chín] tỷ
        m_word_ty = re.search(r"\b(một|hai|ba|bốn|tư|năm|sáu|bảy|bẩy|tám|chín|mười)\s*(?:tỷ|ty)\b", raw)
        if m_word_ty:
            val_word = text_num_map.get(m_word_ty.group(1), 1)
            return int(round(val_word * 1_000_000_000))

        # 0.4: [hai trăm ba mươi nghìn, năm trăm nghìn, một trăm nghìn...]
        m_tram_chuc = re.search(r"\b(một|hai|ba|bốn|tư|năm|sáu|bảy|bẩy|tám|chín)\s*trăm(?:\s*(?:lẻ|linh)\s*(một|hai|ba|bốn|tư|năm|lăm|sáu|bảy|tám|chín)|(?:\s*(hai|ba|bốn|tư|năm|sáu|bảy|tám|chín)?\s*mươi(?:\s*(mốt|hai|ba|bốn|tư|năm|lăm|sáu|bảy|tám|chín))?))?\s*(?:nghìn|nghin|ngàn|ngan|k)?\b", raw)
        if m_tram_chuc and any(u in raw for u in ["trăm", "nghìn", "nghin", "ngàn", "ngan", "k"]):
            tram = text_num_map.get(m_tram_chuc.group(1), 1) * 100
            chuc = 0
            if m_tram_chuc.group(2):
                chuc = text_num_map.get(m_tram_chuc.group(2), 0)
            elif m_tram_chuc.group(3) or m_tram_chuc.group(4):
                t_val = text_num_map.get(m_tram_chuc.group(3), 1) * 10 if m_tram_chuc.group(3) else 10
                u_val = text_num_map.get(m_tram_chuc.group(4), 0) if m_tram_chuc.group(4) else 0
                chuc = t_val + u_val
            total_k = tram + chuc
            return int(total_k * 1_000)

        # 0.5: [hai mươi, ba mươi, năm mươi...] nghìn/ngàn
        m_chuc_word = re.search(r"\b(hai|ba|bốn|tư|năm|sáu|bảy|bẩy|tám|chín)?\s*mươi(?:\s*(năm|lăm|mốt|hai|ba|bốn|tư|sáu|bảy|tám|chín))?\s*(?:nghìn|nghin|ngàn|ngan|k)\b", raw)
        if m_chuc_word:
            tens = text_num_map.get(m_chuc_word.group(1), 1) * 10
            units = text_num_map.get(m_chuc_word.group(2), 0) if m_chuc_word.group(2) else 0
            if m_chuc_word.group(2) == "mốt":
                units = 1
            return int((tens + units) * 1_000)

        # 1. Pattern: 1tr5, 2tr8, 1 triệu 5, 2 triệu 8, 1 củ 2, 2 củ 5
        m_combo = re.search(r"(\d+)\s*(?:tr|triệu|trieu|củ|cu)\s*(\d+)(?!\d)", raw)
        if m_combo:
            base = int(m_combo.group(1)) * 1_000_000
            dec = m_combo.group(2)
            if len(dec) == 1:
                val = base + int(dec) * 100_000
            else:
                val = base + int(dec) * (10 ** (6 - len(dec)))
            return int(val)

        # 1.1. Pattern: 1 tỷ 2, 2 tỷ 5
        m_combo_ty = re.search(r"(\d+)\s*(?:tỷ|ty)\s*(\d+)(?!\d)", raw)
        if m_combo_ty:
            base = int(m_combo_ty.group(1)) * 1_000_000_000
            dec = m_combo_ty.group(2)
            if len(dec) == 1:
                val = base + int(dec) * 100_000_000
            else:
                val = base + int(dec) * (10 ** (9 - len(dec)))
            return int(val)

        # 1.5. Pattern: Tiếng lóng vé (1 vé = 500k, 2 vé = 1tr)
        m_ve = re.search(r"(\d+)\s*(?:vé|ve)\b", raw)
        if m_ve:
            return int(m_ve.group(1)) * 500_000

        # 2. Pattern: Số + chục + đơn vị (2 chục triệu, 3 chục ngàn, 5 chục k, 2 chục củ)
        m_chuc = re.search(r"(\d+(?:[.,]\d+)?)\s*chục\s*(triệu|trieu|tr|củ|nghìn|nghin|ngàn|ngan|k)?\b", raw)
        if m_chuc:
            base_chuc = float(m_chuc.group(1).replace(",", ".")) * 10
            unit = m_chuc.group(2)
            if unit in ("triệu", "trieu", "tr", "củ"):
                return int(round(base_chuc * 1_000_000))
            elif unit in ("nghìn", "nghin", "ngàn", "ngan", "k"):
                return int(round(base_chuc * 1_000))
            else:
                return int(round(base_chuc * 1_000))

        # 3. Pattern: Số thập phân hoặc nguyên + tỷ
        m_ty = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:tỷ|ty)\b", raw)
        if m_ty:
            num = float(m_ty.group(1).replace(",", "."))
            return int(round(num * 1_000_000_000))

        # 4. Pattern: Số thập phân hoặc nguyên + triệu / tr / củ
        m_tr = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:triệu|trieu|tr|củ)\b", raw)
        if m_tr:
            num = float(m_tr.group(1).replace(",", "."))
            return int(round(num * 1_000_000))

        # 5. Pattern: Số + k, nghìn, ngàn (50k, 50 nghìn, 1.5k, 1,5k)
        m_k = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:k|nghìn|nghin|ngàn|ngan)\b", raw)
        if m_k:
            num = float(m_k.group(1).replace(",", "."))
            return int(round(num * 1_000))

        # 5.5. Pattern: Tiếng lóng 'lít', 'lốp' (1 lít = 100.000đ, 3 lít = 300.000đ)
        m_lit = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:lít|lit|loét|loet|lốp|lop)\b", raw)
        if m_lit:
            num = float(m_lit.group(1).replace(",", "."))
            return int(round(num * 100_000))

        # 6. Pattern: Số có định dạng phân cách hàng nghìn (ví dụ 50.000đ, 50.000 VNĐ, 50,000 đ, 50.000, 150,000)
        # Bắt buộc xử lý TRƯỚC plain number + đ để không bao giờ nhầm .000 thành số thập phân!
        m_grouped = re.search(r"(?<!\d)(\d{1,3}(?:[.,]\d{3})+)(?:\s*(?:đ|đồng|dong|vnđ|vnd))?(?!\d)", raw)
        if m_grouped:
            s = m_grouped.group(1)
            clean_s = re.sub(r"[.,]", "", s)
            try:
                return int(clean_s)
            except ValueError:
                pass

        # 7. Pattern: Số nguyên + đơn vị tiền tệ (50đ, 50000đ, 50 đồng, 0đ)
        m_dong = re.search(r"(\d+)\s*(?:đ|đồng|dong|vnđ|vnd)\b", raw)
        if m_dong:
            return int(m_dong.group(1))

        # 8. Pattern: Số nguyên đơn thuần (>= 4 chữ số, hoặc >= 3 chữ số nếu có từ chỉ tiền / chi tiêu)
        m_plain = re.search(r"(?:hết|tiền|chi|thu|số tiền|giá|giá là|khoảng|tầm)?\s*(\d{4,})(?!\d)", raw)
        if m_plain:
            return int(m_plain.group(1))

        # 9. Pattern: Số nguyên 2-3 chữ số sau từ chỉ tiền/chi (hết 500, giá 200)
        m_short_plain = re.search(r"(?:hết|giá|tổng|chi|thu|trả)\s*(\d{2,3})(?!\d)", raw)
        if m_short_plain:
            return int(m_short_plain.group(1))

        return None

    @classmethod
    def parse_explicit_date(cls, text: str) -> Optional[str]:
        """Trích xuất ngày từ văn bản nếu người dùng có nói rõ (hôm nay, hôm qua, hôm kia, ngày mai, DD/MM/YYYY, YYYY-MM-DD), ngược lại trả về None."""
        raw = text.lower()
        today = datetime.date.today()

        if "hôm nay" in raw or "hom nay" in raw:
            return today.strftime("%Y-%m-%d")
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

        return None

    @classmethod
    def parse_date(cls, text: str) -> str:
        """Trích xuất ngày từ văn bản, mặc định là ngày hôm nay YYYY-MM-DD"""
        d = cls.parse_explicit_date(text)
        if d:
            return d
        return datetime.date.today().strftime("%Y-%m-%d")

    @classmethod
    def extract_date(cls, text: str) -> str:
        """Trích xuất ngày từ văn bản (alias tương thích)"""
        return cls.parse_date(text)

    @classmethod
    def extract_transfer_wallets(cls, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Trích xuất tên ví nguồn và ví đích từ câu chuyển tiền.
        Ví dụ: 'Chuyển 500 nghìn từ ví A sang ví B' -> ('A', 'B')
        'Chuyển tiền mặt sang momo' -> ('tiền mặt', 'momo')
        'Chuyển 1 triệu từ ví điện tử sang tiền mặt' -> ('ví điện tử', 'tiền mặt')
        'Chuyển từ ví ngân hàng' -> ('ví ngân hàng', None)
        'Chuyển 500 nghìn cho ví Vietcombank' -> (None, 'Vietcombank')
        """
        raw = text.strip()
        # Pattern 1: chuyển [tiền] [từ] X sang/đến/qua/vào/cho Y
        m = re.search(
            r"(?:chuyển\s+(?:tiền(?!\s+mặt)\s+)?|chuyen\s+(?:tien(?!\s+mat)\s+)?|từ\s+|tu\s+)(?:từ\s+|tu\s+)?([^,\n]+?)\s+(?:sang|đến|qua|den|vao|vào|cho)\s+([^,.\n;]+)",
            raw,
            re.IGNORECASE
        )
        if m:
            raw_from = m.group(1).strip()
            # Bỏ số tiền đi kèm ở đầu ví nguồn nếu có (ví dụ '500k từ momo' -> 'momo')
            raw_from = re.sub(r'^\d+[\d.,]*\s*(?:triệu|trieu|nghìn|nghin|ngàn|ngan|tr|k|củ|tỷ|ty|vnđ|vnd|đ|đồng)?\s*(?:từ\s+|tu\s+)?', '', raw_from, flags=re.IGNORECASE).strip()
            raw_to = m.group(2).strip()

            if re.search(r"^(?:ví|vi)\s+(?:điện tử|dien tu)\b", raw_from, re.IGNORECASE):
                w_from = "ví điện tử"
            elif raw_from.lower() in ("tiền mặt", "tien mat"):
                w_from = "tiền mặt"
            else:
                w_from = re.sub(r'^(?:ví|túi|vi|tui)\s+', '', raw_from, flags=re.IGNORECASE).strip(" .,!?:;")

            if re.search(r"^(?:ví|vi)\s+(?:điện tử|dien tu)\b", raw_to, re.IGNORECASE):
                w_to = "ví điện tử"
            elif raw_to.lower() in ("tiền mặt", "tien mat"):
                w_to = "tiền mặt"
            else:
                w_to = re.sub(r'^(?:ví|túi|vi|tui)\s+', '', raw_to, flags=re.IGNORECASE).strip(" .,!?:;")

            # Cắt bỏ số tiền ở đuôi ví đích (cả số và chữ)
            w_to = re.sub(r"\s*(?:với|khoảng|tầm)?\s*(?:\b\d+[\d.,]*\s*(?:chục\s*)?(?:k|nghìn|nghin|ngàn|ngan|tr|triệu|trieu|củ|tỷ|ty|vnđ|vnd|đ|đồng)?|\b(?:nửa|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\s*(?:triệu|tr|trăm|nghìn|ngàn|tỷ))\b.*$", "", w_to, flags=re.IGNORECASE).strip()
            return w_from, w_to

        # Pattern 2: Chỉ có ví đích: sang/đến/qua/vào/cho [ví] Y
        m2 = re.search(r"(?:sang|đến|qua|den|vao|vào|cho)\s+(?:ví\s+|túi\s+|vi\s+|tui\s+)?([^,.\n;]+)", raw, re.IGNORECASE)
        if m2:
            raw_cand = m2.group(1).strip()
            if re.search(r"^(?:điện tử|dien tu)\b", raw_cand, re.IGNORECASE):
                candidate = "ví điện tử"
            elif raw_cand.lower() in ("tiền mặt", "tien mat"):
                candidate = "tiền mặt"
            else:
                candidate = re.sub(r'^(?:ví|túi|vi|tui)\s+', '', raw_cand, flags=re.IGNORECASE).strip(" .,!?:;")
            candidate = re.sub(r"\s*(?:với|khoảng|tầm)?\s*(?:\b\d+[\d.,]*\s*(?:chục\s*)?(?:k|nghìn|nghin|ngàn|ngan|tr|triệu|trieu|củ|tỷ|ty|vnđ|vnd|đ|đồng)?|\b(?:nửa|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\s*(?:triệu|tr|trăm|nghìn|ngàn|tỷ))\b.*$", "", candidate, flags=re.IGNORECASE).strip()
            if candidate and not any(w in candidate.lower() for w in ["bao nhiêu", "ai", "được không", "thế nào"]):
                return None, candidate

        # Pattern 3: Chỉ có ví nguồn: từ [ví] X
        m3 = re.search(r"(?:chuyển\s+từ|từ|tu)\s+(?:ví\s+|túi\s+|vi\s+|tui\s+)?([^,.\n;]+)", raw, re.IGNORECASE)
        if m3:
            raw_cand = m3.group(1).strip()
            if re.search(r"^(?:điện tử|dien tu)\b", raw_cand, re.IGNORECASE):
                candidate = "ví điện tử"
            elif raw_cand.lower() in ("tiền mặt", "tien mat"):
                candidate = "tiền mặt"
            else:
                candidate = re.sub(r'^(?:ví|túi|vi|tui)\s+', '', raw_cand, flags=re.IGNORECASE).strip(" .,!?:;")
            candidate = re.sub(r"\s*(?:với|khoảng|tầm)?\s*(?:\b\d+[\d.,]*\s*(?:chục\s*)?(?:k|nghìn|nghin|ngàn|ngan|tr|triệu|trieu|củ|tỷ|ty|vnđ|vnd|đ|đồng)?|\b(?:nửa|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\s*(?:triệu|tr|trăm|nghìn|ngàn|tỷ))\b.*$", "", candidate, flags=re.IGNORECASE).strip()
            if candidate and not any(w in candidate.lower() for w in ["bao nhiêu", "ai", "được không", "thế nào"]):
                return candidate, None

        return None, None

    @classmethod
    def extract_goal_name(cls, text: str) -> Optional[str]:
        """Trích xuất tên mục tiêu tiết kiệm.
        Ví dụ: 'Đưa 1 triệu vào mục tiêu mua laptop' -> 'mua laptop'
        """
        raw = text.lower()
        if any(q in raw for q in ["mục tiêu của ta", "mục tiêu của tôi", "mục tiêu tiết kiệm của ta", "tiết kiệm của ta thế nào", "tiến độ mục tiêu", "các mục tiêu", "tất cả mục tiêu"]):
            return None

        m = re.search(r"(?:mục tiêu|tiết kiệm cho|quỹ|muc tieu)\s+(?:là\s+|để\s+)?([^?.,\n;]+)", text, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip()
            # Bóc tách số tiền ở đuôi nếu có (ví dụ: 'mua laptop 30 triệu' -> 'mua laptop')
            candidate = re.sub(r"\s*(?:với|khoảng|tầm|số tiền)?\s*\b\d+[\d.,]*\s*(?:chục\s*)?(?:k|nghìn|nghin|ngàn|ngan|tr|triệu|trieu|củ|tỷ|ty|vnđ|vnd|đ|đồng)?\b.*$", "", candidate, flags=re.IGNORECASE).strip()
            for stop_w in ["tiết kiệm", "của ta", "của tôi", "thế nào", "ra sao", "tiến triển thế nào", "tiến triển ra sao"]:
                candidate = re.sub(rf"\b{re.escape(stop_w)}\b", "", candidate, flags=re.IGNORECASE).strip()
            if candidate and len(candidate) > 1 and not any(w in candidate.lower() for w in ["thế nào", "ra sao", "gì"]):
                return candidate
        return None

    @classmethod
    def guess_category(cls, text: str) -> Optional[str]:
        """Dự đoán danh mục thu/chi từ ngữ cảnh câu nói"""
        raw = text.lower()
        if any(k in raw for k in ["ăn uống", "cơm", "phở", "bún", "bánh mì", "trà sữa", "cafe", "cà phê", "nhậu", "tiệc", "ăn sáng", "ăn trưa", "ăn tối", "bữa sáng", "bữa trưa", "bữa tối", "điểm tâm"]) or re.search(r"\b(ăn|uống)\b", raw):
            return "Ăn Uống"
        if any(k in raw for k in ["xăng", "đổ xăng", "grab", "taxi", "gửi xe", "vé xe", "sửa xe", "đi lại"]) or re.search(r"\b(xe|be)\b", raw):
            return "Đi Lại"
        if any(k in raw for k in ["điện", "nước", "internet", "wifi", "tiền nhà", "phòng trọ", "hóa đơn", "chung cư"]):
            return "Hóa Đơn"
        # Tránh nhầm lẫn 'ngân sách' với 'sách' (mua sắm), hoặc 'mục tiêu mua' với mua sắm
        if any(k in raw for k in ["quần áo", "giày", "dép", "shopee", "lazada", "tiki", "mua sắm"]):
            return "Mua Sắm"
        if re.search(r"(?<!ngân\s)\bsách\b", raw):
            return "Mua Sắm"
        if re.search(r"\bmua\b", raw) and not any(k in raw for k in ["mục tiêu", "muc tieu", "tiết kiệm", "tiet kiem"]):
            return "Mua Sắm"
        if any(k in raw for k in ["thuốc", "bệnh viện", "khám", "bác sĩ", "y tế"]):
            return "Y Tế"
        if any(k in raw for k in ["lương", "thưởng", "bonus", "hoa hồng"]):
            return "Tiền Lương"
        return None

    @classmethod
    def parse_period(cls, text: str) -> Optional[str]:
        """Trích xuất khoảng thời gian từ văn bản tự nhiên"""
        raw = text.lower()
        if any(k in raw for k in ["hôm nay", "hom nay", "ngày nay"]):
            return "today"
        if any(k in raw for k in ["hôm qua", "hom qua"]):
            return "yesterday"
        if any(k in raw for k in ["tuần trước", "tuan truoc", "tuần vừa rồi", "tuan vua roi"]):
            return "last_week"
        if any(k in raw for k in ["tuần này", "tuan nay"]):
            return "this_week"
        if any(k in raw for k in ["tháng trước", "thang truoc", "tháng vừa rồi", "thang vua roi", "tháng đó", "thang do"]):
            return "last_month"
        if any(k in raw for k in ["tháng này", "thang nay"]):
            return "this_month"
        if any(k in raw for k in ["tháng sau", "thang sau", "tháng tới", "thang toi", "tháng tiếp", "thang tiep"]):
            today = datetime.date.today()
            if today.month == 12:
                next_y, next_m = today.year + 1, 1
            else:
                next_y, next_m = today.year, today.month + 1
            return f"{next_y:04d}-{next_m:02d}"
        if any(k in raw for k in ["7 ngày qua", "7 ngày gần đây", "7 ngay qua", "7 ngay gan day"]):
            return "last_7_days"
        if any(k in raw for k in ["30 ngày qua", "30 ngày gần đây", "30 ngay qua", "30 ngay gan day"]):
            return "last_30_days"
        if any(k in raw for k in ["3 tháng gần đây", "3 thang gan day", "ba tháng gần đây"]):
            return "last_3_months"
        if any(k in raw for k in ["từ đầu tháng đến giờ", "đầu tháng", "tu dau thang den gio", "dau thang"]):
            return "month_to_date"
        if any(k in raw for k in ["cuối tháng", "cuoi thang"]):
            return "month_end"
        if any(k in raw for k in ["quý trước", "quy truoc"]):
            return "last_quarter"
        if any(k in raw for k in ["quý này", "quy nay"]):
            return "this_quarter"
        if any(k in raw for k in ["năm ngoái", "nam ngoai", "năm trước", "nam truoc"]):
            return "last_year"
        if any(k in raw for k in ["năm nay", "nam nay"]):
            return "this_year"

        # Regex YYYY-MM
        m_ym = re.search(r"\b(\d{4})-(\d{2})\b", raw)
        if m_ym:
            return m_ym.group(0)

        # Regex tháng M/YYYY hoặc tháng M
        m_thang = re.search(r"tháng\s*(\d{1,2})(?:[/-](\d{4}))?", raw)
        if m_thang:
            m = int(m_thang.group(1))
            y = int(m_thang.group(2)) if m_thang.group(2) else datetime.date.today().year
            if 1 <= m <= 12:
                return f"{y:04d}-{m:02d}"

        return None

    @classmethod
    def is_debt_intent(cls, text: str) -> bool:
        """Kiểm tra câu nói có liên quan đến nợ / vay mượn hay không"""
        raw = text.lower().strip()
        debt_keywords = [
            "khoản nợ", "khoan no", "sổ nợ", "so no", "vay mượn", "vay muon",
            "khoản vay", "khoan vay", "khoản phải trả", "khoan phai tra",
            "khoản phải thu", "khoan phai thu", "cho vay", "cho muợn", "cho mượn",
            "đi vay", "di vay", "vay tiền", "vay tien", "mượn tiền", "muon tien",
            "tất toán nợ", "tat toan no", "quyết toán nợ", "quyet toan no", "trả nợ", "tra no"
        ]
        if any(kw in raw for kw in debt_keywords):
            return True
        return bool(re.search(r"\b(?:nợ|vay|mượn)\b", raw))

    @classmethod
    def is_debt_create_intent(cls, text: str) -> bool:
        """Kiểm tra ý định ghi nhận/tạo khoản nợ mới (cho vay hoặc đi vay)"""
        raw = text.lower().strip()
        if not cls.is_debt_intent(text):
            return False

        # Loại trừ các hành động hủy/xóa, quyết toán, cập nhật, hoặc chỉ đọc
        if any(neg in raw for neg in ["xóa", "xoa", "hủy", "huy", "gỡ", "go", "bỏ", "bo", "quyết toán", "quyet toan", "tất toán", "tat toan", "đã trả", "da tra", "đã thu", "da thu"]):
            return False
        if any(kw in raw for kw in ["sửa", "sua", "đổi", "doi", "cập nhật", "cap nhat", "chỉnh", "chinh"]):
            return False

        # Loại trừ các câu hỏi tìm hiểu, tra cứu quy trình hoặc chức năng
        inquiry_kws = [
            "chức năng nào", "chuc nang nao", "dùng chức năng", "dung chuc nang",
            "phân hệ nào", "phan he nao", "tab nào", "tab nao", "ở đâu", "o dau",
            "thế nào", "the nao", "làm sao", "lam sao", "là gì", "la gi",
            "hướng dẫn", "huong dan", "giải thích", "giai thich", "như thế nào", "ra sao", "cách nào", "cach nao"
        ]
        if any(q in raw for q in inquiry_kws):
            return False

        # Nếu chỉ là xem/hỏi mà không có số tiền:
        amt = cls.parse_amount(text)
        if not amt and any(q in raw for q in ["xem", "tra cứu", "thế nào", "bao nhiêu", "sao kê", "danh sách", "kiểm tra", "quản lý"]):
            return False

        # Các mẫu tạo nợ tổng quát:
        # 1. Động từ tạo/thêm/ghi + khoản nợ/vay/mượn/phải trả
        if re.search(r"\b(?:thêm|tạo|ghi|ghi nhận|lập|nhập)\s+(?:cho\s+(?:tôi|ta|mình)\s+)?(?:một\s+|1\s+)?(?:khoản\s+)?(?:nợ|vay|mượn|phải trả|phải thu)\b", raw, re.IGNORECASE):
            return True

        # 2. tôi đang nợ / đang nợ [số tiền]
        if re.search(r"\b(?:tôi|ta|mình)?\s*(?:đang\s+)?nợ\s+\d+", raw, re.IGNORECASE) or re.search(r"\b(?:tôi|ta|mình)\s+đang\s+nợ\b", raw, re.IGNORECASE):
            return True

        # 3. 'khoản nợ / khoản vay / khoản phải trả' đi kèm số tiền cụ thể
        has_amount = bool(re.search(r"\b\d+[\d.,]*\s*(?:k|nghìn|ngàn|tr|triệu|tỷ|vnđ|đ|đồng)?\b", raw, re.IGNORECASE))
        if has_amount and re.search(r"\b(?:khoản\s+nợ|khoản\s+vay|khoản\s+mượn|khoản\s+phải\s+trả|khoản\s+phải\s+thu)\b", raw, re.IGNORECASE):
            return True

        # 4. cho/đưa ... vay/mượn
        if re.search(r"\b(?:cho|đưa)\b.*?\b(?:vay|mượn)\b", raw, re.IGNORECASE):
            return True

        # 5. cho vay / đi vay / vay của / mượn của ...
        if re.search(r"\b(?:cho vay|cho mượn|đi vay|vay của|mượn của|vay mượn|vay tiền|mượn tiền)\b", raw, re.IGNORECASE):
            return True

        return False

    @classmethod
    def extract_debt_creation_args(cls, text: str) -> Optional[Dict[str, Any]]:
        """Trích xuất tham số cho công cụ create_debt (chiều nợ, đối tác, số tiền, ghi chú)"""
        if not cls.is_debt_create_intent(text):
            return None

        raw = text.lower().strip()
        amt = cls.parse_amount(text)
        p_name = cls.extract_person_name(text)

        # Xác định chiều nợ (LEND: cho vay / BORROW: đi vay hoặc nợ phải trả)
        is_lend = (
            any(kw in raw for kw in ["cho vay", "cho mượn", "phải thu", "phai thu"]) or
            bool(re.search(r"\b(?:cho|đưa)\b.*?\b(?:vay|mượn)\b", raw))
        )
        d_type = "LEND" if is_lend else "BORROW"

        return {
            "debt_type": d_type,
            "person_name": p_name or "Đối tác",
            "amount": amt or 0,
            "note": text.strip()
        }

    @classmethod
    def is_debt_delete_intent(cls, text: str) -> bool:
        """Kiểm tra ý định xóa/hủy khoản nợ khỏi sổ sách"""
        raw = text.lower().strip()
        if not cls.is_debt_intent(text):
            return False
        return any(kw in raw for kw in ["xóa", "xoa", "hủy", "huy", "gỡ", "go", "bỏ", "bo"])

    @classmethod
    def is_debt_settle_intent(cls, text: str) -> bool:
        """Kiểm tra ý định tất toán / quyết toán / đã trả xong khoản nợ"""
        raw = text.lower().strip()
        if not cls.is_debt_intent(text):
            return False
        settle_triggers = [
            "tất toán", "tat toan", "quyết toán", "quyet toan",
            "đã trả", "da tra", "trả xong", "tra xong", "trả hết", "tra het",
            "đã thu", "da thu", "thu hồi", "thu hoi", "thu xong", "thu xog"
        ]
        return any(trig in raw for trig in settle_triggers)

    @classmethod
    def is_wallet_create_intent(cls, text: str) -> bool:
        """Kiểm tra câu nói có mang ý định tạo/thêm/mở ví hoặc tài khoản hay không"""
        raw = text.lower().strip()
        # Tuyệt đối không nhầm lẫn với nợ/vay mượn
        if cls.is_debt_intent(text):
            return False
        # Không được là xóa, hủy, chuyển tiền, hay xem
        if any(neg in raw for neg in ["xóa", "xoa", "hủy", "huy", "chuyển", "chuyen", "đóng", "dong", "khóa", "khoa", "xem", "tra cứu", "sao kê"]):
            return False

        create_triggers = [
            "thêm ví", "them vi", "tạo ví", "tao vi", "mở ví", "mo vi", "lập ví", "lap vi",
            "thêm một ví", "them mot vi", "tạo một ví", "tao mot vi", "mở một ví", "mo mot vi",
            "thêm 1 ví", "tạo 1 ví", "mở 1 ví",
            "tạo tài khoản", "tao tai khoan", "mở tài khoản", "mo tai khoan", "thêm tài khoản", "them tai khoan",
            "tạo túi càn khôn", "thêm túi càn khôn", "mở túi càn khôn"
        ]
        if any(trig in raw for trig in create_triggers):
            return True

        # Cấu trúc: động từ tạo/thêm/mở ... ví/tài khoản/túi càn khôn
        m = re.search(r"\b(thêm|tạo|mở|lập|đăng ký)\b.*?\b(ví|tài khoản|túi càn khôn|túi)\b", raw)
        return m is not None

    @classmethod
    def extract_dynamic_wallet_creation_args(cls, text: str) -> Optional[Dict[str, Any]]:
        """Trích xuất động tên ví, số dư ban đầu và phân loại ví từ ngôn ngữ tự nhiên.
        Hoàn toàn KHÔNG dùng whitelist tên ví/ngân hàng.
        """
        if not cls.is_wallet_create_intent(text):
            return None

        amt = cls.parse_amount(text)
        clean = text.strip()

        # 1. Bóc tách tiền tố chỉ hành động tạo ví
        clean = re.sub(
            r"^(?:hãy\s+|vui lòng\s+)?(?:cho\s+(?:tôi|ta|mình)\s+)?(?:thêm|tạo|mở|lập|đăng ký)\s+(?:cho\s+(?:tôi|ta|mình)\s+)?(?:một\s+|1\s+)?(?:cái\s+)?(?:ví|tài khoản|túi càn khôn|túi|quỹ)(?:\s+mới)?\s*",
            "",
            clean,
            flags=re.IGNORECASE
        ).strip()

        # 2. Bóc tách phần giới từ + số tiền ở đuôi (ví dụ: 'với 10 triệu', '20 triệu', 'số dư 5 triệu')
        clean = re.sub(
            r"\s*(?:với|có|số dư|chứa|ban đầu|khoảng|tầm)?\s*(?:\d+[\d.,]*\s*(?:chục\s*)?(?:k|nghìn|nghin|ngàn|ngan|tr|triệu|trieu|củ|tỷ|ty|vnđ|vnd|đ|đồng)?).*$",
            "",
            clean,
            flags=re.IGNORECASE
        ).strip()

        # 3. Dọn dẹp từ phụ trợ ở đuôi (ví dụ: 'đi', 'nha', 'nhé', 'giúp', 'giùm', 'mới')
        for stop in ["đi", "di", "nha", "nhé", "nhe", "giúp", "giup", "giùm", "gium", "với", "voi", "cho tôi", "cho ta", "mới", "moi"]:
            clean = re.sub(rf"\b{re.escape(stop)}\b$", "", clean, flags=re.IGNORECASE).strip()

        clean = clean.strip(" \t\n\r\"'.,-:")
        w_name = clean or "Ví Mới"
        if w_name.islower():
            w_name = w_name.title()

        # Suy luận loại ví (bank, e-wallet, cash, crypto)
        raw_full = (clean + " " + text).lower()
        if any(w in raw_full for w in ["bank", "ngân hàng", "ngan hang", "vcb", "mb", "techcombank", "acb", "bidv", "vietinbank", "tpbank", "vpbank", "agribank", "sacombank", "vib"]):
            w_type = "bank"
        elif any(w in raw_full for w in ["momo", "zalopay", "zalo", "shopeepay", "shopee", "viettelpay", "viettel", "vnpay", "ví điện tử", "vi dien tu", "pay"]):
            w_type = "e-wallet"
        elif any(w in raw_full for w in ["crypto", "tiền ảo", "tien ao", "usdt", "btc", "binance", "eth"]):
            w_type = "crypto"
        elif any(w in raw_full for w in ["tiền mặt", "tien mat", "két sắt", "ket sat", "heo đất", "heo dat"]):
            w_type = "cash"
        else:
            w_type = "bank" if any(w in raw_full for w in ["tài khoản", "tai khoan", "stk"]) else "cash"

        return {
            "wallet_name": w_name,
            "balance": float(amt or 0),
            "wallet_type": w_type
        }

    @classmethod
    def extract_wallet_name(cls, text: str) -> Optional[str]:
        """Trích xuất tên ví tiền từ câu nói"""
        raw = text.lower()
        if any(q in raw for q in ["ví nào", "vi nao", "túi nào", "tui nao", "nhiều tiền nhất", "nhiều nhất", "lớn nhất", "các ví", "mọi ví", "tất cả ví"]):
            return None

        # Check specific wallet keywords first
        if "vietcombank" in raw or "vcb" in raw:
            return "Vietcombank"
        if "momo" in raw:
            return "MoMo"
        if "tiền mặt" in raw or "tien mat" in raw:
            return "Tiền Mặt"
        if "zalopay" in raw or "zalo pay" in raw:
            return "ZaloPay"

        m = re.search(r"(?:ví|túi|tài khoản|tai khoan|vi|tui)\s+([^?.,\n;]+)", text, re.IGNORECASE)
        if m:
            w_candidate = m.group(1).strip()
            w_candidate = re.sub(r"\s*(?:với|có|số dư|chứa|ban đầu)?\s*(?:\d+[\d.,]*\s*(?:chục\s*)?(?:k|nghìn|nghin|ngàn|ngan|tr|triệu|trieu|củ|tỷ|ty|vnđ|vnd|đ|đồng)?).*$", "", w_candidate, flags=re.IGNORECASE).strip()
            for stop_w in [
                "có bao nhiêu tiền", "co bao nhieu tien", "còn bao nhiêu tiền", "con bao nhieu tien",
                "còn bao nhiêu", "con bao nhieu", "bao nhiêu tiền", "bao nhieu tien", "của tôi", "của ta",
                "nào", "gì", "bao nhiêu", "hiện tại", "nhiều nhất", "lớn nhất", "đang còn", "dang con",
                "đi", "nha", "nhé", "giúp", "giùm", "đây", "có", "tiền"
            ]:
                w_candidate = re.sub(rf"\b{re.escape(stop_w)}\b", "", w_candidate, flags=re.IGNORECASE).strip()
            w_candidate = w_candidate.strip(" \t\n\r\"'.,-:")
            if w_candidate and len(w_candidate) > 1 and not any(w in w_candidate.lower() for w in ["nào", "gì", "đang", "còn"]):
                return w_candidate.title() if w_candidate.islower() else w_candidate

        return None

    @classmethod
    def is_followup_query(cls, text: str) -> bool:
        """Kiểm tra câu nói có mang ngữ cảnh tiếp nối/follow-up hay không"""
        clean = text.lower().strip(" ?.,!")

        # Nếu có từ khóa hành động độc lập mới -> không phải follow-up
        independent_keywords = [
            "tìm ", "tim ", "tra cứu", "tra cuu", "lọc giao dịch",
            "ngân sách", "ngan sach", "hạn mức", "han muc",
            "mục tiêu", "muc tieu", "tiết kiệm", "tiet kiem",
            "sổ nợ", "so no", "cho vay", "đi vay", "tôi vừa", "vừa chi", "vừa tiêu"
        ]
        if any(kw in clean for kw in independent_keywords):
            return False

        # Các tiền tố tiếp nối câu trước
        prefix_triggers = [
            "còn ", "con ", "thế còn ", "the con ", "vậy còn ", "vay con ",
            "chỉ lấy", "chi lay", "chỉ tính", "chi tinh", "chỉ xem", "chi xem",
            "lọc theo", "loc theo", "lấy thêm", "lay them"
        ]
        if any(clean.startswith(p) for p in prefix_triggers):
            return True

        # Hoặc câu siêu ngắn chỉ là chu kỳ thời gian tiếp nối (ví dụ: 'tháng trước?', 'tuần này?', 'hôm qua?')
        period_phrases = [
            "tháng trước", "thang truoc", "tháng này", "thang nay",
            "tuần trước", "tuan truoc", "tuần này", "tuan nay",
            "hôm qua", "hom qua", "hôm nay", "hom nay"
        ]
        if clean in period_phrases:
            return True

        return False

    @classmethod
    def is_pronoun_reference(cls, text: str) -> Tuple[bool, Optional[str]]:
        """Nhận diện câu hỏi có tham chiếu đại từ / ngữ cảnh đến thực thể gần nhất (Entity Reference Memory).
        Ví dụ: 'kiểm tra nó', 'cái ví đó', 'ví đó còn bao nhiêu', 'ví đó thế nào', 'khoản vừa rồi', 'khoản đó sửa lại'
        """
        raw = text.lower().strip()
        raw_unacc = remove_accents(raw)

        # 1. Tham chiếu ví tiền: "cái ví đó", "ví đó", "kiểm tra nó", "nó còn bao nhiêu"
        wallet_refs = [
            "cái ví đó", "cai vi do", "ví đó", "vi do", "ví đấy", "vi day", "túi đó", "tui do",
            "ví này", "vi nay", "cái ví này", "cai vi nay", "ví ấy", "vi ay", "cái ví hôm trước", "cai vi hom truoc"
        ]
        if any(w in raw or w in raw_unacc for w in wallet_refs):
            return True, "wallet"
        if any(w in raw for w in ["kiểm tra nó", "xem nó", "nó còn bao nhiêu", "nó có bao nhiêu", "số dư nó", "tra cứu nó"]):
            return True, "wallet"

        # 2. Tham chiếu giao dịch: "khoản vừa rồi", "khoản đó", "cái vừa rồi", "khoản kia"
        txn_refs = [
            "khoản vừa rồi", "khoan vua roi", "khoản đó", "khoan do", "khoản đấy", "khoan day",
            "giao dịch vừa rồi", "giao dich vua roi", "giao dịch đó", "giao dich do",
            "khoản kia", "khoan kia", "khoản này", "khoan nay", "cái vừa rồi", "cai vua roi"
        ]
        if any(t in raw or t in raw_unacc for t in txn_refs):
            return True, "transaction"

        # 3. Tham chiếu nợ
        debt_refs = ["khoản nợ đó", "khoan no do", "khoản nợ kia", "khoan no kia", "món nợ đó", "mon no do", "khoản vay đó", "khoan vay do"]
        if any(d in raw or d in raw_unacc for d in debt_refs):
            return True, "debt"

        # 4. Tham chiếu ngân sách
        budget_refs = ["hạn mức đó", "han muc do", "ngân sách đó", "ngan sach do", "hạn mức này", "han muc nay"]
        if any(b in raw or b in raw_unacc for b in budget_refs):
            return True, "budget"

        # 5. Tham chiếu mục tiêu
        goal_refs = ["mục tiêu đó", "muc tieu do", "mục tiêu này", "muc tieu nay", "kế hoạch đó", "ke hoach do"]
        if any(g in raw or g in raw_unacc for g in goal_refs):
            return True, "saving_goal"

        return False, None

    @classmethod
    def is_conditional_statement(cls, text: str) -> Tuple[bool, str]:
        """Nhận diện câu điều kiện ('nếu... thì...').
        Phân biệt giữa:
        - 'read_only': Tra cứu dữ liệu có điều kiện, ví dụ: 'Nếu ví MoMo còn dưới 500k thì báo ta'
        - 'mixed_write': Đọc dữ liệu rồi nếu thỏa mãn điều kiện mới thực thi ghi (mutation), ví dụ: 'Xem hạn mức ăn uống còn bao nhiêu, nếu dưới 500k thì tăng lên 2 triệu'
        """
        raw = text.lower().strip()
        raw_unacc = remove_accents(raw)

        if not re.search(r"\b(nếu|neu|hễ|giả sử|gia su)\b", raw):
            return False, ""

        # Kiểm tra xem có mệnh đề biến động dữ liệu (write/mutation) sau điều kiện không
        write_triggers = [
            "thì tăng", "thi tang", "thì giảm", "thi giam", "thì đổi", "thi doi",
            "thì sửa", "thi sua", "thì chuyển", "thi chuyen", "thì nạp", "thi nap",
            "thì trừ", "thi tru", "thì cộng", "thi cong", "thì thêm", "thi them",
            "thì xóa", "thi xoa", "tăng lên", "tang len", "giảm xuống", "giam xuong",
            "đặt thành", "dat thanh", "nâng lên", "nang len"
        ]
        if any(w in raw or w in raw_unacc for w in write_triggers):
            return True, "mixed_write"

        return True, "read_only"


    @classmethod
    def extract_person_name(cls, text: str) -> Optional[str]:
        """Trích xuất tên đối tác từ câu vay mượn / nợ (ví dụ: 'Cho Tuấn vay 2 triệu', 'Vay của Nam 500k', 'Cho tôi thêm một khoản nợ 5 triệu cho anh A')"""
        clean = text.strip()

        # 1. 'Cho [Tên] vay/mượn' (e.g. 'Cho Tuấn vay 2 triệu', 'Cho anh Nam mượn 500k')
        m_cho = re.search(r"^cho\s+([A-ZÀ-Ỹa-zà-ỹ0-9_ ]+?)\s+(?:vay|mượn)\b", clean, re.IGNORECASE)
        if m_cho:
            cand = m_cho.group(1).strip()
            if cand.lower() not in ["tôi", "ta", "mình"] and len(cand) >= 2:
                return cand.title()

        # 2. '[Tên] vay/mượn [tôi/ta]' (e.g. 'Anh Minh vay tôi 10 triệu')
        m_sub = re.search(r"^([A-ZÀ-Ỹa-zà-ỹ0-9_ ]+?)\s+(?:vay|mượn)\s+(?:tôi|ta|mình)\b", clean, re.IGNORECASE)
        if m_sub:
            cand = m_sub.group(1).strip()
            if cand.lower() not in ["tôi", "ta", "mình"] and len(cand) >= 2:
                return cand.title()

        # 3. 'Tôi/ta/mình nợ [Tên] [số tiền]' (e.g. 'Tôi nợ anh Hùng 2 triệu')
        m_no = re.search(r"^(?:tôi|ta|mình)\s+nợ\s+([A-ZÀ-Ỹa-zà-ỹ_ ]+?)(?:\s+\d+|\s+số tiền|$)", clean, re.IGNORECASE)
        if m_no:
            cand = m_no.group(1).strip()
            if cand.lower() not in ["tôi", "ta", "mình", "ai"] and len(cand) >= 2:
                return cand.title()

        # 4. Giới từ + tên ở đuôi: '... cho anh A', '... từ chị Hoa', '... của Nam', '... với anh Ba'
        m_prep = re.search(r"(?:cho|từ|của|với|bởi|đối tác)\s+([A-ZÀ-Ỹa-zà-ỹ_ ]+?)(?:\s+(?:nha|nhé|đi|giúp|với|ạ)|[.,!?]|$)", clean, re.IGNORECASE)
        if m_prep:
            start_idx = m_prep.start()
            if start_idx == 0 and clean.lower().startswith(("cho tôi", "cho ta", "cho mình")):
                second_matches = list(re.finditer(r"(?:cho|từ|của|với|bởi|đối tác)\s+([A-ZÀ-Ỹa-zà-ỹ_ ]+?)(?:\s+(?:nha|nhé|đi|giúp|với|ạ)|[.,!?]|$)", clean, re.IGNORECASE))
                if len(second_matches) > 1:
                    cand = second_matches[-1].group(1).strip()
                    if cand.lower() not in ["tôi", "ta", "mình", "người", "bạn", "ai"] and len(cand) >= 2:
                        return cand.title()
            else:
                cand = m_prep.group(1).strip()
                for stop in ["tôi", "ta", "mình", "người", "bạn", "ai", "khoản nợ", "nợ", "khoản vay", "ví"]:
                    if cand.lower() == stop or cand.lower().startswith("một khoản") or cand.lower().startswith("khoản"):
                        cand = None
                        break
                if cand and not re.search(r"\b(?:triệu|tr|nghìn|ngàn|k|tỷ|đồng|đ|vnđ)\b", cand, re.IGNORECASE) and len(cand) >= 2:
                    return cand.title()

        # 5. 'Vay/mượn (của/từ) [Tên] ...'
        m_vay = re.search(r"\b(?:vay|mượn)\s+(?:của|từ)?\s*([A-ZÀ-Ỹa-zà-ỹ_ ]+?)(?:\s+\d+|\s+số tiền|$)", clean, re.IGNORECASE)
        if m_vay:
            cand = m_vay.group(1).strip()
            for stop in ["tôi", "ta", "mình", "tiền", "bạc", "ai"]:
                if cand.lower() == stop:
                    cand = None
                    break
            if cand and len(cand) >= 2:
                return cand.title()

        return None

    @classmethod
    def extract_frequency(cls, text: str) -> str:
        """Trích xuất tần suất định kỳ (weekly / monthly)"""
        raw = text.lower()
        if any(w in raw for w in ["hàng tuần", "mỗi tuần", "từng tuần", "weekly"]):
            return "weekly"
        return "monthly"

    @classmethod
    def extract_target_tab(cls, text: str) -> Optional[str]:
        """Trích xuất tab điều hướng từ câu nói (ví dụ: 'mở sổ nợ', 'sang trang ví')"""
        raw = text.lower()
        if any(w in raw for w in ["sổ nợ", "vay mượn", "công nợ"]):
            return "debts"
        if any(w in raw for w in ["sổ giao dịch", "giao dịch", "lịch sử giao dịch"]):
            return "transactions"
        if any(w in raw for w in ["túi càn khôn", "danh sách ví", "quản lý ví", "các ví"]):
            return "wallets"
        if any(w in raw for w in ["ngân sách", "hạn mức"]):
            return "budgets"
        if any(w in raw for w in ["mục tiêu", "tiết kiệm"]):
            return "goals"
        if any(w in raw for w in ["danh mục"]):
            return "categories"
        if any(w in raw for w in ["hóa đơn", "ocr", "quét"]):
            return "ocr"
        if any(w in raw for w in ["thống kê", "báo cáo", "biểu đồ"]):
            return "stats"
        if any(w in raw for w in ["tổng quan", "trang chủ"]):
            return "dashboard"
        if any(w in raw for w in ["quản trị", "admin", "phân quyền", "chưởng môn"]):
            return "admin"
        return None

    @classmethod
    def is_contextual_reference(cls, text: str) -> bool:
        """Kiểm tra câu nói có chứa các tham chiếu ngữ cảnh tới thao tác hoặc thực thể trước đó.
        Ví dụ: 'vừa rồi', 'khoản vừa rồi', 'giao dịch vừa rồi', 'khoản đó', 'giao dịch đó',
        'nó', 'cái vừa tạo', 'cái vừa ghi', 'vừa làm', 'vừa chuyển', 'ví vừa tạo'...
        """
        raw = text.lower().strip()
        ref_patterns = [
            r"\bvừa\s*(?:rồi|xong|nãy|đây|làm|tạo|ghi|chi|chuyển)\b",
            r"\bvua\s*(?:roi|xong|nay|day|lam|tao|ghi|chi|chuyen)\b",
            r"\bkhoản\s*(?:vừa\s*rồi|đó|này|ấy|vừa\s*ghi|vừa\s*chi)\b",
            r"\bkhoan\s*(?:vua\s*roi|do|nay|ay|vua\s*ghi|vua\s*chi)\b",
            r"\bgiao\s*dịch\s*(?:vừa\s*rồi|đó|này|ấy|vừa\s*tạo|gần\s*nhất)\b",
            r"\bgiao\s*dich\s*(?:vua\s*roi|do|nay|ay|vua\s*tao|gan\s*nhat)\b",
            r"\b(?:nó|no|cái\s*đó|cai\s*do|cái\s*vừa\s*rồi|cai\s*vua\s*roi)\b",
            r"\b(?:mục\s*tiêu\s*đó|ngân\s*sách\s*đó|ví\s*vừa\s*tạo|ví\s*đó)\b"
        ]
        return any(re.search(p, raw) for p in ref_patterns)

    @classmethod
    def is_destructive_intent(cls, text: str) -> bool:
        """Kiểm tra ý định xóa / hủy bỏ / gỡ / loại bỏ thực thể"""
        raw = text.lower().strip()
        destructive_verbs = [
            "xóa", "xoa", "hủy", "huy", "gỡ", "go", "bỏ", "bo", "xóa bỏ", "xoa bo",
            "loại bỏ", "loai bo", "delete", "remove"
        ]
        return any(re.search(rf"\b{re.escape(v)}\b", raw) for v in destructive_verbs)

    @classmethod
    def is_update_intent(cls, text: str) -> bool:
        """Kiểm tra ý định sửa đổi / cập nhật thông tin thực thể"""
        raw = text.lower().strip()
        update_verbs = [
            "sửa", "sua", "đổi", "doi", "cập nhật", "cap nhat", "chỉnh", "chinh",
            "thay đổi", "thay doi", "update", "modify"
        ]
        return any(re.search(rf"\b{re.escape(v)}\b", raw) for v in update_verbs)

    @classmethod
    def extract_selection_index(cls, text: str) -> Optional[int]:
        """Trích xuất số thứ tự lựa chọn (ví dụ: 'ví số 1' -> 1, 'số 2' -> 2, 'cái thứ nhất' -> 1, '1' -> 1)"""
        raw = text.lower().strip()
        m = re.search(r"(?:ví|túi|mục|cái|số|thứ)?\s*(?:số|thứ)?\s*(\d+)\b", raw)
        if m:
            return int(m.group(1))
        words_map = {
            "nhất": 1, "đầu": 1, "đầu tiên": 1, "một": 1,
            "hai": 2, "nhì": 2,
            "ba": 3,
            "bốn": 4, "tư": 4
        }
        for k, v in words_map.items():
            if re.search(rf"\b(?:thứ|số)?\s*{re.escape(k)}\b", raw):
                return v
        return None

    @classmethod
    def is_unrelated_new_intent(cls, text: str, pending_tool: Optional[str] = None) -> bool:
        """Kiểm tra xem câu nói của người dùng có phải là một ý định MỚI KHÔNG LIÊN QUAN tới thao tác đang chờ hay không.
        Ví dụ: Đang chờ xác nhận hoặc tham số chuyển tiền (transfer_money), nhưng người dùng lại nói:
        - 'Hôm nay tôi ăn sáng 50 nghìn' (Intent: create_expense)
        - 'Vừa nhận lương 15 triệu' (Intent: create_income)
        - 'Cho Tuấn vay 2 triệu' (Intent: create_debt)
        - 'Tạo ví mới ACB' (Intent: create_wallet)
        - 'Đặt ngân sách ăn uống 3 triệu' (Intent: create_budget)
        - 'Thêm danh mục Quà tặng' (Intent: create_category)
        - 'Xóa giao dịch vừa rồi' (Intent: delete_transaction)
        - 'Ta hiện có bao nhiêu tiền?' (Intent: read query / financial_overview)
        """
        clean = text.strip()
        raw = clean.lower()

        # 1. Nếu là câu xác nhận, hủy bỏ, hoặc sửa đổi tham số -> KHÔNG phải intent mới
        if cls.is_confirmation(clean) or cls.is_cancellation(clean) or cls.is_modification(clean):
            return False

        # 2. Nếu câu quá ngắn chỉ chứa số tiền hoặc tên ví (ví dụ '1 triệu', 'momo', 'ví 2') -> thường là tham số bổ sung
        words = raw.split()
        if len(words) <= 4:
            amt = cls.parse_amount(clean)
            if amt and len(words) <= 3 and not any(w in raw for w in ["ăn", "uống", "mua", "chi", "lương", "thu", "vay", "nợ", "xăng"]):
                return False
            # Nếu chỉ là tên ví hoặc 'ví số 1'
            if any(w in raw for w in ["momo", "zalopay", "tiền mặt", "vietcombank", "mb bank", "acb", "techcombank", "số 1", "số 2", "ví 1", "ví 2"]):
                return False

        # 3. Kiểm tra các trigger ý định độc lập
        if cls.is_debt_create_intent(clean) and pending_tool != "create_debt":
            return True

        if cls.is_wallet_create_intent(clean) and pending_tool != "create_wallet":
            return True

        if cls.is_budget_write(clean) and pending_tool != "create_budget":
            return True

        if any(kw in raw for kw in ["thêm danh mục", "tạo danh mục"]) and pending_tool != "create_category":
            return True

        # Chi tiêu độc lập (ví dụ: 'hôm nay tôi ăn sáng 50 nghìn', 'mua cafe 35k', 'đổ xăng 50k')
        if any(kw in raw for kw in ["ăn sáng", "ăn trưa", "ăn tối", "uống cafe", "mua sắm", "đổ xăng", "chi tiêu", "tiêu hết", "chi hết"]):
            return True

        # Thu nhập độc lập (ví dụ: 'vừa nhận lương', 'thưởng tết', 'bán đồ được')
        if any(kw in raw for kw in ["nhận lương", "thưởng", "thu nhập", "nhận được tiền"]):
            return True

        # Chuyển tiền độc lập
        fw, tw = cls.extract_transfer_wallets(clean)
        if fw and tw:
            return True
        if any(kw in raw for kw in ["chuyển tiền", "chuyển khoản", "bắn tiền", "chuyển từ", "bắn sang"]) and pending_tool != "transfer_money":
            return True

        # Câu hỏi tra cứu dữ liệu cá nhân hoặc tri thức (ví dụ 'ta có bao nhiêu tiền', 'ngân sách tháng này thế nào', 'xem ngân sách')
        read_intents = [
            "bao nhiêu tiền", "số dư", "hạn mức thế nào", "ngân sách thế nào",
            "xem ngân sách", "ngân sách tháng này", "tình hình ngân sách", "hạn mức",
            "xem báo cáo", "xem tình hình", "kiểm tra ví", "xem sổ nợ", "xem nợ",
            "xem chi tiêu", "chi tiêu tháng này", "tiêu bao nhiêu", "tiêu gì",
            "tiết kiệm được bao nhiêu", "khoản nào bất thường", "so với tháng trước",
            "ví nào", "khoản nợ", "ngân khố"
        ]
        if any(kw in raw for kw in read_intents):
            return True

        return False


