"""AI Pulse 后端主应用"""
import json
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings
import database
from scheduler import TaskScheduler


# 全局调度器实例
scheduler = TaskScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    await database.init_db()
    scheduler.start()
    print("AI Pulse 后端服务已启动")

    yield

    # 关闭时
    scheduler.stop()
    print("AI Pulse 后端服务已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="AI Pulse API",
    description="AI 脉动 - 一站式 AI 行业前沿深度情报扫描与自动化摘要系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],  # 开发环境允许所有
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 响应模型 ============

class ArticleResponse(BaseModel):
    id: str
    title: str
    summary: Optional[str]
    original_content: Optional[str]
    category: str
    sub_category: Optional[str]
    source: str
    source_url: str
    author: Optional[str]
    tags: Optional[list[str]]
    published_at: Optional[str]
    collected_at: str
    is_favorited: bool


class TrendResponse(BaseModel):
    date: str
    title: str
    summary: str
    highlights: list[str]
    article_count: int


class StatsResponse(BaseModel):
    total: int
    by_category: dict
    today: int
    available_dates: list[str]


# ============ API 路由 ============

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "AI Pulse API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/articles", response_model=list[ArticleResponse])
async def get_articles(
    category: Optional[str] = Query(None, description="分类筛选: tech-innovation, benchmarking, product"),
    date: Optional[str] = Query(None, description="日期筛选: YYYY-MM-DD"),
    favorites: bool = Query(False, description="仅显示收藏"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """获取文章列表"""
    articles = await database.get_articles(
        category=category,
        date=date,
        limit=limit,
        offset=offset,
        favorites_only=favorites
    )

    return [
        ArticleResponse(
            id=a.id,
            title=a.title,
            summary=a.summary,
            original_content=a.original_content,
            category=a.category,
            sub_category=a.sub_category,
            source=a.source,
            source_url=a.source_url,
            author=a.author,
            tags=a.tags.split(",") if a.tags else [],
            published_at=a.published_at.isoformat() if a.published_at else None,
            collected_at=a.collected_at.isoformat(),
            is_favorited=a.is_favorited
        )
        for a in articles
    ]


@app.get("/api/articles/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: str):
    """获取单篇文章"""
    article = await database.get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    return ArticleResponse(
        id=article.id,
        title=article.title,
        summary=article.summary,
        original_content=article.original_content,
        category=article.category,
        sub_category=article.sub_category,
        source=article.source,
        source_url=article.source_url,
        author=article.author,
        tags=article.tags.split(",") if article.tags else [],
        published_at=article.published_at.isoformat() if article.published_at else None,
        collected_at=article.collected_at.isoformat(),
        is_favorited=article.is_favorited
    )


@app.post("/api/articles/{article_id}/favorite")
async def toggle_favorite(article_id: str):
    """切换收藏状态"""
    new_status = await database.toggle_favorite(article_id)
    if new_status is None:
        raise HTTPException(status_code=404, detail="文章不存在")

    return {"id": article_id, "is_favorited": new_status}


@app.get("/api/trend", response_model=Optional[TrendResponse])
async def get_trend(date: Optional[str] = Query(None, description="日期: YYYY-MM-DD")):
    """获取趋势总结"""
    trend = await database.get_trend_summary(date)
    if not trend:
        return None

    highlights = []
    if trend.highlights:
        try:
            highlights = json.loads(trend.highlights)
        except:
            highlights = []

    return TrendResponse(
        date=trend.date,
        title=trend.title,
        summary=trend.summary,
        highlights=highlights,
        article_count=trend.article_count
    )


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """获取统计信息"""
    stats = await database.get_article_stats()
    dates = await database.get_available_dates()

    return StatsResponse(
        total=stats["total"],
        by_category=stats["by_category"],
        today=stats["today"],
        available_dates=dates
    )


@app.post("/api/crawl")
async def trigger_crawl():
    """手动触发爬取（管理员接口）"""
    result = await scheduler.run_crawl_now()
    return result


@app.post("/api/trend/generate")
async def generate_trend(date: Optional[str] = Query(None, description="日期: YYYY-MM-DD，不指定则使用最近有文章的日期")):
    """手动生成趋势总结"""
    target_date = date

    if not target_date:
        # 获取有文章的日期列表
        available_dates = await database.get_available_dates()
        if available_dates:
            target_date = available_dates[0]  # 最近的日期
        else:
            return {"status": "error", "message": "没有找到任何文章数据"}

    await scheduler.generate_trend_for_date(target_date)
    return {"status": "success", "message": f"已为 {target_date} 生成趋势总结"}


@app.get("/api/categories")
async def get_categories():
    """获取分类列表"""
    from ai_processor import AIProcessor
    return AIProcessor.CATEGORIES


# ============ 启动入口 ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
