import os
import re
import base64
import logging
import tempfile
from datetime import datetime
from openai import OpenAI

logger = logging.getLogger(__name__)

def _safe_filename(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9-_]+", "_", s)
    return s.strip("_") or "image"

def generate_animal_image(
    client: OpenAI,
    animal_name: str,
    size: str = "1024x1024",
    model: str = "gpt-image-1.5",
) -> str:
    """
    Generates an image for the given animal and saves it to a temp file.
    Returns the temp file path.
    """
    prompt = (
        f"A cute, wholesome, high-quality illustration of a {animal_name}, "
        "centered subject, soft lighting, simple pastel background, "
        "high detail, friendly vibe, no text, no watermark."
    )

    img = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
    )

    # Decode image
    image_bytes = base64.b64decode(img.data[0].b64_json)

    # Create temp file (NOT auto-deleted so Telegram can read it)
    safe_name = _safe_filename(animal_name)
    tmp = tempfile.NamedTemporaryFile(
        suffix=f"_{safe_name}.png",
        delete=False
    )

    with tmp as f:
        f.write(image_bytes)
        temp_path = f.name

    logger.info("Saved temp image to: %s", temp_path)
    return temp_path
