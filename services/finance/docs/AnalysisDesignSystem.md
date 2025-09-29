# Hệ Thống Chatbot Agent Tài Chính: Đặc Tả Hệ Thống

## 1\. Tổng Quan Hệ Thống

Hệ thống chatbot agent tài chính được thiết kế để cung cấp thông tin thời gian thực về thị trường tài chính, chứng khoán và tiền điện tử thông qua nền tảng nhắn tin (Telegram, Zalo, Web). Hệ thống sử dụng kiến trúc microservice với trọng tâm là khả năng tích hợp AI agent thông minh, xử lý truy vấn người dùng và cung cấp thông tin chính xác từ nguồn dữ liệu trực tuyến.

## 2\. Thành Phần Hệ Thống

### 2.1. Messaging Service

- Chức năng: Tiếp nhận truy vấn từ người dùng qua các nền tảng (Telegram, Zalo, Web), xác định user_id và nội dung truy vấn
- Định tuyến: Sử dụng cú pháp lệnh có dấu "/" (ví dụ: /news) để định tuyến đến các agent phù hợp, tương thích với khả năng xử lý lệnh của Telegram
- Yêu cầu: Hỗ trợ đa nền tảng, xử lý định dạng tin nhắn khác nhau

### 2.2. Finance Service & Agent Router

- Chức năng: Tiếp nhận truy vấn từ Messaging Service, xác định loại truy vấn và chuyển đến agent chuyên biệt
- Agent Router: Cơ chế định tuyến thông minh dựa trên nội dung truy vấn và cú pháp lệnh, cho phép mở rộng thêm các agent trong tương lai
- Xử lý lệnh: Triển khai cơ chế xử lý lệnh tương tự như FinGen - hệ thống phân tích tài chính sử dụng LangChain và API bên ngoài

### 2.3. Information Agent (Agent Cung Cấp Thông Tin)

#### 2.3.1. Query Analysis Module

- Chức năng: Phân tích truy vấn người dùng, trích xuất từ khóa quan trọng và xác định mục đích
- Công nghệ: LLM đầu tiên trong chuỗi xử lý, được tối ưu cho lĩnh vực tài chính

#### 2.3.2. Web Search Module

- Chức năng: Thực hiện tìm kiếm thông tin thời gian thực dựa trên từ khóa
- Công nghệ: Brave Search API - cung cấp dữ liệu thời gian thực cho các mô hình LLM và hỗ trợ tìm kiếm tác nhân (agentic search)
- Lưu ý: Cần đăng ký API Key qua quy trình chính thức để truy cập Brave Search API
- Bảo mật: Tuân thủ nguyên tắc "least privilege" trong truy cập API, yêu cầu xem xét bảo mật/riêng tư và thu hồi kịp thời khi cần

#### 2.3.3. Web Scraping Module

- Chức năng: Trích xuất nội dung từ các URL trả về từ kết quả tìm kiếm
- Công nghệ: Crawl4AI cho phép thực hiện Web Search, Tìm kiếm điểm quan tâm địa phương, Tìm kiếm hình ảnh và Tìm kiếm video

#### 2.3.4. Content Processing Module

- Chức năng: Phân tích dữ liệu đã thu thập, tạo báo cáo/tóm tắt cho người dùng
- Công nghệ: LLM thứ hai chuyên về xử lý thông tin tài chính, tích hợp với RAG từ Vector DB

### 2.4. Data Storage Components

#### 2.4.1. Vector Database

- Chức năng: Lưu trữ thông tin quan trọng dưới dạng embedding cho hệ thống RAG
- Yêu cầu: Hỗ trợ truy vấn tương tự ngữ nghĩa, tối ưu cho dữ liệu tài chính
- Ứng dụng: Cung cấp dữ liệu nền cho các truy vấn tương lai, giảm tải cho việc tìm kiếm thời gian thực

#### 2.4.2. Cache System

- Chức năng: Lưu trữ kết quả truy vấn phổ biến, giảm thời gian phản hồi và chi phí API
- Chiến lược: TTL ngắn cho dữ liệu tài chính (do tính thời sự), ưu tiên lưu trữ các truy vấn có tần suất cao

#### 2.4.3. Chat History Storage

- Chức năng: Lưu trữ lịch sử trò chuyện cho từng người dùng
- Công nghệ: Supabase (sẽ triển khai ở giai đoạn sau)

## 3\. Luồng Dữ Liệu

1.  Người dùng gửi truy vấn qua nền tảng (Telegram/Zalo/Web)
2.  Messaging Service nhận và xử lý tin nhắn, xác định user_id và nội dung
3.  Finance Service phân tích truy vấn, định tuyến đến Information Agent
4.  Query Analysis Module xử lý truy vấn, trích xuất từ khóa
5.  Web Search Module sử dụng Brave Search API để tìm kiếm thông tin thời gian thực
6.  Web Scraping Module thu thập nội dung từ các URL trả về
7.  Content Processing Module phân tích dữ liệu và tạo báo cáo/tóm tắt
8.  Data Storage lưu trữ thông tin quan trọng vào Vector DB và Cache
9.  Messaging Service trả kết quả về cho người dùng

## 4\. Yêu Cầu Bảo Mật

- API Key Management: Quản lý API Key cho Brave Search API theo quy trình đăng ký chính thức
- Nguyên tắc Least Privilege: Áp dụng nguyên tắc tối thiểu đặc quyền cho các thành phần truy cập API
- Thu thập dữ liệu: Hiểu rõ chính sách thu thập dữ liệu của Brave để tuân thủ các yêu cầu pháp lý

## 5\. Công Nghệ Đề Xuất

### 5.1. Công nghệ chính

- Framework chính: LangChain để xây dựng và orchestrate các thành phần AI agent
- Web Search: Brave Search API - "API tìm kiếm Web lớn nhất thế giới"
- Web Scraping: Crawl4AI cho việc thu thập dữ liệu từ Web
- Document extraction: Docling
- Memory: LangChain Memory cho ngữ cảnh trò chuyện
- Cache: Redis
- Vector Database: Pinecone
- Database: Supabase cho lưu trữ lịch sử trò chuyện

### 5.2. Cần Lựa Chọn Thêm

#### 5.2.1. Công Cụ Giám Sát

- Lựa chọn: Prometheus + Grafana hoặc ELK Stack
- Tiêu chí: Giám sát hiệu suất hệ thống, phát hiện lỗi thời gian thực

#### 5.2.2. Hàng Đợi Task

- Lựa chọn: Celery hoặc RabbitMQ
- Tiêu chí: Xử lý bất đồng bộ các tác vụ nặng (như scraping, xử lý dữ liệu)

#### 5.2.3. Cơ Chế Rate Limiting

- Lựa chọn: Middleware tích hợp với Nginx hoặc dịch vụ chuyên dụng
- Tiêu chí: Ngăn chặn lạm dụng API, đặc biệt quan trọng với Brave Search API có giới hạn

## 6\. Vấn Đề Cần Giải Quyết

1.  Xử lý giới hạn API: Brave Search API có giới hạn sử dụng, cần thiết kế cơ chế xử lý lỗi và quản lý rate limit hiệu quả

2.  Chất lượng dữ liệu: Xây dựng cơ chế xác thực và làm sạch dữ liệu sau khi scraping để đảm bảo độ chính xác

3.  Tính thời sự: Xác định TTL hợp lý cho cache dữ liệu tài chính (thường ngắn hơn các lĩnh vực khác)

4.  Tuân thủ pháp lý: Đảm bảo hệ thống tuân thủ các quy định về cung cấp thông tin tài chính

5.  Tích hợp đa nền tảng: Thiết kế Messaging Service để dễ dàng mở rộng sang các nền tảng khác ngoài Telegram

---

---

---

# Phân Tích Hệ Thống Chatbot Agent Tài Chính: Triển Khai Chi Tiết

## 1\. Phân Tích Sâu Các Thành Phần Cốt Lõi

### 1.1. Messaging Service (Đã Xây Dựng)

Phân tích chi tiết:

- Cơ chế định tuyến lệnh: Sử dụng regex để xử lý cú pháp lệnh `/command` (ví dụ: `/news`, `/stock`, `/crypto`)
- Chuẩn hóa đầu vào:
  - Xử lý đa nền tảng bằng cách chuyển đổi định dạng tin nhắn thành một cấu trúc chuẩn. Messaging-service khi gọi sẽ kèm theo request với cấu trúc như ví dụ phía dưới.
  - Ví dụ: `{user_id: "18a72bd69a", platform: "telegram", query: "/news tổng hợp thông tin thị trường, crypto hôm nay"}`
- Xác thực nguồn: Kiểm tra tính hợp lệ của user_id từ hệ thống xác thực trước khi chuyển tiếp

Điểm cần chú ý:

- Cần triển khai middleware để chuẩn hóa các trường `user_id` (UUID format) và `user_query` (loại bỏ ký tự đặc biệt không cần thiết)
- Xây dựng cơ chế rate limiting tại tầng này để ngăn lạm dụng hệ thống

### 1.2. Finance Service & Agent Router

Cơ chế định tuyến thông minh:

```graph TD
    A[Truy vấn đầu vào] --> B{Phân tích cú pháp}
    B -->|Có lệnh /command| C[Xác định loại agent]
    B -->|Không có lệnh| D[Phân tích intent bằng LLM]
    C --> E[Chuyển đến Agent cụ thể]
    D --> F[Xác định agent mặc định]
    F --> E
    E --> G[Xử lý bởi Agent]
```

Triển khai chi tiết:

- Command-based routing:

  - Danh sách lệnh được cấu hình trong file YAML (dễ mở rộng):

```YAML
commands:
  - name: "/news"
    description: "Tin tức tài chính tổng hợp"
    agent: "information_agent"
    parameters: ["topic"]
  - name: "/stock"
    description: "Thông tin cổ phiếu"
    agent: "stock_agent"
    parameters: ["symbol"]
```

- Intent-based routing (khi không có lệnh):

  - Triển khai nhỏ với LLM chuyên về phân loại intent:

```Python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

intent_prompt = PromptTemplate(
    input_variables=["query"],
    template="Phân loại intent của truy vấn sau thành một trong các loại: [news, analysis, stock, crypto, general]. Truy vấn: {query}"
)

intent_classifier = LLMChain(
    llm=financial_llm,
    prompt=intent_prompt
)
```

Lợi thế thiết kế:

- Tách biệt rõ ràng giữa định tuyến dựa trên lệnh và định tuyến dựa trên intent
- Dễ dàng mở rộng bằng cách thêm vào file cấu hình hoặc cập nhật prompt

### 1.3. Information Agent: Phân Tích Chi Tiết

#### 1.3.1. Query Analysis Module

Công nghệ triển khai:

- Sử dụng LLM nhỏ, tối ưu cho tài chính (ví dụ: `finance-llm-mini`)
- Prompt engineering chuyên sâu:

```Python
from langchain.prompts import ChatPromptTemplate

query_analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", "Bạn là chuyên gia phân tích truy vấn tài chính. Hãy xác định:\n"
               "1. Chủ đề chính (ví dụ: thị trường chứng khoán, crypto, lãi suất)\n"
               "2. Thực thể quan trọng (cổ phiếu, đồng tiền, chỉ số)\n"
               "3. Mục đích truy vấn (tổng hợp tin tức, phân tích chuyên sâu, so sánh)\n"
               "4. Phạm vi thời gian (nếu có)\n"
               "Trả về dưới dạng JSON với các trường: main_topic, entities, intent, time_range"),
    ("user", "{query}")
])
```

Quy trình xử lý:

1.  Tiền xử lý truy vấn: Chuẩn hóa văn bản, loại bỏ stop words không liên quan
2.  Phân tích bằng LLM với prompt được tối ưu
3.  Xác thực đầu ra: Kiểm tra tính hợp lệ của JSON trả về
4.  Trích xuất từ khóa cho tìm kiếm: Kết hợp từ phân tích của LLM và thuật toán TF-IDF

#### 1.3.2. Web Search Module (Brave Search API)

Triển khai chi tiết:

- Tối ưu hóa truy vấn tìm kiếm:

```Python
def optimize_search_query(analysis_result):
    # Kết hợp các thành phần từ phân tích
    search_terms = [
        analysis_result['main_topic'],
        *analysis_result['entities'],
        "tin tức mới nhất",
        "phân tích chuyên sâu"
    ]

    # Thêm bộ lọc thời gian nếu có
    if analysis_result['time_range']:
        search_terms.append(f"trong {analysis_result['time_range']}")

    return " ".join(search_terms)
```

- Xử lý giới hạn API:

  - Triển khai circuit breaker pattern
  - Cơ chế retry với exponential backoff
  - Cache kết quả tìm kiếm trong Redis với TTL 15 phút

Cấu hình Brave Search API:

```Python
from langchain.tools import BraveSearch

search_tool = BraveSearch(
    api_key=os.getenv("BRAVE_API_KEY"),
    search_kwargs={
        "count": 10,  # Số kết quả tối đa
        "freshness": "day",  # Chỉ lấy kết quả mới trong 24h
        "country": "VN",  # Ưu tiên nguồn tiếng Việt
        "text_decorations": False
    }
)
```

#### 1.3.3. Web Scraping Module (Crawl4AI + Docling)

Quy trình xử lý:

1.  Lọc URL: Chỉ lấy từ các nguồn tin cậy (được định nghĩa trong danh sách trắng)
2.  Crawl4AI thực hiện scraping với các cấu hình:
    - Tự động phát hiện nội dung chính (main content)
    - Xử lý JavaScript nếu cần
    - Trích xuất metadata (ngày đăng, tác giả)
3.  Docling xử lý văn bản:
    - Chuẩn hóa định dạng
    - Xác định cấu trúc tài liệu (tiêu đề, đoạn văn)
    - Trích xuất thông tin thực thể quan trọng

Xử lý dữ liệu tài chính đặc thù:

- Phát hiện và chuẩn hóa số liệu (ví dụ: "1.2 tỷ USD" → 1200000000)
- Xác định xu hướng (tăng/giảm) từ văn bản mô tả
- Trích xuất các chỉ số quan trọng (VN-Index, BTC price, USD/VND)

#### 1.3.4. Content Processing Module

Kiến trúc RAG nâng cao:

```graph LR
    A[Truy vấn người dùng] --> B[Pinecone Retriever]
    C[Lịch sử hội thoại] --> D[Context Enrichment]
    B --> D
    D --> E[LLM Tổng Hợp]
    F[Dữ liệu đã scrape] --> E
    E --> G[Phản hồi cho người dùng]
```

Triển khai chi tiết:

- RAG Pipeline:

```Python
from langchain.chains import RetrievalQA
from langchain.retrievers import PineconeHybridSearchRetriever

retriever = PineconeHybridSearchRetriever(
    embeddings=financial_embeddings,
    sparse_encoder=BM25Encoder(),
    index_name="financial-knowledge"
)

qa_chain = RetrievalQA.from_chain_type(
    llm=financial_analyst_llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": financial_qa_prompt}
)
```

- Prompt Engineering cho phân tích tài chính:

```Python
financial_qa_prompt = PromptTemplate(
    template="""
    Bạn là chuyên gia phân tích tài chính với 10 năm kinh nghiệm. Dựa trên các thông tin sau:

    {context}

    Và lịch sử hội thoại:
    {chat_history}

    Hãy trả lời câu hỏi của người dùng về {main_topic} một cách chuyên nghiệp, chính xác:
    "{question}"

    Yêu cầu:
    1. Trình bày dưới dạng bảng tóm tắt với các cột: Chỉ số, Giá trị hiện tại, Thay đổi, Nhận định
    2. Đưa ra phân tích ngắn gọn về xu hướng
    3. Cảnh báo rủi ro (nếu có)
    4. Trích dẫn nguồn thông tin
    """,
    input_variables=["context", "chat_history", "main_topic", "question"]
)
```

### 1.4. Hệ Thống Lưu Trữ Dữ Liệu

#### 1.4.1. Vector Database (Pinecone)

Cấu trúc index:

- Namespace: Phân chia theo chủ đề (stocks, crypto, forex, general)
- Metadata filters:

```Json
{
  "source": "cafef.vn",
  "date": "2023-10-15",
  "reliability_score": 0.85,
  "entities": ["VN-INDEX", "SSI", "VCB"]
}
```

Quy trình cập nhật:

1.  Khi có dữ liệu mới từ Content Processing Module
2.  Tạo embedding bằng model `text-embedding-3-large`
3.  Lọc metadata quan trọng (ngày, nguồn, thực thể)
4.  Cập nhật vào Pinecone với TTL 7 ngày (dữ liệu tài chính)

#### 1.4.2. Cache System (Redis)

Cấu trúc lưu trữ:

- Key pattern: `finance:cache:{hash(query)}`
- TTL strategy:
  - Tin tức tổng hợp: 15 phút
  - Dữ liệu thị trường (giá cổ phiếu): 5 phút
  - Phân tích chuyên sâu: 1 giờ

Triển khai cache layer:

```Python
import hashlib

def get_cached_response(query):
    key = f"finance:cache:{hashlib.md5(query.encode()).hexdigest()}"
    return redis_client.get(key)

def set_cached_response(query, response, ttl=900):
    key = f"finance:cache:{hashlib.md5(query.encode()).hexdigest()}"
    redis_client.setex(key, ttl, json.dumps(response))
```

#### 1.4.3. Chat History Storage (Supabase)

Cấu trúc bảng:

```SQL
CREATE TABLE chat_history (
    id UUID PRIMARY KEY,
    user_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    intent TEXT,
    entities JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    context_summary TEXT
);

-- Index cho truy vấn nhanh
CREATE INDEX idx_user_id ON chat_history(user_id);
CREATE INDEX idx_created_at ON chat_history(created_at);
```

## 2\. Luồng Xử Lý Chi Tiết Với Công Nghệ

### 2.1. Quy Trình Xử Lý Truy Vấn Từ Người Dùng

Bước 1: Tiếp nhận và định tuyến (Messaging Service → Finance Service)

- Input: `/news tổng hợp thông tin thị trường, crypto hôm nay`
- Xử lý:
  - Xác định command: `/news`
  - Trích xuất nội dung: `tổng hợp thông tin thị trường, crypto hôm nay`
  - Định tuyến đến Information Agent

Bước 2: Phân tích truy vấn (Query Analysis Module)

- Output JSON:

```Python
{
  "main_topic": "thị trường tài chính và crypto",
  "entities": ["thị trường", "crypto"],
  "intent": "tổng hợp tin tức",
  "time_range": "hôm nay"
}
```

Bước 3: Tìm kiếm thông tin (Brave Search API)

- Truy vấn tối ưu: `thị trường tài chính crypto tin tức mới nhất trong hôm nay`
- Kết quả: 10 URL từ các nguồn uy tín (cafef.vn, vietstock.vn, coindesk.com)

Bước 4: Thu thập và xử lý nội dung (Crawl4AI + Docling)

- Lọc 5 URL chất lượng cao nhất
- Trích xuất nội dung chính, chuẩn hóa số liệu
- Phát hiện thực thể và xu hướng

Bước 5: Tạo phản hồi (Content Processing Module)

- Kết hợp:
  - Dữ liệu từ scraping
  - Thông tin từ Pinecone (kiến thức nền)
  - Ngữ cảnh từ Redis (lịch sử hội thoại)
- Output mẫu:

```
BẢNG TỔNG HỢP THỊ TRƯỜNG TÀI CHÍNH & CRYPTO HÔM NAY

| Chỉ số       | Giá trị hiện tại | Thay đổi | Nhận định       |
|--------------|------------------|----------|-----------------|
| VN-Index     | 1,245.67         | +0.8%    | Tích cực        |
| BTC          | $26,450          | -1.2%    | Điều chỉnh      |
| USD/VND      | 24,500           | 0.0%     | Ổn định         |

PHÂN TÍCH:
- Thị trường chứng khoán Việt Nam tăng nhẹ do dòng tiền đầu tư nước ngoài...
- Crypto giảm nhẹ do tâm lý chốt lời sau đợt tăng trước đó...

NGUỒN: Cafef, Vietstock, CoinDesk (cập nhật 15/10/2023)
```

Bước 6: Lưu trữ và tối ưu

- Cache kết quả với TTL 15 phút
- Lưu embedding vào Pinecone
- Cập nhật lịch sử trò chuyện trong Supabase

### 2.2. Quản Lý Ngữ Cảnh Với LangChain Memory

Triển khai đa tầng:

```Python
from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory

# Khởi tạo Redis làm backend
chat_history = RedisChatMessageHistory(
    session_id=f"user:{user_id}",
    url=os.getenv("REDIS_URL"),
    key_prefix="finance:chat_history:"
)

# Memory cho phiên hiện tại
memory = ConversationSummaryBufferMemory(
    llm=summary_llm,  # LLM nhỏ cho tóm tắt
    chat_history=chat_history,
    max_token_limit=1000,
    memory_key="chat_history",
    return_messages=True
)

# Tích hợp vào quy trình xử lý
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=financial_analyst_llm,
    retriever=pinecone_retriever,
    memory=memory,
    return_source_documents=True
)
```

Chiến lược quản lý ngữ cảnh tài chính:

- Tóm tắt thông minh: Chỉ lưu thông tin quan trọng (chỉ số, xu hướng, cảnh báo)
- Phân tầng thông tin:
  - Thông tin thời sự (giá cả): TTL 24h
  - Phân tích chuyên sâu: TTL 7 ngày
  - Thông tin nền tảng: Lưu trữ lâu dài trong Pinecone

## 3\. Phân Tích Rủi Ro và Giải Pháp

### 3.1. Rủi Ro Chính và Giải pháp

- Giới hạn API của Brave Search:
  - Triển khai hệ thống cache hiệu quả
  - Sử dụng multiple API keys với round-robin
  - Xây dựng cơ chế fallback sang Google Custom Search
- Chất lượng thông tin không đảm bảo:
  - Danh sách trắng nguồn tin
  - Xây dựng hệ thống đánh giá độ tin cậy
  - Kết hợp nhiều nguồn để cross-verify
- Độ trễ xử lý cao:
  - Xử lý bất đồng bộ các bước nặng
  - Tiền cache các chủ đề phổ biến
  - Tối ưu số lượng URL cần scrape
- Thông tin lỗi thời:
  - TTL ngắn cho cache
  - Ưu tiên nguồn có ngày đăng mới nhất
  - Cảnh báo người dùng nếu thông tin > 24h

### 3.2. Chiến Lược Xử Lý Dữ Liệu Tài Chính

Quy trình đảm bảo chất lượng:

1.  Source Validation:

    - Chỉ chấp nhận từ danh sách 20 nguồn uy tín đã được xác minh
    - Đánh giá độ tin cậy theo thang điểm 1-5

2.  Data Verification:

    - Cross-check số liệu giữa ít nhất 2 nguồn
    - Phát hiện mâu thuẫn tự động

3.  Temporal Validation:

    - Xác minh ngày đăng của bài viết
    - Ưu tiên thông tin trong vòng 24h

4.  Financial Entity Recognition:

    - Sử dụng custom NER model cho thực thể tài chính
    - Chuẩn hóa tên công ty/cổ phiếu (SSI → CTCP Chứng khoán SSI)
