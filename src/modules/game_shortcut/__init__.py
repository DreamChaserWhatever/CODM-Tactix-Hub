"""
游戏快捷方式模块
提供创建游戏快捷方式的功能
"""

from .service import GameShortcutService


def create_service() -> GameShortcutService:
    """创建游戏快捷方式服务实例"""
    return GameShortcutService()


# 公共API
__all__ = [
    'create_service',
    'GameShortcutService'
]
