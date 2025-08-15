import subprocess
from pathlib import Path

class PermissionDenied(Exception):
    pass

async def delete_file(
    file_path: Path,
    current_user_id: int,
    owner_id: int | None = None,
    admin_override: bool = False
):
    """
    删除物理文件并做权限检查
    - 普通用户只能删除自己的文件
    - admin_override=True 时管理员可删除任何文件
    """
    # 权限检查
    if not admin_override:
        if owner_id is not None and current_user_id != owner_id:
            raise PermissionDenied("你没有权限删除这个文件")

    if file_path.exists():
        try:
            # 尝试正常删除
            file_path.unlink()
            print(f"🗑 已删除文件: {file_path}")
        except PermissionError:
            # 如果权限不足，使用 shell 强制删除
            try:
                subprocess.run(["rm", "-f", str(file_path)], check=True)
                print(f"🗑 强制删除文件: {file_path}")
            except Exception as e:
                print(f"❌ 强制删除文件失败: {file_path} -> {e}")
                raise
        except Exception as e:
            print(f"❌ 删除文件失败: {file_path} -> {e}")
            raise
    else:
        print(f"⚠️ 文件不存在: {file_path}")
