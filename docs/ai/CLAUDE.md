# AI Configuration

> Ngôn ngữ trao đổi: tiếng Việt.

## Context
- Bài test "Developer Assessment: Full-Stack Engineering & Quality Assurance" (FastAPI + PostgreSQL + Redis / React 19 + TanStack Query).
- Nguồn yêu cầu, theo thứ tự ưu tiên:
  1. `README.md`: đề bài, ưu tiên cao nhất.
  2. `templates/SPEC_TEMPLATE.md`: cấu trúc spec 3A.
  3. `templates/TEST_PLAN_TEMPLATE.md`: cấu trúc test plan 2C.
  4. `GUIDE.md`: lệnh chạy, URL, tài khoản demo, API hiện có.
- Khi mâu thuẫn: README thắng; template quyết định cấu trúc tài liệu; GUIDE quyết định lệnh và môi trường.

## Working rules
1. Đọc và hiểu code liên quan trước khi sửa.
2. Trước mỗi bước: nêu file, nội dung sửa, lý do, rồi **chờ người làm đồng ý**.
3. Chỉ làm đúng phạm vi đề yêu cầu, không tự mở rộng.
4. Sau khi sửa: chạy test liên quan, báo kết quả thật (test fail thì nói rõ kèm output).
5. Mỗi lỗi một test ngắn theo style có sẵn; test phải fail trên code cũ và pass sau khi sửa.
6. Ghi log ý chính.

## Decisions
| Vấn đề | Quyết định |
|---|---|
| Truy cập todo của user khác (TC-03 cho phép 403 hoặc 404) | Trả `404 Not Found` cho `GET`/`PUT`/`DELETE /todos/{id}` |
| README cần "expected vs actual", template không có cột Actual | Giữ nguyên cột của template; ghi kết quả thực tế trong cột `Status (Pass/Fail)` |
| Tài khoản test của template không có trong seed | Tạo `user_a@test.com` / `user_b@test.com` qua `POST /api/v1/auth/register` |
| Mã lỗi ngoài danh sách của template (vd. 409) | Được dùng nhưng phải giải thích lý do trong spec |
| Playwright `baseURL` | `http://localhost:3000` (frontend chạy bằng Docker theo GUIDE) |
| Phạm vi Tier 3 | Chỉ thêm một migration |
| Tài liệu nộp | Ngắn gọn, đúng khung template |
| Tier 4 (tuỳ chọn) | Không làm |
