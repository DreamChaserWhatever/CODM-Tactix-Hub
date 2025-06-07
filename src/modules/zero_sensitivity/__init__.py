"""
ZeroSensitivity主模块
提供简化的服务创建接口
"""

from .service import ZeroSensitivityService


def create_service() -> ZeroSensitivityService:
    """创建零灵敏度服务实例"""
    return ZeroSensitivityService()


# 公共API
__all__ = [
    'create_service',
    'ZeroSensitivityService',
]
