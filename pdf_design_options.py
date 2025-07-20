"""PDF design utility functions and presets."""
import base64
from pathlib import Path
from typing import Dict, Optional

BACKGROUND_PRESETS: Dict[str, Dict[str, Optional[str]]] = {
    "light_gray": {"color": "#F8F9FA", "image": None},
    "solar_blue": {"color": "#E5EEF8", "image": None},
}

def load_background_image_base64(path: str) -> Optional[str]:
    """Load an image file and return a base64 encoded string."""
    try:
        data = Path(path).read_bytes()
        return base64.b64encode(data).decode("ascii")
    except Exception:
        return None
