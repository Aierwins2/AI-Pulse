"""HuggingFace Papers 爬虫"""
import re
from datetime import datetime
from typing import Optional
from .base import BaseCrawler


class HuggingFaceCrawler(BaseCrawler):
    """HuggingFace Daily Papers 爬虫"""

    def __init__(self):
        super().__init__()
        self.source_name = "HuggingFace"
        self.base_url = "https://huggingface.co"
        self.papers_url = "https://huggingface.co/papers"

    async def crawl(self) -> list[dict]:
        """爬取 HuggingFace 每日论文"""
        print(f"[{self.source_name}] 开始爬取论文...")

        html = await self.fetch_page(self.papers_url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # 查找论文卡片
        paper_cards = soup.select("article")

        for card in paper_cards:
            try:
                article = self._parse_paper_card(card)
                if article:
                    articles.append(article)
            except Exception as e:
                print(f"[{self.source_name}] 解析论文卡片失败: {e}")
                continue

        print(f"[{self.source_name}] 爬取完成，共 {len(articles)} 篇论文")
        return articles

    def _parse_paper_card(self, card) -> Optional[dict]:
        """解析单个论文卡片"""
        # 获取标题和链接
        title_elem = card.select_one("h3 a")
        if not title_elem:
            return None

        title = self.clean_text(title_elem.get_text())
        href = title_elem.get("href", "")

        # 构建完整 URL
        if href.startswith("/"):
            paper_url = f"{self.base_url}{href}"
        else:
            paper_url = href

        if not paper_url or not title:
            return None

        # 获取摘要/描述
        summary_elem = card.select_one("p")
        summary = self.clean_text(summary_elem.get_text()) if summary_elem else ""

        # 获取作者
        author_elem = card.select_one(".text-gray-500")
        author = self.clean_text(author_elem.get_text()) if author_elem else ""

        # 获取标签
        tag_elems = card.select("a[href*='/models?other=']") or card.select(".tag")
        tags = [self.clean_text(t.get_text()) for t in tag_elems]

        # 提取 arXiv ID（如果有）
        arxiv_match = re.search(r"arxiv\.org/abs/(\d+\.\d+)", paper_url)
        if arxiv_match:
            tags.append(f"arXiv:{arxiv_match.group(1)}")

        return {
            "id": self.generate_id(paper_url),
            "title": title,
            "original_content": summary,
            "source": self.source_name,
            "source_url": paper_url,
            "author": author,
            "tags": ",".join(tags) if tags else None,
            "published_at": datetime.utcnow(),
            "collected_at": datetime.utcnow(),
            # 分类由 AI 处理模块后续填充
            "category": "tech-innovation",  # 默认值，后续 AI 会重新分类
            "sub_category": None,
            "summary": None,  # 由 AI 生成
        }

    async def get_paper_detail(self, paper_url: str) -> Optional[dict]:
        """获取论文详情页信息"""
        html = await self.fetch_page(paper_url)
        if not html:
            return None

        soup = self.parse_html(html)

        # 尝试获取完整摘要
        abstract_elem = soup.select_one(".abstract") or soup.select_one("[class*='abstract']")
        abstract = self.clean_text(abstract_elem.get_text()) if abstract_elem else None

        return {
            "abstract": abstract
        }
