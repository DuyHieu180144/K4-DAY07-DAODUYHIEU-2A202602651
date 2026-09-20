from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin phù hợp trong cơ sở tri thức."

        context_blocks = []
        for index, result in enumerate(results, start=1):
            metadata = result["metadata"]
            source = metadata.get("source_url") or metadata.get("source") or metadata.get("doc_id", "không rõ nguồn")
            context_blocks.append(f"[{index}] Nguồn: {source}\n{result['content']}")

        context = "\n\n".join(context_blocks)
        prompt = (
            "Trả lời câu hỏi chỉ dựa trên ngữ cảnh dưới đây. "
            "Nếu ngữ cảnh không có câu trả lời, hãy nói rõ không tìm thấy thông tin. "
            "Khi dùng một thông tin, hãy trích dẫn số chunk tương ứng dạng [1], [2].\n\n"
            f"Ngữ cảnh:\n{context}\n\n"
            f"Câu hỏi: {question}\n"
            "Trả lời:"
        )
        return self.llm_fn(prompt)
