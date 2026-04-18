"""
导入流程主图 - LangGraph 标准实现
"""
from typing import TypedDict, Annotated, Sequence
from operator import add
from langgraph.graph import StateGraph, END

from processor.import_process.state import ImportState
from processor.import_process.nodes.parse_document import parse_document
from processor.import_process.nodes.split_document import split_document
from processor.import_process.nodes.embedding import generate_embedding
from processor.import_process.nodes.vector_upsert import vector_upsert


def should_continue(state: ImportState) -> str:
    """条件边：根据状态决定下一步"""
    status = state.get("status")

    if status == "failed":
        return "end"

    current_step = state.get("current_step")

    # 流程控制
    if current_step == "parse_document":
        return "split"
    elif current_step == "split_document":
        return "embed"
    elif current_step == "generate_embedding":
        return "upsert"
    elif current_step == "vector_upsert":
        return "end"
    else:
        return "end"


def build_import_graph() -> StateGraph:
    """构建导入流程图"""

    # 创建状态图
    workflow = StateGraph(ImportState)

    # 添加节点
    workflow.add_node("parse", parse_document)
    workflow.add_node("split", split_document)
    workflow.add_node("embed", generate_embedding)
    workflow.add_node("upsert", vector_upsert)

    # 设置入口
    workflow.set_entry_point("parse")

    # 添加条件边
    workflow.add_conditional_edges(
        "parse",
        should_continue,
        {
            "split": "split",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "split",
        should_continue,
        {
            "embed": "embed",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "embed",
        should_continue,
        {
            "upsert": "upsert",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "upsert",
        should_continue,
        {
            "end": END
        }
    )

    return workflow.compile()


def run_import_pipeline(file_path: str) -> ImportState:
    """
    运行导入流程

    Args:
        file_path: 要处理的文件路径

    Returns:
        最终的 ImportState
    """
    # 初始化状态
    initial_state: ImportState = {
        "file_path": file_path,
        "status": "pending",
        "current_step": ""
    }

    # 构建并运行图
    graph = build_import_graph()

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
    file_path = r"D:\ProjectLlists\babycare\processor\import_process\tem\餐桌冲突与挑食沟通话术.md"

    result = run_import_pipeline(file_path)

    print("\n===== 执行结果 =====")
    print(f"状态: {result.get('status')}")
    print(f"当前步骤: {result.get('current_step')}")
    print(f"错误: {result.get('error', '无')}")

    if result.get("status") == "completed":
        print(f"文本长度: {len(result.get('raw_text', ''))}")
        print(f"切分段数: {len(result.get('chunks', []))}")
        print(f"向量数量: {len(result.get('embeddings', []))}")
        print(f"向量ID数量: {len(result.get('vector_ids', []))}")
