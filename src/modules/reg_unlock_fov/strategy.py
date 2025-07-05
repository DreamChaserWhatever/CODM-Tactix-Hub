"""
处理策略实现
包含具体的注册表修改策略
"""
from src.core.utils.registry_utils import read_reg_binary_value, write_reg_binary_value
from ...core.exceptions.exceptions import RegistryReadError, RegistryWriteError, RegistryPermissionError


class BaseRegUnlockFOV:
    """FOV策略基类"""

    def execute(self, root_key, sub_key, value_name, byte_):
        """
        执行注册表修改操作

        返回:
            dict: 包含操作结果和修改前后数据的字典
        """
        raise NotImplementedError("子类必须实现此方法")


class DefaultRegUnlockFOV(BaseRegUnlockFOV):
    def execute(self, root_key, sub_key, value_name, byte_):
        result = {
            'key': f"{root_key}\\{sub_key}\\{value_name}",
            'original_data': None,
            'modified_data': None,
            'modified': False,
            'success': False,
            'byte': byte_
        }
        try:
            # 读取当前值
            raw_data = read_reg_binary_value(root_key, sub_key, value_name)
            if raw_data is None:
                raise RegistryReadError("无法读取注册表值", key_path=sub_key, value_name=value_name)
            result['original_data'] = raw_data
            # 检查数据长度是否足够
            if len(raw_data) < 6:
                raise ValueError(f"数据长度不足6个字节，实际长度: {len(raw_data)}")
            # 转换为字节数组以便修改
            modified_bytes = bytearray(raw_data)
            if modified_bytes[6] == byte_:
                result['modified'] = False
                return result

            modified_bytes[6] = byte_

            # 转换回字节
            modified_data = bytes(modified_bytes)
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
