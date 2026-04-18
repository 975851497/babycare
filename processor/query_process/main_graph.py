"""查询主流程图：意图路由 → 检索 → 融合排序 → 流式生成（可追溯引用）。"""

from langgraph.graph import StateGraph, END

from processor.query_process.state import QueryState


async def knowledge_search(state: QueryState) -> QueryState:
    """知识搜索节点：检索相关文档片段。

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    # TODO: 实现知识检索逻辑
    pass


async def answer_output(state: QueryState) -> QueryState:
    """答案输出节点：基于检索结果生成回答。

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    # TODO: 实现答案生成逻辑
    pass


def build_query_graph() -> StateGraph:
    """构建查询流程图。

    Returns:
        编译后的状态图
    """
    # 创建状态图
    workflow = StateGraph(QueryState)

    # 添加节点
    workflow.add_node("knowledge_search", knowledge_search)
    workflow.add_node("answer_output", answer_output)

    # 设置入口
    workflow.set_entry_point("knowledge_search")

    # 添加边：线性流程
    workflow.add_edge("knowledge_search", "answer_output")
    workflow.add_edge("answer_output", END)

    return workflow.compile()


def run_query_pipeline(question: str) -> QueryState:
    """运行查询流程。

    Args:
        question: 用户问题

    Returns:
        最终的 QueryState
    """
    # 初始化状态
    initial_state: QueryState = {
        "question": question,
        "status": "searching",
        "retrieved_docs": [],
        "final_answer": ""
    }

    # 构建并运行图
    graph = build_query_graph()

    try:
        result = graph.invoke(initial_state)

        # 设置最终状态
        if result.get("status") != "failed":
            result["status"] = "completed"

        return result

    except Exception as e:
        # 异常处理
        initial_state["status"] = "failed"
        initial_state["error"] = str(e)
        return initial_state


if __name__ == "__main__":
    # 测试用例
    test_question = "宝宝挑食怎么办？"

    result = run_query_pipeline(test_question)

    print("\n===== 执行结果 =====")
    print(f"问题: {result.get('question')}")
    print(f"状态: {result.get('status')}")
    print(f"错误: {result.get('error', '无')}")
    print(f"检索文档数: {len(result.get('retrieved_docs', []))}")
    print(f"最终回答: {result.get('final_answer', '暂无')}")
