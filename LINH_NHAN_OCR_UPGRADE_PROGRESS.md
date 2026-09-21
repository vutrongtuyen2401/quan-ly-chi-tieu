# LINH NHÃN — OCR INTELLIGENCE UPGRADE PROGRESS

## Current Phase: Phase 1 — Implementation & Architecture Upgrade

### Checkpoint Overview
- **Objective**: Multi-layout receipt recognition, normalized receipt schema, editable line items without auto-calculation, receipt total as single source of truth, one receipt creates exactly one expense transaction, multi-strategy fallback, truthful failure (HTTP 422 Strict).
- **Files to Change**:
  - `ai_agent/ocr_engine.py` (NEW): Core OCR intelligence engine, multi-strategy vision prompts, number & date normalizers, semantic validator.
  - `main.py` (MODIFY): Integrate OCR engine into `/api/ai/scan-invoice`, update `validate_ocr_response` with backward compatibility.
  - `frontend/src/components/ocr/OcrView.vue` (MODIFY): Interactive line item editor (quantity, unit_price, line_total, total), no auto-recalculation, discrepancy alert.
  - `frontend/src/App.vue` (MODIFY): Handle normalized OCR response schema and ensure single expense transaction creation flow.
  - `test_ocr_intelligence.py` (NEW): Test suite covering karaoke receipt, clothing receipt, multiline item, number parsing, total ground truth, single transaction assertion.
- **Root Causes Identified**:
  1. Brittle `store_name` validation in `validate_ocr_response` rejecting receipts with null/missing merchant.
  2. Strict ISO date check crashing on Vietnamese date formats (`DD/MM/YYYY`).
  3. Inability to parse Vietnamese number formatting (`4.030.000`, `4,030,000`, `4.030.000 đ`).
  4. Minimalist 7-line prompt giving zero semantic guidance on varied column layouts.
  5. Lack of multi-strategy fallback when first vision call outputs non-standard JSON.
  6. Read-only UI in `OcrView.vue` with dynamic `quantity * price` auto-calculation instead of editable line items.

### Strategy Implementation Plan
- Strategy A: Semantic Multi-Layout Extraction (Karaoke, clothing, retail, F&B, phone screenshot).
- Strategy B: Targeted Receipt Fallback (Focus on table rows and grand total anchor).
- Validation: Total > 0, items list, store name (optional/null), receipt date (normalized ISO or null).
- Ground Truth: Receipt Total printed on bill is immutable source of truth; never overwrite with sum of items.

### Status Tracker
- [x] Audit implementation & identify root causes
- [x] Create implementation plan & obtain approval
- [ ] Create `ai_agent/ocr_engine.py`
- [ ] Update `main.py` endpoint & validation
- [ ] Update `OcrView.vue` editable line items & total
- [ ] Update `App.vue` OCR state handling
- [ ] Create `test_ocr_intelligence.py` & verify automated tests
- [ ] Run regression test suite (`test_suite.py`, `test_conversational_financial_ai.py`)
- [ ] Validate frontend build (`npm run build`)
- [ ] Browser E2E verification
- [ ] Final Walkthrough & Report
