from __future__ import annotations

import abc
import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.core.config import settings


class ArtifactStorage(abc.ABC):
    @abc.abstractmethod
    def save_artifact(self, relative_path: str, content: str | bytes) -> str:
        """Saves artifact and returns storage path or public/read URL."""
        pass

    @abc.abstractmethod
    def read_artifact(self, storage_identifier: str) -> Optional[str]:
        """Reads artifact content as string."""
        pass

    @abc.abstractmethod
    def artifact_exists(self, storage_identifier: str) -> bool:
        """Checks if artifact exists."""
        pass


class LocalFilesystemStorage(ArtifactStorage):
    """Local filesystem storage used during local development."""

    def __init__(self, base_dir: Path | str = settings.ARTIFACTS_DIR):
        self.base_dir = Path(base_dir)

    def save_artifact(self, relative_path: str, content: str | bytes) -> str:
        dest = self.base_dir / relative_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        mode = "wb" if isinstance(content, bytes) else "w"
        encoding = None if isinstance(content, bytes) else "utf-8"
        with open(dest, mode, encoding=encoding) as f:
            f.write(content)
        return str(dest)

    def read_artifact(self, storage_identifier: str) -> Optional[str]:
        path = Path(storage_identifier)
        if not path.is_absolute():
            path = self.base_dir / storage_identifier
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def artifact_exists(self, storage_identifier: str) -> bool:
        path = Path(storage_identifier)
        if not path.is_absolute():
            path = self.base_dir / storage_identifier
        return path.exists()


class VercelBlobStorage(ArtifactStorage):
    """Durable cloud storage via Vercel Blob REST API (or S3-compatible)."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("BLOB_READ_WRITE_TOKEN")

    def save_artifact(self, relative_path: str, content: str | bytes) -> str:
        if not self.token:
            # Fallback to in-memory/ephemeral if token not configured
            raise RuntimeError("BLOB_READ_WRITE_TOKEN not configured for Vercel Blob storage.")

        url = f"https://blob.vercel-storage.com/{relative_path}"
        data = content.encode("utf-8") if isinstance(content, str) else content
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "authorization": f"Bearer {self.token}",
                "x-api-version": "7",
                "content-type": "application/json",
            },
            method="PUT",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode())
                return result.get("url", url)
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Vercel Blob upload failed: {e.code} {e.reason}")

    def read_artifact(self, storage_identifier: str) -> Optional[str]:
        if storage_identifier.startswith("http://") or storage_identifier.startswith("https://"):
            try:
                with urllib.request.urlopen(storage_identifier, timeout=15) as resp:
                    return resp.read().decode("utf-8")
            except Exception:
                return None
        return None

    def artifact_exists(self, storage_identifier: str) -> bool:
        if storage_identifier.startswith("http://") or storage_identifier.startswith("https://"):
            req = urllib.request.Request(storage_identifier, method="HEAD")
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    return resp.status == 200
            except Exception:
                return False
        return False


def get_artifact_storage() -> ArtifactStorage:
    provider = os.getenv("STORAGE_PROVIDER", "local").lower()
    if provider == "vercel_blob" or (os.getenv("VERCEL") and os.getenv("BLOB_READ_WRITE_TOKEN")):
        return VercelBlobStorage()
    return LocalFilesystemStorage()
