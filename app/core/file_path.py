# app/core/file_path.py
from pathlib import Path
from app.core.config import settings
from app.models.user import User

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"

TYPE_DIRS = {
    "image": "images",
    "video": "videos",
    "pdf": "pdfs",
}

IS_PROD = settings.environment == "production"
PUBLIC_DIR = Path("/usr/share/nginx/html") if IS_PROD else BASE_DIR / "frontend" / "public"

if not IS_PROD:
    for base_dir in (UPLOAD_DIR, PUBLIC_DIR):
        for sub_dir in TYPE_DIRS.values():
            (base_dir / sub_dir).mkdir(parents=True, exist_ok=True)


def get_save_path(current_user: User, file_type: str, filename: str) -> tuple[Path, str]:
    if file_type not in TYPE_DIRS:
        raise ValueError(f"Unsupported file type: {file_type}")

    sub_dir = TYPE_DIRS[file_type]

    if getattr(current_user, "is_admin", False):
        base_dir = PUBLIC_DIR
        base_url = f"/{sub_dir}"
    else:
        base_dir = UPLOAD_DIR
        base_url = f"/uploads/{sub_dir}"

    save_dir = base_dir / sub_dir
    file_url = f"{base_url}/{filename}"
    return save_dir, file_url


def get_file_path_from_url(url: str) -> Path:
    if url.startswith("/uploads/"):
        relative_path = url[len("/uploads/"):]
        return UPLOAD_DIR / relative_path
    else:
        relative_path = url.lstrip("/")
        return PUBLIC_DIR / relative_path
