"""
HyDE (Hypothetical Document Embeddings) 提示词模板
用于生成假设性文档，解决查询-文档语义鸿沟问题
"""

# HyDE 用户提示词���板
HYDE_USER_PROMPT_TEMPLATE = """
作为一位{item_names}领域的专家，请针对以下用户问题生成一个假设性的理想回答。

**用户问题：** {rewritten_query}

**要求：**
1. 回答应该详细、专业，能够解决用户的问题
2. 回答应该包含相关的技术细节和实用建议
3. 回答的格式应该像一篇简短的技术文档或操作指南
4. 字数控制在200-300字之间

请生成这个假设性回答：
"""

# HyDE 系统提示词
HYDE_SYSTEM_PROMPT = """
你是一位专业的技术文档专家，擅长编写高质量的技术文档、操作手册和规格说明。

你的任务是为用户的查询问题生成一个假设性的理想回答。这个回答将被用于向量检索，以帮助找到更相关的真实文档。

请确��生成的回答：
- 内容详实，包含具体的技术细节
- 结构清晰，便于阅读和理解
- 语言专业，符合技术文档的写作规范
- 长度适中，既要充分回答问题，又不要过于冗长
"""

# 育儿场景专用的HyDE提示词
BABYCARE_HYDE_PROMPT = """
作为一位资深的育儿专家，请针对以下家长的问题生成一个假设性的理想回答。

**家长问题：** {query}

**要求：**
1. **共情理解**：首先理解家长的难处和情感需求
2. **专业分析**：基于儿童心理学或权威理论进行分析
3. **实操建议**：给出具体的沟通话术或行动步骤
4. **温暖语气**：使用温暖、支持性的语言，避免说教
5. **结构清晰**：分段组织内容，便于阅读

字数控制在150-250字之间。

请生成这个假设性的育儿建议：
"""


def get_hyde_prompt_template(query_type: str = "general") -> str:
    """
    获取HyDE提示词模板

    Args:
        query_type: 查询类型 ("general", "babycare", "technical")

    Returns:
        str: 对应的提示词模板
    """
    templates = {
        "general": HYDE_USER_PROMPT_TEMPLATE,
        "babycare": BABYCARE_HYDE_PROMPT,
        "technical": HYDE_USER_PROMPT_TEMPLATE  # 技术场景使用通用模板
    }

    return templates.get(query_type, HYDE_USER_PROMPT_TEMPLATE)


if __name__ == "__main__":
    # 测试HyDE提示词
    print("🧪 测试HyDE提示词模板")
    print("=" * 60)

    test_query = "宝宝挑食怎么办？"

    # 测试育儿场景提示词
    babycare_prompt = BABYCARE_HYDE_PROMPT.format(query=test_query)
    print(f"📝 育儿场景HyDE提示词：")
    print("-" * 60)
    print(babycare_prompt)
    print("=" * 60)

    print(f"\n💡 说明：这个提示词将用于生成假设性育儿建议，"
          f"\n   然后对假设性建议进行向量检索，以解决查询-文档语义鸿沟问题。")
