"""答案生成与流式输出：方法步骤、话术、注意事项、引用卡片；对接 SSE。"""

from processor.query_process.state import QueryState


async def answer_output(state: QueryState) -> QueryState:
    """答案输出节点：基于检索结果生成回答。

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    try:
        # 获取检索到的文档
        retrieved_docs = state.get("retrieved_docs", [])
        question = state.get("question", "")

        # 如果没有检索到文档，返回提示
        if not retrieved_docs:
            return {
                **state,
                "final_answer": "抱歉，我没有找到相关的育儿知识。您可以换个方式提问，或者咨询专业的育儿顾问。",
                "status": "completed"
            }

        # 构造"育儿专家"风格的回答
        # 结构：共情 -> 专业分析 -> 实操话术

        # 1. 共情部分
        empathy = _get_empathy_response(question)

        # 2. 专业分析（基于检索文档）
        analysis = _build_analysis(retrieved_docs)

        # 3. 实操话术
        practical = _build_practical_advice(retrieved_docs)

        # 拼接最终回答
        final_answer = f"{empathy}\n\n{analysis}\n\n{practical}"

        return {
            **state,
            "final_answer": final_answer,
            "status": "completed"
        }

    except Exception as e:
        return {
            **state,
            "status": "failed",
            "error": f"答案生成失败: {str(e)}"
        }


def _get_empathy_response(question: str) -> str:
    """根据问题生成共情回应。

    Args:
        question: 用户问题

    Returns:
        共情语句
    """
    empathy_templates = [
        "带娃确实很辛苦，我完全理解您的难处。",
        "每个家长都会遇到这样的问题，您不是一个人在战斗。",
        "育儿路上充满挑战，您能主动寻求建议，已经是位很用心的家长了。",
        "这个问题确实让人头疼，很多家长都有类似的困扰。",
        "理解您的担忧，这是育儿过程中非常正常的情况。"
    ]

    # 根据问题关键词选择合适的共情语句
    if "挑食" in question or "不吃" in question:
        return "看着宝宝不爱吃东西，确实让人着急又心疼。您能这么关注孩子的饮食，已经很用心了。"

    if "哭" in question or "闹" in question:
        return "面对宝宝的情绪爆发，任何家长都会感到疲惫和无助。您已经做得很好了。"

    if "睡" in question:
        return "睡眠不足真的太考验家长的耐心了。您能坚持到现在，真的很不容易。"

    # 默认返回通用共情
    return empathy_templates[hash(question) % len(empathy_templates)]


def _build_analysis(retrieved_docs: list) -> str:
    """基于检索文档构建专业分析。

    Args:
        retrieved_docs: 检索到的文档列表

    Returns:
        专业分析内容
    """
    if not retrieved_docs:
        return "**专业分析：**\n根据儿童发展心理学的研究，这个阶段的孩子正在探索自己的边界和偏好。"

    # 提取第一个文档的核心内容作为分析基础
    doc_content = retrieved_docs[0]

    return f"""**专业分析：**\n
根据相关的育儿理论和实践经验：

{doc_content[:200]}...

从儿童发展的角度来看，这是孩子成长过程中的正常现象。关键是要用耐心和正确的方法来引导，而不是强制或压抑。"""


def _build_practical_advice(retrieved_docs: list) -> str:
    """构建实操建议和话术。

    Args:
        retrieved_docs: 检索到的文档列表

    Returns:
        实操建议内容
    """
    advice_parts = []

    # 基于检索文档生成具体建议
    if retrieved_docs:
        for i, doc in enumerate(retrieved_docs[:3], 1):
            advice_parts.append(f"{i}. {doc[:150]}...")

    # 如果没有足够文档，补充通用建议
    if len(advice_parts) < 3:
        advice_parts.extend([
            "保持冷静，不要在情绪激动时做决定。",
            "用孩子能理解的语言沟通，避免说教。",
            "给孩子选择的权利，让他们感到被尊重。"
        ])

    practical_text = "\n".join(advice_parts)

    return f"""**实操建议与话术：**\n
{practical_text}

**温馨提示：**
每个孩子都是独特的，建议您根据自己孩子的性格和情况，灵活调整这些方法。如果问题持续或加重，建议咨询专业的育儿医生或心理咨询师。"""
