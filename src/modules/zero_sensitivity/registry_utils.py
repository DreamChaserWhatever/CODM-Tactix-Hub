"""
Windows注册表操作工具模块
包含底层API封装和辅助函数
"""
from ctypes import wintypes
import ctypes
import winreg

# 定义Windows API所需的数据结构和函数
advapi32 = ctypes.WinDLL("advapi32.dll")

RegOpenKeyEx = advapi32.RegOpenKeyExW
RegOpenKeyEx.argtypes = [
    wintypes.HKEY,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.HKEY),
]
RegOpenKeyEx.restype = wintypes.LONG

RegQueryValueEx = advapi32.RegQueryValueExW
RegQueryValueEx.argtypes = [
    wintypes.HKEY,
    wintypes.LPCWSTR,
    wintypes.LPDWORD,
    ctypes.POINTER(wintypes.DWORD),
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.POINTER(wintypes.DWORD),
]
RegQueryValueEx.restype = wintypes.LONG

RegSetValueEx = advapi32.RegSetValueExW
RegSetValueEx.argtypes = [
    wintypes.HKEY,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.DWORD,
    ctypes.POINTER(ctypes.c_ubyte),
    wintypes.DWORD
]
RegSetValueEx.restype = wintypes.LONG

RegCloseKey = advapi32.RegCloseKey
RegCloseKey.argtypes = [wintypes.HKEY]
RegCloseKey.restype = wintypes.LONG

# 常量定义
ERROR_SUCCESS = 0
KEY_READ = winreg.KEY_READ
KEY_WRITE = winreg.KEY_WRITE
REG_BINARY = winreg.REG_BINARY


def read_reg_binary_value(hkey, sub_key, value_name):
    """
    读取注册表键值的原始二进制数据

    返回:
        bytes: 二进制数据，读取失败返回None
    """
    h_key = wintypes.HKEY()
    if RegOpenKeyEx(hkey, sub_key, 0, KEY_READ, ctypes.byref(h_key)) != ERROR_SUCCESS:
        return None

    data_type = wintypes.DWORD()
    data_size = wintypes.DWORD()

    # 第一次调用获取数据大小
    if RegQueryValueEx(
            h_key,
            value_name,
            None,
            ctypes.byref(data_type),
            None,
            ctypes.byref(data_size)
    ) != ERROR_SUCCESS:
        RegCloseKey(h_key)
        return None

    # 分配缓冲区并读取数据
    data_buffer = (ctypes.c_ubyte * data_size.value)()
    if RegQueryValueEx(
            h_key,
            value_name,
            None,
            None,
            data_buffer,
            ctypes.byref(data_size)
    ) != ERROR_SUCCESS:
        RegCloseKey(h_key)
        return None

    RegCloseKey(h_key)
    return bytes(data_buffer)


def write_reg_binary_value(hkey, sub_key, value_name, data):
    """
    写入二进制数据到注册表

    返回:
        bool: 写入是否成功
    """
    h_key = wintypes.HKEY()
    if RegOpenKeyEx(hkey, sub_key, 0, KEY_WRITE, ctypes.byref(h_key)) != ERROR_SUCCESS:
        return False

    # 准备数据
    data_size = len(data)
    data_buffer = (ctypes.c_ubyte * data_size)(*data)

    # 写入数据
    result = RegSetValueEx(
        h_key,
        value_name,
        0,
        REG_BINARY,
        data_buffer,
        data_size
    )

    RegCloseKey(h_key)
    return result == ERROR_SUCCESS
