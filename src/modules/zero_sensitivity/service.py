"""
服务层实现
提供高层业务逻辑
"""
from src.core.utils.logger import LoggerManager
from .strategy import BaseZeroSensitivityStrategy, DefaultZeroSensitivityStrategy
from ...core.exceptions.exceptions import RegistryOperationError


class ZeroSensitivityService:
    """零灵敏度服务"""

    def __init__(self, strategy: BaseZeroSensitivityStrategy = None):
        """
        初始化服务

        参数:
            strategy: 灵敏度修改策略 (默认为DefaultZeroSensitivityStrategy)
        """
        self.strategy = strategy or DefaultZeroSensitivityStrategy()
        self.logger = LoggerManager.get_logger("ZeroSensitivity", show_time=False)

    def apply_zero_sensitivity(self, root_key, sub_key, value_name):
        """
        应用零灵敏度修改

        返回:
            dict: 包含操作结果和修改前后数据的字典
        """
        try:
            result = self.strategy.execute(root_key, sub_key, value_name)

            if result['modified']:
                # 格式化原始数据
                orig_hex = ' '.join(f'{b:02X}' for b in result['original_data'])
                mod_hex = ' '.join(f'{b:02X}' for b in result['modified_data'])

                self.logger.success(
                    f"成功修改灵敏度设置: {result['key']}\n"
                    f"原始值: {orig_hex}\n"
                    f"新值: {mod_hex}"
                )
            else:
                # 格式化数据
                data_hex = ' '.join(f'{b:02X}' for b in result['original_data'])

                self.logger.info(
                    f"无需修改灵敏度设置: {result['key']}\n"
                    f"当前值已为期望值: {data_hex}"
                )

            return result

        except RegistryOperationError as e:
            self.logger.error(f"灵敏度设置失败: {str(e)}")
            raise
