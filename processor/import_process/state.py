from typing import List, TypedDict

class ImportState(TypedDict, total=False):
    file_path: str
    raw_text: str
    chunks: List[str]
    embeddings: List[List[float]]
    vector_ids: List[str]
    status: str
    error: str