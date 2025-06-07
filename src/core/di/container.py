from typing import Dict, Type, Any, Callable


class DependencyContainer:
    """轻量级依赖注入容器"""
    _registry: Dict[Type, tuple] = {}
    _instances: Dict[Type, Any] = {}

    @classmethod
    def register(cls,
                 interface: Type,
                 implementation: Type | Callable,
                 singleton: bool = True):
        """注册依赖关系"""
        cls._registry[interface] = (implementation, singleton)

    @classmethod
    def resolve(cls, interface: Type) -> Any:
        """解析依赖项"""
        if interface not in cls._registry:
            raise DependencyError(f"未注册的依赖: {interface.__name__}")

        impl, singleton = cls._registry[interface]

        # 处理单例模式
        if singleton:
            if interface not in cls._instances:
                instance = impl() if callable(impl) else impl
                cls._instances[interface] = instance
            return cls._instances[interface]

        return impl() if callable(impl) else impl

    @classmethod
    def reset(cls):
        """重置容器(测试用)"""
        cls._registry.clear()
        cls._instances.clear()


class DependencyError(Exception):
    """依赖解析异常"""
