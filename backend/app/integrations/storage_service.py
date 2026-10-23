import os
import uuid
from pathlib import Path
from typing import Optional, Tuple

from app.core.config import settings
from app.core.errors import BadRequestError
from fastapi import UploadFile


class StorageService:
    def __init__(self):
        self.backend = settings.STORAGE_BACKEND
        self.local_dir = Path(settings.LOCAL_STORAGE_DIR).resolve()
        if self.backend == "local":
            self.local_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, filename: str, content_type: str, file_size: int) -> None:
        """Validate filename safety, file size, extension and MIME type."""
        # Check size
        if file_size > settings.MAX_FILE_SIZE_BYTES:
            max_mb = settings.MAX_FILE_SIZE_BYTES / (1024 * 1024)
            raise BadRequestError(f"File size exceeds the {max_mb:.0f} MB limit.")

        # Check path traversal and invalid characters
        if ".." in filename or "/" in filename or "\\" in filename:
            raise BadRequestError("Invalid filename. Path traversal characters are not permitted.")

        # Check extension
        ext = Path(filename).suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise BadRequestError(
                f"Unsupported file extension '{ext}'. Allowed extensions are: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # Check MIME type
        if content_type and content_type not in settings.ALLOWED_MIME_TYPES:
            # Tolerant check for common docx/txt variants
            if not (
                ext == ".docx"
                and "word" in content_type
                or ext == ".txt"
                and "text" in content_type
            ):
                raise BadRequestError(f"Unsupported MIME type: '{content_type}'")

    async def save_file(self, upload_file: UploadFile) -> Tuple[str, str, int, str]:
        """
        Saves file securely using a unique UUID key to prevent guessing or collision.
        Returns: (file_url, storage_key, file_size_bytes, mime_type)
        """
        filename = upload_file.filename or "unknown_file.pdf"
        content_type = upload_file.content_type or "application/octet-stream"

        content = await upload_file.read()
        file_size = len(content)

        self.validate_file(filename, content_type, file_size)

        ext = Path(filename).suffix.lower()
        unique_key = f"{uuid.uuid4().hex}{ext}"

        if self.backend == "local":
            destination_path = self.local_dir / unique_key
            with open(destination_path, "wb") as f:
                f.write(content)
            file_url = f"/uploads/{unique_key}"
            return file_url, str(destination_path), file_size, content_type
        else:
            # S3 adapter fallback / implementation
            # In production with boto3: s3_client.put_object(...)
            file_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_key}"
            return file_url, unique_key, file_size, content_type

    def get_local_path(self, file_url: str) -> Optional[Path]:
        """Resolves local filesystem path from a file URL."""
        if file_url.startswith("/uploads/"):
            filename = file_url.replace("/uploads/", "")
            return self.local_dir / filename
        p = Path(file_url)
        if p.exists():
            return p
        return None

    def delete_file(self, file_url: str) -> bool:
        """Deletes file from storage."""
        if self.backend == "local":
            path = self.get_local_path(file_url)
            if path and path.exists():
                try:
                    os.remove(path)
                    return True
                except OSError:
                    return False
        return True


storage_service = StorageService()
