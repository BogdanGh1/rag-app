import os
from pathlib import Path

from fastapi import UploadFile


async def save_upload(upload: UploadFile, upload_dir: str, document_id: str) -> str:
    os.makedirs(upload_dir, exist_ok=True)
    filename = upload.filename or "unknown"
    suffix = Path(filename).suffix
    file_path = os.path.join(upload_dir, f"{document_id}{suffix}")
    content = await upload.read()
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path
