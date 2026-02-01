"""AI 处理模块 - 使用 dashscope 进行分类和摘要生成"""
import json
import asyncio
from typing import Optional
import dashscope
from dashscope import Generation

from config import settings


class AIProcessor:
    """AI 处理器 - 文章分类和摘要生成"""

    # 分类定义
    CATEGORIES = {
        "tech-innovation": {
            "name": "技术创新",
            "description": "涉及模型架构、训练方法、算法改进的论文和技术文章",
            "sub_categories": ["LLM", "多模态", "强化学习", "模型压缩", "推理优化", "架构创新", "训练方法", "其他"]
        },
        "benchmarking": {
            "name": "模型评测",
            "description": "涉及评估标准、Benchmark、安全性测试、能力评测的内容",
            "sub_categories": ["代码能力", "推理能力", "多模态", "安全性", "GUI/Agent", "语言理解", "其他"]
        },
        "product": {
            "name": "产品动态",
            "description": "AI公司的产品发布、功能更新、商业动态",
            "sub_categories": ["OpenAI", "Anthropic", "Google", "Meta", "Microsoft", "国内厂商", "创业公司", "其他"]
        }
    }

    def __init__(self):
        self.api_key = settings.dashscope_api_key
        self.model = settings.ai_model

    async def process_article(self, article: dict) -> dict:
        """处理单篇文章：分类 + 生成摘要"""
        title = article.get("title", "")
        content = article.get("original_content", "")
        source = article.get("source", "")

        # 1. 分类
        category, sub_category = await self._classify_article(title, content, source)
        article["category"] = category
        article["sub_category"] = sub_category

        # 2. 生成摘要
        if content:
            summary = await self._generate_summary(title, content)
            article["summary"] = summary

        return article

    async def _classify_article(self, title: str, content: str, source: str) -> tuple[str, str]:
        """对文章进行分类"""
        prompt = f"""请对以下AI领域的文章进行分类。

文章标题：{title}
文章来源：{source}
文章内容：{content[:1000] if content else '无'}

请从以下三个主分类中选择最合适的一个：
1. tech-innovation（技术创新）：涉及模型架构、训练方法、算法改进的论文和技术文章
2. benchmarking（模型评测）：涉及评估标准、Benchmark、安全性测试、能力评测的内容
3. product（产品动态）：AI公司的产品发布、功能更新、商业动态

同时，请选择一个子分类：
- 技术创新子分类：LLM, 多模态, 强化学习, 模型压缩, 推理优化, 架构创新, 训练方法, 其他
- 模型评测子分类：代码能力, 推理能力, 多模态, 安全性, GUI/Agent, 语言理解, 其他
- 产品动态子分类：OpenAI, Anthropic, Google, Meta, Microsoft, 国内厂商, 创业公司, 其他

请以JSON格式返回，格式如下：
{{"category": "分类ID", "sub_category": "子分类名称"}}

只返回JSON，不要其他内容。"""

        try:
            result = await self._call_api(prompt)
            if result:
                # 解析 JSON
                data = json.loads(result)
                category = data.get("category", "tech-innovation")
                sub_category = data.get("sub_category", "其他")

                # 验证分类是否有效
                if category not in self.CATEGORIES:
                    category = "tech-innovation"

                return category, sub_category
        except Exception as e:
            print(f"分类失败: {e}")

        # 默认分类
        return "tech-innovation", "其他"

    async def _generate_summary(self, title: str, content: str) -> str:
        """生成文章摘要"""
        prompt = f"""请为以下AI领域的文章生成一段简洁的中文摘要（100-150字）。
摘要应该突出文章的核心观点、技术创新点或重要信息。

文章标题：{title}
文章内容：{content[:2000] if content else '无详细内容'}

请直接返回摘要内容，不要包含"摘要："等前缀。"""

        try:
            result = await self._call_api(prompt)
            if result:
                return result.strip()
        except Exception as e:
            print(f"生成摘要失败: {e}")

        return content[:200] if content else ""

    async def generate_daily_trend(self, articles: list[dict], date: str) -> dict:
        """生成每日趋势总结"""
        # 按分类统计
        category_stats = {}
        article_summaries = []

        for article in articles[:30]:  # 限制数量
            cat = article.get("category", "unknown")
            category_stats[cat] = category_stats.get(cat, 0) + 1

            title = article.get("title", "")
            summary = article.get("summary", article.get("original_content", ""))[:100]
            article_summaries.append(f"- {title}: {summary}")

        articles_text = "\n".join(article_summaries[:20])

        prompt = f"""请根据以下今日({date})收集的AI领域文章，生成一份趋势总结报告。

今日文章统计：
- 技术创新类：{category_stats.get('tech-innovation', 0)} 篇
- 模型评测类：{category_stats.get('benchmarking', 0)} 篇
- 产品动态类：{category_stats.get('product', 0)} 篇

部分文章列表：
{articles_text}

请生成：
1. 一个简短的标题（20字以内）
2. 一段总结描述（50-100字）
3. 3-5个今日要点（每个要点20-40字）

以JSON格式返回：
{{
  "title": "标题",
  "summary": "总结描述",
  "highlights": ["要点1", "要点2", "要点3"]
}}

只返回JSON，不要其他内容。"""

        try:
            result = await self._call_api(prompt)
            if result:
                data = json.loads(result)
                return {
                    "title": data.get("title", f"{date} AI行业趋势"),
                    "summary": data.get("summary", "今日AI领域动态汇总"),
                    "highlights": data.get("highlights", []),
                    "article_count": len(articles)
                }
        except Exception as e:
            print(f"生成趋势总结失败: {e}")

        # 默认返回
        return {
            "title": f"{date} AI行业趋势",
            "summary": f"今日共收集 {len(articles)} 篇AI领域相关文章",
            "highlights": [
                f"技术创新类文章 {category_stats.get('tech-innovation', 0)} 篇",
                f"模型评测类文章 {category_stats.get('benchmarking', 0)} 篇",
                f"产品动态类文章 {category_stats.get('product', 0)} 篇",
            ],
            "article_count": len(articles)
        }

    async def _call_api(self, prompt: str) -> Optional[str]:
        """调用 dashscope API"""
        if not self.api_key:
            print("警告: DASHSCOPE_API_KEY 未配置")
            return None

        messages = [
            {"role": "system", "content": "你是一个专业的AI行业分析师，擅长对AI领域的文章进行分类和摘要。"},
            {"role": "user", "content": prompt}
        ]

        try:
            # 使用同步调用（dashscope 目前主要是同步API）
            response = await asyncio.to_thread(
                Generation.call,
                api_key=self.api_key,
                model=self.model,
                messages=messages,
                result_format="message"
            )

            # 更健壮的响应检查
            if response and hasattr(response, 'output') and response.output:
                if hasattr(response.output, 'choices') and response.output.choices:
                    choice = response.output.choices[0]
                    if hasattr(choice, 'message') and choice.message:
                        content = getattr(choice.message, 'content', None)
                        if content:
                            return content.strip()

            # 打印响应以便调试
            print(f"API 响应格式异常: {response}")
            return None
        except Exception as e:
            print(f"API 调用失败: {e}")
            return None
