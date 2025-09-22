# from crewai.tools import BaseTool
# from typing import Type
# from pydantic import BaseModel, Field
# from crawl4ai import Crawler, BrowserConfig, CrawlerRunConfig

# class WebCrawlerInput(BaseModel):
#     url: str = Field(..., description="URL to crawl and extract content from")

# class WebCrawlerTool(BaseTool):
#     name: str = "Web Crawler"
#     description: str = "Crawl and extract content from web pages"
#     args_schema: Type[BaseModel] = WebCrawlerInput

#     def _run(self, url: str) -> str:
#         browser_config = BrowserConfig(
#             headless=True,
#             verbose=False
#         )
        
#         crawler = Crawler(browser_config=browser_config)
#         config = CrawlerRunConfig(
#             word_count_threshold=10,
#             include_raw_html=False
#         )
        
#         result = crawler.run(url=url, config=config)
#         return result.html