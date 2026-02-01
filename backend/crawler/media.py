"""媒体网站爬虫"""
import re
from datetime import datetime
from typing import Optional
from .base import BaseCrawler


class MediaCrawler(BaseCrawler):
    """科技媒体网站爬虫"""

    # 媒体源配置
    MEDIA_SOURCES = {
        "openai": {
            "name": "OpenAI Blog",
            "url": "https://openai.com/blog",
            "company": "OpenAI",
            "selectors": {
                "articles": "a[href*='/index/']",
                "title": "h3, h2, .title",
                "summary": "p, .description",
            }
        },
        "anthropic": {
            "name": "Anthropic News",
            "url": "https://www.anthropic.com/news",
            "company": "Anthropic",
            "selectors": {
                "articles": "a[href*='/news/']",
                "title": "h2, h3, .title",
                "summary": "p, .description",
            }
        },
        "google_ai": {
            "name": "Google AI Blog",
            "url": "https://blog.google/technology/ai/",
            "company": "Google",
            "selectors": {
                "articles": "a[href*='/technology/ai/']",
                "title": "h3, h2",
                "summary": "p",
            }
        },
        "techcrunch": {
            "name": "TechCrunch AI",
            "url": "https://techcrunch.com/category/artificial-intelligence/",
            "company": None,
            "selectors": {
                "articles": "a.post-block__title__link, article a[href*='techcrunch.com/20']",
                "title": "h2, h3, .post-block__title",
                "summary": "p, .post-block__content",
            }
        },
        "jiqizhixin": {
            "name": "机器之心",
            "url": "https://www.jiqizhixin.com/",
            "company": None,
            "selectors": {
                "articles": "a[href*='/articles/']",
                "title": "h4, h3, .article-title",
                "summary": "p, .article-summary",
            }
        },
        "qbitai": {
            "name": "量子位",
            "url": "https://www.qbitai.com/",
            "company": None,
            "selectors": {
                "articles": "a[href*='qbitai.com/20']",
                "title": "h2, h3, .title",
                "summary": "p, .excerpt",
            }
        },
    }

    def __init__(self, source_key: str = None):
        super().__init__()
        self.source_key = source_key
        if source_key and source_key in self.MEDIA_SOURCES:
            config = self.MEDIA_SOURCES[source_key]
            self.source_name = config["name"]
            self.source_url = config["url"]
            self.company = config.get("company")
            self.selectors = config["selectors"]
        else:
            self.source_name = "Unknown Media"
            self.source_url = ""
            self.company = None
            self.selectors = {}

    async def crawl(self) -> list[dict]:
        """爬取媒体文章"""
        if not self.source_url:
            return []

        print(f"[{self.source_name}] 开始爬取...")

        html = await self.fetch_page(self.source_url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # 查找文章链接
        article_links = soup.select(self.selectors.get("articles", "article a"))

        seen_urls = set()
        for link in article_links[:20]:  # 限制数量
            try:
                href = link.get("href", "")
                if not href or href in seen_urls:
                    continue

                # 构建完整 URL
                if href.startswith("/"):
                    full_url = self._get_base_url() + href
                elif not href.startswith("http"):
                    continue
                else:
                    full_url = href

                # 过滤非文章链接
                if not self._is_article_url(full_url):
                    continue

                seen_urls.add(full_url)

                # 提取标题
                title_elem = link.select_one(self.selectors.get("title", "h2, h3"))
                if not title_elem:
                    title = self.clean_text(link.get_text())
                else:
                    title = self.clean_text(title_elem.get_text())

                if not title or len(title) < 5:
                    continue

                # 提取摘要
                parent = link.parent or link
                summary_elem = parent.select_one(self.selectors.get("summary", "p"))
                summary = self.clean_text(summary_elem.get_text()) if summary_elem else ""

                article = {
                    "id": self.generate_id(full_url),
                    "title": title,
                    "original_content": summary,
                    "source": self.source_name,
                    "source_url": full_url,
                    "author": self.company,
                    "tags": self.company if self.company else None,
                    "published_at": datetime.utcnow(),
                    "collected_at": datetime.utcnow(),
                    "category": "product",  # 默认产品动态，AI 会重新分类
                    "sub_category": self.company,
                    "summary": None,
                }
                articles.append(article)

            except Exception as e:
                print(f"[{self.source_name}] 解析文章失败: {e}")
                continue

        print(f"[{self.source_name}] 爬取完成，共 {len(articles)} 篇文章")
        return articles

    def _get_base_url(self) -> str:
        """获取基础 URL"""
        from urllib.parse import urlparse
        parsed = urlparse(self.source_url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _is_article_url(self, url: str) -> bool:
        """判断是否为文章 URL"""
        # 排除一些非文章链接
        exclude_patterns = [
            r"/tag/", r"/category/", r"/author/", r"/page/",
            r"/search", r"/login", r"/register", r"/about",
            r"#", r"javascript:", r"mailto:"
        ]
        for pattern in exclude_patterns:
            if pattern in url.lower():
                return False
        return True

    @classmethod
    async def crawl_all_sources(cls) -> list[dict]:
        """爬取所有配置的媒体源"""
        all_articles = []
        for source_key in cls.MEDIA_SOURCES.keys():
            crawler = cls(source_key)
            try:
                articles = await crawler.crawl()
                all_articles.extend(articles)
            except Exception as e:
                print(f"[{source_key}] 爬取失败: {e}")
        return all_articles
