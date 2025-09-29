# Phân Tích và Thiết Kế Hệ Thống Chatbot Agent Tài Chính

## 1\. Cấu Trúc Kho Lưu Trữ Chi Tiết

Tôi đã mở rộng cấu trúc kho lưu trữ dựa trên yêu cầu của hệ thống, tập trung vào thư mục `finagent/app`, đồng thời bổ sung các thành phần cần thiết cho lưu trữ dữ liệu tài chính dài hạn:

```
finagent/
├── data/
│   ├── prompts/                # Templates cho prompt engineering
│   │   ├── query_analysis.yaml # Prompt cho phân tích truy vấn
│   │   ├── financial_qa.yaml   # Prompt cho trả lời tài chính
│   │   └── intent_classification.yaml # Prompt cho phân loại intent
│   ├── config/                 # Cấu hình dữ liệu
│   │   ├── sources_whitelist.txt # Danh sách trắng nguồn tin
│   │   └── api_keys.example.json # Mẫu cấu hình API keys
│   └── time_series/            # Schema cho lưu trữ dữ liệu thời gian thực
│       └── financial_schema.sql # Schema cho time-series DB
├── app/
│   ├── agents/                 # Các agent chính
│   │   ├── __init__.py
│   │   ├── base.py             # Lớp cơ sở cho các agent
│   │   ├── information.py      # Information Agent
│   │   ├── stock.py            # Stock Agent (sẽ phát triển sau)
│   │   └── crypto.py           # Crypto Agent (sẽ phát triển sau)
│   ├── apis/                   # API wrappers
│   │   ├── __init__.py
│   │   ├── brave_search.py     # Wrapper cho Brave Search API
│   │   ├── crawl4ai.py         # Wrapper cho Crawl4AI
│   │   ├── vector_db.py        # Wrapper cho Pinecone
│   │   ├── time_series_db.py   # Wrapper cho lưu trữ dữ liệu thời gian thực
│   │   └── supabase.py         # Wrapper cho Supabase
│   ├── configs/                # Cấu hình hệ thống
│   │   ├── __init__.py
│   │   ├── settings.py         # Cài đặt hệ thống
│   │   ├── routing.yaml        # Cấu hình định tuyến lệnh
│   │   └── cache_config.py     # Cấu hình cache
│   ├── core/                   # Lõi hệ thống
│   │   ├── __init__.py
│   │   ├── router.py           # Agent Router
│   │   ├── memory.py           # Quản lý ngữ cảnh
│   │   ├── cache.py            # Cache system
│   │   ├── time_series_db.py   # Time-series database
│   │   ├── user_identity.py    # Quản lý identity đa nền tảng
│   │   └── security.py         # Bảo mật API keys
│   ├── models/                 # Mô hình dữ liệu
│   │   ├── __init__.py
│   │   ├── query.py            # Mô hình truy vấn
│   │   ├── response.py         # Mô hình phản hồi
│   │   └── financial_entities.py # Mô hình thực thể tài chính
│   ├── tools/                  # Các công cụ hỗ trợ
│   │   ├── __init__.py
│   │   ├── web_search.py       # Công cụ tìm kiếm web
│   │   ├── web_scraping.py     # Công cụ scraping
│   │   ├── content_processing.py # Xử lý nội dung
│   │   └── query_analyzer.py   # Phân tích truy vấn
│   └── utils/                  # Tiện ích
│       ├── __init__.py
│       ├── logger.py           # Logging
│       ├── validators.py       # Xác thực dữ liệu
│       ├── rate_limiter.py     # Rate limiting
│       └── financial_utils.py  # Tiện ích tài chính
├── main.py
├── .env
├── requirements.txt
└── Dockerfile
```

## 2\. Sơ Đồ Lớp (Class Diagram)

### 2.1. Information Agent và Các Module Liên Quan

#### Lớp cơ sở (base.py)

```Python
"""
Lớp cơ sở cho tất cả các agent
"""
class BaseAgent:
    def __init__(self, config: dict):
        self.config = config

    async def process(self, query: QueryModel) -> ResponseModel:
        """
        Xử lý truy vấn và trả về phản hồi
        """
        raise NotImplementedError()
```

#### Information Agent (information.py)

```Python
"""
Agent cung cấp thông tin tài chính tổng hợp
"""
class InformationAgent(BaseAgent):
    def __init__(self, config: dict, query_analyzer: QueryAnalyzer,
                 web_search_tool: WebSearchTool, web_scraping_tool: WebScrapingTool,
                 content_processor: ContentProcessor, time_series_db: TimeSeriesDB):
        super().__init__(config)
        self.query_analyzer = query_analyzer
        self.web_search_tool = web_search_tool
        self.web_scraping_tool = web_scraping_tool
        self.content_processor = content_processor
        self.time_series_db = time_series_db  # Bổ sung để lưu trữ dữ liệu dài hạn

    async def process(self, query: QueryModel) -> ResponseModel:
        # 1. Phân tích truy vấn
        analysis_result = await self.query_analyzer.analyze(query.text)

        # 2. Tìm kiếm thông tin
        search_results = await self.web_search_tool.search(analysis_result)

        # 3. Thu thập nội dung
        scraped_content = await self.web_scraping_tool.scrape(search_results.urls)

        # 4. Lưu trữ dữ liệu thời gian thực (bổ sung)
        await self._store_time_series_data(scraped_content)

        # 5. Xử lý nội dung
        response = await self.content_processor.process(query, analysis_result, scraped_content)

        return response

    async def _store_time_series_data(self, scraped_content: ScrapedContent):
        """
        Lưu trữ dữ liệu tài chính vào time-series DB
        """
        # Trích xuất và lưu trữ các điểm dữ liệu quan trọng
        for entity in scraped_content.financial_entities:
            data_point = {
                "timestamp": datetime.now(),
                "entity_type": entity.type,
                "entity_id": entity.name,
                "value": entity.value,
                "change": entity.change,
                "change_percent": entity.change_percent,
                "source": scraped_content.source,
                "metadata": {
                    "reliability_score": scraped_content.reliability_score,
                    "analysis_result": scraped_content.analysis_result
                }
            }
            await self.time_series_db.store_financial_data(data_point)
```

#### Query Analyzer (query_analyzer.py)

```Python
"""
Module phân tích truy vấn người dùng
"""
class QueryAnalyzer:
    def __init__(self, llm: LLM, prompt_template: str):
        self.llm = llm
        self.prompt_template = prompt_template

    async def analyze(self, query_text: str) -> dict:
        """
        Phân tích truy vấn và trả về kết quả dưới dạng JSON
        """
        # Tiền xử lý truy vấn
        processed_query = self._preprocess(query_text)

        # Tạo prompt
        prompt = self._create_prompt(processed_query)

        # Gọi LLM
        raw_result = await self.llm.generate(prompt)

        # Xác thực và xử lý kết quả
        return self._validate_and_process(raw_result)

    def _preprocess(self, query_text: str) -> str:
        """Chuẩn hóa văn bản, loại bỏ stop words"""
        pass

    def _create_prompt(self, processed_query: str) -> str:
        """Tạo prompt từ template"""
        pass

    def _validate_and_process(self, raw_result: str) -> dict:
        """Xác thực JSON và xử lý kết quả"""
        pass
```

#### Web Search Tool (web_search.py)

```Python
"""
Công cụ tìm kiếm web sử dụng Brave Search API
"""
class WebSearchTool:
    def __init__(self, api_key: str, config: dict = None):
        self.api_key = api_key
        self.config = config or {
            "count": 10,
            "freshness": "day",
            "country": "VN",
            "text_decorations": False
        }
        self.brave_search = BraveSearch(api_key=self.api_key, search_kwargs=self.config)
        self.request_queue = asyncio.Queue()  # Bổ sung cho xử lý queue
        self.processing_task = asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        """Xử lý các request trong queue với rate limit chính xác (1 request/giây)"""
        while True:
            query, result_queue = await self.request_queue.get()
            try:
                # Đảm bảo tuân thủ 1 request/giây
                await asyncio.sleep(1.1)  # Margin nhỏ để đảm bảo không vượt giới hạn
                results = await self._call_brave_api(query)
                result_queue.put_nowait(results)
            except Exception as e:
                result_queue.put_nowait(None)
                system_logger.error(f"Queue processing error: {str(e)}")
            finally:
                self.request_queue.task_done()

    async def search(self, analysis_result: dict) -> SearchResults:
        """
        Thực hiện tìm kiếm với truy vấn được tối ưu
        """
        optimized_query = self._optimize_query(analysis_result)

        # Sử dụng queue mechanism thay vì decorator trực tiếp
        result_queue = asyncio.Queue(maxsize=1)
        await self.request_queue.put((optimized_query, result_queue))

        try:
            results = await asyncio.wait_for(result_queue.get(), timeout=15.0)
            if results is None:
                return self._fallback_search(optimized_query)
            return self._process_results(results)
        except asyncio.TimeoutError:
            system_logger.warning("Web search timed out")
            return self._fallback_search(optimized_query)

    def _optimize_query(self, analysis_result: dict) -> str:
        """
        Tối ưu hóa truy vấn tìm kiếm dựa trên kết quả phân tích
        """
        search_terms = [
            analysis_result['main_topic'],
            *analysis_result['entities'][:2],  # Chỉ lấy tối đa 2 thực thể quan trọng nhất
            "tin tức mới nhất"
        ]

        # Chỉ thêm time_range nếu thực sự cần
        if analysis_result.get('time_range') in ["hôm nay", "today"]:
            search_terms.append("trong 24h")

        return " ".join(search_terms)

    async def _call_brave_api(self, query: str) -> dict:
        """
        Gọi Brave Search API với cơ chế retry
        """
        # Loại bỏ retry decorator, để queue xử lý rate limiting
        raw_results = self.brave_search.run(query)
        return self._parse_brave_results(raw_results)

    def _parse_brave_results(self, raw_results: str) -> dict:
        """Phân tích kết quả thô từ Brave Search API"""
        try:
            # Brave trả về kết quả dưới dạng JSON string
            return json.loads(raw_results)
        except json.JSONDecodeError:
            # Xử lý trường hợp kết quả không phải JSON
            system_logger.warning("Brave API returned non-JSON response")
            return {"results": []}

    def _process_results(self, results: dict) -> SearchResults:
        """Xử lý kết quả thô từ API"""
        # Lọc và xử lý kết quả
        pass

    def _fallback_search(self, query: str) -> SearchResults:
        """
        Cơ chế fallback khi Brave Search API gặp lỗi
        - Sử dụng Google Custom Search hoặc cơ sở dữ liệu cache
        """
        system_logger.warning("Using fallback search mechanism")
        # Trong thực tế, sẽ triển khai fallback thực sự
        return SearchResults([], [], [], [])
```

#### Web Scraping Tool (web_scraping.py)

```Python
"""
Công cụ thu thập nội dung từ web sử dụng Crawl4AI
"""
class WebScrapingTool:
    def __init__(self, sources_whitelist: list = None):
        self.sources_whitelist = sources_whitelist or self._load_whitelist()

    async def scrape(self, urls: list) -> ScrapedContent:
        """
        Thu thập nội dung từ danh sách URL
        """
        # Lọc URL theo danh sách trắng
        filtered_urls = self._filter_urls(urls)

        # Thu thập nội dung
        raw_contents = await self._crawl_urls(filtered_urls)

        # Xử lý nội dung
        return self._process_contents(raw_contents)

    def _filter_urls(self, urls: list) -> list:
        """
        Lọc URL theo danh sách trắng nguồn tin
        """
        return [url for url in urls if self._is_trusted_source(url)]

    def _is_trusted_source(self, url: str) -> bool:
        """
        Kiểm tra xem nguồn có đáng tin cậy không
        """
        domain = self._extract_domain(url)
        return domain in self.sources_whitelist

    async def _crawl_urls(self, urls: list) -> list:
        """
        Sử dụng Crawl4AI để thu thập nội dung
        """
        # Triển khai việc gọi Crawl4AI
        pass

    def _process_contents(self, raw_contents: list) -> ScrapedContent:
        """
        Xử lý nội dung đã thu thập
        """
        # Sử dụng Docling để xử lý văn bản
        # Xác định thực thể tài chính
        # Chuẩn hóa số liệu
        pass

    def _load_whitelist(self) -> list:
        """
        Tải danh sách trắng nguồn tin
        """
        # Đọc từ file sources_whitelist.txt
        pass
```

#### Content Processor (content_processing.py)

```Python
"""
Module xử lý nội dung và tạo phản hồi
"""
class ContentProcessor:
    def __init__(self, llm: LLM, vector_db: VectorDB, memory: ConversationMemory,
                 time_series_db: TimeSeriesDB, prompt_template: str):
        self.llm = llm
        self.vector_db = vector_db
        self.memory = memory
        self.time_series_db = time_series_db  # Bổ sung để truy vấn dữ liệu lịch sử
        self.prompt_template = prompt_template

    async def process(self, query: QueryModel, analysis_result: dict,
                     scraped_content: ScrapedContent) -> ResponseModel:
        """
        Xử lý nội dung và tạo phản hồi cho người dùng
        """
        # Lấy ngữ cảnh trò chuyện
        chat_history = await self.memory.get_history(query.user_id)

        # Tìm kiếm thông tin nền tảng từ Vector DB
        relevant_docs = await self.vector_db.search(
            query=query.text,
            filters={"topic": analysis_result['main_topic']}
        )

        # Truy vấn dữ liệu lịch sử (bổ sung)
        historical_data = await self._get_historical_data(analysis_result)

        # Tạo prompt
        prompt = self._create_prompt(query, analysis_result, scraped_content,
                                     relevant_docs, chat_history, historical_data)

        # Sinh phản hồi
        response_text = await self.llm.generate(prompt)

        # Định dạng phản hồi
        return self._format_response(response_text, scraped_content.sources)

    async def _get_historical_data(self, analysis_result: dict) -> dict:
        """
        Lấy dữ liệu lịch sử cho phân tích xu hướng
        """
        historical_data = {}

        # Truy vấn dữ liệu theo từng thực thể
        for entity in analysis_result['entities']:
            # Giả sử có hàm get_historical_data cho từng entity
            historical_data[entity] = await self.time_series_db.get_historical_data(
                entity_id=entity,
                entity_type="financial",  # Có thể xác định loại thực thể
                start_date=datetime.now() - timedelta(days=7),
                end_date=datetime.now()
            )

        return historical_data

    def _create_prompt(self, query: QueryModel, analysis_result: dict,
                      scraped_content: ScrapedContent, relevant_docs: list,
                      chat_history: list, historical_data: dict) -> str:
        """
        Tạo prompt cho LLM
        """
        # Điền vào template với các biến
        pass

    def _format_response(self, response_text: str, sources: list) -> ResponseModel:
        """
        Định dạng phản hồi theo cấu trúc mong muốn
        """
        # Tạo bảng tóm tắt, thêm nguồn tham khảo
        pass
```

### 2.2. Agent Router và Hỗ Trợ

#### Router (router.py)

```Python
"""
Router định tuyến truy vấn đến các agent phù hợp
"""
class AgentRouter:
    def __init__(self, config: dict, command_config: dict,
                 intent_classifier: IntentClassifier):
        self.config = config
        self.command_config = command_config  # Từ routing.yaml
        self.intent_classifier = intent_classifier

    async def route(self, query: QueryModel) -> BaseAgent:
        """
        Định tuyến truy vấn đến agent phù hợp
        - Ưu tiên định tuyến theo lệnh (/command)
        - Nếu không có lệnh, sử dụng intent classification
        """
        if query.has_command:
            return self._route_by_command(query)

        # Nếu không có lệnh, phân tích intent
        intent = await self.intent_classifier.classify(query.text)
        return self._route_by_intent(intent)

    def _route_by_command(self, query: QueryModel) -> BaseAgent:
        """
        Định tuyến dựa trên lệnh (/command)
        """
        command = query.command
        if command in self.command_config['commands']:
            agent_name = self.command_config['commands'][command]['agent']
            return self._get_agent_instance(agent_name)
        return self._get_default_agent()

    async def _route_by_intent(self, intent: str) -> BaseAgent:
        """
        Định tuyến dựa trên intent
        """
        # Sử dụng cấu hình từ routing.yaml
        if intent in self.command_config['intents']:
            agent_name = self.command_config['intents'][intent]
            return self._get_agent_instance(agent_name)
        return self._get_default_agent()

    def _get_agent_instance(self, agent_name: str) -> BaseAgent:
        """
        Lấy instance của agent
        """
        # Triển khai dependency injection
        pass

    def _get_default_agent(self) -> BaseAgent:
        """
        Lấy agent mặc định
        """
        return self._get_agent_instance(self.config['default_agent'])
```

#### Intent Classifier (intent_classification.py)

```Python
"""
Classifier phân loại intent của truy vấn
"""
class IntentClassifier:
    def __init__(self, llm: LLM, prompt_template: str):
        self.llm = llm
        self.prompt_template = prompt_template

    async def classify(self, query_text: str) -> str:
        """
        Phân loại intent của truy vấn
        """
        prompt = self._create_prompt(query_text)
        result = await self.llm.generate(prompt)
        return self._parse_result(result)

    def _create_prompt(self, query_text: str) -> str:
        # Tạo prompt từ template
        pass

    def _parse_result(self, llm_result: str) -> str:
        # Parse kết quả để lấy intent
        pass
```

#### Memory (memory.py)

```Python
"""
Quản lý ngữ cảnh trò chuyện
"""
class ConversationMemory:
    def __init__(self, redis_client: Redis, llm: LLM,
                 max_token_limit: int = 1000):
        self.redis_client = redis_client
        self.llm = llm
        self.max_token_limit = max_token_limit

    async def get_history(self, user_id: str) -> list:
        """
        Lấy lịch sử trò chuyện cho người dùng
        - Tự động tóm tắt nếu vượt quá giới hạn token
        """
        # Lấy từ Redis
        # Tóm tắt nếu cần thiết
        pass

    async def update_history(self, user_id: str, query: str, response: str):
        """
        Cập nhật lịch sử trò chuyện
        """
        # Thêm vào Redis
        # Quản lý kích thước
        pass

    def _summarize_context(self, history: list) -> str:
        """
        Tóm tắt ngữ cảnh khi vượt quá giới hạn token
        """
        # Sử dụng LLM để tóm tắt
        pass
```

#### Time Series Database (time_series_db.py)

```Python
"""
Module lưu trữ dữ liệu tài chính dạng time-series
- Thu thập và lưu trữ dữ liệu hàng ngày cho phân tích xu hướng
- Hỗ trợ truy vấn theo khoảng thời gian (tuần/tháng/quý/năm)
"""
class TimeSeriesDB:
    """
    Quản lý lưu trữ và truy vấn dữ liệu tài chính theo thời gian
    """
    def __init__(self, supabase_client=None):
        from .settings import settings
        import supabase

        if supabase_client is None:
            self.supabase = supabase.create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
        else:
            self.supabase = supabase_client

        self.logger = setup_logger("time_series_db")

    def store_financial_data(self, data_point: dict):
        """
        Lưu trữ điểm dữ liệu tài chính

        data_point format:
        {
            "timestamp": ISO8601,
            "entity_type": "stock|crypto|forex",
            "entity_id": "BTC|ETH|SSI|VCB",
            "value": float,
            "change": float,
            "change_percent": float,
            "source": "cafef|coindesk|...",
            "metadata": {additional info}
        }
        """
        try:
            self.supabase.table("financial_time_series").insert(data_point).execute()
            self.logger.info(f"Stored financial data point for {data_point['entity_id']}")
        except Exception as e:
            self.logger.error(f"Error storing financial data: {str(e)}")

    def get_historical_data(self, entity_id: str, entity_type: str,
                           start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Lấy dữ liệu lịch sử cho phân tích xu hướng
        """
        # Triển khai truy vấn Supabase và chuyển đổi thành DataFrame
        pass

    def aggregate_data(self, entity_id: str, entity_type: str,
                      period: str = "daily") -> pd.DataFrame:
        """
        Tổng hợp dữ liệu theo khoảng thời gian (daily/weekly/monthly)
        """
        # Triển khai aggregate query
        pass
```

#### User Identity Manager (user_identity.py)

```Python
"""
Module quản lý identity của người dùng từ các nền tảng khác nhau
- Chuyển đổi user_id từ các nền tảng thành định dạng chung
- Quản lý mapping giữa các định danh
"""
class UserIdentityManager:
    """
    Quản lý identity của người dùng từ nhiều nền tảng
    """
    def __init__(self):
        self.platform_mapping = {}
        self.logger = system_logger.getChild("UserIdentity")

    def normalize_user_id(self, platform: str, platform_user_id: str) -> str:
        """
        Chuẩn hóa user_id từ nền tảng thành internal user_id

        Ví dụ:
        - Telegram: "123456789" → internal ID
        - Web: "user@example.com" → internal ID
        """
        # Tạo internal ID dựa trên platform và platform_user_id
        internal_id = self._generate_internal_id(platform, platform_user_id)

        # Lưu mapping cho việc tra cứu ngược
        self.platform_mapping[(platform, platform_user_id)] = internal_id

        return internal_id

    def get_platform_user_id(self, internal_id: str, platform: str) -> str:
        """
        Lấy platform user_id từ internal ID
        """
        for (plat, plat_user_id), int_id in self.platform_mapping.items():
            if int_id == internal_id and plat == platform:
                return plat_user_id
        return None

    def _generate_internal_id(self, platform: str, platform_user_id: str) -> str:
        """
        Tạo internal ID duy nhất từ platform và platform_user_id
        """
        # Sử dụng SHA-256 để tạo ID cố định từ cặp (platform, user_id)
        hash_input = f"{platform}:{platform_user_id}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def is_valid_user_id(self, user_id: str) -> bool:
        """
        Kiểm tra xem user_id có phải là internal ID hợp lệ không
        """
        # Internal ID là SHA-256 hash (64 ký tự hex)
        return len(user_id) == 64 and all(c in '0123456789abcdef' for c in user_id.lower())

# Singleton instance
user_identity = UserIdentityManager()
```

### 2.3. Mô Hình Dữ Liệu

#### QueryModel (query.py)

```Python
"""
Mô hình đại diện cho truy vấn của người dùng
"""
class QueryModel:
    def __init__(self, platform_user_id: str, platform: str, text: str,
                 timestamp: datetime = None):
        self.platform = platform
        self.platform_user_id = platform_user_id
        # Chuẩn hóa user_id sử dụng UserIdentityManager
        self.user_id = user_identity.normalize_user_id(platform, platform_user_id)
        self.text = text
        self.timestamp = timestamp or datetime.now()
        self.command = self._extract_command()
        self.has_command = bool(self.command)

    def _extract_command(self) -> Optional[str]:
        """
        Trích xuất lệnh từ truy vấn (nếu có)
        """
        # Sử dụng regex để tìm lệnh (/command)
        if self.text.startswith('/'):
            parts = self.text.split(maxsplit=1)
            return parts[0]
        return None

    def get_clean_text(self) -> str:
        """
        Lấy nội dung truy vấn sau khi loại bỏ lệnh
        """
        if self.has_command:
            return self.text[len(self.command):].strip()
        return self.text

    def to_dict(self) -> dict:
        """
        Chuyển đổi thành dictionary cho logging và lưu trữ
        """
        return {
            "user_id": self.user_id,
            "platform": self.platform,
            "platform_user_id": self.platform_user_id,
            "text": self.text,
            "timestamp": self.timestamp.isoformat(),
            "command": self.command,
            "has_command": self.has_command
        }
```

#### ResponseModel (response.py)

```Python
"""
Mô hình đại diện cho phản hồi của hệ thống
"""
class ResponseModel:
    def __init__(self, query: QueryModel,
                 response_text: str, sources: list,
                 metadata: dict = None):
        self.query_id = str(uuid.uuid4())
        self.user_id = query.user_id
        self.platform = query.platform
        self.response_text = response_text
        self.sources = sources
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> dict:
        """
        Chuyển đổi thành dictionary cho logging và lưu trữ
        """
        return {
            "query_id": self.query_id,
            "user_id": self.user_id,
            "platform": self.platform,
            "response_text": self.response_text,
            "sources": self.sources,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }
```

#### Financial Entities (financial_entities.py)

```Python
"""
Thực thể tài chính (cổ phiếu, tiền điện tử, chỉ số)
"""
class FinancialEntity:
    def __init__(self, name: str, type: str, value: float = None,
                 change: float = None, change_percent: float = None,
                 timestamp: datetime = None):
        if not validate_financial_entity(type):
            raise ValueError(f"Invalid financial entity type: {type}")

        self.name = name
        self.type = type  # stock, crypto, forex, index
        self.value = value
        self.change = change
        self.change_percent = change_percent
        self.timestamp = timestamp or datetime.now()

    @classmethod
    def from_text(cls, text: str) -> list:
        """
        Trích xuất thực thể tài chính từ văn bản
        - Sử dụng custom NER model (sẽ được triển khai sau)
        - Hiện tại sử dụng rule-based approach đơn giản
        """
        entities = []

        # Ví dụ đơn giản về rule-based extraction
        if "SSI" in text or "Chứng khoán SSI" in text:
            entities.append(cls("SSI", "stock"))
        if "BTC" in text or "Bitcoin" in text:
            entities.append(cls("BTC", "crypto"))

        return entities

    def normalize(self) -> dict:
        """
        Chuẩn hóa tên và giá trị cho việc hiển thị
        - Chuyển đổi mã cổ phiếu thành tên đầy đủ
        - Định dạng số liệu tài chính
        """
        normalized = {
            "name": self.name,
            "type": self.type,
            "display_value": self._format_value(),
            "trend": self._determine_trend()
        }
        return normalized

    def _format_value(self) -> str:
        """Định dạng giá trị cho hiển thị"""
        if self.value is None:
            return "N/A"

        if self.type == "stock":
            return f"{self.value:,.0f} VND"
        elif self.type == "crypto":
            return f"${self.value:,.2f}"
        return str(self.value)

    def _determine_trend(self) -> str:
        """Xác định xu hướng dựa trên thay đổi giá"""
        if self.change_percent is None:
            return "neutral"
        return "up" if self.change_percent > 0 else "down"
```

## 3\. Sơ Đồ Trình Tự (Sequence Diagram)

Dưới đây là mô tả chi tiết luồng tương tác giữa người dùng, Telegram bot và Agent:

```
Người dùng -> Telegram Bot: Gửi tin nhắn "/news tổng hợp thông tin thị trường, crypto hôm nay"
Telegram Bot -> Messaging Service: Xử lý tin nhắn, chuẩn hóa {platform_user_id, platform, query}
Messaging Service -> Finance Service: Chuyển tiếp truy vấn đã chuẩn hóa
Finance Service -> Agent Router: Yêu cầu định tuyến
Agent Router --> Finance Service: Trả về Information Agent

Finance Service -> Information Agent: process(query)
Information Agent -> Query Analyzer: analyze(query.text)
Query Analyzer --> Information Agent: analysis_result {main_topic, entities, intent, time_range}

Information Agent -> Web Search Tool: search(analysis_result)
Web Search Tool -> Brave Search API: Gửi yêu cầu tìm kiếm với query tối ưu (qua queue)
Brave Search API --> Web Search Tool: Trả về 10 kết quả tìm kiếm
Web Search Tool --> Information Agent: search_results {urls, titles, snippets}

Information Agent -> Web Scraping Tool: scrape(search_results.urls)
Web Scraping Tool -> Crawl4AI: Thu thập nội dung từ các URL (chỉ nguồn tin cậy)
Crawl4AI --> Web Scraping Tool: Trả về nội dung đã thu thập
Web Scraping Tool --> Information Agent: scraped_content {main_content, metadata}

Information Agent -> Time Series DB: store_financial_data (lưu trữ dữ liệu thời gian thực)
Time Series DB --> Information Agent: xác nhận lưu trữ

Information Agent -> Content Processor: process(query, analysis_result, scraped_content)
Content Processor -> Vector DB: Tìm kiếm thông tin nền với filters {topic: main_topic}
Vector DB --> Content Processor: relevant_docs (từ Pinecone)
Content Processor -> Memory: Lấy lịch sử trò chuyện cho user_id
Memory --> Content Processor: chat_history (đã tóm tắt)
Content Processor -> Time Series DB: get_historical_data (lấy dữ liệu lịch sử)
Time Series DB --> Content Processor: historical_data (dữ liệu thời gian thực)
Content Processor -> LLM: Tạo phản hồi với prompt đã tạo
LLM --> Content Processor: response_text (định dạng bảng)
Content Processor --> Information Agent: response {response_text, sources}

Information Agent --> Finance Service: response
Finance Service --> Messaging Service: response
Messaging Service --> Telegram Bot: response
Telegram Bot --> Người dùng: Hiển thị kết quả dưới dạng bảng
```

### Chi Tiết Luồng Xử Lý Với Ví Dụ Cụ Thể

Truy vấn mẫu: `/news tổng hợp thông tin thị trường, crypto hôm nay`

1.  Phân tích truy vấn:

    - Input: "tổng hợp thông tin thị trường, crypto hôm nay"
    - Output:

```Json
{
  "main_topic": "thị trường tài chính và crypto",
  "entities": ["thị trường", "crypto"],
  "intent": "tổng hợp tin tức",
  "time_range": "hôm nay"
}
```

2.  Tối ưu hóa truy vấn tìm kiếm:

    - Chỉ lấy 2 thực thể quan trọng nhất
    - Kết hợp các thành phần: `thị trường tài chính crypto tin tức mới nhất trong 24h`

3.  Kết quả tìm kiếm:

    - 10 URL từ các nguồn: cafef.vn, vietstock.vn, coindesk.com, v.v.

4.  Quá trình scraping:

    - Lọc 5 URL chất lượng cao nhất từ danh sách trắng
    - Trích xuất nội dung chính, chuẩn hóa số liệu
    - Phát hiện thực thể và xu hướng
    - Lưu trữ dữ liệu thời gian thực vào Time Series DB

5.  Tạo phản hồi:

    - Kết hợp dữ liệu từ scraping, thông tin nền từ Pinecone và ngữ cảnh trò chuyện
    - Bổ sung dữ liệu lịch sử từ Time Series DB (xu hướng 7 ngày qua)
    - Output mẫu:

```
BẢNG TỔNG HỢP THỊ TRƯỜNG TÀI CHÍNH & CRYPTO HÔM NAY

| Chỉ số       | Giá trị hiện tại | Thay đổi | Nhận định       | Xu hướng 7 ngày |
|--------------|------------------|----------|-----------------|----------------|
| VN-Index     | 1,245.67         | +0.8%    | Tích cực        | Tăng nhẹ       |
| BTC          | $26,450          | -1.2%    | Điều chỉnh      | Giảm           |
| USD/VND      | 24,500           | 0.0%     | Ổn định         | Ổn định        |

PHÂN TÍCH:
- Thị trường chứng khoán Việt Nam tăng nhẹ do dòng tiền đầu tư nước ngoài...
- Crypto giảm nhẹ do tâm lý chốt lời sau đợt tăng trước đó...

XU HƯỚNG 7 NGÀY QUA:
- VN-Index: Tăng 2.5% trong tuần qua, đạt đỉnh mới
- BTC: Biến động mạnh với mức giảm 5% trong 3 ngày trước

NGUỒN: Cafef, Vietstock, CoinDesk (cập nhật 15/10/2023)
```

1.  Lưu trữ và tối ưu:
    - Cache kết quả với TTL 15 phút (Redis)
    - Lưu embedding vào Pinecone cho RAG
    - Cập nhật lịch sử trò chuyện trong Supabase
    - Lưu trữ dữ liệu thời gian thực cho phân tích dài hạn

## 4\. Thiết Kế Logic Cho Hệ Thống

### 1\. Thứ Tự Triển Khai Các Tệp

#### Giai Đoạn 1: Thiết Lập Cơ Sở (Foundation Setup)

1.1 `finagent/app/configs/settings.py`

```Python
# Mô tả: Thiết lập cấu hình hệ thống trung tâm
# Thứ tự triển khai: 1 (đầu tiên)
# Phụ thuộc: Không có

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Lớp cấu hình trung tâm cho toàn bộ hệ thống
    - Quản lý tất cả các biến môi trường
    - Cung cấp các thiết lập mặc định
    - Đảm bảo tính nhất quán trong toàn hệ thống
    """
    def __init__(self):
        # Cấu hình chung
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        # Giải thích: Xác định môi trường chạy ứng dụng (development, staging, production)
        # Đây là best practice trong phát triển phần mềm, giúp điều chỉnh behavior dựa trên môi trường

        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        # Giải thích: Xác định mức độ logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        # Trong development thường dùng DEBUG, trong production dùng INFO hoặc WARNING

        # Cấu hình API
        self.BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")

        self.PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
        self.PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
        # Giải thích: Trong Pinecone, "environment" (còn gọi là "region") là nơi các index được lưu trữ
        # Ví dụ: gcp-starter, us-west1-gcp, eu-west1-gcp
        # Bạn có thể tìm thấy thông tin này trong dashboard Pinecone khi tạo index

        # Cấu hình database
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.SUPABASE_URL = os.getenv("SUPABASE_URL")
        self.SUPABASE_KEY = os.getenv("SUPABASE_KEY")

        # Cấu hình cache
        self.CACHE_TTL_NEWS = int(os.getenv("CACHE_TTL_NEWS", "900"))  # 15 phút
        self.CACHE_TTL_MARKET = int(os.getenv("CACHE_TTL_MARKET", "300"))  # 5 phút

        # Cấu hình agent
        self.DEFAULT_AGENT = os.getenv("DEFAULT_AGENT", "information_agent")
        self.MAX_TOKEN_LIMIT = int(os.getenv("MAX_TOKEN_LIMIT", "1000"))

# Khởi tạo singleton instance
settings = Settings()
```

1.2 `finagent/app/utils/logger.py`

```Python
# Mô tả: Hệ thống logging trung tâm
# Thứ tự triển khai: 2
# Phụ thuộc: settings.py

import logging
from .settings import settings

def setup_logger(name: str) -> logging.Logger:
    """
    Thiết lập logger với cấu hình phù hợp
    - Đảm bảo logging consistent cho toàn hệ thống
    - Tích hợp với hệ thống monitoring sau này
    """
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    # Cấu hình handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

# Logger chung cho toàn hệ thống
system_logger = setup_logger("finagent-system")
```

1.3 `finagent/app/utils/validators.py`

```Python
# Mô tả: Các hàm xác thực dữ liệu chung
# Thứ tự triển khai: 3
# Phụ thuộc: Không có

import re
from datetime import datetime

def validate_financial_entity(entity: str) -> bool:
    """Xác thực thực thể tài chính"""
    financial_entities = ["stock", "crypto", "forex", "index", "bond"]
    return entity.lower() in financial_entities

def parse_date_range(text: str) -> tuple:
    """Phân tích khoảng thời gian từ văn bản"""
    today = datetime.now()
    if "hôm nay" in text or "today" in text:
        return (today, today)
    elif "tuần này" in text or "this week" in text:
        return (today.replace(day=1), today)
    # Thêm các trường hợp khác...
    return (None, None)
```

#### Giai Đoạn 2: Mô Hình Dữ Liệu (Data Models)

2.1 `finagent/app/models/query.py`

```Python
# Mô tả: Mô hình truy vấn người dùng
# Thứ tự triển khai: 4
# Phụ thuộc: validators.py

from datetime import datetime
from .core.user_identity import user_identity

class QueryModel:
    """
    Mô hình đại diện cho truy vấn của người dùng
    - Chuẩn hóa đầu vào từ các nền tảng khác nhau
    - Xử lý phân tích cú pháp lệnh cơ bản
    """
    def __init__(self, platform_user_id: str, platform: str, text: str,
                 timestamp: datetime = None):
        self.platform = platform
        self.platform_user_id = platform_user_id
        # Chuẩn hóa user_id sử dụng UserIdentityManager
        self.user_id = user_identity.normalize_user_id(platform, platform_user_id)
        self.text = text
        self.timestamp = timestamp or datetime.now()
        self.command = self._extract_command()
        self.has_command = bool(self.command)

    def _extract_command(self) -> str:
        """Trích xuất lệnh từ truy vấn (nếu có)"""
        if self.text.startswith('/'):
            parts = self.text.split(maxsplit=1)
            return parts[0]
        return None

    def get_clean_text(self) -> str:
        """Lấy nội dung truy vấn sau khi loại bỏ lệnh"""
        if self.has_command:
            return self.text[len(self.command):].strip()
        return self.text

    def to_dict(self) -> dict:
        """Chuyển đổi thành dictionary cho logging và lưu trữ"""
        return {
            "user_id": self.user_id,
            "platform": self.platform,
            "platform_user_id": self.platform_user_id,
            "text": self.text,
            "timestamp": self.timestamp.isoformat(),
            "command": self.command,
            "has_command": self.has_command
        }
```

2.2 `finagent/app/models/response.py`

```Python
# Mô tả: Mô hình phản hồi hệ thống
# Thứ tự triển khai: 5
# Phụ thuộc: query.py

import uuid
from datetime import datetime
from .query import QueryModel

class ResponseModel:
    """
    Mô hình đại diện cho phản hồi của hệ thống
    - Đảm bảo định dạng phản hồi nhất quán
    - Hỗ trợ thêm thông tin metadata cho monitoring
    """
    def __init__(self, query: QueryModel,
                 response_text: str, sources: list,
                 metadata: dict = None):
        self.query_id = str(uuid.uuid4())
        self.user_id = query.user_id
        self.platform = query.platform
        self.response_text = response_text
        self.sources = sources
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> dict:
        """Chuyển đổi thành dictionary cho logging và lưu trữ"""
        return {
            "query_id": self.query_id,
            "user_id": self.user_id,
            "platform": self.platform,
            "response_text": self.response_text,
            "sources": self.sources,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }
```

2.3 `finagent/app/models/financial_entities.py`

```Python
# Mô tả: Mô hình thực thể tài chính
# Thứ tự triển khai: 6
# Phụ thuộc: validators.py

from datetime import datetime
from .validators import validate_financial_entity

class FinancialEntity:
    """
    Mô hình thực thể tài chính (cổ phiếu, tiền điện tử, chỉ số)
    - Chuẩn hóa cách biểu diễn thực thể
    - Hỗ trợ trích xuất và nhận dạng thực thể
    """
    def __init__(self, name: str, type: str, value: float = None,
                 change: float = None, change_percent: float = None,
                 timestamp: datetime = None):
        if not validate_financial_entity(type):
            raise ValueError(f"Invalid financial entity type: {type}")

        self.name = name
        self.type = type  # stock, crypto, forex, index
        self.value = value
        self.change = change
        self.change_percent = change_percent
        self.timestamp = timestamp or datetime.now()

    @classmethod
    def from_text(cls, text: str) -> list:
        """
        Trích xuất thực thể tài chính từ văn bản
        - Sử dụng custom NER model (sẽ được triển khai sau)
        - Hiện tại sử dụng rule-based approach đơn giản
        """
        entities = []

        # Ví dụ đơn giản về rule-based extraction
        if "SSI" in text or "Chứng khoán SSI" in text:
            entities.append(cls("SSI", "stock"))
        if "BTC" in text or "Bitcoin" in text:
            entities.append(cls("BTC", "crypto"))

        return entities

    def normalize(self) -> dict:
        """
        Chuẩn hóa tên và giá trị cho việc hiển thị
        - Chuyển đổi mã cổ phiếu thành tên đầy đủ
        - Định dạng số liệu tài chính
        """
        normalized = {
            "name": self.name,
            "type": self.type,
            "display_value": self._format_value(),
            "trend": self._determine_trend()
        }
        return normalized

    def _format_value(self) -> str:
        """Định dạng giá trị cho hiển thị"""
        if self.value is None:
            return "N/A"

        if self.type == "stock":
            return f"{self.value:,.0f} VND"
        elif self.type == "crypto":
            return f"${self.value:,.2f}"
        return str(self.value)

    def _determine_trend(self) -> str:
        """Xác định xu hướng dựa trên thay đổi giá"""
        if self.change_percent is None:
            return "neutral"
        return "up" if self.change_percent > 0 else "down"
```

#### Giai Đoạn 3: Công Cụ Hỗ Trợ (Support Tools)

3.1 `finagent/app/utils/rate_limiter.py`

```Python
# Mô tả: Cơ chế giới hạn tốc độ (rate limiting)
# Thứ tự triển khai: 7
# Phụ thuộc: logger.py, settings.py

import time
import asyncio
from functools import wraps
from .logger import system_logger

class RateLimiter:
    """
    Triển khai cơ chế rate limiting dựa trên thuật toán token bucket
    - Ngăn chặn lạm dụng API (đặc biệt quan trọng với Brave Search API)
    - Hỗ trợ cả synchronous và asynchronous operations
    """
    def __init__(self, rate: int, per: int = 60):
        """
        rate: số lượng yêu cầu tối đa
        per: khoảng thời gian (giây)
        """
        self.rate = rate
        self.per = per
        self.tokens = rate
        self.last = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Acquire token với cơ chế chờ"""
        async with self.lock:
            now = time.time()
            time_passed = now - self.last
            self.last = now
            self.tokens = min(self.rate, self.tokens + time_passed * (self.rate / self.per))

            if self.tokens < 1:
                # Không đủ token, cần chờ
                tokens_needed = 1 - self.tokens
                wait_time = tokens_needed * (self.per / self.rate)
                system_logger.warning(f"Rate limit exceeded. Waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1

            return True

    def decorator(self, func):
        """Decorator để áp dụng rate limiting cho hàm"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await self.acquire()
            return await func(*args, **kwargs)
        return wrapper

# Rate limiter cho Brave Search API (55 requests/phút để có margin)
brave_rate_limiter = RateLimiter(rate=55, per=60)
```

3.2 `finagent/app/tools/web_search.py`

```Python
# Mô tả: Công cụ tìm kiếm web sử dụng Brave Search API
# Thứ tự triển khai: 8
# Phụ thuộc: rate_limiter.py, settings.py, financial_entities.py

import os
import json
from typing import List, Dict
from .rate_limiter import brave_rate_limiter
from .logger import system_logger
from .financial_entities import FinancialEntity

class SearchResults:
    """Lớp đại diện cho kết quả tìm kiếm"""
    def __init__(self, urls: List[str], titles: List[str],
                 snippets: List[str], sources: List[str]):
        self.urls = urls
        self.titles = titles
        self.snippets = snippets
        self.sources = sources

    def to_dict(self) -> dict:
        return {
            "urls": self.urls,
            "titles": self.titles,
            "snippets": self.snippets,
            "sources": self.sources
        }

class WebSearchTool:
    """
    Công cụ tìm kiếm web sử dụng Brave Search API
    - Tối ưu hóa truy vấn dựa trên phân tích intent
    - Áp dụng rate limiting và circuit breaker
    - Lọc kết quả theo nguồn tin cậy
    """
    def __init__(self, api_key: str = None):
        from langchain.tools import BraveSearch

        if api_key is None:
            from .settings import settings
            api_key = settings.BRAVE_API_KEY

        if not api_key:
            raise ValueError("Brave API key is required")

        self.brave_search = BraveSearch(
            api_key=api_key,
            search_kwargs={
                "count": 10,
                "freshness": "day",
                "country": "VN",
                "text_decorations": False
            }
        )

        # Thêm request queue để xử lý bất đồng bộ với giới hạn 1 request/giây
        self.request_queue = asyncio.Queue()
        self.processing_task = asyncio.create_task(self._process_queue())

        system_logger.info("WebSearchTool initialized with Brave Search API")

    async def _process_queue(self):
        """Xử lý các request trong queue với rate limit chính xác (1 request/giây)"""
        while True:
            query, result_queue = await self.request_queue.get()
            try:
                # Đảm bảo tuân thủ 1 request/giây
                await asyncio.sleep(1.1)  # Margin nhỏ để đảm bảo không vượt giới hạn
                results = await self._call_brave_api(query)
                result_queue.put_nowait(results)
            except Exception as e:
                result_queue.put_nowait(None)
                system_logger.error(f"Queue processing error: {str(e)}")
            finally:
                self.request_queue.task_done()

    async def search(self, query: str) -> SearchResults:
        """
        Thực hiện tìm kiếm với truy vấn đã tối ưu
        - Áp dụng rate limiting
        - Xử lý lỗi API
        """
        result_queue = asyncio.Queue(maxsize=1)
        await self.request_queue.put((query, result_queue))

        try:
            results = await asyncio.wait_for(result_queue.get(), timeout=15.0)
            if results is None:
                # Xử lý lỗi API
                return self._fallback_search(query)
            return self._process_results(results)
        except asyncio.TimeoutError:
            system_logger.warning("Web search timed out")
            return self._fallback_search(query)

    async def _call_brave_api(self, query: str) -> dict:
        """Gọi Brave Search API với cơ chế retry"""
        # Loại bỏ retry decorator, để queue xử lý rate limiting
        raw_results = self.brave_search.run(query)
        return self._parse_brave_results(raw_results)

    def _parse_brave_results(self, raw_results: str) -> dict:
        """Phân tích kết quả thô từ Brave Search API"""
        try:
            # Brave trả về kết quả dưới dạng JSON string
            return json.loads(raw_results)
        except json.JSONDecodeError:
            # Xử lý trường hợp kết quả không phải JSON
            system_logger.warning("Brave API returned non-JSON response")
            return {"results": []}

    def _process_results(self, results: dict) -> SearchResults:
        """Xử lý và lọc kết quả tìm kiếm"""
        urls, titles, snippets, sources = [], [], [], []

        for item in results.get("results", [])[:10]:  # Lấy tối đa 10 kết quả
            url = item.get("url")
            title = item.get("title", "")
            snippet = item.get("description", "")

            if url and title:
                urls.append(url)
                titles.append(title)
                snippets.append(snippet)
                sources.append(self._extract_source(url))

        return SearchResults(urls, titles, snippets, sources)

    def _extract_source(self, url: str) -> str:
        """Trích xuất tên nguồn từ URL"""
        # Ví dụ: https://cafef.vn/ -> "cafef.vn"
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return domain

    def _fallback_search(self, query: str) -> SearchResults:
        """
        Cơ chế fallback khi Brave Search API gặp lỗi
        - Sử dụng Google Custom Search hoặc cơ sở dữ liệu cache
        """
        system_logger.warning("Using fallback search mechanism")
        # Trong thực tế, sẽ triển khai fallback thực sự
        return SearchResults([], [], [], [])

    def optimize_query(self, analysis_result: dict) -> str:
        """
        Tối ưu hóa truy vấn tìm kiếm dựa trên kết quả phân tích
        - Kết hợp chủ đề, thực thể và phạm vi thời gian
        """
        # Chỉ lấy tối đa 2 thực thể quan trọng nhất
        main_entities = analysis_result['entities'][:2]

        search_terms = [
            analysis_result['main_topic'],
            *main_entities,
            "tin tức mới nhất"
        ]

        # Chỉ thêm time_range nếu thực sự cần
        if analysis_result.get('time_range') in ["hôm nay", "today"]:
            search_terms.append("trong 24h")

        return " ".join(search_terms)
```

3.3 `finagent/app/core/cache.py`

```Python
# Mô tả: Hệ thống cache sử dụng Redis
# Thứ tự triển khai: 9
# Phụ thuộc: settings.py, logger.py

import json
import hashlib
import redis
from datetime import datetime
from .logger import system_logger
from .settings import settings

class Cache:
    """
    Triển khai hệ thống cache đa tầng với Redis
    - Hỗ trợ TTL khác nhau cho các loại dữ liệu
    - Tích hợp với quy trình xử lý chính
    """
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        system_logger.info(f"Cache system initialized with Redis at {settings.REDIS_URL}")

    def _generate_key(self, query: str) -> str:
        """Tạo key cache từ truy vấn"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return f"finance:cache:{query_hash}"

    def get(self, query: str) -> dict:
        """Lấy dữ liệu từ cache"""
        key = self._generate_key(query)
        cached_data = self.redis_client.get(key)

        if cached_data:
            system_logger.debug(f"Cache hit for query: {query[:50]}...")
            return json.loads(cached_data)

        system_logger.debug(f"Cache miss for query: {query[:50]}...")
        return None

    def set(self, query: str, response: dict, ttl: int = None):
        """Lưu dữ liệu vào cache với TTL"""
        key = self._generate_key(query)

        # Xác định TTL dựa trên loại truy vấn
        if ttl is None:
            from .models.query import QueryModel
            query_model = QueryModel("", "system", query)
            ttl = self._determine_ttl(query_model)

        self.redis_client.setex(key, ttl, json.dumps(response))
        system_logger.debug(f"Data cached with TTL={ttl} seconds")

    def _determine_ttl(self, query: 'QueryModel') -> int:
        """Xác định TTL phù hợp dựa trên loại truy vấn"""
        if "/news" in query.text or "tin tức" in query.text:
            return settings.CACHE_TTL_NEWS
        elif any(entity in query.text for entity in ["cổ phiếu", "stock", "giá"]):
            return settings.CACHE_TTL_MARKET
        return 3600  # Mặc định 1 giờ

    def invalidate(self, pattern: str):
        """Invalid cache theo pattern"""
        keys = self.redis_client.keys(f"finance:cache:*{pattern}*")
        if keys:
            self.redis_client.delete(*keys)
            system_logger.info(f"Invalidated {len(keys)} cache entries matching '{pattern}'")

# Singleton instance
cache = Cache()
```

#### Giai Đoạn 4: Các Module Xử Lý Chính

4.1 `finagent/app/core/memory.py`

```Python
# Mô tả: Quản lý ngữ cảnh trò chuyện
# Thứ tự triển khai: 10
# Phụ thuộc: cache.py, settings.py, logger.py

import json
from datetime import datetime, timedelta
from typing import List, Dict
from .cache import cache
from .logger import system_logger
from .settings import settings
from .models.query import QueryModel
from .models.response import ResponseModel

class ConversationMemory:
    """
    Quản lý ngữ cảnh trò chuyện giữa người dùng và hệ thống
    - Sử dụng Redis làm backend lưu trữ
    - Tự động tóm tắt khi vượt quá giới hạn token
    - Tích hợp với hệ thống cache
    """
    def __init__(self):
        from redis import Redis
        self.redis_client = Redis.from_url(settings.REDIS_URL)
        self.max_token_limit = settings.MAX_TOKEN_LIMIT
        system_logger.info("ConversationMemory initialized")

    def _get_session_key(self, user_id: str) -> str:
        """Tạo key cho session của người dùng"""
        return f"finance:chat_history:{user_id}"

    async def get_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Lấy lịch sử trò chuyện cho người dùng
        - Tự động tóm tắt nếu vượt quá giới hạn token
        """
        session_key = self._get_session_key(user_id)
        history = self.redis_client.lrange(session_key, 0, limit-1)

        if not history:
            return []

        # Chuyển đổi từ binary sang dict
        history = [json.loads(item.decode('utf-8')) for item in history]

        # Kiểm tra giới hạn token
        token_count = self._estimate_token_count(history)
        if token_count > self.max_token_limit:
            return await self._summarize_history(user_id, history)

        return history

    async def update_history(self, query: QueryModel, response: ResponseModel):
        """Cập nhật lịch sử trò chuyện"""
        session_key = self._get_session_key(query.user_id)

        # Chuẩn bị dữ liệu
        entry = {
            "query": query.text,
            "response": response.response_text,
            "sources": response.sources,
            "timestamp": datetime.now().isoformat(),
            "metadata": response.metadata
        }

        # Lưu vào Redis
        self.redis_client.rpush(session_key, json.dumps(entry))
        self.redis_client.expire(session_key, timedelta(days=7))  # TTL 7 ngày

        # Cập nhật cache cho ngữ cảnh hiện tại
        cache.set(f"context:{query.user_id}", entry)

    def _estimate_token_count(self, history: List[Dict]) -> int:
        """Ước tính số token từ lịch sử trò chuyện"""
        total_text = " ".join([
            item["query"] + " " + item["response"]
            for item in history
        ])
        # 1 token ~ 4 ký tự trong tiếng Anh
        return len(total_text) // 4

    async def _summarize_history(self, user_id: str, history: List[Dict]) -> List[Dict]:
        """
        Tóm tắt lịch sử trò chuyện khi vượt quá giới hạn token
        - Sử dụng LLM nhỏ để tóm tắt
        """
        system_logger.info(f"Summarizing conversation history for user {user_id}")

        # Tạo prompt tóm tắt
        summary_prompt = (
            "Tóm tắt lịch sử trò chuyện sau thành một đoạn văn ngắn, "
            "giữ lại các thông tin quan trọng về thị trường tài chính, "
            "chỉ số và xu hướng:\n\n"
        )

        for item in history:
            summary_prompt += f"Q: {item['query']}\n"
            summary_prompt += f"A: {item['response']}\n\n"

        # Sử dụng LLM để tóm tắt (trong thực tế sẽ gọi API)
        # Đây là mô phỏng
        summary = (
            "Người dùng đang tìm hiểu về thị trường chứng khoán và crypto. "
            "Các chủ đề chính bao gồm VN-Index, Bitcoin và tỷ giá USD/VND. "
            "Xu hướng gần đây là tăng nhẹ đối với thị trường chứng khoán, "
            "giảm điều chỉnh đối với crypto."
        )

        # Xóa lịch sử cũ và lưu bản tóm tắt
        session_key = self._get_session_key(user_id)
        self.redis_client.delete(session_key)
        self.redis_client.rpush(session_key, json.dumps({
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }))

        return [{"summary": summary}]

    async def clear_history(self, user_id: str):
        """Xóa lịch sử trò chuyện của người dùng"""
        session_key = self._get_session_key(user_id)
        self.redis_client.delete(session_key)
        system_logger.info(f"Cleared conversation history for user {user_id}")

# Singleton instance
conversation_memory = ConversationMemory()
```

4.2 `finagent/app/core/time_series_db.py`

```Python
# Mô tả: Time-series database cho lưu trữ dữ liệu tài chính dài hạn
# Thứ tự triển khai: 11
# Phụ thuộc: settings.py, logger.py

import pandas as pd
from datetime import datetime, timedelta
import supabase
from .logger import system_logger
from .settings import settings

class TimeSeriesDB:
    """
    Quản lý lưu trữ và truy vấn dữ liệu tài chính theo thời gian
    """
    def __init__(self):
        self.supabase = supabase.create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        self.logger = system_logger.getChild("time_series_db")

    def store_financial_data(self, data_point: dict):
        """
        Lưu trữ điểm dữ liệu tài chính

        data_point format:
        {
            "timestamp": ISO8601,
            "entity_type": "stock|crypto|forex",
            "entity_id": "BTC|ETH|SSI|VCB",
            "value": float,
            "change": float,
            "change_percent": float,
            "source": "cafef|coindesk|...",
            "metadata": {additional info}
        }
        """
        try:
            self.supabase.table("financial_time_series").insert(data_point).execute()
            self.logger.info(f"Stored financial data point for {data_point['entity_id']}")
        except Exception as e:
            self.logger.error(f"Error storing financial data: {str(e)}")

    def get_historical_data(self, entity_id: str, entity_type: str,
                           start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Lấy dữ liệu lịch sử cho phân tích xu hướng
        """
        # Triển khai truy vấn Supabase và chuyển đổi thành DataFrame
        pass

    def aggregate_data(self, entity_id: str, entity_type: str,
                      period: str = "daily") -> pd.DataFrame:
        """
        Tổng hợp dữ liệu theo khoảng thời gian (daily/weekly/monthly)
        """
        # Triển khai aggregate query
        pass

    def get_trend(self, entity_id: str, entity_type: str,
                 period: str = "7d") -> dict:
        """
        Tính toán xu hướng cho thực thể trong khoảng thời gian
        """
        # Triển khai tính toán xu hướng
        pass

# Singleton instance
time_series_db = TimeSeriesDB()
```

4.3 `finagent/app/core/user_identity.py`

```Python
# Mô tả: Quản lý identity đa nền tảng
# Thứ tự triển khai: 12
# Phụ thuộc: logger.py

import uuid
import hashlib
from .logger import system_logger

class UserIdentityManager:
    """
    Quản lý identity của người dùng từ nhiều nền tảng
    """
    def __init__(self):
        self.platform_mapping = {}
        self.logger = system_logger.getChild("UserIdentity")

    def normalize_user_id(self, platform: str, platform_user_id: str) -> str:
        """
        Chuẩn hóa user_id từ nền tảng thành internal user_id

        Ví dụ:
        - Telegram: "123456789" → internal ID
        - Web: "user@example.com" → internal ID
        """
        # Tạo internal ID dựa trên platform và platform_user_id
        internal_id = self._generate_internal_id(platform, platform_user_id)

        # Lưu mapping cho việc tra cứu ngược
        self.platform_mapping[(platform, platform_user_id)] = internal_id

        return internal_id

    def get_platform_user_id(self, internal_id: str, platform: str) -> str:
        """
        Lấy platform user_id từ internal ID
        """
        for (plat, plat_user_id), int_id in self.platform_mapping.items():
            if int_id == internal_id and plat == platform:
                return plat_user_id
        return None

    def _generate_internal_id(self, platform: str, platform_user_id: str) -> str:
        """
        Tạo internal ID duy nhất từ platform và platform_user_id
        """
        # Sử dụng SHA-256 để tạo ID cố định từ cặp (platform, user_id)
        hash_input = f"{platform}:{platform_user_id}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def is_valid_user_id(self, user_id: str) -> bool:
        """
        Kiểm tra xem user_id có phải là internal ID hợp lệ không
        """
        # Internal ID là SHA-256 hash (64 ký tự hex)
        return len(user_id) == 64 and all(c in '0123456789abcdef' for c in user_id.lower())

# Singleton instance
user_identity = UserIdentityManager()
```

4.4 `finagent/app/agents/base.py`

```Python
# Mô tả: Lớp cơ sở cho tất cả các agent
# Thứ tự triển khai: 13
# Phụ thuộc: memory.py, cache.py, logger.py

from abc import ABC, abstractmethod
from typing import Any, Dict
from .core.memory import conversation_memory
from .core.cache import cache
from .core.time_series_db import time_series_db
from .logger import system_logger
from .models.query import QueryModel
from .models.response import ResponseModel

class BaseAgent(ABC):
    """
    Lớp cơ sở trừu tượng cho tất cả các agent
    - Định nghĩa giao diện xử lý chung
    - Triển khai cơ chế cache và quản lý ngữ cảnh
    """
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = system_logger.getChild(self.__class__.__name__)

    @abstractmethod
    async def process(self, query: QueryModel) -> ResponseModel:
        """
        Xử lý truy vấn và trả về phản hồi
        - Được ghi đè bởi các agent cụ thể
        """
        pass

    async def _get_cached_response(self, query: QueryModel) -> ResponseModel:
        """Lấy phản hồi từ cache nếu tồn tại"""
        cached_response = cache.get(query.text)
        if cached_response:
            self.logger.debug(f"Using cached response for query: {query.text[:50]}...")
            return ResponseModel(
                query=query,
                response_text=cached_response["response_text"],
                sources=cached_response["sources"],
                metadata={"from_cache": True, **cached_response.get("metadata", {})}
            )
        return None

    async def _cache_response(self, query: QueryModel, response: ResponseModel, ttl: int = None):
        """Lưu phản hồi vào cache"""
        cache_data = {
            "response_text": response.response_text,
            "sources": response.sources,
            "metadata": response.metadata
        }
        cache.set(query.text, cache_data, ttl)

    async def _update_conversation_context(self, query: QueryModel, response: ResponseModel):
        """Cập nhật ngữ cảnh trò chuyện"""
        await conversation_memory.update_history(query, response)
```

4.5 `finagent/app/agents/information.py`

```Python
# Mô tả: Information Agent - Agent cung cấp thông tin tổng hợp
# Thứ tự triển khai: 14
# Phụ thuộc: base.py, query_analyzer.py, web_search.py, web_scraping.py, content_processing.py

import json
from typing import Dict, List
from .base import BaseAgent
from .tools.query_analyzer import QueryAnalyzer
from .tools.web_search import WebSearchTool
from .tools.web_scraping import WebScrapingTool
from .tools.content_processing import ContentProcessor
from .core.time_series_db import time_series_db
from .models.query import QueryModel
from .models.response import ResponseModel
from .logger import system_logger

class InformationAgent(BaseAgent):
    """
    Agent cung cấp thông tin tài chính tổng hợp
    - Xử lý các truy vấn dạng tổng hợp tin tức
    - Tích hợp đầy đủ quy trình từ phân tích truy vấn đến tạo phản hồi
    """
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.logger = system_logger.getChild("InformationAgent")

        # Khởi tạo các module phụ trợ
        self.query_analyzer = QueryAnalyzer()
        self.web_search_tool = WebSearchTool()
        self.web_scraping_tool = WebScrapingTool()
        self.content_processor = ContentProcessor()
        self.time_series_db = time_series_db  # Bổ sung cho lưu trữ dữ liệu dài hạn

        self.logger.info("InformationAgent initialized with all dependencies")

    async def process(self, query: QueryModel) -> ResponseModel:
        """
        Xử lý truy vấn và trả về phản hồi
        - Quy trình xử lý đầy đủ:
          1. Kiểm tra cache
          2. Phân tích truy vấn
          3. Tìm kiếm thông tin
          4. Thu thập nội dung
          5. Lưu trữ dữ liệu thời gian thực
          6. Xử lý và tạo phản hồi
          7. Cập nhật ngữ cảnh và cache
        """
        self.logger.info(f"Processing query: {query.text}")

        # 1. Kiểm tra cache trước
        cached_response = await self._get_cached_response(query)
        if cached_response:
            return cached_response

        # 2. Phân tích truy vấn
        self.logger.debug("Analyzing query...")
        analysis_result = await self.query_analyzer.analyze(query.text)

        # 3. Tối ưu hóa và thực hiện tìm kiếm
        self.logger.debug("Performing web search...")
        optimized_query = self.web_search_tool.optimize_query(analysis_result)
        search_results = await self.web_search_tool.search(optimized_query)

        # 4. Thu thập nội dung từ các URL
        self.logger.debug(f"Scraping content from {len(search_results.urls)} URLs...")
        scraped_content = await self.web_scraping_tool.scrape(search_results.urls)

        # 5. Lưu trữ dữ liệu thời gian thực
        self.logger.debug("Storing time series data...")
        await self._store_time_series_data(scraped_content)

        # 6. Xử lý nội dung và tạo phản hồi
        self.logger.debug("Processing content and generating response...")
        response = await self.content_processor.process(
            query=query,
            analysis_result=analysis_result,
            scraped_content=scraped_content
        )

        # 7. Cập nhật ngữ cảnh và cache
        await self._update_conversation_context(query, response)
        await self._cache_response(query, response)

        self.logger.info("Query processed successfully")
        return response

    async def _store_time_series_data(self, scraped_content: ScrapedContent):
        """
        Lưu trữ dữ liệu tài chính vào time-series DB
        """
        # Trích xuất và lưu trữ các điểm dữ liệu quan trọng
        for entity in scraped_content.financial_entities:
            data_point = {
                "timestamp": datetime.now(),
                "entity_type": entity.type,
                "entity_id": entity.name,
                "value": entity.value,
                "change": entity.change,
                "change_percent": entity.change_percent,
                "source": scraped_content.source,
                "metadata": {
                    "reliability_score": scraped_content.reliability_score,
                    "analysis_result": scraped_content.analysis_result
                }
            }
            self.time_series_db.store_financial_data(data_point)

# Singleton instance cho DI
information_agent = InformationAgent()
```

4.6 `finagent/app/core/router.py`

```Python
# Mô tả: Agent Router - Định tuyến thông minh đến các agent phù hợp
# Thứ tự triển khai: 15
# Phụ thuộc: base.py, settings.py, logger.py, information.py

import os
import yaml
from typing import Dict, Any
from .logger import system_logger
from .settings import settings
from .agents.base import BaseAgent
from .agents.information import information_agent

class AgentRouter:
    """
    Router định tuyến thông minh cho các truy vấn
    - Xử lý cả định tuyến dựa trên lệnh và intent
    - Tải cấu hình từ file YAML để dễ mở rộng
    """
    def __init__(self):
        self.logger = system_logger.getChild("AgentRouter")
        self.config = self._load_config()
        self.logger.info("AgentRouter initialized with configuration")

    def _load_config(self) -> Dict:
        """Tải cấu hình định tuyến từ file YAML"""
        config_path = os.path.join(os.path.dirname(__file__), "../configs/routing.yaml")

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.logger.info(f"Routing configuration loaded from {config_path}")
                return config
        except Exception as e:
            self.logger.error(f"Error loading routing config: {str(e)}")
            # Cấu hình mặc định nếu không tải được file
            return {
                "commands": {
                    "/news": {"agent": "information_agent", "description": "Tin tức tài chính tổng hợp"},
                    "/stock": {"agent": "stock_agent", "description": "Thông tin cổ phiếu"},
                    "/crypto": {"agent": "crypto_agent", "description": "Thông tin tiền điện tử"}
                },
                "intents": {
                    "news": "information_agent",
                    "analysis": "information_agent",
                    "stock": "stock_agent",
                    "crypto": "crypto_agent",
                    "general": "information_agent"
                },
                "default_agent": "information_agent"
            }

    async def route(self, query: 'QueryModel') -> BaseAgent:
        """
        Định tuyến truy vấn đến agent phù hợp
        - Ưu tiên định tuyến theo lệnh (/command)
        - Nếu không có lệnh, sử dụng intent classification
        """
        if query.has_command:
            return self._route_by_command(query)
        else:
            return await self._route_by_intent(query)

    def _route_by_command(self, query: 'QueryModel') -> BaseAgent:
        """Định tuyến dựa trên lệnh (/command)"""
        command = query.command.lower()

        if command in self.config["commands"]:
            agent_name = self.config["commands"][command]["agent"]
            self.logger.debug(f"Routing by command '{command}' to {agent_name}")
            return self._get_agent_instance(agent_name)

        self.logger.warning(f"Unknown command: {command}. Using default agent.")
        return self._get_default_agent()

    async def _route_by_intent(self, query: 'QueryModel') -> BaseAgent:
        """Định tuyến dựa trên intent (khi không có lệnh)"""
        # Trong phiên bản đầy đủ, sẽ gọi IntentClassifier
        # Hiện tại sử dụng rule-based đơn giản
        text = query.text.lower()

        if any(word in text for word in ["tin tức", "thông tin", "tổng hợp"]):
            intent = "news"
        elif any(word in text for word in ["cổ phiếu", "stock", "ssi", "vcb"]):
            intent = "stock"
        elif any(word in text for word in ["crypto", "bitcoin", "eth"]):
            intent = "crypto"
        else:
            intent = "general"

        self.logger.debug(f"Detected intent: {intent}")

        if intent in self.config["intents"]:
            agent_name = self.config["intents"][intent]
            return self._get_agent_instance(agent_name)

        return self._get_default_agent()

    def _get_agent_instance(self, agent_name: str) -> BaseAgent:
        """Lấy instance của agent dựa trên tên"""
        if agent_name == "information_agent":
            return information_agent
        # Trong tương lai sẽ thêm các agent khác
        elif agent_name == "stock_agent":
            # Sẽ triển khai sau
            return information_agent
        elif agent_name == "crypto_agent":
            # Sẽ triển khai sau
            return information_agent

        self.logger.warning(f"Unknown agent: {agent_name}. Using default.")
        return self._get_default_agent()

    def _get_default_agent(self) -> BaseAgent:
        """Lấy agent mặc định"""
        default_agent = self.config.get("default_agent", "information_agent")
        return self._get_agent_instance(default_agent)

# Singleton instance
agent_router = AgentRouter()
```

#### Giai Đoạn 5: Entry Point và Triển Khai

5.1 `finagent/app/main.py`

```Python
# Mô tả: Entry point chính của hệ thống
# Thứ tự triển khai: 16
# Phụ thuộc: router.py, logger.py

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .core.router import agent_router
from .logger import system_logger
from .models.query import QueryModel
from .models.response import ResponseModel

app = FastAPI(
    title="Finance Agent Service",
    description="API cho hệ thống chatbot agent tài chính",
    version="1.0.0"
)

class UserQuery(BaseModel):
    platform_user_id: str
    platform: str
    text: str

@app.post("/process", response_model=dict)
async def process_query(query: UserQuery):
    """
    Xử lý truy vấn từ người dùng
    - Định tuyến đến agent phù hợp
    - Trả về phản hồi dưới dạng JSON
    """
    try:
        # Chuyển đổi sang QueryModel
        query_model = QueryModel(
            platform_user_id=query.platform_user_id,
            platform=query.platform,
            text=query.text
        )

        # Định tuyến và xử lý
        agent = await agent_router.route(query_model)
        response = await agent.process(query_model)

        # Trả về kết quả
        return response.to_dict()

    except Exception as e:
        system_logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Kiểm tra sức khỏe của service"""
    return {"status": "healthy", "service": "finance-agent"}

if __name__ == "__main__":
    import uvicorn
    system_logger.info("Starting Finance Agent Service...")
    uvicorn.run(app, host="0.0.0.0", port=9001)
```

5.2 `finagent/app/configs/routing.yaml`

```YAML
# Mô tả: Cấu hình định tuyến cho Agent Router
# Thứ tự triển khai: 17 (file cấu hình, không phải code)
# Phụ thuộc: Không có

commands:
  "/news":
    agent: "information_agent"
    description: "Tin tức tài chính tổng hợp"
    parameters: ["topic"]
  "/stock":
    agent: "stock_agent"
    description: "Thông tin cổ phiếu"
    parameters: ["symbol"]
  "/crypto":
    agent: "crypto_agent"
    description: "Thông tin tiền điện tử"
    parameters: ["symbol"]
  "/help":
    agent: "information_agent"
    description: "Hiển thị trợ giúp"
    parameters: []

intents:
  news: "information_agent"
  analysis: "information_agent"
  stock: "stock_agent"
  crypto: "crypto_agent"
  general: "information_agent"

default_agent: "information_agent"
```

## 5\. Luồng Thực Thi Chi Tiết

Dựa trên thứ tự triển khai trên, đây là luồng thực thi khi hệ thống xử lý một truy vấn:

1.  Khởi tạo hệ thống:

    - Khi chạy `main.py`, các cấu hình được tải từ `settings.py`
    - Hệ thống logging được thiết lập
    - Các singleton instances được khởi tạo theo thứ tự:
      - settings
      - system_logger
      - cache
      - conversation_memory
      - time_series_db
      - user_identity
      - information_agent
      - agent_router

2.  Xử lý truy vấn:

    - Người dùng gửi truy vấn đến endpoint `/process` qua Telegram/Zalo/Web
    - FastAPI chuyển đổi payload thành `UserQuery` model
    - `main.py` chuyển đổi thành `QueryModel` sử dụng `user_identity` để chuẩn hóa user_id
    - `agent_router` định tuyến đến agent phù hợp
    - Agent xử lý theo quy trình:
      - Kiểm tra cache
      - Phân tích truy vấn
      - Tìm kiếm thông tin
      - Thu thập nội dung
      - Lưu trữ dữ liệu thời gian thực (bổ sung)
      - Xử lý và tạo phản hồi
      - Cập nhật ngữ cảnh và cache
    - Phản hồi được trả về dưới dạng JSON

3.  Phụ thuộc giữa các thành phần:

    - `main.py` phụ thuộc vào `agent_router`
    - `agent_router` phụ thuộc vào các agent instances
    - Các agent phụ thuộc vào các tools (query_analyzer, web_search, v.v.)
    - Các tools phụ thuộc vào hệ thống cache và config
    - Hệ thống cache phụ thuộc vào config và logging
    - `time_series_db` và `user_identity` được sử dụng xuyên suốt hệ thống

## 6\. Nguyên Tắc Thiết Kế Logic

1.  Thứ tự triển khai từ dưới lên:

    - Bắt đầu từ các thành phần cơ sở (config, utils)
    - Sau đó là các mô hình dữ liệu
    - Tiếp theo là các công cụ hỗ trợ
    - Rồi đến các module xử lý chính
    - Cuối cùng là entry point

2.  Tránh phụ thuộc vòng tròn:

    - Các module không được import các module "phía dưới" trong thứ tự triển khai
    - Sử dụng dependency injection cho các phụ thuộc phức tạp

3.  Singleton pattern cho các service chia sẻ:

    - Cache, conversation_memory, time_series_db, user_identity, information_agent được khởi tạo một lần
    - Đảm bảo tính nhất quán và hiệu năng

4.  Cơ chế fallback và graceful degradation:

    - Các thành phần quan trọng có cơ chế fallback khi gặp lỗi
    - Hệ thống vẫn hoạt động ở mức cơ bản khi một số thành phần gặp sự cố

5.  Cấu hình qua file YAML:

    - Tách biệt logic và cấu hình
    - Dễ dàng mở rộng và điều chỉnh mà không cần thay đổi code

6.  Xử lý giới hạn API hiệu quả:

    - Sử dụng queue mechanism để đảm bảo tuân thủ giới hạn 1 request/giây của Brave API
    - Tối ưu hóa truy vấn để giảm số lượng request cần thiết
    - Cơ chế fallback khi đạt giới hạn

7.  Lưu trữ dữ liệu dài hạn:

    - Time Series DB lưu trữ dữ liệu tài chính hàng ngày
    - Hỗ trợ phân tích xu hướng trong tương lai
    - Tách biệt với lưu trữ chat history

8.  Xác thực user_id đa nền tảng:

    - Chuẩn hóa user_id từ các nền tảng khác nhau
    - Đảm bảo tính nhất quán trong toàn hệ thống
    - Không phụ thuộc vào định dạng cụ thể của từng nền tảng

## 7\. Khuyến Nghị Triển Khai

1.  Phân tầng xử lý:

    - Triển khai theo mô hình Clean Architecture để tách biệt giữa business logic và infrastructure
    - Sử dụng dependency injection để quản lý các phụ thuộc

2.  Quản lý lỗi và giám sát:

    - Triển khai hệ thống logging chi tiết với mức độ severity khác nhau
    - Thiết lập cảnh báo cho các trường hợp vượt rate limit của Brave Search API

3.  Bảo mật:

    - Quản lý API keys bằng hệ thống secret management (ví dụ: AWS Secrets Manager)
    - Áp dụng nguyên tắc least privilege cho tất cả các thành phần

4.  Tối ưu hiệu năng:

    - Triển khai cơ chế cache đa tầng (in-memory + Redis)
    - Sử dụng hàng đợi bất đồng bộ cho các tác vụ nặng (scraping, xử lý dữ liệu)
    - Tối ưu hóa truy vấn để giảm số lượng API calls

5.  Mở rộng trong tương lai:

    - Thiết kế hệ thống để dễ dàng thêm các agent mới (stock, forex, v.v.)
    - Chuẩn bị cho việc tích hợp thêm các nguồn dữ liệu và API mới
    - Xây dựng Time Series DB để hỗ trợ phân tích thị trường trong tương lai

6.  Xử lý giới hạn Brave API:

    - Triển khai queue mechanism với sleep 1.1s để đảm bảo không vượt giới hạn 1 request/giây
    - Tối ưu hóa truy vấn để chỉ lấy thông tin thực sự cần thiết
    - Xây dựng cơ chế fallback sang các nguồn tìm kiếm khác
