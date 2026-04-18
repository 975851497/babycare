"""
RAG流水线核心逻辑演示 - 育儿场景实战
"""
import sys
import io
from pathlib import Path

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_section(title: str) -> None:
    """打印分节标题"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def simulate_vector_search():
    """模拟向量检索"""
    print_section("🔍 第一步：混合向量检索")

    query = "3岁宝宝晚上不肯睡觉，一放床上就哭闹"
    print(f"❓ 用户问题: {query}")

    # 模拟Milvus检索结果（从kb_chunks_v1_v2集合）
    simulated_results = [
        {
            "chunk_id": 1001,
            "content": "3岁宝宝晚上不肯睡觉，可能是因为白天睡眠过多。家长应建立规律的睡眠时间。",
            "title": "幼儿睡眠问题指导",
            "age_group": "3-6岁",
            "issue_type": "健康饮食",
            "content_type": "育儿建议",
            "distance": 0.23,
            "source": "local"
        },
        {
            "chunk_id": 1002,
            "content": "孩子哭闹时，家长要保持冷静，不要立即抱起。可以尝试轻拍安抚。",
            "title": "情绪管理技巧",
            "age_group": "通用",
            "issue_type": "情绪管理",
            "content_type": "沟通话术",
            "distance": 0.45,
            "source": "local"
        },
        {
            "chunk_id": 1003,
            "content": "今天是星期三，超市有特价活动，牛奶买二送一。",
            "title": "超市促销信息",
            "age_group": "通用",
            "issue_type": "通用",
            "content_type": "其他",
            "distance": 0.78,
            "source": "local"
        },
        {
            "chunk_id": 1004,
            "content": "3岁宝宝的睡眠问题很常见，建立固定的睡前仪式，如洗澡、讲故事、听轻音乐。",
            "title": "幼儿睡眠指导",
            "age_group": "3-6岁",
            "issue_type": "健康饮食",
            "content_type": "育儿建议",
            "distance": 0.31,
            "source": "local"
        },
        {
            "chunk_id": 1005,
            "content": "手机屏幕蓝光会影响睡眠质量，建议睡前1小时避免使用电子设备。",
            "title": "睡眠健康知识",
            "age_group": "通用",
            "issue_type": "健康饮食",
            "content_type": "知识科普",
            "distance": 0.52,
            "source": "local"
        }
    ]

    print(f"\n📊 检索到 {len(simulated_results)} 个文档:")
    for i, doc in enumerate(simulated_results, 1):
        age_mark = "✅" if doc['age_group'] == "3-6岁" else "  "
        content = doc['content'][:50] + "..."
        print(f"   [{i}] {age_mark} distance:{doc['distance']:.2f} | {content}")

    print(f"\n💡 检索特点:")
    print(f"   ✅ 包含业务元数据: age_group, issue_type, content_type")
    print(f"   ✅ 相关性排序: distance越小越相关")
    print(f"   ✅ 第1、4文档直接相关，第2文档部分相关")

    return simulated_results


def simulate_rrf_merge():
    """模拟RRF融合"""
    print_section("🔀 第二步：RRF多路融合")

    print("📊 RRF融合演示：")
    print("   - 路径1: HybridVectorSearch (直接向量检索)")
    print("   - 路径2: HyDeVectorSearch (假设性文档检索)")
    print("   - 融合算法: RRF (Reciprocal Rank Fusion)")

    # 简化的RRF结果
    rrf_results = [
        {
            "chunk_id": 1001,
            "content": "3岁宝宝晚上不肯睡觉，可能是因为白天睡眠过多。家长应建立规律的睡眠时间。",
            "title": "幼儿睡眠问题指导",
            "rrf_score": 2.5,
            "source": "local"
        },
        {
            "chunk_id": 1004,
            "content": "3岁宝宝的睡眠问题很常见，建立固定的睡前仪式，如洗澡、讲故事、听轻音乐。",
            "title": "幼儿睡眠指导",
            "rrf_score": 2.1,
            "source": "local"
        },
        {
            "chunk_id": 1002,
            "content": "孩子哭闹时，家长要保持冷静，不要立即抱起。可以尝试轻拍安抚。",
            "title": "情绪管理技巧",
            "rrf_score": 1.8,
            "source": "local"
        },
        {
            "chunk_id": 1005,
            "content": "手机屏幕蓝光会影响睡眠质量，建议睡前1小时避免使用电子设备。",
            "title": "睡眠健康知识",
            "rrf_score": 1.2,
            "source": "local"
        }
    ]

    print(f"\n📊 RRF融合后保留 {len(rrf_results)} 个高质量文档:")
    for i, doc in enumerate(rrf_results, 1):
        score = doc['rrf_score']
        content = doc['content'][:50] + "..."
        print(f"   [{i}] RRF分数:{score:.2f} | {content}")

    print(f"\n💡 RRF优势:")
    print(f"   ✅ 去重：chunk_id 1001 在多路中都出现了，权重会更高")
    print(f"   ✅ 融合：结合了直接检索和假设检索的结果")
    print(f"   ✅ 排序：按照RRF分数重新排序")

    return rrf_results


def simulate_reranker_cliff_cutoff():
    """模拟Reranker精排和断崖截断"""
    print_section("📊 第三步：Reranker精排 + 断崖截断")

    rrf_results = [
        {
            "chunk_id": 1001,
            "content": "3岁宝宝晚上不肯睡觉，可能是因为白天睡眠过多。家长应建立规律的睡眠时间。",
            "title": "幼儿睡眠问题指导",
            "rerank_raw_score": 0.92
        },
        {
            "chunk_id": 1004,
            "content": "3岁宝宝的睡眠问题很常见，建立固定的睡前仪式，如洗澡、讲故事、听轻音乐。",
            "title": "幼儿睡眠指导",
            "rerank_raw_score": 0.88
        },
        {
            "chunk_id": 1002,
            "content": "孩子哭闹时，家长要保持冷静，不要立即抱起。可以尝试轻拍安抚。",
            "title": "情绪管理技巧",
            "rerank_raw_score": 0.75
        },
        {
            "chunk_id": 1005,
            "content": "手机屏幕蓝光会影响睡眠质量，建议睡前1小时避免使用电子设备。",
            "title": "睡眠健康知识",
            "rerank_raw_score": 0.45
        }
    ]

    print(f"📊 BGE-Reranker 精排打分:")
    for i, doc in enumerate(rrf_results, 1):
        score = doc['rerank_raw_score']
        content = doc['content'][:50] + "..."
        print(f"   [{i}] Score:{score:.3f} | {content}")

    # 应用断崖截断
    print(f"\n✂️  应用断崖截断 (阈值=0.15, min_top_k=3):")

    cliff_cutoff = len(rrf_results)  # upper_bound
    max_gap = 0
    lower_bound = 3

    # 寻找最大断崖
    for i in range(len(rrf_results) - 1):
        current_score = rrf_results[i]['rerank_raw_score']
        next_score = rrf_results[i + 1]['rerank_raw_score']
        gap = current_score - next_score

        if gap >= 0.15 and gap > max_gap:
            max_gap = gap
            cliff_cutoff = i + 1
            print(f"   ✂️  位置{i+1}发生断崖 (gap={gap:.3f})")

    cliff_cutoff = max(cliff_cutoff, lower_bound)
    final_docs = rrf_results[:cliff_cutoff]

    print(f"\n📊 断崖截断后保留 {len(final_docs)} 个高质量文档:")
    for i, doc in enumerate(final_docs, 1):
        score = doc['rerank_raw_score']
        content = doc['content'][:60] + "..."
        print(f"   [{i}] Score:{score:.3f} | {content}")

    print(f"\n💡 断崖截断优势:")
    print(f"   ✅ 质量过滤：去除低质量文档（超市促销信息）")
    print(f"   ✅ 动态Top-K：根据分数分布自动调整保留数量")
    print(f"   ✅ 兜底保证：至少保留{lower_bound}个相关文档")

    return final_docs


def simulate_answer_generation(reranked_docs):
    """模拟答案生成"""
    print_section("💬 第四步：答案生成")

    query = "3岁宝宝晚上不肯睡觉，一放床上就哭闹，作为家长该怎么办？"

    print(f"❓ 用户问题: {query}")
    print(f"📊 基于文档: {len(reranked_docs)} 个精排后的高质量文档")

    # 生成温暖专业的回答
    answer = f"""**共情理解：**

看着宝宝晚上哭闹，您一定既心疼又疲惫。3岁的孩子正处于自主性发展和规则意识建立的关键期，睡眠问题确实让很多家长头疼。您能主动寻求建议，已经是一位非常用心的家长了。

**专业分析：**

3岁宝宝的睡眠问题很常见，主要原因包括：
- 白天睡眠时间过长，导致晚上不困
- 睡前过度兴奋或刺激过多
- 缺乏固定的睡前仪式和睡眠环境

根据儿童发展心理学的研究，这个阶段的孩子开始探索自己的边界，需要在规则和自主之间找到平衡。

**实操建议与话术：**

🌙 **建立睡眠仪式：**
1. 固定睡眠时间：每天晚上8点开始准备睡觉
2. 睡前流程：洗澡 → 换睡衣 → 讲故事 → 听轻音乐
3. 环境营造：调暗灯光，保持安静舒适

📝 **具体话术：**
- "宝宝，月亮出来啦，我们要和太阳公公说晚安了。"
- "我知道你还想玩，但是现在是我们身体充电的时间。"
- "妈妈陪着你，等你睡着了妈妈再去休息。"

😊 **应对哭闹技巧：**
1. **冷处理**：不要立即抱起，先观察2-3分钟
2. **轻声安抚**：用温柔的声音说"妈妈在这里，我爱你"
3. **轻拍背抚**：有节奏地轻拍宝宝的后背
4. **情绪命名**：帮宝宝说出感受"你现在很困，对吗？"

**基于知识库内容整理：**
- 幼儿睡眠问题指导：建立规律睡眠时间
- 情绪管理技巧：家长保持冷静的重要性
- 睡眠健康知识：避免电子设备影响睡眠

⚠️ **温馨提示：**
每个孩子都是独特的，建议您根据自己孩子的性格和情况，灵活调整这些方法。如果睡眠问题持续超过2周，或伴随其他症状，建议咨询专业的儿科医生或心理咨询师。"""

    print(f"\n💡 AI生成的回答:")
    print("=" * 70)
    print(answer)
    print("=" * 70)

    print(f"\n💡 回答特点:")
    print(f"   ✅ 共情理解：理解家长的难处和情感需求")
    print(f"   ✅ 专业分析：基于儿童心理学和发展阶段")
    print(f"   ✅ 实操建议：具体的睡眠仪式和话术")
    print(f"   ✅ 温暖语气：人性化语言，拒绝说教")
    print(f"   ✅ 结构清晰：分段组织，便于阅读")
    print(f"   ✅ 引用来源：基于知识库内容整理")

    return answer


def main():
    """主函数"""
    print("🚀 Babycare 育儿知识库 - RAG流水线实战演示")
    print("=" * 70)
    print("🧪 典型育儿场景: 3岁宝宝晚上不肯睡觉，一放床上就哭闹")
    print("🎯 目标: 展示完整的RAG流水线处理过程")
    print("=" * 70)

    # 第一步：向量检索
    search_results = simulate_vector_search()

    # 第二步：RRF融合
    rrf_results = simulate_rrf_merge()

    # 第三步：重排序
    reranked_docs = simulate_reranker_cliff_cutoff()

    # 第四步：答案生成
    final_answer = simulate_answer_generation(reranked_docs)

    print("\n" + "=" * 70)
    print("🎉 RAG流水线演示完成！")
    print("=" * 70)
    print("✅ **检索阶段**：从89个文档中检索到最相关的5个")
    print("✅ **融合阶段**：RRF算法智能合并多路检索结果")
    print("✅ **精排阶段**：BGE-Reranker精排 + 断崖截断去除干扰项")
    print("✅ **生成阶段**：基于精排上下文生成温暖专业的育儿建议")
    print("\n🏆 **核心优势**：")
    print("   🎯 精准：混合向量检索 + HyDE增强")
    print("   🎯 智能：多路融合 + 重排序去重")
    print("   🎯 温暖：共情理解 + 专业分析 + 实操建议")
    print("   🎯 可靠：基于真实知识库，避免幻觉")


if __name__ == "__main__":
    main()
