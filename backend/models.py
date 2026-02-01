"""数据库模型定义"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum

Base = declarative_base()


class CategoryType(str, Enum):
    """文章分类"""
    TECH_INNOVATION = "tech-innovation"  # 技术创新
    BENCHMARKING = "benchmarking"        # 模型评测
    PRODUCT = "product"                  # 产品动态


class Article(Base):
    """文章/论文表"""
    __tablename__ = "articles"

    id = Column(String(64), primary_key=True)  # URL hash
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)  # AI 生成的摘要
    original_content = Column(Text, nullable=True)  # 原始内容/摘要

    # 分类
    category = Column(String(50), nullable=False)  # tech-innovation / benchmarking / product
    sub_category = Column(String(100), nullable=True)  # 子分类: LLM, 多模态, Code, GUI, OpenAI等

    # 来源信息
    source = Column(String(100), nullable=False)  # HuggingFace, TechCrunch 等
    source_url = Column(String(1000), nullable=False, unique=True)
    author = Column(String(200), nullable=True)

    # 标签
    tags = Column(Text, nullable=True)  # JSON 格式存储

    # 时间
    published_at = Column(DateTime, nullable=True)  # 原文发布时间
    collected_at = Column(DateTime, default=datetime.utcnow)  # 采集时间

    # 状态
    is_favorited = Column(Boolean, default=False)  # 是否被收藏

    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title[:30]}...)>"


class TrendSummary(Base):
    """每日趋势总结表"""
    __tablename__ = "trend_summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(10), unique=True, nullable=False)  # YYYY-MM-DD
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)  # AI 生成的当日总结
    highlights = Column(Text, nullable=True)  # JSON 格式，要点列表
    article_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TrendSummary(date={self.date})>"


class CrawlLog(Base):
    """爬虫日志表"""
    __tablename__ = "crawl_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # success / failed
    articles_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<CrawlLog(source={self.source}, status={self.status})>"
