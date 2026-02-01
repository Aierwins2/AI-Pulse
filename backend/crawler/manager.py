"""爬虫管理器"""
import asyncio
from datetime import datetime
from typing import Callable, Optional

from .huggingface import HuggingFaceCrawler
from .media import MediaCrawler


class CrawlerManager:
    """爬虫管理器 - 协调所有爬虫"""

    def __init__(self, ai_processor=None):
        self.hf_crawler = HuggingFaceCrawler()
        self.ai_processor = ai_processor
        self.on_progress: Optional[Callable] = None

    def set_progress_callback(self, callback: Callable):
        """设置进度回调"""
        self.on_progress = callback

    def _report_progress(self, message: str):
        """报告进度"""
        print(message)
        if self.on_progress:
            self.on_progress(message)

    async def run_all_crawlers(self) -> dict:
        """运行所有爬虫"""
        start_time = datetime.utcnow()
        results = {
            "total_articles": 0,
            "by_source": {},
            "errors": [],
            "started_at": start_time.isoformat(),
            "finished_at": None,
        }

        all_articles = []

        # 1. 爬取 HuggingFace Papers
        self._report_progress("开始爬取 HuggingFace Papers...")
        try:
            hf_articles = await self.hf_crawler.crawl()
            all_articles.extend(hf_articles)
            results["by_source"]["HuggingFace"] = len(hf_articles)
        except Exception as e:
            error_msg = f"HuggingFace 爬取失败: {str(e)}"
            results["errors"].append(error_msg)
            self._report_progress(error_msg)

        # 2. 爬取媒体网站
        self._report_progress("开始爬取媒体网站...")
        for source_key in MediaCrawler.MEDIA_SOURCES.keys():
            try:
                crawler = MediaCrawler(source_key)
                articles = await crawler.crawl()
                all_articles.extend(articles)
                results["by_source"][crawler.source_name] = len(articles)
            except Exception as e:
                error_msg = f"{source_key} 爬取失败: {str(e)}"
                results["errors"].append(error_msg)
                self._report_progress(error_msg)

            # 避免请求过快
            await asyncio.sleep(1)

        # 3. 去重
        self._report_progress(f"去重前文章数: {len(all_articles)}")
        all_articles = self._deduplicate(all_articles)
        self._report_progress(f"去重后文章数: {len(all_articles)}")

        # 注意：不再对每篇文章调用 AI，只在生成每日趋势时调用一次 AI

        results["total_articles"] = len(all_articles)
        results["articles"] = all_articles
        results["finished_at"] = datetime.utcnow().isoformat()

        return results

    def _deduplicate(self, articles: list[dict]) -> list[dict]:
        """去重：基于 URL 和标题相似度"""
        seen_urls = set()
        seen_titles = set()
        unique_articles = []

        for article in articles:
            url = article.get("source_url", "")
            title = article.get("title", "").lower().strip()

            # URL 去重
            if url in seen_urls:
                continue

            # 标题相似度去重（简单实现：完全匹配）
            title_key = self._normalize_title(title)
            if title_key in seen_titles:
                continue

            seen_urls.add(url)
            seen_titles.add(title_key)
            unique_articles.append(article)

        return unique_articles

    def _normalize_title(self, title: str) -> str:
        """标准化标题用于去重"""
        import re
        # 移除标点符号和多余空格
        title = re.sub(r'[^\w\s]', '', title.lower())
        title = ' '.join(title.split())
        return title

    async def run_single_source(self, source: str) -> list[dict]:
        """运行单个数据源的爬虫"""
        if source == "huggingface":
            return await self.hf_crawler.crawl()
        elif source in MediaCrawler.MEDIA_SOURCES:
            crawler = MediaCrawler(source)
            return await crawler.crawl()
        else:
            raise ValueError(f"未知数据源: {source}")
