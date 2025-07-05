"""
ZeroSensitivity主模块
提供简化的服务创建接口
"""

from .service import RegUnlockFOVService


def create_service() -> RegUnlockFOVService:
    """创建零灵敏度服务实例"""
    return RegUnlockFOVService()


# 公共API
__all__ = [
    'create_service',
    'RegUnlockFOVService',
]