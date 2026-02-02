"""数据库操作"""
import json
import os
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, delete, func, and_
from sqlalchemy.orm import selectinload

from models import Base, Article, TrendSummary, CrawlLog
from config import settings


# 确保数据目录存在
os.makedirs("data", exist_ok=True)

# 创建异步引擎
engine = create_async_engine(settings.database_url, echo=False)

# 创建异步 session 工厂
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """初始化数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """获取数据库 session"""
    async with async_session() as session:
        yield session


# ============ Article 操作 ============

async def add_article(article_data: dict) -> Optional[Article]:
    """添加文章，如果已存在则跳过"""
    async with async_session() as session:
        # 检查是否已存在
        result = await session.execute(
            select(Article).where(Article.source_url == article_data["source_url"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            return None

        article = Article(**article_data)
        session.add(article)
        await session.commit()
        await session.refresh(article)
        return article


async def add_articles_batch(articles_data: list[dict]) -> int:
    """批量添加文章，返回成功添加的数量"""
    added_count = 0
    async with async_session() as session:
        for data in articles_data:
            result = await session.execute(
                select(Article).where(Article.source_url == data["source_url"])
            )
            if not result.scalar_one_or_none():
                article = Article(**data)
                session.add(article)
                added_count += 1
        await session.commit()
    return added_count


async def get_articles(
    category: Optional[str] = None,
    date: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    favorites_only: bool = False
) -> list[Article]:
    """获取文章列表"""
    async with async_session() as session:
        query = select(Article)

        conditions = []
        if category:
            conditions.append(Article.category == category)
        if date:
            # 解析日期，根据发布日期筛选当天的文章
            target_date = datetime.strptime(date, "%Y-%m-%d")
            next_date = target_date + timedelta(days=1)
            conditions.append(Article.published_at >= target_date)
            conditions.append(Article.published_at < next_date)
        if favorites_only:
            conditions.append(Article.is_favorited == True)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Article.published_at.desc()).offset(offset).limit(limit)

        result = await session.execute(query)
        return result.scalars().all()


async def get_article_by_id(article_id: str) -> Optional[Article]:
    """根据 ID 获取文章"""
    async with async_session() as session:
        result = await session.execute(
            select(Article).where(Article.id == article_id)
        )
        return result.scalar_one_or_none()


async def toggle_favorite(article_id: str) -> Optional[bool]:
    """切换收藏状态，返回新状态"""
    async with async_session() as session:
        result = await session.execute(
            select(Article).where(Article.id == article_id)
        )
        article = result.scalar_one_or_none()
        if not article:
            return None

        article.is_favorited = not article.is_favorited
        await session.commit()
        return article.is_favorited


async def get_available_dates() -> list[str]:
    """获取有数据的日期列表（基于发布日期）"""
    async with async_session() as session:
        result = await session.execute(
            select(func.date(Article.published_at).label("date"))
            .distinct()
            .order_by(func.date(Article.published_at).desc())
        )
        dates = result.scalars().all()
        return [str(d) for d in dates if d]


async def get_article_stats() -> dict:
    """获取文章统计信息"""
    async with async_session() as session:
        # 总数
        total_result = await session.execute(select(func.count(Article.id)))
        total = total_result.scalar()

        # 按分类统计
        category_result = await session.execute(
            select(Article.category, func.count(Article.id))
            .group_by(Article.category)
        )
        by_category = {row[0]: row[1] for row in category_result}

        # 今日新增
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_result = await session.execute(
            select(func.count(Article.id)).where(Article.collected_at >= today)
        )
        today_count = today_result.scalar()

        return {
            "total": total,
            "by_category": by_category,
            "today": today_count
        }


# ============ TrendSummary 操作 ============

async def save_trend_summary(date: str, title: str, summary: str, highlights: list[str], article_count: int):
    """保存每日趋势总结"""
    async with async_session() as session:
        # 检查是否已存在
        result = await session.execute(
            select(TrendSummary).where(TrendSummary.date == date)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.title = title
            existing.summary = summary
            existing.highlights = json.dumps(highlights, ensure_ascii=False)
            existing.article_count = article_count
        else:
            trend = TrendSummary(
                date=date,
                title=title,
                summary=summary,
                highlights=json.dumps(highlights, ensure_ascii=False),
                article_count=article_count
            )
            session.add(trend)

        await session.commit()


async def get_trend_summary(date: Optional[str] = None) -> Optional[TrendSummary]:
    """获取趋势总结"""
    async with async_session() as session:
        if date:
            result = await session.execute(
                select(TrendSummary).where(TrendSummary.date == date)
            )
        else:
            # 获取最新的
            result = await session.execute(
                select(TrendSummary).order_by(TrendSummary.date.desc()).limit(1)
            )
        return result.scalar_one_or_none()


# ============ CrawlLog 操作 ============

async def add_crawl_log(source: str, status: str, articles_count: int = 0,
                        error_message: str = None, started_at: datetime = None,
                        finished_at: datetime = None):
    """添加爬虫日志"""
    async with async_session() as session:
        log = CrawlLog(
            source=source,
            status=status,
            articles_count=articles_count,
            error_message=error_message,
            started_at=started_at or datetime.utcnow(),
            finished_at=finished_at
        )
        session.add(log)
        await session.commit()


# ============ 数据清理 ============

async def cleanup_old_articles():
    """清理过期文章（基于发布日期，保留收藏的）"""
    async with async_session() as session:
        cutoff_date = datetime.utcnow() - timedelta(days=settings.data_retention_days)

        # 删除发布日期超过保留期且未收藏的文章
        await session.execute(
            delete(Article).where(
                and_(
                    Article.published_at < cutoff_date,
                    Article.is_favorited == False
                )
            )
        )
        await session.commit()
