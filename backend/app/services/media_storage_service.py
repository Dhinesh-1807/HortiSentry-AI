import os
import uuid
import io
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
from PIL import Image, ImageOps
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

class MediaStorageInterface(ABC):
    @abstractmethod
    def save_image(self, file_bytes: bytes, original_filename: str) -> Tuple[str, str, int, int, int, str]:
        """
        Saves image and returns:
        (saved_relative_path, unique_filename, file_size_bytes, width, height, mime_type)
        """
        pass

class LocalMediaStorageService(MediaStorageInterface):
    """
    Local filesystem storage implementation with strict security checking:
    - Validates file size (< 10MB)
    - Validates PIL decoding and image integrity
    - Generates UUID filenames preventing directory traversal
    """

    def __init__(self, upload_dir: str = settings.UPLOAD_DIR):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def validate_file(self, file_bytes: bytes, filename: str) -> Image.Image:
        # 1. Size check
        file_size = len(file_bytes)
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )

        # 2. Extension check
        ext = os.path.splitext(filename)[1].lower().lstrip(".")
        if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file extension '.{ext}'. Allowed: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
            )

        # 3. Pillow Decoding & Content Integrity check
        try:
            image = Image.open(io.BytesIO(file_bytes))
            image.verify() # Verify file header & structure
            
            # Re-open for actual processing (verify closes file descriptor)
            image = Image.open(io.BytesIO(file_bytes))
            image = ImageOps.exif_transpose(image) # Auto-rotate based on EXIF orientation
            return image
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file or corrupted image data."
            )

    def save_image(self, file_bytes: bytes, original_filename: str) -> Tuple[str, str, int, int, int, str]:
        # Validate image payload
        image = self.validate_file(file_bytes, original_filename)

        ext = os.path.splitext(original_filename)[1].lower()
        if not ext or ext.lstrip(".") not in settings.ALLOWED_IMAGE_EXTENSIONS:
            ext = ".jpg"

        # Generate safe UUID filename
        unique_name = f"{uuid.uuid4()}{ext}"
        destination_path = os.path.join(self.upload_dir, unique_name)

        # Save to disk cleanly
        with open(destination_path, "wb") as f:
            f.write(file_bytes)

        width, height = image.size
        mime_type = f"image/{image.format.lower() if image.format else 'jpeg'}"

        return (
            destination_path,
            unique_name,
            len(file_bytes),
            width,
            height,
            mime_type
        )

media_storage_service = LocalMediaStorageService()
