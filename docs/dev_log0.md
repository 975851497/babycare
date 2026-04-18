# 开发记录

## Import Process

### state 定义

```python
class ImportState...
```

我来为你设计这个育儿知识库系统的 LangGraph 流程和 State 结构。

  1. 导入流程（import_process）

  流程节点设计

  START → validate_input → parse_document → extract_metadata → chunk_content → generate_embedding → store_vector →
  store_metadata → update_task_status → END
                      ↓
              [格式不支持/解析失败] → error_handler → update_task_status

  ┌────────────────────┬───────────────────────┬─────────────────────────────┬───────────────────────────────────┐
  │        节点        │         职责          │            输入             │               输出                │
  ├────────────────────┼───────────────────────┼─────────────────────────────┼───────────────────────────────────┤
  │ validate_input     │ 校验输入文件          │ file_path, file_type        │ valid: bool, error_msg?: str      │
  ├────────────────────┼───────────────────────┼─────────────────────────────┼───────────────────────────────────┤
  │ parse_document     │ 文档内容提取          │ file_path                   │ raw_content: str, extract_status: │
  │                    │                       │                             │  str                              │
  ├────────────────────┼───────────────────────┼─────────────────────────────┼───────────────────────────────────┤
  │ extract_metadata   │ 元数据提取（AI+规则） │ raw_content, file_name      │ metadata: Dict, cleaned_content:  │
  │                    │                       │                             │ str                               │
  ├────────────────────┼───────────────────────┼─────────────────────────────┼───────────────────────────────────┤
  │ chunk_content      │ 内容分块              │ cleaned_content,            │ chunks: List[Chunk]               │
  │                    │                       │ chunk_config                │                                   │
  ├────────────────────┼───────────────────────┼─────────────────────────────┼───────────────────────────────────┤
  │ generate_embedding │ 生成向量              │ chunks                      │ chunks_with_embedding:            │
  │                    │                       │                             │ List[Chunk]                       │
  ├────────────────────┼───────────────────────┼─────────────────────────────┼───────────────────────────────────┤
  │ store_vector       │ 存入向量库            │ chunks_with_embedding       │ vector_ids: List[str]             │
  ├────────────────────┼───────────────────────┼─────────────────────────────┼───────────────────────────────────┤
  │ store_metadata     │ 存入结构化数据        │ metadata, chunks,           │ doc_id: str                       │
  │                    │                       │ vector_ids                  │                                   │
  ├────────────────────┼───────────────────────┼─────────────────────────────┼───────────────────────────────────┤
  │ update_task_status │ 更新任务状态          │ task_id, status, result     │ -                                 │
  └────────────────────┴───────────────────────┴─────────────────────────────┴───────────────────────────────────┘

  关键字段流转

  ┌─────────────────────────────────────────────────────────────────┐
  │  输入层 (Input State)                                            │
  │  ├── task_id: str              # 任务唯一标识                    │
  │  ├── file_path: str            # 文件路径                        │
  │  ├── file_type: str            # pdf/docx/md/txt等               │
  │  ├── file_name: str            # 原始文件名                      │
  │  ├── file_size: int            # 文件大小                        │
  │  ├── source_type: str          # upload/api/crawl                │
  │  ├── upload_user: str          # 上传用户                        │
  │  └── upload_time: datetime     # 上传时间                        │
  └─────────────────────────────────────────────────────────────────┘
                                ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  解析层 (Parse State)                                            │
  │  ├── raw_content: str          # 原始文本内容                    │
  │  ├── parse_status: str         # success/partial/failed          │
  │  ├── parse_error: str          # 解析错误信息                    │
  │  └── content_hash: str         # 内容指纹（去重用）               │
  └─────────────────────────────────────────────────────────────────┘
                                ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  元数据层 (Metadata State)                                       │
  │  ├── metadata: Dict {                                           │
  │  │   ├── title: str            # 文章标题（AI提取/文件名）       │
  │  │   ├── author: str           # 作者                            │
  │  │   ├── content_type: str     # 育儿建议/专家文章/亲子案例/     │
  │  │   │                          沟通话术/知识科普               │
  │  │   ├── age_groups: List[str] # 0-3岁/3-6岁/6-12岁/12+岁       │
  │  │   ├── issue_types: List[str]# 情绪管理/行为引导/学习能力...   │
  │  │   ├── scene_desc: str       # 场景描述                        │
  │  │   ├── keywords: List[str]   # 提取关键词                      │
  │  │   └── source_url: str       # 来源链接（可选）                │
  │  │   }                                                          │
  │  └── cleaned_content: str      # 清洗后的正文                    │
  └─────────────────────────────────────────────────────────────────┘
                                ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  分块层 (Chunk State)                                            │
  │  ├── chunks: List[{                                             │
  │  │   ├── chunk_id: str         # 分块ID                         │
  │  │   ├── content: str          # 分块内容                        │
  │  │   ├── seq_num: int          # 顺序编号                        │
  │  │   ├── start_char: int       # 起始位置                        │
  │  │   ├── end_char: int         # 结束位置                        │
  │  │   └── metadata: Dict        # 继承文档元数据+分块特有         │
  │  │   }]                                                         │
  │  └── chunk_strategy: str       # 分块策略                        │
  └─────────────────────────────────────────────────────────────────┘
                                ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  存储层 (Storage State)                                          │
  │  ├── embeddings: List[List[float]]  # 向量列表                   │
  │  ├── vector_ids: List[str]     # 向量库ID                       │
  │  ├── doc_id: str               # 文档主表ID                      │
  │  └── storage_status: str       # success/partial/failed          │
  └─────────────────────────────────────────────────────────────────┘
                                ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  任务状态层 (Task State)                                         │
  │  ├── task_status: str          # pending/processing/             │
  │  │                               completed/failed               │
  │  ├── process_stage: str        # 当前阶段                        │
  │  ├── progress_percent: int     # 进度百分比                      │
  │  ├── result_info: Dict {       # 结果信息                        │
  │  │   ├── doc_id: str                                           │
  │  │   ├── chunk_count: int                                      │
  │  │   ├── vector_count: int                                     │
  │  │   └── failed_reason: str    # 失败原因（如有）                │
  │  │   }                                                          │
  │  ├── error_info: Dict          # 错误详情                        │
  │  └── completed_at: datetime    # 完成时间                        │
  └─────────────────────────────────────────────────────────────────┘

---
  2. 查询流程（query_process）

  流程节点设计

  START → receive_query → analyze_intent → rewrite_query → select_strategy
                                                                ↓
                        ┌───────────────────────────────────────┘
                        ↓
              hybrid_retrieve → rerank_results → generate_answer → stream_output → END
                     ↓                ↓              ↓
              [检索为空]         [重排过滤]      [需要澄清]
                     ↓                ↓              ↓
              fallback_handler → filter_low_score → clarify_question
                        ↑_____________________________↑

  ┌──────────────────┬─────────────────────────┬─────────────────────────────────┬──────────────────────────────┐
  │       节点       │          职责           │              输入               │             输出             │
  ├──────────────────┼─────────────────────────┼─────────────────────────────────┼──────────────────────────────┤
  │ receive_query    │ 接收用户输入            │ query_text, session_id, user_id │ query_obj: Dict              │
  ├──────────────────┼─────────────────────────┼─────────────────────────────────┼──────────────────────────────┤
  │ analyze_intent   │ 意图识别                │ query_obj                       │ intent: Dict                 │
  ├──────────────────┼─────────────────────────┼─────────────────────────────────┼──────────────────────────────┤
  │ rewrite_query    │ 查询改写（可选）        │ query_obj, chat_history         │ rewritten_queries: List[str] │
  ├──────────────────┼─────────────────────────┼─────────────────────────────────┼──────────────────────────────┤
  │ select_strategy  │ 检索策略选择            │ intent, query_type              │ strategy: Dict               │
  ├──────────────────┼─────────────────────────┼─────────────────────────────────┼──────────────────────────────┤
  │ hybrid_retrieve  │ 混合检索（向量+结构化） │ query, strategy, filters        │ raw_results: List[Doc]       │
  ├──────────────────┼─────────────────────────┼─────────────────────────────────┼──────────────────────────────┤
  │ rerank_results   │ 重排序+过滤             │ raw_results, query              │ ranked_results: List[Doc]    │
  ├──────────────────┼─────────────────────────┼─────────────────────────────────┼──────────────────────────────┤
  │ generate_answer  │ 答案生成                │ ranked_results, query, intent   │ answer: str, refs: List      │
  ├──────────────────┼─────────────────────────┼─────────────────────────────────┼──────────────────────────────┤
  │ stream_output    │ 流式输出                │ answer, refs                    │ chunk_stream                 │
  ├──────────────────┼─────────────────────────┼─────────────────────────────────┼──────────────────────────────┤
  │ clarify_question │ 问题澄清                │ query, intent                   │ clarify_msg: str             │
  └──────────────────┴─────────────────────────┴─────────────────────────────────┴──────────────────────────────┘

  关键字段流转

  ┌─────────────────────────────────────────────────────────────────┐
  │  输入层 (Query Input)                                            │
  │  ├── query_id: str             # 查询唯一标识                    │
  │  ├── query_text: str           # 用户原始问题                    │
  │  ├── session_id: str           # 会话ID（多轮对话）              │
  │  ├── user_id: str              # 用户标识                        │
  │  ├── query_type: str           # explicit/implicit               │
  │  │   # explicit: 明确的知识查询                                 │
  │  │   # implicit: 需要推理的问题                                 │
  │  └── chat_history: List[{      # 历史对话（最近N轮）             │
  │       ├── role: str            # user/assistant                  │
  │       ├── content: str                                          │
  │       └── timestamp: datetime                                   │
  │       }]                                                        │
  └─────────────────────────────────────────────────────────────────┘
                                ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  意图层 (Intent State)                                           │
  │  ├── intent: Dict {                                             │
  │  │   ├── primary_intent: str   # knowledge/case/chat/            │
  │  │   │                          clarification/unknown            │
  │  │   ├── sub_intent: str       # 细分意图                        │
  │  │   │   # 育儿知识推荐/育儿问题建议/案例检索/知识科普          │
  │  │   ├── entities: Dict {      # 提取的实体                      │
  │  │   │   ├── age_group: str    # 年龄段                          │
  │  │   │   ├── issue_type: str   # 问题类型                        │
  │  │   │   ├── scene: str        # 场景                            │
  │  │   │   └── keywords: List[str]                                │
  │  │   │   }                                                      │
  │  │   ├── urgency: str          # high/normal                     │
  │  │   └── confidence: float     # 置信度                          │
  │  │   }                                                          │
  │  ├── clarified: bool           # 是否需要澄清                    │
  │  └── clarification_msg: str    # 澄清话术（如需要）              │
  └─────────────────────────────────────────────────────────────────┘
                                ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  查询优化层 (Query Rewrite)                                      │
  │  ├── rewritten_queries: List[str]  # 改写后的查询（多路召回）    │
  │  ├── expansion_terms: List[str]    # 扩展词                      │
  │  └── filter_conditions: Dict {   # 结构化过滤条件                │
  │       ├── age_groups: List[str]                                 │
  │       ├── content_types: List[str]                              │
  │       ├── issue_types: List[str]                                │
  │       └── date_range: Tuple[datetime, datetime]                │
  │       }                                                         │
  └─────────────────────────────────────────────────────────────────┘
                                ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  检索层 (Retrieval State)                                        │
  │  ├── strategy: Dict {            # 检索策略                      │
  │  │   ├── method: str           # dense/sparse/hybrid             │
  │  │   ├── top_k: int            # 召回数量                        │
  │  │   ├── use_metadata_filter: bool                              │
  │  │   └── rerank_model: str     # 重排模型                        │
  │  │   }                                                          │
  │  ├── vector_results: List[{      # 向量检索结果                  │
  │  │   ├── doc_id: str                                            │
  │  │   ├── chunk_id: str                                          │
  │  │   ├── content: str                                           │
  │  │   ├── score: float                                           │
  │  │   └── metadata: Dict                                         │
  │  │   }]                                                         │
  │  ├── keyword_results: List[{     # 关键词检索结果                │
  │  │   # 同上结构                                                 │
  │  │   }]                                                         │
  │  └── hybrid_results: List[{      # 合并后结果                   │
  │       # 同上结构                                                │
  │       }]                                                        │
  └─────────────────────────────────────────────────────────────────┘
                                ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  重排层 (Rerank State)                                           │
  │  ├── reranked_results: List[{                                    │
  │  │   ├── doc_id: str                                            │
  │  │   ├── chunk_id: str                                          │
  │  │   ├── content: str          # 内容片段                        │
  │  │   ├── final_score: float    # 最终排序分数                    │
  │  │   ├── original_scores: Dict # 各阶段分数                      │
  │  │   ├── metadata: Dict {      # 来源元数据                      │
  │  │   │   ├── title: str                                         │
  │  │   │   ├── author: str                                        │
  │  │   │   ├── content_type: str                                  │
  │  │   │   ├── age_groups: List[str]                             │
  │  │   │   ├── issue_types: List[str]                            │
  │  │   │   ├── scene_desc: str                                    │
  │  │   │   └── source_file: str                                   │
  │  │   │   }                                                      │
  │  │   └── highlight_ranges: List[Tuple]  # 高亮范围              │
  │  │   }]                                                         │
  │  ├── filtered_count: int       # 过滤掉的数量                    │
  │  └── insufficient_results: bool # 结果是否不足                   │
  └─────────────────────────────────────────────────────────────────┘
                                ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  生成层 (Generation State)                                       │
  │  ├── context_prepared: str     # 组织好的上下文                  │
  │  ├── answer_plan: Dict {       # 答案规划                        │
  │  │   ├── structure: str        # 回答结构                        │
  │  │   │   # eg: "建议列表+方法步骤+注意事项"                     │
  │  │   ├── sections: List[str]   # 段落规划                        │
  │  │   └── citations_needed: bool                                 │
  │  │   }                                                          │
  │  ├── references: List[{        # 引用来源                        │
  │  │   ├── ref_id: str           # 引用编号 [1], [2]              │
  │  │   ├── doc_id: str                                            │
  │  │   ├── title: str                                             │
  │  │   ├── content_type: str                                      │
  │  │   └── relevance: str        # 相关说明                        │
  │  │   }]                                                         │
  │  └── generated_answer: str     # 生成的完整答案                  │
  └─────────────────────────────────────────────────────────────────┘
                                ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  输出层 (Output State)                                           │
  │  ├── response_type: str        # answer/clarification/error      │
  │  ├── answer_text: str          # 最终答案文本                    │
  │  ├── stream_chunks: List[str]  # 流式输出块（用于SSE）           │
  │  ├── suggested_questions: List[str]  # 推荐后续问题              │
  │  ├── related_content: List[{   # 相关内容推荐                    │
  │  │   ├── title: str                                             │
  │  │   ├── content_type: str                                      │
  │  │   └── doc_id: str                                            │
  │  │   }]                                                         │
  │  └── token_usage: Dict {       # Token消耗统计                   │
  │       ├── prompt_tokens: int                                    │
  │       ├── completion_tokens: int                                │
  │       └── total_tokens: int                                     │
  │       }                                                         │
  └─────────────────────────────────────────────────────────────────┘

---
  3. State 结构详细定义

  3.1 ImportState（导入流程 State）

  # 核心字段定义说明

  class ImportState:
      # === 基础信息 ===
      task_id: str                    # UUID
      task_status: TaskStatus         # Enum: PENDING, PROCESSING, COMPLETED, FAILED

      # === 文件信息 ===
      file_info: Dict {
          "path": str,                # 文件存储路径
          "name": str,                # 原始文件名
          "type": FileType,           # Enum: PDF, DOCX, MD, TXT
          "size": int,
          "mime_type": str,
          "encoding": str,            # 编码检测
      }
    
      # === 来源信息 ===
      source_info: Dict {
          "source_type": str,         # upload/api/crawl/manual
          "upload_by": str,           # 用户ID
          "upload_at": datetime,
          "batch_id": str,            # 批量任务ID（可选）
      }
    
      # === 解析结果 ===
      parse_result: Dict {
          "status": Status,           # success/partial/failed
          "raw_content": str,         # 原始文本
          "cleaned_content": str,     # 清洗后文本
          "error_msg": str,
          "content_hash": str,        # MD5去重
          "extract_time_ms": int,
      }
    
      # === 提取的元数据 ===
      metadata: ContentMetadata {
          "title": str,
          "author": str,
          "content_type": ContentType,  # Enum
          "age_groups": List[str],      # ["0-3岁", "3-6岁"]
          "issue_types": List[str],     # ["情绪管理", "行为引导"]
          "scene_description": str,
          "keywords": List[str],
          "summary": str,               # AI生成摘要
          "source_url": Optional[str],
      }
    
      # === 分块信息 ===
      chunks: List[Chunk] {
          "chunk_id": str,
          "doc_id": str,                # 关联文档ID
          "content": str,
          "seq_num": int,               # 顺序号
          "char_range": Tuple[int, int],
          "token_count": int,
          "heading_context": str,       # 所属标题（用于上下文）
      }
    
      # === 向量信息 ===
      embeddings: Dict {
          "model": str,                 # 使用的模型
          "vectors": List[List[float]],
          "vector_ids": List[str],      # 向量库返回ID
          "dimension": int,
      }
    
      # === 存储结果 ===
      storage_result: Dict {
          "doc_id": str,                # 文档主表ID
          "chunk_count": int,
          "vector_count": int,
          "metadata_saved": bool,
          "storage_at": datetime,
      }
    
      # === 错误处理 ===
      error: Optional[Dict] {
          "stage": str,                 # 出错阶段
          "code": str,                  # 错误码
          "message": str,
          "stack_trace": str,
          "retryable": bool,            # 是否可重试
      }
    
      # === 进度追踪 ===
      progress: Dict {
          "current_stage": str,
          "percent": int,               # 0-100
          "stage_history": List[Dict],  # 阶段耗时记录
      }

  3.2 QueryState（查询流程 State）

  # 核心字段定义说明

  class QueryState:
      # === 查询基础 ===
      query_id: str                   # UUID
      query_text: str                 # 用户原始输入
      query_status: QueryStatus       # Enum: RECEIVED, PROCESSING, ANSWERED, FAILED

      # === 会话信息 ===
      session: Dict {
          "session_id": str,
          "user_id": str,
          "user_profile": Dict {      # 用户画像（可选）
              "child_age": str,       # 孩子年龄段
              "interests": List[str],
          },
          "history": List[Turn] {     # 历史对话
              "role": str,            # user/assistant
              "content": str,
              "timestamp": datetime,
              "turn_id": str,
          },
          "history_summary": str,     # 历史对话摘要（长对话压缩）
      }
    
      # === 意图分析 ===
      intent: Intent {
          "primary": IntentType,      # Enum: KNOWLEDGE, CASE, CHAT, CLARIFY
          "sub_intent": str,          # 细分意图
          "confidence": float,        # 0-1
          "entities": Dict {
              "age_group": Optional[str],
              "issue_type": Optional[str],
              "scene": Optional[str],
              "keywords": List[str],
              "explicit_filters": Dict,  # 用户明确指定的过滤条件
          },
          "needs_clarification": bool,
          "clarification_msg": Optional[str],
      }
    
      # === 查询优化 ===
      query_rewrite: Dict {
          "original": str,
          "rewritten": List[str],     # 多路改写（用于召回）
          "expansion": List[str],     # 同义词扩展
          "filters": FilterConfig {   # 结构化过滤
              "age_groups": List[str],
              "content_types": List[ContentType],
              "issue_types": List[str],
              "date_range": Optional[Tuple],
          },
      }
    
      # === 检索配置 ===
      retrieval_config: Dict {
          "strategy": str,            # hybrid/vector/keyword
          "top_k": int,               # 召回数量
          "rerank_top_n": int,        # 重排后保留
          "score_threshold": float,   # 分数阈值
      }
    
      # === 检索结果 ===
      retrieval_results: Dict {
          "vector_hits": List[Hit],
          "keyword_hits": List[Hit],
          "merged_hits": List[Hit],
          "hit_count": int,
      }
    
      # === 重排结果 ===
      ranked_results: List[RankedHit] {
          "hit_id": str,
          "doc_id": str,
          "chunk_id": str,
          "content": str,             # 文本片段
          "final_score": float,
          "vector_score": float,
          "keyword_score": float,
          "rerank_score": float,
          "metadata": ContentMetadata,
          "highlights": List[str],    # 匹配高亮
      }
    
      # === 答案生成 ===
      generation: Dict {
          "context": str,             # 组织好的RAG上下文
          "plan": AnswerPlan {        # 答案结构规划
              "structure": str,       # 回答结构类型
              "sections": List[str],  # 段落规划
              "tone": str,            # 语气风格
          },
          "draft": str,               # 初稿
          "final_answer": str,        # 最终答案
          "citations": List[Citation] {
              "ref_id": str,          # [1], [2]
              "doc_id": str,
              "title": str,
              "relevant_text": str,
              "link": Optional[str],
          },
      }
    
      # === 输出结果 ===
      output: Dict {
          "response_type": str,       # answer/clarification/error
          "content": str,             # 最终输出内容
          "stream_buffer": List[str], # 流式输出缓冲区
          "suggestions": List[str],   # 推荐问题
          "related_docs": List[Dict], # 相关文档推荐
      }
    
      # === 监控指标 ===
      metrics: Dict {
          "start_time": datetime,
          "stage_timings": Dict,      # 各阶段耗时
          "token_usage": TokenUsage {
              "embedding": int,
              "llm_input": int,
              "llm_output": int,
          },
          "latency_ms": int,          # 总延迟
      }
    
      # === 错误处理 ===
      error: Optional[Dict] {
          "stage": str,
          "code": str,
          "message": str,
          "fallback_used": bool,      # 是否使用降级策略
      }

---
  4. 关键设计要点

  4.1 导入流程设计要点

  ┌────────────┬──────────────────────────────────────────────┐
  │   设计点   │                     说明                     │
  ├────────────┼──────────────────────────────────────────────┤
  │ 幂等性     │ 通过 content_hash 实现去重，重复内容跳过处理 │
  ├────────────┼──────────────────────────────────────────────┤
  │ 断点续传   │ task_status + current_stage 支持任务恢复     │
  ├────────────┼──────────────────────────────────────────────┤
  │ 部分成功   │ 允许部分分块成功，记录 partial 状态          │
  ├────────────┼──────────────────────────────────────────────┤
  │ 批量控制   │ batch_id 支持批量导入的进度追踪              │
  ├────────────┼──────────────────────────────────────────────┤
  │ 元数据校验 │ AI提取后通过规则校验 age_groups 等字段合法性 │
  └────────────┴──────────────────────────────────────────────┘

  4.2 查询流程设计要点

  ┌────────────┬───────────────────────────────────────────────┐
  │   设计点   │                     说明                      │
  ├────────────┼───────────────────────────────────────────────┤
  │ 意图路由   │ 不同 sub_intent 触发不同检索策略权重          │
  ├────────────┼───────────────────────────────────────────────┤
  │ 混合检索   │ vector_hits + keyword_hits 融合，解决语义漂移 │
  ├────────────┼───────────────────────────────────────────────┤
  │ 年龄感知   │ user_profile.child_age 自动添加过滤条件       │
  ├────────────┼───────────────────────────────────────────────┤
  │ 多轮上下文 │ history_summary 压缩长对话，避免token溢出     │
  ├────────────┼───────────────────────────────────────────────┤
  │ 引用溯源   │ citations 确保答案可解释、可追溯              │
  ├────────────┼───────────────────────────────────────────────┤
  │ 流式状态   │ stream_buffer 管理流式输出过程中的状态        │
  └────────────┴───────────────────────────────────────────────┘

  4.3 两种流程的交互

  导入流程 ──→ 写入向量库 ──┐
                           ├──→ 查询流程从向量库检索
  导入流程 ──→ 写入元数据表─┘

  这个设计贴近 Python + LangGraph 的实现习惯，每个节点函数接收完整的 State，返回更新后的 State，通过 ShouldContinue
  等条件边控制流程分支。