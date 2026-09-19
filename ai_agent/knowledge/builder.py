"""
Knowledge Base Index Builder — Càn Khôn Linh Thạch Các
Idempotent script to extract, normalize, chunk, and index system knowledge.
"""

import json
import os
import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Any


def remove_accents(text: str) -> str:
    """Loại bỏ dấu tiếng Việt để phục vụ so khớp không dấu"""
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    return text.replace('đ', 'd').replace('Đ', 'D')


def tokenize(text: str) -> List[str]:
    """Tokenize văn bản tiếng Việt thành mảng từ đơn và từ ghép chuẩn hóa"""
    clean = re.sub(r'[^\w\s]', ' ', text.lower())
    tokens = clean.split()
    return [t for t in tokens if len(t) > 1]


class KnowledgeBuilder:
    def __init__(self, base_dir: Path = None):
        if base_dir is None:
            self.base_dir = Path(__file__).resolve().parent
        else:
            self.base_dir = Path(base_dir)
        self.capabilities_file = self.base_dir / "capabilities.json"
        self.docs_dir = self.base_dir / "docs"
        self.index_file = self.base_dir / "index.json"

    def build_index(self) -> Dict[str, Any]:
        """Tạo chỉ mục tìm kiếm chuẩn hóa từ capabilities và tài liệu markdown"""
        chunks: List[Dict[str, Any]] = []

        # 1. Parse Capabilities Inventory
        capabilities_data = {}
        if self.capabilities_file.exists():
            with open(self.capabilities_file, "r", encoding="utf-8") as f:
                cap_json = json.load(f)
                capabilities_data = {c["id"]: c for c in cap_json.get("capabilities", [])}

        for cap_id, cap in capabilities_data.items():
            cap_text = (
                f"{cap.get('vietnamese_name', '')} ({cap.get('name', '')}). "
                f"Mục đích: {cap.get('purpose', '')}. "
                f"Vị trí giao diện: {cap.get('UI_location', '')}. "
                f"Thao tác khả dụng: {', '.join(cap.get('available_actions', []))}. "
                f"Quy trình sử dụng: {cap.get('user_workflow', '')}. "
                f"Giới hạn: {cap.get('limitations', '')}. "
                f"Trạng thái: {cap.get('status', 'ACTIVE')}."
            )
            chunks.append({
                "chunk_id": f"cap_{cap_id}",
                "doc_id": cap_id,
                "category": cap.get("category", "FEATURE"),
                "capability": cap_id,
                "title": f"Năng Lực: {cap.get('vietnamese_name', cap.get('name', ''))}",
                "status": cap.get("status", "ACTIVE"),
                "content": cap_text,
                "tokens": tokenize(cap_text),
                "unaccented_tokens": tokenize(remove_accents(cap_text)),
                "source_file": "capabilities.json"
            })

        # 2. Parse Markdown Docs
        if self.docs_dir.exists():
            for md_file in self.docs_dir.rglob("*.md"):
                category = md_file.parent.name
                doc_name = md_file.stem
                try:
                    with open(md_file, "r", encoding="utf-8") as f:
                        raw_content = f.read()
                except Exception:
                    continue

                # Tách văn bản thành các section dựa trên header ##
                sections = re.split(r'\n(?=##\s+)', raw_content)
                doc_title = md_file.stem.replace("_", " ").title()
                if sections and sections[0].startswith("# "):
                    first_lines = sections[0].split("\n")
                    doc_title = first_lines[0].replace("#", "").strip()

                for idx, sec in enumerate(sections):
                    sec_clean = sec.strip()
                    if not sec_clean:
                        continue

                    sec_lines = sec_clean.split("\n")
                    sec_title = doc_title
                    if sec_lines and (sec_lines[0].startswith("##") or sec_lines[0].startswith("#")):
                        sec_title = sec_lines[0].replace("#", "").strip()

                    status = "ACTIVE"
                    if "chưa hỗ trợ" in sec_clean.lower() or "planned" in sec_clean.lower() or "unsupported" in doc_name.lower():
                        status = "PLANNED"

                    chunk_id = f"doc_{category.lower()}_{doc_name}_{idx}"
                    chunks.append({
                        "chunk_id": chunk_id,
                        "doc_id": f"{category.lower()}_{doc_name}",
                        "category": category,
                        "capability": doc_name,
                        "title": f"{doc_title} - {sec_title}",
                        "status": status,
                        "content": sec_clean,
                        "tokens": tokenize(sec_clean),
                        "unaccented_tokens": tokenize(remove_accents(sec_clean)),
                        "source_file": f"docs/{category}/{md_file.name}"
                    })

        index_data = {
            "version": "1.0",
            "total_chunks": len(chunks),
            "chunks": chunks
        }

        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

        return index_data


if __name__ == "__main__":
    builder = KnowledgeBuilder()
    res = builder.build_index()
    print(f"Successfully indexed {res['total_chunks']} chunks into {builder.index_file}")
