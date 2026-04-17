"""
查询与对话服务路由（建议独立进程 / 端口，如 8001）。

- POST   /query                    发起检索 / 问答 / 推荐（可区分场景）
- GET    /stream/{session_id}     SSE 流式输出
- GET    /history/{session_id}    多轮对话历史
- DELETE /history/{session_id}    清除会话历史
"""
