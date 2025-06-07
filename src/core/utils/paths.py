import sys
from pathlib import Path


def resource_path(relative_path: str) -> str:
    """获取资源绝对路径（兼容开发环境和打包环境）"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包环境
        base_path = Path(sys._MEIPASS)
    else:
        # 开发环境：src/core/utils -> src/
        base_path = Path(__file__).resolve().parent.parent.parent

    # 处理Windows路径分隔符
    full_path = base_path / relative_path
    return str(full_path).replace('\\', '/')
