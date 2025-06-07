"""
处理策略实现
包含具体的注册表修改策略
"""
import re
import winreg
from ...core.exceptions.exceptions import RegistryOperationError, RegistryWriteError, RegistryPermissionError


class BaseRegUnlockFPSStrategy:
    """注册表修改策略基类"""

    def execute(self, root_key, sub_key, value_name):
        """
        执行注册表修改操作

        返回:
            dict: 包含操作结果和修改前后数据的字典
        """
        raise NotImplementedError("子类必须实现此方法")


class DefaultRegUnlockFPSStrategy(BaseRegUnlockFPSStrategy):
    """默认帧率修改策略"""

    def execute(self, root_key, sub_key, value_name):
        result = {
            'key': f"{root_key}\\{sub_key}\\{value_name}",
            'original_value': None,
            'new_value': None,
            'modified': False,
            'success': False
        }

        try:
            # 读取当前值
            with winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_READ) as key:
                current_value, value_type = winreg.QueryValueEx(key, value_name)
                result['original_value'] = current_value

                # 确定需要修改的值
                if re.search(r'EnableFramerateCustomize', value_name):
                    modified_data = 1 if current_value != 1 else current_value
                elif re.search(r'FramerateCustomizeValue', value_name):
                    modified_data = 0 if current_value != 0 else current_value
                else:
                    # 不需要修改
                    result['modified'] = False
                    return result

                # 检查是否需要修改
                if current_value == modified_data:
                    result['modified'] = False
                    return result

                result['new_value'] = modified_data

                # 写入新值
                with winreg.OpenKey(
                        root_key, sub_key, 0, winreg.KEY_SET_VALUE
                ) as write_key:
                    winreg.SetValueEx(
                        write_key, value_name, 0, winreg.REG_DWORD, modified_data)

                    result['modified'] = True
                    result['success'] = True
                    return result

        except WindowsError as e:
            error_code = e.winerror if hasattr(e, 'winerror') else None
            if error_code == 5:  # 权限不足
                raise RegistryPermissionError(f"注册表写入权限不足: {str(e)}",
                                              key_path=sub_key,
                                              value_name=value_name)
            else:
                raise RegistryWriteError(f"注册表写入失败: {str(e)}",
                                         key_path=sub_key,
                                         value_name=value_name)
