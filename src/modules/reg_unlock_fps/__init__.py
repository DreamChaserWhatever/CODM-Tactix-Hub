"""
RegUnlockFPS主模块
提供简化的API接口
"""

from .service import RegUnlockFPSService


def create_service() -> RegUnlockFPSService:
    """创建注册表解锁帧率服务实例"""
    return RegUnlockFPSService()


# 公共API
__all__ = [
    'create_service',
    'RegUnlockFPSService',
]
