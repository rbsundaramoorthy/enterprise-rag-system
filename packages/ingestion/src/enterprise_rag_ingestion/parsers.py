from __future__ import annotations

from abc import ABC, abstractmethod
from html import unescape

from bs4 import BeautifulSoup

from enterprise_rag_ingestion.models import ParsedContent


class TextExtractor(ABC):
    @abstractmethod
    def extract(self, content: bytes) -> str:
        raise NotImplementedError


class PlainTextExtractor(TextExtractor):
    def extract(self, content: bytes) -> str:
        return content.decode("utf-8")


class HTMLTextExtractor(TextExtractor):
    def extract(self, content: bytes) -> str:
        soup = BeautifulSoup(content.decode("utf-8"), "html.parser")
        return unescape(soup.get_text(separator=" ", strip=True))


class PDFTextExtractor(TextExtractor):
    def extract(self, content: bytes) -> str:
        raise NotImplementedError("PDF text extraction is not implemented in Phase 02.")


class Parser(ABC):
    @abstractmethod
    def parse(self, content: bytes, mime_type: str) -> ParsedContent:
        raise NotImplementedError


class BasicParser(Parser):
    def __init__(self) -> None:
        self._extractors: dict[str, TextExtractor] = {
            "application/pdf": PDFTextExtractor(),
            "text/html": HTMLTextExtractor(),
            "text/plain": PlainTextExtractor(),
        }

    def parse(self, content: bytes, mime_type: str) -> ParsedContent:
        extractor = self._extractors.get(mime_type)
        if extractor is None:
            raise ValueError(f"Unsupported mime type: {mime_type}")
        return ParsedContent(text=extractor.extract(content), mime_type=mime_type)
