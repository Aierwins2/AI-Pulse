"""媒体网站爬虫"""
import re
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urljoin, urlparse
from .base import BaseCrawler


# 需要过滤的社交媒体和登录页面域名
BLOCKED_DOMAINS = [
    "linkedin.com", "facebook.com", "x.com", "twitter.com",
    "instagram.com", "weibo.com", "zhihu.com", "douyin.com",
    "tiktok.com", "youtube.com", "bilibili.com"
]

# 常见网站名称（标题如果只是这些，说明内容抓取失败）
WEBSITE_NAMES = [
    "linkedin", "facebook", "x.com", "twitter", "instagram",
    "weibo", "微博", "知乎", "抖音", "tiktok", "youtube", "bilibili",
    "google", "meta", "openai", "anthropic", "登录", "login", "sign in"
]


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

                # 构建完整 URL（使用 urljoin 确保正确拼接）
                full_url = urljoin(self.source_url, href)

                # 验证 URL 格式
                if not full_url.startswith(("http://", "https://")):
                    continue

                # 过滤非文章链接
                if not self._is_article_url(full_url):
                    continue

                # 过滤社交媒体和需要登录的链接
                if self._is_blocked_domain(full_url):
                    continue

                seen_urls.add(full_url)

                # 提取标题
                title_elem = link.select_one(self.selectors.get("title", "h2, h3"))
                if not title_elem:
                    title = self.clean_text(link.get_text())
                else:
                    title = self.clean_text(title_elem.get_text())

                # 内容质量检测
                if not self._is_valid_title(title):
                    continue

                # 提取摘要
                parent = link.parent or link
                summary_elem = parent.select_one(self.selectors.get("summary", "p"))
                summary = self.clean_text(summary_elem.get_text()) if summary_elem else ""

                # 尝试提取发布日期
                published_at = self._extract_publish_date(link, parent)

                article = {
                    "id": self.generate_id(full_url),
                    "title": title,
                    "original_content": summary,
                    "source": self.source_name,
                    "source_url": full_url,
                    "author": self.company,
                    "tags": self.company if self.company else None,
                    "published_at": published_at,
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

    def _is_blocked_domain(self, url: str) -> bool:
        """检查是否为需要过滤的域名"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            for blocked in BLOCKED_DOMAINS:
                if blocked in domain:
                    return True
        except:
            pass
        return False

    def _is_valid_title(self, title: str) -> bool:
        """检查标题是否有效（非网站名称、长度足够）"""
        if not title or len(title) < 10:
            return False

        title_lower = title.lower().strip()

        # 检查是否只是网站名称
        for name in WEBSITE_NAMES:
            if title_lower == name or title_lower == name.lower():
                return False
            # 标题太短且包含网站名称
            if len(title) < 20 and name in title_lower:
                return False

        return True

    def _extract_publish_date(self, link, parent) -> datetime:
        """尝试从页面元素提取发布日期"""
        now = datetime.utcnow()

        # 尝试从 time 标签提取
        time_elem = parent.select_one("time") if parent else None
        if time_elem:
            datetime_attr = time_elem.get("datetime", "")
            if datetime_attr:
                try:
                    return datetime.fromisoformat(datetime_attr.replace("Z", "+00:00"))
                except:
                    pass

        # 尝试从 URL 提取日期（常见格式：/2026/02/01/ 或 /20260201/）
        url = link.get("href", "")
        date_patterns = [
            r'/(\d{4})/(\d{2})/(\d{2})/',  # /2026/02/01/
            r'/(\d{4})(\d{2})(\d{2})/',     # /20260201/
            r'(\d{4})-(\d{2})-(\d{2})',     # 2026-02-01
        ]
        for pattern in date_patterns:
            match = re.search(pattern, url)
            if match:
                try:
                    year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    return datetime(year, month, day)
                except:
                    pass

        # 默认返回当前时间
        return now

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
