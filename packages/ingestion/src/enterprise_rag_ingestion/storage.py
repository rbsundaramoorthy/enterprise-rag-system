from __future__ import annotations

from pathlib import Path

from enterprise_rag_core.settings import get_settings


class LocalRawContentStore:
    def __init__(self, root: Path | None = None) -> None:
        settings = get_settings()
        self._root = root or Path(settings.raw_storage_root)

    def write_bytes(
        self,
        *,
        tenant_id: str,
        document_id: str,
        version: int,
        filename: str,
        content: bytes,
    ) -> str:
        directory = self._root / tenant_id / document_id / str(version)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / filename
        path.write_bytes(content)
        return str(path)
