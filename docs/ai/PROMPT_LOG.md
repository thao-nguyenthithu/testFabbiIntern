# AI Prompt Log

> Công cụ: Claude Code (VS Code extension), model Claude Opus 5.5. Cấu hình: [`CLAUDE.md`](CLAUDE.md).

| Phase | Nội dung prompt |
|---|---|
| Planning | "Đóng vai kỹ sư Full-Stack & QA. Phân tích codebase (backend FastAPI, frontend React, Docker), xác định tech stack và luồng chính. Đọc kỹ README, GUIDE, SPEC_TEMPLATE và TEST_PLAN_TEMPLATE: README là ưu tiên cao nhất, template quyết định cấu trúc tài liệu, GUIDE quyết định lệnh chạy. Tìm các lỗi trong code thuộc nhóm authentication, business logic, caching, state management, ghi rõ vị trí và mức độ. Lập kế hoạch làm bài theo từng tier, mỗi mục ghi rõ là yêu cầu của đề hay đề xuất thêm; ghi lại các điểm mâu thuẫn giữa các nguồn và cách xử lý. Không tự sửa code khi chưa được duyệt." |
| Planning | "Khi README và template mâu thuẫn (403 hay 404, test plan không có cột Actual) thì xử lý thế nào?" |
| Phase 0: Setup | "Chạy app bằng Docker, tạo tài khoản user_a/user_b theo template, viết script tái hiện từng lỗi trước khi sửa." |
| Phase 0: Setup | "Lỗi email trùng làm khoá luôn tài khoản (login 500), nâng mức độ lên High." |
| Phase 1: Tier 1 | "Sửa lần lượt từng lỗi, mỗi lỗi kèm một test ngắn theo style có sẵn của repo; test phải fail trước khi sửa và pass sau khi sửa." |
| Phase 1: Tier 1 | "Sau khi bắt buộc token hết hạn, frontend chưa dùng refresh token thì user bị đăng xuất sau 30 phút. Thêm tự refresh token khi gặp 401." |
| Phase 1: Tier 1 | "Kiểm tra hộp đen bản sửa phân quyền: user A gọi GET/PUT/DELETE todo của user B." |
| Phase 1: Tier 1 | "Partial update phải giữ nguyên các field không gửi; kiểm tra cả trường hợp bấm toggle trên UI." |
| Phase 1: Tier 1 | "Phân trang hiển thị sai số trang, kiểm tra lại query key và rollback khi request lỗi." |
| Phase 1: PR | "Viết danh sách lỗi cho mô tả PR theo Location / Severity / Reason / Fix Proposal." |
| Phase 2: 2A | "Chạy pytest theo lệnh của đề và ghi kết quả vào PR." |
| Phase 2: 2B | "Cài Playwright từ đầu, viết kịch bản Full User Journey và Cross-User Data Isolation, chạy cả headless và headed." |
| Phase 2: 2B | "Thêm kịch bản A logout rồi B login cùng trình duyệt; tạm bỏ bản sửa để chứng minh test bắt được lỗi." |
| Phase 2: 2C | "Viết manual test plan theo template, chạy thật từng case và ghi kết quả." |
| Phase 3: 3A | "Viết spec Todo Sharing theo SPEC_TEMPLATE, đủ các ý README yêu cầu." |
| Phase 3: 3A | "README có quy định editor được xoá todo không? Mời trùng và email chưa đăng ký trả mã lỗi gì?" |
| Phase 3: 3B | "Rà soát docker-compose và Dockerfile hiện tại theo 5 tiêu chí của README: healthcheck, .dockerignore, kích thước image, tách dev/prod, bảo mật Redis và secret. Đo kích thước image trước/sau và kiểm tra cold boot." |
| Phase 3: 3B | "Giải thích lợi ích của .dockerignore và multi-stage build so với cấu hình ban đầu." |
| Phase 3: 3C | "Seed 1 triệu todo, chạy EXPLAIN ANALYZE cho các truy vấn lọc theo user, sắp xếp theo created_at và đếm todo trước khi thêm index. Thêm composite index qua Alembic migration, đo lại và phân tích trade-off: tốc độ ghi, dung lượng index, an toàn khi migrate bảng lớn." |
| Phase 5 | "Hoàn thiện mô tả PR theo đủ các mục README yêu cầu. Đưa danh sách commit theo thứ tự, mỗi commit một nhóm thay đổi, đúng Conventional Commits và .commitlintrc.json." |
