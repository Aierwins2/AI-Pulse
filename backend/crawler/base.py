"""爬虫基类"""
import hashlib
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
import httpx
from bs4 import BeautifulSoup


class BaseCrawler(ABC):
    """爬虫基类"""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5,zh-CN;q=0.3",
        }
        self.timeout = 30.0
        self.source_name = "Unknown"

    @abstractmethod
    async def crawl(self) -> list[dict]:
        """执行爬取，返回文章列表"""
        pass

    async def fetch_page(self, url: str) -> Optional[str]:
        """获取页面内容"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"[{self.source_name}] 获取页面失败 {url}: {e}")
            return None

    async def fetch_json(self, url: str) -> Optional[dict]:
        """获取 JSON 数据"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[{self.source_name}] 获取 JSON 失败 {url}: {e}")
            return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """解析 HTML"""
        return BeautifulSoup(html, "lxml")

    def generate_id(self, url: str) -> str:
        """根据 URL 生成唯一 ID"""
        return hashlib.md5(url.encode()).hexdigest()

    def clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        # 移除多余空白
        text = " ".join(text.split())
        return text.strip()

    def extract_date(self, date_str: str) -> Optional[datetime]:
        """尝试解析日期字符串"""
        from dateutil import parser
        try:
            return parser.parse(date_str)
        except:
            return None
