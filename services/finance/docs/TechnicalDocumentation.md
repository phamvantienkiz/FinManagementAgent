# Tổng quan hệ thống

Hệ thống của bạn là một Telegram bot tích hợp hai agent chuyên biệt:

1.  Agent lập kế hoạch tài chính cá nhân: Xử lý dữ liệu đầu vào của người dùng (thu nhập, chi tiêu, mục tiêu...) để sinh kế hoạch chi tiết.
2.  Agent cung cấp kiến thức kinh tế/thị trường: Phân tích truy vấn, lên kế hoạch tìm kiếm, kết hợp RAG (data nội bộ + web search) để tạo báo cáo tổng hợp.

Nền tảng: Telegram bot (xây dựng trên Python), tích hợp với LangChain để quản lý workflow, RAG, và công cụ tìm kiếm.\
Ưu điểm: Tận dụng khả năng linh hoạt của LangChain để xây dựng pipeline phức tạp, đồng thời dễ dàng kết nối với Telegram và các dịch vụ bên ngoài (SerpAPI, vector DB).

---

# Phân tích chi tiết từng Agent

## 1\. Agent Lập kế hoạch tài chính cá nhân

Mục tiêu:

- Trích xuất thông tin từ input người dùng (thu nhập, chi tiêu, mục tiêu, thời gian, mức độ chấp nhận rủi ro...).
- Sinh kế hoạch tài chính phù hợp với mức độ chi tiết của dữ liệu đầu vào (ví dụ: nếu thiếu thông tin, hỏi thêm; nếu đủ, tạo kế hoạch chi tiết).

Workflow:

Người dùng → Telegram bot → Agent tài chính cá nhân  
→ Trích xuất dữ liệu (kiểm tra thiếu sót)  
→ Nếu thiếu: yêu cầu bổ sung thông tin  
→ Nếu đủ: sinh kế hoạch (ví dụ: "Bạn cần tiết kiệm 2 triệu/tháng để đạt mục tiêu 100 triệu trong 5 năm")

Cấu thành phần:

- LangChain `ConversationChain` với `Memory`:

  - Lưu trữ lịch sử hội thoại để theo dõi thông tin đã cung cấp.
  - Prompt mẫu:
    Bạn là trợ lý tài chính cá nhân. Hãy trích xuất các thông tin sau từ tin nhắn của người dùng:
    - Thu nhập hàng tháng
    - Chi tiêu hàng tháng
    - Mục tiêu tiết kiệm (ví dụ: mua nhà, du lịch)
    - Thời gian mong muốn đạt mục tiêu
    - Mức độ chấp nhận rủi ro (thấp/trung bình/cao)  
      Nếu thiếu bất kỳ thông tin nào, hãy hỏi người dùng để bổ sung.  
      Khi đủ thông tin, hãy sinh kế hoạch chi tiết kèm giải thích.

- Cơ chế xử lý dữ liệu:
  - Dùng `StructuredOutputParser` của LangChain để định dạng đầu ra thành JSON (dễ dàng kiểm tra thiếu sót).
  - Ví dụ: Nếu thiếu "thời gian", trả lời: "Bạn muốn đạt mục tiêu trong bao lâu? (Ví dụ: 3 năm)".

Công cụ cần dùng:

- Không cần web search (vì dữ liệu hoàn toàn từ người dùng).
- Chỉ cần LLM (GPT-4, Llama 3, hoặc model tùy chọn) + LangChain memory.

---

## Architecture Design

### 1\. Cấu trúc Thư mục

Cấu trúc phù hợp với nguyên tắc Single Responsibility Principle và tính mở rộng khi tích hợp thêm các agent khác (ví dụ: đầu tư, bảo hiểm):

```
services/
├── messaging/ # Đã phát triển xong
├── finagent/ # Service Agent tài chính
│ ├── data/ # Dữ liệu persisten
│ │ ├── cache/ # Cache (Redis)
│ │ └── schemas/ # Schema DB (SQLAlchemy models)
│ ├── app/
│ │ ├── agents/ # Tách theo loại agent
│ │ │ ├── financial/ # Agent tài chính
│ │ │ │ ├── planner.py # Core logic (FinancialPlannerAgent)
│ │ │ │ ├── parser.py # StructuredOutputParser
│ │ │ │ └── prompts/ # Prompt templates (financial_prompt.txt)
│ │ │ └── ... # Future agents (investment, insurance)
│ │ ├── apis/
│ │ │ ├── v1/ # Phiên bản API
│ │ │ │ ├── financial.py # Route /financial
│ │ │ │ └── ...
│ │ ├── core/
│ │ │ ├── orchestrator.py # Điều phối giữa các agent (nếu có)
│ │ │ └── exceptions.py # Xử lý lỗi chung
│ │ ├── models/ # Pydantic models
│ │ │ ├── financial.py # FinancialPlanRequest, FinancialPlanResponse
│ │ │ └── ...
│ │ ├── tools/ # Công cụ hỗ trợ
│ │ │ └── validators.py # Kiểm tra dữ liệu đầu vào
│ │ └── utils/ # Utility helper
│ ├── main.py # Entry point khởi động service
│ ├── .env # Biến môi trường
│ ├── requirements.txt # Dependencies
│ └── Dockerfile # Cấu hình Docker (nếu cần)
└── .gitignore
```

### 2\. Sơ đồ Lớp (Class Diagram) - Biểu diễn tĩnh

#### Core Classes

```
+--------------------------------+
| FinancialPlannerAgent          |
+--------------------------------+
| - memory: ConversationBuffer   |
| - parser: StructuredOutputParser|
| - prompt_template: str         |
+--------------------------------+
| + extract_data(user_input: str)|
|   → dict (thông tin đã parse)  |
| + validate_data(data: dict)    |
|   → bool                       |
| + generate_plan(data: dict)    |
|   → str (kế hoạch chi tiết)    |
+--------------------------------+

+--------------------------------+
| FinancialPlanRequest           |
+--------------------------------+
| - monthly_income: float        |
| - monthly_expense: float       |
| - goal: str                    |
| - timeframe: int (years)       |
| - risk_tolerance: str          |
+--------------------------------+

+--------------------------------+
| FinancialPlanResponse          |
+--------------------------------+
| - summary: str                 |
| - monthly_saving: float        |
| - investment_suggestion: str   |
| - risk_analysis: str           |
+--------------------------------+
```

#### Mối quan hệ

- `FinancialPlannerAgent` sử dụng `FinancialPlanRequest` để validate input.
- `FinancialPlannerAgent` trả về `FinancialPlanResponse`.
- `StructuredOutputParser` (LangChain) được inject vào `FinancialPlannerAgent` qua constructor.

### 3\. Sơ đồ Trình tự (Sequence Diagram) - Tương tác động

#### Quy trình xử lý kế hoạch tài chính

User → Messaging Service: Gửi tin nhắn (Ví dụ: "Tôi muốn tiết kiệm 100 triệu trong 5 năm")
Messaging Service → FinAgent API: POST /financial { message: "..." }
FinAgent API → FinancialPlannerAgent: extract_data(message)
FinancialPlannerAgent → StructuredOutputParser: Phân tích input
StructuredOutputParser → FinancialPlannerAgent: Trả về dict (thiếu timeframe)
FinancialPlannerAgent → FinAgent API: Yêu cầu bổ sung thông tin
FinAgent API → Messaging Service: "Bạn muốn đạt mục tiêu trong bao lâu? (Ví dụ: 3 năm)"
Messaging Service → User: Hiển thị câu hỏi
User → Messaging Service: Trả lời "5 năm"
Messaging Service → FinAgent API: POST /financial { message: "5 năm" }
FinAgent API → FinancialPlannerAgent: validate_data() → ĐỦ THÔNG TIN
FinancialPlannerAgent → FinancialPlannerAgent: generate_plan()
FinancialPlannerAgent → FinAgent API: Trả về FinancialPlanResponse
FinAgent API → Messaging Service: Response JSON
Messaging Service → User: Hiển thị kế hoạch ("Bạn cần tiết kiệm 1.67 triệu/tháng...")

#### Điểm quan trọng:

- Memory Handling: `ConversationBuffer` lưu trữ thông tin qua các lần request → Đảm bảo context-aware.
- Validation Loop: Chỉ sinh kế hoạch khi đủ 5 trường bắt buộc (income, expense, goal, timeframe, risk).
- Error Handling: Nếu `validate_data()` trả về `False`, hệ thống tự động hỏi lại thay vì throw exception.

### 4\. Sơ đồ Lớp Chi tiết (Class Diagram) cho Thư mục `app/`

#### Cấu trúc lớp chính

Dưới đây là biểu diễn tĩnh của các lớp cốt lõi trong `app/` với mối quan hệ và trách nhiệm rõ ràng:

```
+-------------------------------------------------------------------+
|                           FinancialRouter                         |
+-------------------------------------------------------------------+
| - agent: FinancialPlannerAgent                                    |
+-------------------------------------------------------------------+
| + handle_request(request: FinancialPlanRequest)                   |
|   → FinancialPlanResponse                                         |
+-------------------------------------------------------------------+
           ▲
           | uses
           |
+-------------------------------------------------------------------+
|                       FinancialPlannerAgent                       |
+-------------------------------------------------------------------+
| - memory: ConversationBufferMemory                                |
| - parser: StructuredOutputParser                                  |
| - prompt_loader: PromptTemplateLoader                             |
| - validator: DataValidator                                        |
+-------------------------------------------------------------------+
| + extract_data(user_id: str, message: str) → dict                 |
| + validate_data(data: dict) → Tuple[bool, List[str]]              |
| + generate_plan(data: dict) → FinancialPlanResponse               |
| + save_to_memory(user_id: str, key: str, value: Any)              |
+-------------------------------------------------------------------+
           ▲                           ▲                  ▲
           | uses                      | uses             | uses
           |                           |                  |
+---------------------+   +---------------------------+   +---------------------+
|   PromptTemplate    |   |      DataValidator        |   | ConversationBuffer  |
+---------------------+   +---------------------------+   |      Memory         |
| - template_path: str|   | + validate_required_fields|   +---------------------+
| + load() → str      |   |   (data: dict) → List[str]|   | - storage: dict     |
+---------------------+   +---------------------------+   | + get(user_id) → str|
                                                           | + save(user_id, str)|
                                                           +---------------------+

+-------------------------------------------------------------------+
|                       FinancialPlanRequest                        |
+-------------------------------------------------------------------+
| - user_id: str                                                    |
| - message: str                                                    |
+-------------------------------------------------------------------+

+-------------------------------------------------------------------+
|                       FinancialPlanResponse                       |
+-------------------------------------------------------------------+
| - status: Literal["success", "missing_data"]                      |
| - plan: Optional[PlanDetails]                                     |
| - missing_fields: Optional[List[str]]                             |
| - next_question: Optional[str]                                    |
+-------------------------------------------------------------------+

+-------------------------------------------------------------------+
|                           PlanDetails                             |
+-------------------------------------------------------------------+
| - summary: str                                                    |
| - monthly_saving: float                                           |
| - investment_strategy: str                                        |
| - risk_analysis: str                                              |
+-------------------------------------------------------------------+
```

#### Giải thích chi tiết từng lớp

##### 1\. `FinancialPlannerAgent` (Core Business Logic)

- Trách nhiệm: Xử lý toàn bộ quy trình từ trích xuất dữ liệu → validate → sinh kế hoạch.
- Thuộc tính quan trọng:
  - `memory`: Lưu trữ context hội thoại theo `user_id` (dùng `ConversationBufferMemory` của LangChain).
  - `parser`: Phân tích input người dùng thành cấu trúc JSON (dùng `StructuredOutputParser`).
  - `validator`: Kiểm tra tính đầy đủ của dữ liệu (tương tác với `DataValidator`).
- Phương thức nổi bật:
  - `extract_data()`: Kết hợp lịch sử hội thoại + tin nhắn mới để parse thông tin.
  - `validate_data()`: Trả về `True` nếu đủ 5 trường bắt buộc, ngược lại liệt kê `missing_fields`.
  - `generate_plan()`: Tính toán kế hoạch dựa trên công thức (ví dụ: `monthly_saving = goal / (timeframe * 12)`).

##### 2\. `FinancialRouter` (API Layer)

- Trách nhiệm: Tiếp nhận request từ `messaging-service`, chuyển giao cho `FinancialPlannerAgent`.
- Luồng xử lý:

```Python
async def handle_request(request: FinancialPlanRequest):

    response = agent.extract_data(request.user_id, request.message)

    if response.status == "missing_data":

        agent.save_to_memory(request.user_id, "pending", response.missing_fields)

    return response

```

##### 3\. `DataValidator` (Tools Layer)

- Trách nhiệm: Kiểm tra tính hợp lệ của dữ liệu theo quy tắc nghiệp vụ.
- Cơ chế hoạt động:

```Python
REQUIRED_FIELDS = ["monthly_income", "monthly_expense", "goal", "timeframe", "risk_tolerance"]

def validate_required_fields(data: dict) -> List[str]:
    return [field for field in REQUIRED_FIELDS if not data.get(field)]
```

##### 4\. `PromptTemplateLoader` (Core Layer)

- Trách nhiệm: Quản lý prompt templates từ file (tránh hardcode).
- Cơ chế:
  - Đọc template từ `app/agents/financial/prompts/financial_prompt.txt`.
  - Inject biến động (ví dụ: `{{missing_fields}}`) khi sinh câu hỏi bổ sung.

##### 5\. `FinancialPlanResponse` (Models Layer)

- Phân nhánh trạng thái:
  - Khi đủ dữ liệu: `status="success"`, `plan` chứa thông tin chi tiết.
  - Khi thiếu dữ liệu: `status="missing_data"`, `next_question` gợi ý câu hỏi tiếp theo (ví dụ: `"Bạn muốn đạt mục tiêu trong bao lâu?"`).

---

### 5\. Sơ đồ Trình tự (Sequence Diagram) - Luồng tương tác

#### Scenario: Người dùng tạo kế hoạch tài chính (2 vòng lặp)

```
Người dùng       Telegram Bot       Messaging Service       FinAgent API       FinancialPlannerAgent       Memory       Validator
    |                  |                    |                     |                     |                  |              |
    | Gửi "Tôi muốn   |                    |                     |                     |                  |              |
    | tiết kiệm 100tr" |                    |                     |                     |                  |              |
    |----------------->|                    |                     |                     |                  |              |
    |                  | Forward request    |                     |                     |                  |              |
    |                  |------------------->|                     |                     |                  |              |
    |                  |                    | POST /financial     |                     |                  |              |
    |                  |                    |-------------------->|                     |                  |              |
    |                  |                    |                     | extract_data()      |                  |              |
    |                  |                    |                     |-------------------->|                  |              |
    |                  |                    |                     |                     | get_history()    |              |
    |                  |                    |                     |                     |----------------->|              |
    |                  |                    |                     |                     |                  | return {}    |
    |                  |                    |                     |                     |<-----------------|              |
    |                  |                    |                     |                     | parse_data()     |              |
    |                  |                    |                     |                     |----------------->| Structured...  |
    |                  |                    |                     |                     |<-----------------|              |
    |                  |                    |                     |                     | validate_data()  |              |
    |                  |                    |                     |                     |----------------->|              |
    |                  |                    |                     |                     |                  | validate()   |
    |                  |                    |                     |                     |                  |------------->|
    |                  |                    |                     |                     |                  | return ["timeframe"]|
    |                  |                    |                     |                     |<-----------------|              |
    |                  |                    |                     |<--------------------|                  |              |
    |                  |                    | 200 OK {                            |                  |              |
    |                  |                    |   "status": "missing_data",        |                  |              |
    |                  |                    |   "next_question": "Bạn muốn..."} |                  |              |
    |                  |<-------------------|                     |                  |                  |              |
    | Nhận câu hỏi     |                    |                     |                  |                  |              |
    | "Bạn muốn...?"   |                    |                     |                  |                  |              |
    |<-----------------|                    |                     |                  |                  |              |
    |                  |                    |                     |                  |                  |              |
    | Gửi "5 năm"      |                    |                     |                  |                  |              |
    |----------------->|                    |                     |                  |                  |              |
    |                  | Forward request    |                     |                  |                  |              |
    |                  |------------------->|                     |                  |                  |              |
    |                  |                    | POST /financial     |                  |                  |              |
    |                  |                    |-------------------->|                  |                  |              |
    |                  |                    |                     | extract_data()   |                  |              |
    |                  |                    |                     |----------------->|                  |              |
    |                  |                    |                     |                     | get_history()    |              |
    |                  |                    |                     |                     |----------------->|              |
    |                  |                    |                     |                     |                  | return {...} |
    |                  |                    |                     |                     |<-----------------|              |
    |                  |                    |                     |                     | parse_data() +   |              |
    |                  |                    |                     |                     | validate_data()  |              |
    |                  |                    |                     |                     |----------------->|              |
    |                  |                    |                     |                     |                  | validate()   |
    |                  |                    |                     |                     |                  |------------->|
    |                  |                    |                     |                     |                  | return []    |
    |                  |                    |                     |                     |<-----------------|              |
    |                  |                    |                     |                     | generate_plan()  |              |
    |                  |                    |                     |                     |----------------->|              |
    |                  |                    |                     |<--------------------|                  |              |
    |                  |                    | 200 OK {                            |                  |              |
    |                  |                    |   "status": "success",             |                  |              |
    |                  |                    |   "plan": { ... } }                |                  |              |
    |                  |<-------------------|                     |                  |                  |              |
    | Nhận kế hoạch    |                    |                     |                  |                  |              |
    | "Bạn cần tiết... |                    |                     |                  |                  |              |
    |<-----------------|                    |                     |                  |                  |              |
```

#### Phân tích luồng quan trọng

1.  Context Management:

    - `Memory` lưu trữ toàn bộ hội thoại theo `user_id` → Đảm bảo Agent hiểu ngữ cảnh khi người dùng trả lời tiếp.
    - Ví dụ: Lần 1 thiếu `timeframe`, lần 2 khi người dùng gửi "5 năm", Agent tự động gán giá trị này vào context.

2.  Validation Loop:

    - `DataValidator` kiểm tra 5 trường bắt buộc. Nếu thiếu, hệ thống không throw error mà sinh câu hỏi tự nhiên.
    - Cơ chế `next_question` được tính toán động dựa trên `missing_fields` (ví dụ: `["timeframe"]` → "Bạn muốn đạt mục tiêu trong bao lâu?").

3.  Stateless API Design:

    - `FinAgent API` không lưu trạng thái → Toàn bộ context được quản lý bởi `Memory` (Redis/DB).
    - Điều này giúp hệ thống scale ngang và tránh mất dữ liệu khi restart service.

4.  Error Prevention:

    - `StructuredOutputParser` đảm bảo dữ liệu đầu ra luôn có cấu trúc → Tránh LLM sinh response không kiểm soát được.
    - Ví dụ: Nếu người dùng nói "Tôi muốn mua nhà 5 tỷ", parser sẽ extract `goal="mua nhà"`, `goal_amount=5000000000`.

---
