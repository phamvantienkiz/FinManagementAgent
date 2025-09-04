# MVP Cố vấn Tài chính AI

## 1\. Giới thiệu Dự án

**MVP Cố vấn Tài chính AI** là một trợ lý tài chính ảo đột phá, được thiết kế để tương tác với người dùng thông qua các kênh giao tiếp quen thuộc như tin nhắn SMS và các nền tảng chat như Zalo [1, 1]. Mục tiêu chính của dự án là giải quyết "nỗi đau" về thiếu kiến thức và nỗi sợ hãi trong quản lý tài chính của thế hệ Gen Z tại Việt Nam. Bằng cách tận dụng sức mạnh của Trí tuệ nhân tạo, hệ thống cung cấp lời khuyên dễ tiếp cận, tiện lợi và được cá nhân hóa, giúp người dùng đưa ra các quyết định tài chính thông minh.

Dự án này được phát triển để tham gia Cuộc thi HDBank Hackathon & Galaxy of Innovation Event 2025, phù hợp hoàn hảo với Chủ đề ưu tiên số 1 của cuộc thi: "Cố vấn Tài chính AI qua Tin nhắn SMS & Microservices".

## 2\. Các Tính năng Chính

- **Tư vấn Cá nhân hóa:** Cung cấp đề xuất đầu tư và lập kế hoạch tài chính dựa trên mục tiêu và mức độ chấp nhận rủi ro của người dùng.

- **Cảnh báo theo thời gian thực:** Gửi thông báo tức thì về biến động số dư hoặc các sự kiện tài chính quan trọng qua tin nhắn SMS/Zalo [1, 1].

- **Mô phỏng rủi ro:** Giúp người dùng hiểu rõ các kịch bản rủi ro tiềm ẩn cho một khoản đầu tư cụ thể.

- **Hỗ trợ Ra quyết định:** Cung cấp thông tin và phân tích chuyên sâu để hỗ trợ các quyết định tài chính lớn.

## 3\. Kiến trúc Hệ thống

Dự án được xây dựng trên kiến trúc Microservices (MS), đáp ứng một yêu cầu cốt lõi của cuộc thi [1, 1]. Các dịch vụ độc lập giúp tăng tốc độ phát triển và đảm bảo khả năng mở rộng [1, 1].

Các Microservices cốt lõi bao gồm:

- **AI Agent Service:** Chứa lõi trí tuệ, điều phối các tác vụ phức tạp.

- **Messaging Service:** Cổng giao tiếp với người dùng qua tin nhắn.

- **Financial Data Service:** Cung cấp dữ liệu tài chính từ các nguồn bên ngoài.

- **RAG Service:** Quản lý kho kiến thức chuyên sâu để hỗ trợ AI.

- **User Management Service:** Quản lý thông tin và lịch sử tương tác của người dùng.

## 4\. Công nghệ Nổi bật

- **Kiến trúc:** Microservices.

- **Web Framework:** FastAPI, để xây dựng các API hiệu suất cao.

- **AI Agent Framework:** CrewAI, được lựa chọn vì tính đơn giản và hiệu quả trong việc tạo mẫu nhanh.

- **Mô hình Ngôn ngữ Lớn (LLM):** Google Gemini API (cho MVP) , với tầm nhìn dài hạn sử dụng các mô hình chuyên biệt về tài chính nguồn mở như Open-FinLLMs.

- **Cơ chế Dữ liệu:** Retrieval-Augmented Generation (RAG) để cung cấp thông tin cập nhật, sử dụng LlamaIndex và vector database cục bộ Vectra [1, 1].

- **Tích hợp Giao tiếp:** Zalo API [1, 1] và TextBee để xử lý tin nhắn.

- **Cơ sở dữ liệu:** PostgreSQL hoặc MongoDB [1, 1].

## 5\. Bắt đầu

Để khởi chạy dự án, bạn có thể clone repository và cài đặt các dependencies cần thiết bằng `pip install -r requirements.txt`. Sau đó, khởi chạy các microservices theo hướng dẫn trong tài liệu kỹ thuật.

## 6\. Đóng góp

Mọi đóng góp đều được hoan nghênh. Vui lòng liên hệ với các thành viên trong nhóm để thảo luận.
