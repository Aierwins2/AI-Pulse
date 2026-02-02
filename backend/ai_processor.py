"""AI 处理模块 - 使用规则分类 + dashscope 生成每日趋势"""
import json
import asyncio
import re
from typing import Optional
import dashscope
from dashscope import Generation

from config import settings


class AIProcessor:
    """AI 处理器 - 规则分类 + 每日趋势生成"""

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

    # 产品动态关键词（公司/产品名）
    PRODUCT_KEYWORDS = [
        "openai", "gpt-4", "gpt-5", "chatgpt", "dall-e", "sora",
        "anthropic", "claude",
        "google", "gemini", "bard", "deepmind",
        "meta", "llama",
        "microsoft", "copilot", "bing",
        "百度", "文心", "ernie", "阿里", "通义", "qwen", "腾讯", "混元",
        "字节", "豆包", "coze", "智谱", "chatglm",
        "发布", "上线", "更新", "推出", "开放", "收购", "融资", "合作"
    ]

    # 评测关键词
    BENCHMARK_KEYWORDS = [
        "bench", "eval", "evaluation", "benchmark", "leaderboard",
        "测试", "评测", "评估", "排行", "对比", "comparison",
        "mmlu", "humaneval", "gsm8k", "hellaswag", "arc", "winogrande"
    ]

    def __init__(self):
        self.api_key = settings.dashscope_api_key
        self.model = settings.ai_model

    async def process_article(self, article: dict) -> dict:
        """处理单篇文章：纯规则分类，不调用API"""
        title = article.get("title", "")
        content = article.get("original_content", "")
        source = article.get("source", "")

        # 规则分类
        category, sub_category = self._classify_by_rules(title, content, source)
        article["category"] = category
        article["sub_category"] = sub_category

        # 摘要直接使用原始内容的前200字
        if content and not article.get("summary"):
            article["summary"] = content[:200]

        return article

    def _classify_by_rules(self, title: str, content: str, source: str) -> tuple[str, str]:
        """纯规则分类，不调用API"""
        text = f"{title} {content}".lower()
        title_lower = title.lower()

        # 1. 评测类：标题或内容包含评测关键词
        for keyword in self.BENCHMARK_KEYWORDS:
            if keyword in title_lower or keyword in text:
                sub_cat = self._get_benchmark_subcategory(text)
                return "benchmarking", sub_cat

        # 2. 产品动态：包含公司/产品名或商业关键词
        for keyword in self.PRODUCT_KEYWORDS:
            if keyword in text:
                sub_cat = self._get_product_subcategory(text)
                return "product", sub_cat

        # 3. 默认：技术创新（论文通常是技术创新）
        sub_cat = self._get_tech_subcategory(text)
        return "tech-innovation", sub_cat

    def _get_benchmark_subcategory(self, text: str) -> str:
        """获取评测子分类"""
        if any(k in text for k in ["code", "代码", "humaneval", "mbpp"]):
            return "代码能力"
        if any(k in text for k in ["reason", "推理", "gsm", "math"]):
            return "推理能力"
        if any(k in text for k in ["multimodal", "多模态", "vision", "image", "video"]):
            return "多模态"
        if any(k in text for k in ["safe", "安全", "toxic", "bias"]):
            return "安全性"
        if any(k in text for k in ["agent", "gui", "web", "tool"]):
            return "GUI/Agent"
        return "其他"

    def _get_product_subcategory(self, text: str) -> str:
        """获取产品子分类"""
        if any(k in text for k in ["openai", "gpt", "chatgpt", "dall-e", "sora"]):
            return "OpenAI"
        if any(k in text for k in ["anthropic", "claude"]):
            return "Anthropic"
        if any(k in text for k in ["google", "gemini", "bard", "deepmind"]):
            return "Google"
        if any(k in text for k in ["meta", "llama"]):
            return "Meta"
        if any(k in text for k in ["microsoft", "copilot", "bing"]):
            return "Microsoft"
        if any(k in text for k in ["百度", "文心", "阿里", "通义", "腾讯", "混元", "字节", "豆包", "智谱"]):
            return "国内厂商"
        return "创业公司"

    def _get_tech_subcategory(self, text: str) -> str:
        """获取技术创新子分类"""
        if any(k in text for k in ["llm", "language model", "大模型", "大语言"]):
            return "LLM"
        if any(k in text for k in ["multimodal", "多模态", "vision", "image", "video", "audio"]):
            return "多模态"
        if any(k in text for k in ["reinforcement", "rlhf", "强化学习", "reward"]):
            return "强化学习"
        if any(k in text for k in ["quantiz", "prune", "distill", "compress", "量化", "蒸馏", "剪枝"]):
            return "模型压缩"
        if any(k in text for k in ["inference", "推理优化", "加速", "accelerat", "efficient"]):
            return "推理优化"
        if any(k in text for k in ["attention", "transformer", "架构", "mamba", "ssm"]):
            return "架构创新"
        if any(k in text for k in ["train", "pretrain", "finetun", "训练"]):
            return "训练方法"
        return "其他"

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

            if response and response.output:
                content = response.output.choices[0].message.content
                return content.strip()
        except Exception as e:
            print(f"API 调用失败: {e}")
            return None

        return None
