Hiện tại khi services/messaging/app/agent_client.py nhận kết quả từ agents-service là raw markdown hoặc markdown.
Tuy nhiên khi trả về response cho user trên telegram thì telegram không hiểu markdown vì vậy tồn tại các ký tự "##", "\*\*",...

Tôi cần bạn review lại và khi nhận raw markdown, hay markdown từ agents-service thì chuyển về lại thuần text trước khi trả về cho user.

Chỉ phân tích và thực hiện đúng việc convert từ markdown về text trước khi trả về cho user, không thay đổi bất kỳ thứ gì khác. Không thay đổi code trong agents-service. được phép tạo thêm file để xử lý nếu cần.

Viết báo cáo những gì bạn đã phân tích và thay đổi code ở đây:

````
- Issue: Telegram does not render Markdown by default; raw Markdown (##, **, ``` etc.) appears in messages.
- Scope: Only convert Markdown to plain text in messaging service before sending to users. No changes to agents-service.

Changes made:
1) Added a lightweight converter at `services/messaging/app/markdown_utils.py` with function `md_to_text(md: str)`, handling:
   - code fences and inline code (strip fences, keep content),
   - headings, bold/italic/strikethrough,
   - links/images converted to `text (url)`,
   - blockquotes/lists normalization, and general token cleanup.
2) Updated `services/messaging/app/agent_client.py` to call `md_to_text(...)` on all possible reply fields:
   - `reply.raw`, `reply.text`, `reply.content`, and inside `tasks_output` (`raw`/`summary`).
   - Also applies as a fallback when stringifying unexpected structures.

Result:
- Users now receive clean plain text on Telegram even when agents-service returns Markdown.
- No behavior change in routing or APIs; only presentation formatting is adjusted on the messaging side.
````
