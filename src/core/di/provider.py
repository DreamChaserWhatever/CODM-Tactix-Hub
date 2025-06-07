from .container import DependencyContainer
from typing import Dict, Type, Any, Callable


class DependencyProvider:
    """提供依赖注入的便捷访问方法"""

    @staticmethod
    def get(interface: Type) -> Any:
        """获取依赖实例"""
        return DependencyContainer.resolve(interface)

    @staticmethod
    def register(interface: Type, implementation: Type | Callable, singleton=True):
        """注册依赖"""
        DependencyContainer.register(interface, implementation, singleton)

    @staticmethod
    def register_instance(interface: Type, instance: Any):
        """直接注册实例"""
        DependencyContainer.register(interface, lambda: instance, singleton=True)
