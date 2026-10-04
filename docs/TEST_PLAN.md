# Manual Test Plan: Regression các bug đã sửa

## 1. Scope & Objective
- Mục tiêu kiểm thử: Xác thực các tính năng hiện có và kiểm tra hồi quy (regression) các bug đã được sửa.
- Phạm vi kiểm thử: Authentication, Todo CRUD, Authorization, Caching.

## 2. Test Environment & Prerequisites
- Base URL Backend: `http://localhost:8000`
- Base URL Frontend: `http://localhost:3000`
- Pre-seeded Test Accounts (tạo trước bằng `POST /api/v1/auth/register`, vì seed không tạo sẵn):
  - Account 1 (User A): `user_a@test.com` / `Password@123`
  - Account 2 (User B): `user_b@test.com` / `Password@123`

## 3. Test Cases Matrix

| TC ID | Module / Feature | Test Scenario | Preconditions | Test Steps | Expected Result | Priority / Severity | Status (Pass/Fail) |
|---|---|---|---|---|---|---|---|
| TC-01 | Auth | Login thành công với mật khẩu đúng | User đã đăng ký | 1. Nhập email/pass đúng<br>2. Bấm Login | Trả về token, chuyển hướng vào Todo page | High / Blocker | Pass |
| TC-02 | Auth | Login thất bại với mật khẩu sai (Tránh User Enumeration) | User đã đăng ký | 1. Nhập email đúng, pass sai<br>2. Bấm Login | Báo lỗi chung "Invalid email or password" (HTTP 401) | Medium / Security | Pass |
| TC-03 | Todo Security | User A không thể sửa Todo của User B | User A & B đã login | 1. User B tạo todo ID X<br>2. User A gọi PUT /todos/X | Trả về 404 Not Found | High / Critical | Pass |
| TC-04 | Todo Logic | Đổi trạng thái todo hoàn thành sang chưa hoàn thành | Todo đang completed | 1. Bấm checkbox bỏ completed<br>2. Refresh trang | Todo vẫn ở trạng thái incomplete (completed = false) | Medium / Major | Pass |
| TC-05 | Cache | Cập nhật Todo xóa cache lập tức | Todo đã được cache | 1. Sửa title Todo<br>2. F5 hoặc gọi GET /todos | Hiển thị title mới, không nhận cache cũ | Medium / Major | Pass |
| TC-06 | Auth | Access token hết hạn bị từ chối | Có access token đã hết hạn | 1. Gọi GET /auth/me với token hết hạn | 401 | High / Critical | Pass |
| TC-07 | Auth | Refresh token không dùng thay access token được | User A đã login | 1. Gọi GET /todos với refresh token | 401 | High / Critical | Pass |
| TC-08 | Auth | Login với email không tồn tại | Email chưa đăng ký | 1. Gọi POST /auth/login với email lạ | 401 "Invalid email or password", giống TC-02 | Medium / Security | Pass |
| TC-09 | Auth | Đăng ký trùng email | User A đã tồn tại | 1. Gọi POST /auth/register với `user_a@test.com` | 400 "Email already registered" | High / Major | Pass |
| TC-10 | Auth | Frontend tự làm mới access token | User A đã login trên trình duyệt | 1. Sửa `access_token` trong localStorage thành chuỗi sai<br>2. Refresh trang | Vẫn ở Todo page (frontend tự gọi /auth/refresh) | Medium / Major | Pass |
| TC-11 | Todo Security | User A không thể xem Todo của User B | Todo X của User B | 1. User A gọi GET /todos/X | 404 Not Found | High / Critical | Pass |
| TC-12 | Todo Security | User A không thể xoá Todo của User B | Todo X của User B | 1. User A gọi DELETE /todos/X<br>2. User B gọi GET /todos/X | Bước 1: 404; bước 2: todo vẫn còn | High / Critical | Pass |
| TC-13 | Auth | Gọi API khi chưa đăng nhập | Chưa đăng nhập | 1. Gọi GET /todos không có token<br>2. Mở `/` trên trình duyệt | Bước 1: 401; bước 2: chuyển về /login | Low / Minor | Pass |
| TC-14 | Todo CRUD | Tạo todo hiện ngay trong danh sách | Danh sách của User A đã được cache | 1. Tạo todo mới<br>2. Gọi GET /todos | Todo mới nằm đầu danh sách | Medium / Major | Pass |
| TC-15 | Todo CRUD | Sửa một phần không xoá description | Todo có description | 1. PUT chỉ có `title`<br>2. PUT chỉ có `completed` | Description giữ nguyên sau cả 2 bước | High / Major | Pass |
| TC-16 | Todo CRUD | Xoá todo biến mất ngay khỏi danh sách | Danh sách của User A đã được cache | 1. DELETE todo<br>2. Gọi GET /todos | Todo không còn trong danh sách | Medium / Major | Pass |
| TC-17 | Cache | Danh sách todo không lẫn giữa các user | Danh sách của User A đã được cache | 1. User A gọi GET /todos<br>2. User B gọi GET /todos | User B chỉ thấy todo của B | High / Critical | Pass |
| TC-18 | Cache | Cache tách theo trang | User A có ít nhất 2 todo | 1. GET /todos?page=1&size=1<br>2. GET /todos?page=2&size=1 | Hai trang trả về hai todo khác nhau | Medium / Major | Pass |
| TC-19 | Todo Logic | Danh sách sắp xếp mới nhất trước | User A có nhiều todo | 1. Gọi GET /todos | Todo mới tạo đứng trước | Low / Minor | Pass |
| TC-20 | Auth | Logout xoá dữ liệu của user trước | User A đã login, có todo | 1. User A logout<br>2. User B login trên cùng trình duyệt | User B không thấy email và todo của A | High / Critical | Pass |

## 4. Defect Tracking & Known Limitations
- TC-13 lần chạy đầu Fail (thiếu token trả 403 thay vì 401). Đã sửa, chạy lại Pass.
- Toast thông báo thành công che nút Logout khoảng 4 giây (UX, chưa sửa).
- Lỗi đã biết, chưa sửa: logout chưa thu hồi token; `size` của danh sách không có giới hạn trên.
- Chưa cover: chờ token hết hạn thật sau 30 phút (TC-06 dùng token đã hết hạn sẵn); email chỉ khác hoa thường; nhiều người sửa cùng một todo cùng lúc.
