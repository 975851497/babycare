import sys

from processor.import_process.nodes.chunk_content import chunk_content
from processor.import_process.nodes.embedding import generate_embedding
from processor.import_process.nodes.parse_document import parse_document
from processor.import_process.nodes.vector_upsert import vector_upsert


def run_import_pipeline(file_path: str) -> dict:
    state = {
        "file_path": file_path
    }

    # 1. 解析文档
    result = parse_document(state)
    if result.get("status") == "failed":
        return result
    state.update(result)

    # 2. 切分内容
    result = chunk_content(state)
    if result.get("status") == "failed":
        return result
    state.update(result)

    # 3. 生成向量
    result = generate_embedding(state)
    if result.get("status") == "failed":
        return result
    state.update(result)

    # 4. 存储向量
    result = vector_upsert(state)
    if result.get("status") == "failed":
        return result
    state.update(result)

    state["status"] = "completed"
    return state


if __name__ == "__main__":
    file_path = r"D:\ProjectLlists\babycare\processor\import_process\tem\餐桌冲突与挑食沟通话术.md"
    result = run_import_pipeline(file_path)
    print(result)