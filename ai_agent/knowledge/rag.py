"""
Knowledge RAG Engine — Càn Khôn Linh Thạch Các
Triển khai hệ thống Retrieval-Augmented Generation (RAG) thực sự cho Khí Linh AI Lớn:
- Hybrid Search (BM25 / Token Overlap / Unaccented & Accented / Title & Keyword Boost)
- Relevance Filtering & Unknown Detection (Không bao giờ hallucinate)
- Grounded Context Assembly & Traceability Metadata
- Phân biệt rõ Active vs Planned/Unsupported
"""

import json
import math
import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from .builder import KnowledgeBuilder, remove_accents, tokenize


class RetrievalResult:
    def __init__(self, chunk: Dict[str, Any], score: float):
        self.chunk = chunk
        self.score = score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk["chunk_id"],
            "title": self.chunk["title"],
            "category": self.chunk["category"],
            "capability": self.chunk["capability"],
            "status": self.chunk["status"],
            "source_file": self.chunk["source_file"],
            "score": round(self.score, 4),
            "content": self.chunk["content"]
        }


class KnowledgeRAG:
    """Động cơ truy xuất và sinh phản hồi tri thức hệ thống (System Knowledge RAG)"""

    def __init__(self, knowledge_dir: Optional[Path] = None):
        if knowledge_dir is None:
            self.knowledge_dir = Path(__file__).resolve().parent
        else:
            self.knowledge_dir = Path(knowledge_dir)

        self.index_file = self.knowledge_dir / "index.json"
        self.capabilities_file = self.knowledge_dir / "capabilities.json"
        self._chunks: List[Dict[str, Any]] = []
        self._idf: Dict[str, float] = {}
        self._capabilities_map: Dict[str, Any] = {}
        self.load_or_build_index()

    def load_or_build_index(self):
        """Tải chỉ mục tìm kiếm hoặc tự động build nếu chưa có"""
        if not self.index_file.exists():
            builder = KnowledgeBuilder(self.knowledge_dir)
            builder.build_index()

        with open(self.index_file, "r", encoding="utf-8") as f:
            index_data = json.load(f)
            self._chunks = index_data.get("chunks", [])

        if self.capabilities_file.exists():
            with open(self.capabilities_file, "r", encoding="utf-8") as f:
                cap_json = json.load(f)
                self._capabilities_map = {c["id"]: c for c in cap_json.get("capabilities", [])}

        # Tính toán IDF cho BM25
        doc_count = len(self._chunks)
        df: Dict[str, int] = {}
        for c in self._chunks:
            unique_terms = set(c["tokens"] + c["unaccented_tokens"])
            for t in unique_terms:
                df[t] = df.get(t, 0) + 1

        self._idf = {}
        for t, count in df.items():
            self._idf[t] = math.log((doc_count - count + 0.5) / (count + 0.5) + 1.0)

    def retrieve(self, query: str, top_k: int = 4, threshold: float = 0.35, recent_history: str = "") -> List[RetrievalResult]:
        """Truy xuất các đoạn tri thức có độ liên quan cao nhất (hỗ trợ phân giải ngữ cảnh follow-up từ recent_history)"""
        clean_q = query.strip()
        q_tokens = tokenize(clean_q)
        q_unacc = tokenize(remove_accents(clean_q))
        q_all = set(q_tokens + q_unacc)

        # Hỗ trợ phân giải ngữ cảnh hội thoại (Contextual Reference Resolution)
        raw_lower = clean_q.lower()
        followup_triggers = ["kỹ hơn", "ky hon", "rõ hơn", "ro hon", "chi tiết", "nó", "cái này", "cái đó", "còn cái", "thế nào", "làm gì"]
        is_followup = any(t in raw_lower for t in followup_triggers) or len(q_tokens) <= 4

        if is_followup and recent_history:
            # Ưu tiên trích xuất từ câu hỏi của người dùng trong lịch sử (dòng bắt đầu bằng 'Đạo hữu:' hoặc 'User:')
            user_hist_lines = [
                line.split(":", 1)[1] for line in recent_history.splitlines()
                if any(line.strip().lower().startswith(p) for p in ["đạo hữu:", "user:", "người dùng:"])
            ]
            user_hist_text = " ".join(user_hist_lines) if user_hist_lines else recent_history
            user_hist_lower = user_hist_text.lower()
            user_hist_unacc = remove_accents(user_hist_lower)

            # Thêm các keyword quan trọng từ câu hỏi trước của user vào context truy xuất
            for kw in ["túi càn khôn", "ví", "ngân sách", "hạn mức", "mục tiêu", "tiết kiệm", "sổ nợ", "nợ", "ocr", "hóa đơn", "giao dịch", "định kỳ", "chuyển tiền"]:
                if kw in user_hist_lower or remove_accents(kw) in user_hist_unacc:
                    q_all.update(tokenize(kw))
                    q_all.update(tokenize(remove_accents(kw)))
                    raw_lower += f" {kw}"

        if not q_all or not self._chunks:
            return []

        scores: List[Tuple[Dict[str, Any], float]] = []

        # Các từ khóa tăng cường (Entity Boosting)
        boost_map = {
            "hệ thống": ["system_overview", "cap_dashboard", "cap_large_khi_linh", "capabilities"],
            "chức năng": ["system_overview", "capabilities"],
            "tính năng": ["system_overview", "capabilities"],
            "túi càn khôn": ["wallets_tui_can_khon", "cap_wallets", "how_to_create_wallet"],
            "ví": ["wallets_tui_can_khon", "cap_wallets", "how_to_create_wallet"],
            "tạo ví": ["how_to_create_wallet", "wallets_tui_can_khon", "cap_wallets"],
            "thêm ví": ["how_to_create_wallet", "wallets_tui_can_khon", "cap_wallets"],
            "ngân hàng": ["wallets_tui_can_khon", "cap_wallets"],
            "tài khoản ngân hàng": ["wallets_tui_can_khon", "cap_wallets"],
            "nhiều tài khoản": ["wallets_tui_can_khon", "cap_wallets"],
            "chuyển tiền": ["wallets_tui_can_khon", "financial_workflows", "how_to_transfer_money"],
            "chuyển khoản": ["wallets_tui_can_khon", "financial_workflows", "how_to_transfer_money"],
            "giao dịch": ["transactions", "cap_transactions", "how_to_add_transaction"],
            "ngân sách": ["budgets", "cap_budgets"],
            "hạn mức": ["budgets", "cap_budgets"],
            "sổ nợ": ["debts", "cap_debts", "how_to_manage_debts"],
            "khoản nợ": ["debts", "cap_debts", "how_to_manage_debts"],
            "quản lý nợ": ["debts", "cap_debts", "how_to_manage_debts"],
            "nợ": ["debts", "cap_debts", "how_to_manage_debts"],
            "cho vay": ["debts", "cap_debts", "how_to_manage_debts"],
            "đi vay": ["debts", "cap_debts", "how_to_manage_debts"],
            "tất toán": ["debts", "cap_debts", "how_to_manage_debts"],
            "quyết toán": ["debts", "cap_debts", "how_to_manage_debts"],
            "mục tiêu": ["saving_goals", "cap_saving_goals"],
            "tiết kiệm": ["saving_goals", "cap_saving_goals", "saving_tips", "cap_saving_tips"],
            "định kỳ": ["recurring", "cap_recurring", "how_to_setup_recurring"],
            "giao dịch định kỳ": ["recurring", "cap_recurring", "how_to_setup_recurring"],
            "linh trận định kỳ": ["recurring", "cap_recurring", "how_to_setup_recurring"],
            "linh trận": ["recurring", "cap_recurring", "how_to_setup_recurring"],
            "ocr": ["ocr_invoice", "cap_ocr", "how_to_use_ocr"],
            "hóa đơn": ["ocr_invoice", "cap_ocr", "how_to_use_ocr"],
            "quét hóa đơn": ["ocr_invoice", "cap_ocr", "how_to_use_ocr"],
            "linh nhãn": ["ocr_invoice", "cap_ocr", "how_to_use_ocr"],
            "danh mục": ["categories", "cap_categories"],
            "khai thị": ["saving_tips", "cap_saving_tips"],
            "thống kê": ["reports_stats", "cap_reports"],
            "báo cáo": ["reports_stats", "cap_reports"],
            "xuất excel": ["reports_stats", "transactions", "cap_reports"],
            "xuất csv": ["reports_stats", "transactions", "cap_reports"],
            "khí linh": ["khi_linh_architecture", "cap_large_khi_linh", "cap_small_khi_linh"],
            "khí linh lớn": ["khi_linh_architecture", "cap_large_khi_linh"],
            "khí linh ai lớn": ["khi_linh_architecture", "cap_large_khi_linh"],
            "khí linh nhỏ": ["khi_linh_architecture", "cap_small_khi_linh"],
            "live": ["khi_linh_architecture", "cap_small_khi_linh"],
            "bảo mật": ["security_and_permissions", "cap_security_auth"],
            "hồn đăng": ["security_and_permissions", "cap_security_auth"],
            "bản mệnh hồn đăng": ["security_and_permissions", "cap_security_auth"],
            "phân quyền": ["security_and_permissions", "cap_security_auth", "admin_portal", "cap_admin"],
            "chưởng môn": ["admin_portal", "cap_admin"],
            "chưởng môn các": ["admin_portal", "cap_admin"],
            "admin": ["admin_portal", "cap_admin"],
            "quyền": ["security_and_permissions", "khi_linh_architecture", "limitations_and_unsupported"],
            "cổ phiếu": ["limitations_and_unsupported", "cap_stock_trading"],
            "chứng khoán": ["limitations_and_unsupported", "cap_stock_trading"],
            "crypto": ["limitations_and_unsupported", "cap_crypto_wallet"],
            "tiền mã hóa": ["limitations_and_unsupported", "cap_crypto_wallet"],
            "tiền ảo": ["limitations_and_unsupported", "cap_crypto_wallet"],
            "bitcoin": ["limitations_and_unsupported", "cap_crypto_wallet"],
            "vàng": ["limitations_and_unsupported"],
            "forex": ["limitations_and_unsupported"],
            "ngoại hối": ["limitations_and_unsupported"],
            "thẻ tín dụng": ["limitations_and_unsupported"],
            "cà thẻ": ["limitations_and_unsupported"],
            "bill": ["ocr_invoice", "cap_ocr", "how_to_use_ocr"],
            "quét bill": ["ocr_invoice", "cap_ocr", "how_to_use_ocr"],
            "khí linh bự": ["khi_linh_architecture", "cap_large_khi_linh"],
            "khí linh to": ["khi_linh_architecture", "cap_large_khi_linh"],
            "chi rứa": ["system_overview", "cap_dashboard", "capabilities"],
            "mần răng": ["debts", "how_to_manage_debts", "cap_debts"],
            "rag": ["common_questions", "khi_linh_architecture"]
        }

        # Tìm các boost target cho câu hỏi hiện tại
        active_boosts = []
        for kw, targets in boost_map.items():
            if kw in raw_lower or remove_accents(kw) in remove_accents(raw_lower):
                active_boosts.extend(targets)

        for chunk in self._chunks:
            chunk_tokens = set(chunk["tokens"] + chunk["unaccented_tokens"])
            if not chunk_tokens:
                continue

            # 1. Điểm BM25 cơ bản
            score = 0.0
            overlap = 0
            for term in q_all:
                if term in chunk_tokens:
                    overlap += 1
                    idf_val = self._idf.get(term, 1.0)
                    score += idf_val

            if overlap == 0:
                continue

            # 2. Điều chỉnh theo tỷ lệ bao phủ từ khóa
            coverage = overlap / len(q_all)
            score = score * (1.0 + coverage)

            # 3. Thưởng điểm Title & Capability Boost
            title_lower = chunk["title"].lower()
            cap_id = chunk["capability"].lower()
            doc_id = chunk["doc_id"].lower()

            for b in active_boosts:
                if b.lower() in cap_id or b.lower() in doc_id or b.lower() in title_lower:
                    score += 5.0

            # Thưởng điểm nếu truy vấn tổng quan khớp tài liệu system_overview / capability
            if any(k in raw_lower for k in ["chức năng nào", "những chức năng", "toàn bộ chức năng", "có gì", "tính năng nào"]):
                if not any(specific in raw_lower for specific in ["khoản nợ", "nợ", "chuyển tiền", "tạo ví", "định kỳ", "hóa đơn", "ocr", "ngân hàng"]):
                    if "system_overview" in doc_id or "cap_dashboard" in cap_id or "capabilities.json" in chunk["source_file"]:
                        score += 10.0

            scores.append((chunk, score))

        # Sắp xếp theo điểm giảm dần
        scores.sort(key=lambda x: x[1], reverse=True)

        # Lọc theo threshold và lấy top_k
        results: List[RetrievalResult] = []
        for c, s in scores[:top_k]:
            if s >= threshold:
                results.append(RetrievalResult(c, s))

        return results

    def is_unknown_query(self, query: str, retrieved_results: List[RetrievalResult]) -> bool:
        """Kiểm tra xem câu hỏi có đang hỏi về một tính năng không được hỗ trợ trong hệ thống không"""
        raw_lower = query.lower()
        raw_unacc = remove_accents(raw_lower)

        # 1. Các từ khóa tính năng ngoại lai rõ ràng không hỗ trợ
        unsupported_keywords = [
            "cổ phiếu", "chứng khoán", "chứng khoán tự động", "chay cổ phiếu", "đầu tư cổ phiếu",
            "crypto", "tiền mã hóa", "tiền mã hoá", "tiền điện tử", "tiền ảo", "bitcoin", "blockchain",
            "đầu tư vàng", "vàng", "ngoại hối", "forex", "thẻ tín dụng", "cà thẻ", "quẹt thẻ"
        ]
        for kw in unsupported_keywords:
            if kw in raw_lower or remove_accents(kw) in raw_unacc:
                return True

        # 2. Nếu không có bất kỳ chunk nào vượt qua threshold
        if not retrieved_results:
            return True

        # 3. Nếu top chunk có điểm quá thấp (< 0.6) đối với câu hỏi xác nhận có/không
        if retrieved_results and retrieved_results[0].score < 0.6 and any(w in raw_lower for w in ["hệ thống có", "có hỗ trợ", "có tính năng"]):
            return True

        return False

    def build_grounded_prompt(self, query: str, retrieved_results: List[RetrievalResult], recent_history: str = "") -> str:
        """Tạo system prompt giàu ngữ cảnh được kiểm chứng từ kết quả RAG"""
        context_blocks = []
        for idx, res in enumerate(retrieved_results, 1):
            status_tag = f"[{res.chunk['status']}]"
            context_blocks.append(
                f"--- Nguồn {idx}: {res.chunk['title']} (File: {res.chunk['source_file']}) {status_tag} ---\n"
                f"{res.chunk['content']}\n"
            )

        context_text = "\n".join(context_blocks)

        prompt = f"""Bạn là "Khí Linh AI Lớn" — Trợ Lý Tri Thức Toàn Hệ Thống (System Knowledge Assistant) của Càn Khôn Linh Thạch Các.

QUY TẮC CỐT LÕI BẮT BUỘC:
1. Bạn là trợ lý tri thức chuyên sâu, nắm rõ toàn bộ năng lực thực tế của hệ thống Càn Khôn Linh Thạch Các.
2. Trả lời chi tiết, mạch lạc, chính xác, có cấu trúc rõ ràng dựa trên các TÀI LIỆU NGUỒN được cung cấp bên dưới.
3. TUYỆT ĐỐI KHÔNG BỊA ĐẶT chức năng chưa tồn tại. Nếu trong tài liệu nguồn thể hiện tính năng chưa hỗ trợ (PLANNED / Chưa hỗ trợ), hãy khẳng định rõ ràng là hệ thống hiện CHƯA hỗ trợ tính năng này.
4. Đối với câu hỏi tổng quan "Hệ thống có những chức năng nào?": Hãy liệt kê đầy đủ các chức năng ACTIVE (Tổng Quan, Túi Càn Khôn, Giao Dịch, Danh Mục, Hạn Mức / Ngân Sách, Sổ Nợ, Mục Tiêu Tiết Kiệm, Giao Dịch Định Kỳ, OCR Hóa Đơn, Thống Kê & Báo Cáo, Khai Thị Tiết Kiệm, Bản Mệnh Hồn Đăng/Bảo Mật, Khí Linh Lớn & Nhỏ). Nhóm theo các trụ cột tài chính rõ ràng.
5. Đối với câu hỏi về vai trò/quyền hạn: Khẳng định rõ Khí Linh AI Lớn là Knowledge Assistant (chỉ giải đáp, hướng dẫn, tra cứu dữ liệu chỉ đọc, KHÔNG CÓ QUYỀN thay đổi dữ liệu tài chính); còn Khí Linh Nhỏ (Live System Mode) là Action Agent mới có quyền thực thi.
6. Khi giải thích khái niệm chung không thuộc riêng hệ thống (ví dụ "RAG là gì?"): Trình bày định nghĩa khái quát chung trước, sau đó phân biệt rõ cách hệ thống Càn Khôn áp dụng.

TÀI LIỆU NGUỒN TRI THỨC (RETRIEVED CONTEXT):
{context_text}

{recent_history}
CÂU HỎI CỦA ĐẠO HỮU: {query}

HÃY TRẢ LỜI ĐẦY ĐỦ, CHÍNH XÁC VÀ BÁM SÁT TÀI LIỆU TRÊN:"""
        return prompt

    async def answer_question(self, query: str, provider, recent_history: str = "") -> Tuple[str, List[Dict[str, Any]]]:
        """Quy trình RAG hoàn chỉnh: Truy xuất -> Lọc độ liên quan -> LLM Grounded Answer"""
        retrieved = self.retrieve(query, top_k=4, recent_history=recent_history)

        # 1. Xử lý câu hỏi về chức năng ngoài phạm vi / chưa hỗ trợ
        if self.is_unknown_query(query, retrieved):
            q_low = query.lower()
            if any(w in q_low for w in ["cổ phiếu", "chứng khoán"]):
                ans = (
                    "Hiện tại, Càn Khôn Linh Thạch Các **CHƯA hỗ trợ** tính năng giao dịch chứng khoán hay cổ phiếu tự động. "
                    "Hệ thống hiện tập trung tối ưu cho việc quản lý tài chính cá nhân toàn diện (thu chi, hạn mức ngân sách, "
                    "sổ nợ, mục tiêu tiết kiệm, hóa đơn OCR và đa ví tài sản)."
                )
                return ans, [r.to_dict() for r in retrieved]

            if any(w in q_low for w in ["crypto", "tiền mã hóa", "tiền mã hoá", "tiền ảo", "bitcoin"]):
                ans = (
                    "Hiện tại, Càn Khôn Linh Thạch Các **CHƯA hỗ trợ** tích hợp ví Bitcoin, tiền mã hóa (crypto), blockchain hay Web3. "
                    "Hệ thống hiện hỗ trợ quản lý các nguồn tiền truyền thống (tiền mặt, nhiều tài khoản ngân hàng, ví điện tử Momo/ZaloPay và sổ tiết kiệm)."
                )
                return ans, [r.to_dict() for r in retrieved]

            if any(w in q_low for w in ["vàng", "ngoại hối", "forex"]):
                ans = (
                    "Hiện tại, Càn Khôn Linh Thạch Các **CHƯA hỗ trợ** tính năng đầu tư vàng hay giao dịch ngoại hối Forex. "
                    "Hệ thống hiện tập trung tối ưu cho việc quản lý tài chính cá nhân, đa ví tài sản, ngân sách, sổ nợ và tiết kiệm."
                )
                return ans, [r.to_dict() for r in retrieved]

            if any(w in q_low for w in ["thẻ tín dụng", "cà thẻ", "quẹt thẻ"]):
                ans = (
                    "Hiện tại, Càn Khôn Linh Thạch Các **CHƯA hỗ trợ** liên kết thẻ tín dụng quốc tế để tự động cà thẻ hay trừ tiền tự động. "
                    "Mọi giao dịch chi tiêu qua thẻ do người dùng tự ghi nhận thủ công hoặc quét hóa đơn qua Linh Nhãn OCR."
                )
                return ans, [r.to_dict() for r in retrieved]

            if not retrieved:
                ans = (
                    "Khí Linh chưa tìm thấy thông tin đáng tin cậy trong kiến thức hiện tại của hệ thống về vấn đề này. "
                    "Đạo hữu có thể hỏi về các tính năng hiện có của Càn Khôn Linh Thạch Các như Túi Càn Khôn, Giao Dịch, "
                    "Hạn Mức Ngân Sách, Sổ Nợ, Mục Tiêu Tiết Kiệm hoặc Khám Hóa Đơn OCR."
                )
                return ans, []

        # 2. Xây dựng prompt có căn cứ và gọi provider
        prompt = self.build_grounded_prompt(query, retrieved, recent_history)
        answer = await provider.generate_response(prompt)
        trace_metadata = [r.to_dict() for r in retrieved]
        return answer.strip(), trace_metadata
