"""
服务层实现
提供高层业务逻辑
"""
from src.core.di.provider import DependencyProvider
from src.core.utils.logger import LoggerManager
from .strategy import BaseRegUnlockFPSStrategy, DefaultRegUnlockFPSStrategy
from ...core.exceptions.exceptions import RegistryOperationError


class RegUnlockFPSService:
    """注册表解锁帧率服务"""

    def __init__(self, strategy: BaseRegUnlockFPSStrategy = None):
        """
        初始化服务

        参数:
            strategy: 注册表修改策略 (默认为DefaultRegUnlockFPSStrategy)
        """
        self.strategy = strategy or DefaultRegUnlockFPSStrategy()
        self.logger = LoggerManager.get_logger("RegUnlockFPS", show_time=False)

    def apply_reg_unlock(self, root_key, sub_key, value_name):
        """
        应用帧率解锁修改

        返回:
            dict: 包含操作结果和修改前后数据的字典
        """
        try:
            result = self.strategy.execute(root_key, sub_key, value_name)

            if result['modified']:
                self.logger.success(
                    f"成功修改注册表: {result['key']}\n"
                    f"原始值: {result['original_value']} → 新值: {result['new_value']}"
                )
            else:
                self.logger.info(
                    f"无需修改注册表: {result['key']}\n"
                    f"当前值已为期望值: {result['original_value']}"
                )

            return result

        except RegistryOperationError as e:
            self.logger.error(f"注册表操作失败: {str(e)}")
            raise
