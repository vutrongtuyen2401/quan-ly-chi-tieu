# Cài bộ Antigravity Developer System

## Cách dùng

1. Giải nén thư mục `.agents` vào thư mục gốc project.
2. Giữ `AI_PROJECT_CONTEXT.md` và `ROADMAP.md` ở thư mục gốc project hiện tại.
3. Giữ nguyên `AGENTS.md` và `.specify` của project.
4. Mở lại workspace trong Antigravity.

## Cách giao việc sau khi cài

Thay vì prompt dài, có thể dùng:

- `/feature` nếu bạn đã tạo workflow tương ứng, hoặc nói: "Implement feature..."
- "Fix bug..."
- "Audit security..."
- "Verify regression..."

Agent phải tuân thủ `.agents/AGENT_DEVELOPMENT_PROTOCOL.md`.

## Lưu ý

Bộ này cố tình không tự động thay thế AGENTS.md hiện tại và không chứa secret.
Không bật quyền thao tác phá huỷ/production một cách không kiểm soát.

## Khuyến nghị

Trước task lớn, commit/checkpoint Git để có điểm quay lại.
