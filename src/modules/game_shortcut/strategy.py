import os
import psutil
import win32com.client
from ...core.exceptions.exceptions import GameProcessNotFoundError, ShortcutCreationError


class BaseShortcutStrategy:
    """快捷方式策略基类"""

    def find_game_process(self, process_name):
        """查找游戏进程路径"""
        raise NotImplementedError("子类必须实现此方法")

    def create_shortcut(self, target_path, arguments, shortcut_name):
        """创建快捷方式"""
        raise NotImplementedError("子类必须实现此方法")


class DefaultShortcutStrategy(BaseShortcutStrategy):
    """默认快捷方式策略"""

    def find_game_process(self, process_name):
        """查找游戏进程路径"""
        for proc in psutil.process_iter(['name', 'exe']):
            if proc.info['name'].lower() == process_name.lower():
                return proc.info['exe']
        raise GameProcessNotFoundError(f"未找到运行中的 {process_name} 进程")

    def create_shortcut(self, target_path, arguments, shortcut_name):
        """创建快捷方式"""
        try:
            # 获取桌面路径
            desktop = os.path.join(os.path.expanduser("~"), 'Desktop')

            # 创建快捷方式路径
            shortcut_path = os.path.join(desktop, f"{shortcut_name}.lnk")

            # 获取游戏目录作为起始位置
            working_directory = os.path.dirname(target_path)

            # 创建快捷方式
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = target_path
            shortcut.Arguments = arguments
            shortcut.WorkingDirectory = working_directory  # 设置起始位置
            shortcut.IconLocation = target_path
            shortcut.save()

            return shortcut_path
        except Exception as e:
            raise ShortcutCreationError(f"创建快捷方式失败: {str(e)}")
