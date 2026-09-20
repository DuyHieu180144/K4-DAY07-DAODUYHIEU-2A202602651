"""Section-aware chunking for policy documents written in Markdown."""

from __future__ import annotations

import re

from .chunking import RecursiveChunker


class HeadingChunker:
    """Keep each Markdown heading with its section; split long sections safely."""

    HEADING_PATTERN = re.compile(r"^#{1,6}\s+.+$", re.MULTILINE)

    def __init__(self, chunk_size: int = 900) -> None:
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        matches = list(self.HEADING_PATTERN.finditer(text))
        if not matches:
            return RecursiveChunker(chunk_size=self.chunk_size).chunk(text)

        sections: list[str] = []
        if text[: matches[0].start()].strip():
            sections.append(text[: matches[0].start()].strip())
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            sections.append(text[match.start() : end].strip())

        chunks: list[str] = []
        for section in sections:
            chunks.extend(self._split_section(section))
        return chunks

    def _split_section(self, section: str) -> list[str]:
        if len(section) <= self.chunk_size:
            return [section]

        lines = section.splitlines()
        heading = lines[0] if lines and self.HEADING_PATTERN.fullmatch(lines[0]) else ""
        body = "\n".join(lines[1:]).strip() if heading else section
        if not heading:
            return RecursiveChunker(chunk_size=self.chunk_size).chunk(body)

        # Reserve room so every split fragment retains the section title.
        body_size = max(1, self.chunk_size - len(heading) - 1)
        body_chunks = RecursiveChunker(chunk_size=body_size).chunk(body)
        return [f"{heading}\n{chunk}".strip() for chunk in body_chunks]
