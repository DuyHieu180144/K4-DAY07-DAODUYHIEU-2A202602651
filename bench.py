"""Run the shared Lab 07 benchmark against the policy corpus.

Only change the CHUNKER assignment to compare a different strategy.  Everything
else (documents, embedding backend, queries and top_k) stays identical.
"""

from __future__ import annotations

import re
import sys
import os
from pathlib import Path

from dotenv import load_dotenv

from src import (
    EMBEDDING_PROVIDER_ENV,
    GEMINI_EMBEDDING_MODEL,
    Document,
    EmbeddingStore,
    FixedSizeChunker,
    GeminiEmbedder,
    RecursiveChunker,
    SentenceChunker,
    _mock_embed,
)
from src.heading_chunker import HeadingChunker

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path("data/policies")
QUERY_FILE = Path("benchmark_queries.yaml")
OUTPUT_FILE = Path("ket_qua_benchmark.txt")
TOP_K = 3

# Change only this line for an individual strategy comparison.
CHUNKER = HeadingChunker(chunk_size=900)
# Alternatives: FixedSizeChunker(chunk_size=900, overlap=120),
# SentenceChunker(max_sentences_per_chunk=4), RecursiveChunker(chunk_size=900).

# The folder has one general website-terms page outside the return/warranty
# benchmark scope.  Keeping this selection at 10 documents meets the lab limit.
EXCLUDED_FILES = {"hacom-general-terms.md"}


class _Tee:
    """Write benchmark output to both the terminal and a hand-in artifact."""

    def __init__(self, *streams) -> None:
        self.streams = streams

    def write(self, text: str) -> int:
        for stream in self.streams:
            stream.write(text)
        return len(text)

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()


def build_embedding_fn():
    """Select the benchmark embedding backend from .env."""
    load_dotenv(dotenv_path=Path(".env"), override=False)
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "mock":
        return _mock_embed
    if provider == "gemini":
        try:
            return GeminiEmbedder(
                model_name=os.getenv("GEMINI_EMBEDDING_MODEL", GEMINI_EMBEDDING_MODEL)
            )
        except ImportError as error:
            raise RuntimeError(
                "Gemini backend chưa được cài. Chạy: .\\.venv\\Scripts\\python.exe -m pip install google-genai"
            ) from error
    raise RuntimeError("EMBEDDING_PROVIDER chỉ hỗ trợ 'mock' hoặc 'gemini' trong bench.py.")


def _value(raw: str) -> str:
    """Read a simple YAML scalar without adding a third-party YAML dependency."""
    value = raw.strip()
    if " #" in value:
        value = value.split(" #", 1)[0].rstrip()
    return value.strip("\"'")


def split_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text.strip()

    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Frontmatter is not closed: {path}")
    metadata = {}
    for line in parts[1].splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = _value(value)
    return metadata, parts[2].strip()


def load_queries(path: Path) -> list[dict]:
    """Parse the small, fixed benchmark YAML format using the standard library."""
    queries: list[dict] = []
    current: dict | None = None
    in_filter = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped == "queries:":
            continue
        if line.startswith("  - "):
            if current:
                queries.append(current)
            current = {}
            in_filter = False
            key, value = line[4:].split(":", 1)
            current[key.strip()] = _value(value)
            continue
        if current is None:
            continue
        if line.startswith("    metadata_filter:"):
            current["metadata_filter"] = {}
            in_filter = True
            continue
        if in_filter and line.startswith("      "):
            key, value = stripped.split(":", 1)
            current["metadata_filter"][key.strip()] = _value(value)
            continue
        if line.startswith("    ") and ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = _value(value)
            in_filter = False
    if current:
        queries.append(current)
    if len(queries) != 5:
        raise ValueError(f"Expected exactly 5 benchmark queries, found {len(queries)}")
    return queries


def load_documents() -> list[Document]:
    documents: list[Document] = []
    for path in sorted(DATA_DIR.glob("*.md")):
        if path.name in EXCLUDED_FILES:
            continue
        metadata, content = split_frontmatter(path)
        for index, chunk in enumerate(CHUNKER.chunk(content)):
            documents.append(
                Document(
                    id=f"{path.stem}#{index}",
                    content=chunk,
                    metadata={**metadata, "doc_id": path.stem, "chunk_index": index},
                )
            )
    return documents


def print_result(query: dict, results: list[dict]) -> None:
    print(f"\n{query['id'].upper()} — {query['query']}")
    print(f"Gold doc: {query['gold_doc_id']}")
    if query.get("metadata_filter"):
        print(f"Metadata filter: {query['metadata_filter']}")
    for rank, result in enumerate(results, start=1):
        preview = re.sub(r"\s+", " ", result["content"]).strip()[:180]
        print(
            f"  {rank}. score={result['score']:.3f} "
            f"doc_id={result['metadata']['doc_id']} chunk={result['metadata']['chunk_index']}\n"
            f"     {preview}..."
        )


def main() -> int:
    queries = load_queries(QUERY_FILE)
    documents = load_documents()
    if not documents:
        print("No chunks loaded. Check DATA_DIR and the selected chunker.")
        return 1

    embedding_fn = build_embedding_fn()
    store = EmbeddingStore(collection_name="policy_benchmark", embedding_fn=embedding_fn)
    store.add_documents(documents)
    print(f"Strategy: {CHUNKER.__class__.__name__}")
    print(f"Embedding backend: {getattr(embedding_fn, '_backend_name', 'mock embeddings fallback')}")
    print(f"Documents selected: {len({doc.metadata['doc_id'] for doc in documents})}")
    print(f"Chunks loaded: {store.get_collection_size()}")

    for query in queries:
        results = store.search_with_filter(
            query["query"], top_k=TOP_K, metadata_filter=query.get("metadata_filter")
        )
        print_result(query, results)
    return 0


if __name__ == "__main__":
    original_stdout = sys.stdout
    with OUTPUT_FILE.open("w", encoding="utf-8") as output_file:
        sys.stdout = _Tee(original_stdout, output_file)
        try:
            raise SystemExit(main())
        finally:
            sys.stdout = original_stdout
