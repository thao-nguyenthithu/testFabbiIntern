# Technical Specification: Todo List Sharing

## 1. Overview & Objective
- **Tóm tắt tính năng**: Owner chia sẻ danh sách todo của mình cho user khác (theo email) với quyền `viewer` (chỉ đọc) hoặc `editor` (tạo, sửa, xoá todo); thu hồi quyền bất cứ lúc nào.
- **Vấn đề cần giải quyết**: Hiện mỗi user chỉ thấy todo của mình, muốn làm chung phải dùng chung tài khoản.
- **Đối tượng / Vai trò**: Owner (chủ danh sách, duy nhất được quản lý chia sẻ), Viewer, Editor.

## 2. User Stories & Acceptance Criteria
### User Story 1: Chia sẻ danh sách
- **Là** Owner
- **Tôi muốn** chia sẻ danh sách todo cho user khác theo email, với quyền viewer hoặc editor
- **Để** người khác cùng xem hoặc cùng làm việc
- **Tiêu chí chấp nhận**:
  - [ ] Email đã đăng ký → 201; email chưa đăng ký → 404.
  - [ ] Chia sẻ cho chính mình → 400; chia sẻ trùng người đã có quyền → 409.

### User Story 2: Đổi quyền và thu hồi quyền
- **Là** Owner
- **Tôi muốn** đổi quyền viewer ↔ editor hoặc thu hồi quyền
- **Để** kiểm soát ai được làm gì với danh sách của mình
- **Tiêu chí chấp nhận**:
  - [ ] Đổi quyền có hiệu lực từ request tiếp theo.
  - [ ] Sau khi thu hồi, người bị thu hồi nhận 404 ngay, kể cả khi dữ liệu đang có trong cache.

### User Story 3: Viewer chỉ đọc
- **Là** Viewer
- **Tôi muốn** xem todo của owner
- **Để** theo dõi công việc mà không sửa nhầm
- **Tiêu chí chấp nhận**:
  - [ ] Xem danh sách, chi tiết → 200; tạo / sửa / xoá → 403.

### User Story 4: Editor cùng làm việc
- **Là** Editor
- **Tôi muốn** tạo, sửa, xoá todo của owner
- **Để** cùng quản lý công việc với owner
- **Tiêu chí chấp nhận**:
  - [ ] Tạo → 201 (todo thuộc owner), sửa → 200, xoá → 204.
  - [ ] Hai người cùng sửa một todo: người lưu sau với `version` cũ → 409.
  - [ ] Không chia sẻ tiếp được danh sách của owner.

## 3. Scope
- **Trong phạm vi**: bảng chia sẻ, API chia sẻ / đổi quyền / thu hồi, API truy cập danh sách được chia sẻ, kiểm tra quyền ở backend, xoá cache, UI "Share" và "Shared with me".
- **Ngoài phạm vi**: lời mời cần chấp nhận, email thông báo, chia sẻ từng todo, chia sẻ theo nhóm hoặc link công khai, realtime, audit log, rate limit.

## 4. Database Design
- **Bảng mới / Bảng thay đổi**:
  - Bảng mới `todo_list_shares`:

    | Cột | Kiểu | Ghi chú |
    |---|---|---|
    | `id` | UUID | Khoá chính |
    | `owner_id` | UUID | NOT NULL, khoá ngoại → `users(id)` |
    | `grantee_id` | UUID | NOT NULL, khoá ngoại → `users(id)` (người được chia sẻ) |
    | `role` | VARCHAR(10) | NOT NULL, `viewer` hoặc `editor` |
    | `created_at`, `updated_at` | TIMESTAMPTZ | NOT NULL |

  - Bảng `todos` thêm cột `version` INTEGER NOT NULL DEFAULT 1, tăng 1 mỗi lần sửa.
- **Ràng buộc & Index**:
  - `UNIQUE (owner_id, grantee_id)`: chặn mời trùng.
  - `CHECK (owner_id <> grantee_id)`: chặn tự chia sẻ.
  - `owner_id`, `grantee_id`: `ON DELETE CASCADE` (xoá user thì share liên quan tự xoá).
  - Index `(grantee_id)` cho danh sách "Shared with me".

## 5. API Contracts & Endpoints
| Method | Endpoint | Mô tả | Cần đăng nhập |
|---|---|---|---|
| POST | `/api/v1/shares` | Owner chia sẻ danh sách | Có |
| GET | `/api/v1/shares` | Owner xem những người đã chia sẻ | Có |
| PATCH | `/api/v1/shares/{share_id}` | Owner đổi quyền | Có |
| DELETE | `/api/v1/shares/{share_id}` | Owner thu hồi quyền | Có |
| GET | `/api/v1/shares/incoming` | Các danh sách được chia sẻ cho tôi | Có |
| GET | `/api/v1/shared-lists/{owner_id}/todos` | Xem todo của owner (phân trang) | Có (viewer, editor) |
| POST | `/api/v1/shared-lists/{owner_id}/todos` | Tạo todo | Có (editor) |
| PUT | `/api/v1/shared-lists/{owner_id}/todos/{todo_id}` | Sửa todo | Có (editor) |
| DELETE | `/api/v1/shared-lists/{owner_id}/todos/{todo_id}` | Xoá todo | Có (editor) |

- **Request body & schema kiểm tra dữ liệu** (Pydantic):

```python
class ShareCreate(BaseModel):
    grantee_email: EmailStr
    role: Literal["viewer", "editor"]

class ShareUpdate(BaseModel):
    role: Literal["viewer", "editor"]

class SharedTodoUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    completed: bool | None = None
    version: int = Field(..., ge=1)
```

- **Response & mã lỗi** (lỗi có dạng `{"detail": "..."}`):

| Mã | Khi nào | Ví dụ payload |
|---|---|---|
| 200 / 201 | Thành công / tạo mới thành công | Object hoặc danh sách |
| 400 | Tự chia sẻ cho chính mình | `{"detail": "Cannot share with yourself"}` |
| 403 | Viewer tạo / sửa / xoá todo | `{"detail": "Insufficient permission"}` |
| 404 | Email chưa đăng ký; không có quyền với danh sách; share hoặc todo không tồn tại | `{"detail": "User not found"}`, `{"detail": "Shared list not found"}` |
| 409 | Mời trùng; sửa todo với `version` cũ | `{"detail": "Todo list already shared with this user"}`, `{"detail": "Todo was modified by another user"}` |
| 422 | Sai schema (email sai, role lạ, thiếu `version`) | `{"detail": [{"loc": ["body", "role"], "msg": "Input should be 'viewer' or 'editor'"}]}` |

  Dùng thêm 409 (ngoài danh sách của template) vì đây là mã chuẩn cho xung đột dữ liệu, giúp client phân biệt với lỗi dữ liệu gửi sai (400).

## 6. Business Logic & Security Considerations
- **Ma trận phân quyền**:

| Hành động | Owner | Editor | Viewer | Không có quyền |
|---|---|---|---|---|
| Xem todo | ✅ | ✅ | ✅ | 404 |
| Tạo / sửa / xoá todo | ✅ | ✅ | 403 | 404 |
| Chia sẻ / đổi quyền / thu hồi | ✅ | ❌ | ❌ | ❌ |

  - Quyền được kiểm tra trong DB ở mỗi request. Không có quyền trả 404, giống cách hệ thống đang xử lý todo của người khác.
  - **Người được chia sẻ tự chia sẻ tiếp**: không được. API `/shares` luôn lấy owner là user hiện tại.
- **Trường hợp biên & xử lý đồng thời**:
  - **Mời trùng lặp**: trả 409. Hai request mời cùng lúc thì `UNIQUE (owner_id, grantee_id)` chỉ cho một request thành công.
  - **Owner thu hồi quyền trong lúc collaborator đang sửa**: request sửa kiểm tra quyền và ghi dữ liệu trong cùng một transaction, có khoá dòng share (`SELECT ... FOR SHARE`). Thu hồi phải chờ request sửa xong; request đến sau khi thu hồi nhận 404.
  - **User tự share cho chính mình**: API trả 400; DB có `CHECK` chặn thêm.
  - **Sửa đồng thời**: `UPDATE ... WHERE id = :id AND version = :version`; không cập nhật được dòng nào → 409, client tải lại rồi sửa tiếp.

## 7. Caching & Invalidation Strategy
- **Cấu trúc Redis cache key**:
  - `todos:list:{owner_id}:{page}:{size}`: owner và người được chia sẻ đọc chung, vì dữ liệu giống nhau.
  - `shares:incoming:{user_id}`: danh sách "Shared with me".
  - Không cache quyền: quyền luôn được kiểm tra trong DB trước khi đọc cache, nên thu hồi có hiệu lực ngay.
- **Khi nào xoá cache** (sau khi transaction commit):
  - Owner hoặc editor tạo / sửa / xoá todo → xoá `todos:list:{owner_id}:*`.
  - Owner chia sẻ, đổi quyền hoặc thu hồi quyền → xoá `shares:incoming:{grantee_id}`.
