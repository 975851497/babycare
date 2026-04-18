"""
RAG查询流水线构建器 - 完整的端到端RAG流程

流程架构：
1. 入口节点 → 处理用户输入
2. 并行检索 → HybridVectorSearch + HyDeVectorSearch + WebMcpSearch
3. RRF融合 → 合并多路检索结果
4. 重排序 → BGE-Reranker精排 + 断崖截断
5. 答案生成 → 基于精排上下文生成回答
"""

import asyncio
from typing import Dict, Any
from pathlib import Path

from processor.query_process.rag_state import QueryGraphState, QueryInput, QueryOutput
# from processor.query_process.nodes.entry import create_entry_state  # 暂时注释掉
from utils.client.storage_clients import StorageClients
from utils.client.ai_clients import AIClients
from core.settings import get_settings


class RAGPipelineBuilder:
    """RAG流水线构建器"""

    def __init__(self):
        self.config = get_settings()
        self.logger = __import__('logging').getLogger(__name__)

    def build_pipeline(self):
        """构建完整的RAG流水线"""
        # 1. 初始化所有节点
        entry_node = self._create_entry_node()
        hybrid_search_node = HybridVectorSearch()
        hyde_search_node = HyDeVectorSearchNode()
        web_search_node = WebMcpSearchNode()
        rrf_merge_node = RrfMergeNode()
        reranker_node = RerankerNode()
        answer_node = self._create_answer_node()

        # 2. 定义流水线流程
        async def pipeline(query_input: QueryInput) -> QueryOutput:
            """
            执行完整的RAG流水线

            Args:
                query_input: 查询输入

            Returns:
                QueryOutput: 查询输出
            """
            # 第一步：入口处理
            state = await self._execute_entry(entry_node, query_input)

            # 第二步：并行检索 (三路并行)
            hybrid_result, hyde_result, web_result = await self._execute_parallel_search(
                state, hybrid_search_node, hyde_search_node, web_search_node
            )

            # 合并并行结果
            state.update(hybrid_result)
            state.update(hyde_result)
            state.update(web_result)

            # 第三步：RRF融合
            state = rrf_merge_node.process(state)
            self.logger.info(f"RRF融合完成，共 {len(state.get('rrf_chunks', []))} 个文档")

            # 第四步：重排序
            state = reranker_node.process(state)
            self.logger.info(f"重排序完成，保留 {len(state.get('reranked_docs', []))} 个高质量文档")

            # 第五步：答案生成
            state = await self._execute_answer(answer_node, state)

            # 构建输出
            return self._build_output(state)

        return pipeline

    async def _execute_entry(self, entry_node, query_input: QueryInput) -> QueryGraphState:
        """执行入口节点"""
        # 这里需要一个入口节点来处理输入
        state = QueryGraphState(
            original_query=query_input.query,
            rewritten_query=query_input.query,  # 暂时使用原始查询
            item_names=[],  # 育儿场景下可以为空
            metadata={
                "age_group": query_input.age_group or "通用",
                "issue_type": query_input.issue_type or "通用"
            }
        )
        return state

    async def _execute_parallel_search(self, state, hybrid_node, hyde_node, web_node):
        """并行执行三路检索"""
        # 并行执行三路检索
        hybrid_task = asyncio.create_task(
            asyncio.to_thread(hybrid_node.process, state.copy()))
        hyde_task = asyncio.create_task(
            asyncio.to_thread(hyde_node.process, state.copy()))
        web_task = asyncio.create_task(
            asyncio.to_thread(web_node.process, state.copy()))

        # 等待所有检索完成
        hybrid_result, hyde_result, web_result = await asyncio.gather(
            hybrid_task, hyde_task, web_task, return_exceptions=True
        )

        # 处理异常
        if isinstance(hybrid_result, Exception):
            self.logger.error(f"HybridVectorSearch失败: {hybrid_result}")
            hybrid_result = {}
        if isinstance(hyde_result, Exception):
            self.logger.error(f"HyDeVectorSearch失败: {hyde_result}")
            hyde_result = {}
        if isinstance(web_result, Exception):
            self.logger.error(f"WebMcpSearch失败: {web_result}")
            web_result = {}

        return hybrid_result, hyde_result, web_result

    def _create_entry_node(self):
        """创建入口节点（简化版）"""
        # 这里可以创建一个专门的入口节点
        # 目前暂时使用简单函数
        pass

    def _create_answer_node(self):
        """创建答案生成节点"""
        # 这里可以创建一个专门的答案生成节点
        # 目前暂时使用简单函数
        pass

    async def _execute_answer(self, answer_node, state: QueryGraphState) -> QueryGraphState:
        """执行答案生成"""
        # 简化的答案生成逻辑
        reranked_docs = state.get('reranked_docs', [])
        original_query = state.get('original_query', '')

        if not reranked_docs:
            state['answer'] = "抱歉，我没有找到相关的育儿知识。您可以换个方式提问，或者咨询专业的育儿顾问。"
            state['status'] = 'completed'
        else:
            # 基于检索到的文档生成回答
            context = self._build_context(reranked_docs)
            answer = await self._generate_with_llm(original_query, context)
            state['answer'] = answer
            state['status'] = 'completed'

        return state

    def _build_context(self, reranked_docs: list) -> str:
        """构建LLM上下文"""
        context_parts = []
        for i, doc in enumerate(reranked_docs[:5], 1):  # 最多使用前5个文档
            content = doc.get('content', '')
            title = doc.get('title', '')
            source = doc.get('source', 'local')

            source_label = f"[来源: {'本地知识库' if source == 'local' else '联网搜索'}]"

            context_parts.append(f"""
【文档{i}】{title} {source_label}
{content}
""")

        return "\n".join(context_parts)

    async def _generate_with_llm(self, query: str, context: str) -> str:
        """使用LLM生成回答"""
        try:
            llm_client = AIClients.get_llm_client(response_format=False)

            system_prompt = """你是一位资深育儿专家，擅长为家长提供实用、温暖的育儿建议。

请基于检索到的知识库内容回答用户问题，并遵循以下原则：
1. **共情理解**：先理解家长的难处，给予情感支持
2. **专业分析**：基于儿童心理学或权威理论进行分析
3. **实操建议**：给出具体的"话术"或"行动步骤"
4. **拒绝说教**：不要讲大道理，用温暖、人性化的语言

如果知识库中没有相关信息，请明确告知。"""

            user_prompt = f"""用户问题：{query}

相关知识库内容：
{context}

请根据上述知识库内容，为家长提供温暖、专业的建议。"""

            response = llm_client.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])

            return response.content

        except Exception as e:
            self.logger.error(f"LLM生成回答失败: {str(e)}")
            return "抱歉，我在生成回答时遇到了问题，请稍后再试。"

    def _build_output(self, state: QueryGraphState) -> QueryOutput:
        """构建查询输出"""
        answer = state.get('answer', '')
        reranked_docs = state.get('reranked_docs', [])

        # 提取来源信息
        sources = []
        for doc in reranked_docs[:3]:  # 最多返回3个来源
            sources.append({
                "title": doc.get('title', ''),
                "source": doc.get('source', 'local'),
                "content": doc.get('content', '')[:100] + "..."
            })

        return QueryOutput(
            answer=answer,
            sources=sources,
            confidence=0.8  # 简化版，实际可以基于rerank分数计算
        )


# 创建全局流水线实例
_rag_pipeline = None


def get_rag_pipeline():
    """获取RAG流水线单例"""
    global _rag_pipeline
    if _rag_pipeline is None:
        builder = RAGPipelineBuilder()
        _rag_pipeline = builder.build_pipeline()
    return _rag_pipeline


async def run_rag_query(query: str, age_group: str = None, issue_type: str = None) -> str:
    """
    运行RAG查询 (简化接口)

    Args:
        query: 用户查询
        age_group: 年龄段过滤
        issue_type: 问题类型过滤

    Returns:
        str: 生成的回答
    """
    pipeline = get_rag_pipeline()
    query_input = QueryInput(
        query=query,
        age_group=age_group,
        issue_type=issue_type
    )

    result = await pipeline(query_input)
    return result.answer


if __name__ == "__main__":
    import asyncio
    import sys
    import io

    # 设置UTF-8编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    async def test():
        """测试RAG流水线"""
        print("🧪 测试RAG流水线")
        print("=" * 60)

        query = "宝宝挑食怎么办？"
        print(f"❓ 用户问题: {query}")
        print("-" * 60)

        try:
            answer = await run_rag_query(query, age_group="3-6岁", issue_type="健康饮食")

            print(f"\n💡 AI回答:")
            print(answer)

        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()

    asyncio.run(test())
