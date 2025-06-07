"""
处理策略实现
包含具体的注册表修改策略
"""

from .registry_utils import read_reg_binary_value, write_reg_binary_value
from ...core.exceptions.exceptions import RegistryReadError, RegistryWriteError, RegistryPermissionError


class BaseZeroSensitivityStrategy:
    """零灵敏度策略基类"""

    def execute(self, root_key, sub_key, value_name):
        """
        执行注册表修改操作

        返回:
            dict: 包含操作结果和修改前后数据的字典
        """
        raise NotImplementedError("子类必须实现此方法")


class DefaultZeroSensitivityStrategy(BaseZeroSensitivityStrategy):
    """默认零灵敏度修改策略"""

    def execute(self, root_key, sub_key, value_name):
        result = {
            'key': f"{root_key}\\{sub_key}\\{value_name}",
            'original_data': None,
            'modified_data': None,
            'modified': False,
            'success': False
        }

        try:
            # 读取当前值
            raw_data = read_reg_binary_value(root_key, sub_key, value_name)
            if raw_data is None:
                raise RegistryReadError("无法读取注册表值", key_path=sub_key, value_name=value_name)

            result['original_data'] = raw_data

            # 检查是否需要修改（第一个字节是否为0x01）
            if raw_data[0] == 0x01:
                result['modified'] = False
                return result

            # 修改第一个字节为0x01
            modified_data = bytes([0x01]) + raw_data[1:]
            result['modified_data'] = modified_data

            # 写入新值
            if not write_reg_binary_value(root_key, sub_key, value_name, modified_data):
                raise RegistryWriteError("注册表写入失败", key_path=sub_key, value_name=value_name)

            result['modified'] = True
            result['success'] = True
            return result

        except OSError as e:
            error_code = e.winerror if hasattr(e, 'winerror') else None
            if error_code == 5:  # 权限不足
                raise RegistryPermissionError(f"注册表写入权限不足: {str(e)}",
                                              key_path=sub_key,
                                              value_name=value_name)
            elif error_code == 2:  # 文件未找到
                raise RegistryReadError(f"注册表路径不存在: {str(e)}",
                                        key_path=sub_key,
                                        value_name=value_name)
            else:
                raise RegistryWriteError(f"注册表操作失败: {str(e)}",
                                         key_path=sub_key,
                                         value_name=value_name)
