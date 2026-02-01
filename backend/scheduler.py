"""定时任务调度器"""
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import settings
from crawler import CrawlerManager
from ai_processor import AIProcessor
import database


class TaskScheduler:
    """定时任务调度器"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        self.ai_processor = AIProcessor()
        self.crawler_manager = CrawlerManager(ai_processor=self.ai_processor)
        self.is_running = False

    def start(self):
        """启动调度器"""
        # 每日定时爬取任务
        self.scheduler.add_job(
            self.daily_crawl_task,
            CronTrigger(
                hour=settings.crawler_schedule_hour,
                minute=settings.crawler_schedule_minute
            ),
            id="daily_crawl",
            name="每日数据采集",
            replace_existing=True
        )

        # 每日清理过期数据
        self.scheduler.add_job(
            self.cleanup_task,
            CronTrigger(hour=3, minute=0),  # 凌晨3点清理
            id="daily_cleanup",
            name="清理过期数据",
            replace_existing=True
        )

        self.scheduler.start()
        print(f"调度器已启动，每日 {settings.crawler_schedule_hour}:{settings.crawler_schedule_minute:02d} 执行数据采集")

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        print("调度器已停止")

    async def daily_crawl_task(self):
        """每日爬取任务"""
        if self.is_running:
            print("爬取任务正在运行中，跳过本次执行")
            return

        self.is_running = True
        print(f"[{datetime.now()}] 开始执行每日数据采集...")

        try:
            # 1. 运行爬虫
            results = await self.crawler_manager.run_all_crawlers()

            # 2. 保存文章到数据库
            articles = results.get("articles", [])
            if articles:
                added_count = await database.add_articles_batch(articles)
                print(f"成功保存 {added_count} 篇新文章")

                # 3. 生成每日趋势
                today = datetime.now().strftime("%Y-%m-%d")
                trend = await self.ai_processor.generate_daily_trend(articles, today)

                await database.save_trend_summary(
                    date=today,
                    title=trend["title"],
                    summary=trend["summary"],
                    highlights=trend["highlights"],
                    article_count=trend["article_count"]
                )
                print(f"每日趋势总结已生成")

            # 4. 记录爬取日志
            await database.add_crawl_log(
                source="all",
                status="success",
                articles_count=results["total_articles"],
                started_at=datetime.fromisoformat(results["started_at"]),
                finished_at=datetime.fromisoformat(results["finished_at"])
            )

            print(f"[{datetime.now()}] 每日数据采集完成，共采集 {results['total_articles']} 篇文章")

        except Exception as e:
            print(f"每日爬取任务失败: {e}")
            await database.add_crawl_log(
                source="all",
                status="failed",
                error_message=str(e),
                started_at=datetime.utcnow()
            )
        finally:
            self.is_running = False

    async def cleanup_task(self):
        """清理过期数据"""
        print(f"[{datetime.now()}] 开始清理过期数据...")
        try:
            await database.cleanup_old_articles()
            print(f"[{datetime.now()}] 过期数据清理完成")
        except Exception as e:
            print(f"清理过期数据失败: {e}")

    async def run_crawl_now(self) -> dict:
        """立即执行一次爬取（手动触发）"""
        if self.is_running:
            return {"status": "error", "message": "爬取任务正在运行中"}

        # 异步执行，不阻塞
        asyncio.create_task(self.daily_crawl_task())
        return {"status": "started", "message": "爬取任务已启动"}
