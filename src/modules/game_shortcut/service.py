from src.core.utils.logger import LoggerManager
from src.core.utils.paths import resource_path
from ...core.exceptions.exceptions import GameProcessNotFoundError, ShortcutCreationError
from .strategy import BaseShortcutStrategy, DefaultShortcutStrategy


class GameShortcutService:
    """游戏快捷方式服务"""

    def __init__(self, strategy: BaseShortcutStrategy = None):
        """
        初始化服务

        参数:
            strategy: 快捷方式创建策略 (默认为DefaultShortcutStrategy)
        """
        self.strategy = strategy or DefaultShortcutStrategy()
        self.logger = LoggerManager.get_logger("GameShortcut", show_time=False)

    def create_exclusive_shortcut(self, game_name="CODM.exe"):
        """
        创建全屏独占模式快捷方式

        参数:
            game_name: 游戏进程名称 (默认: CODM.exe)

        返回:
            str: 创建的快捷方式路径
        """
        try:
            # 获取游戏路径
            game_path = self.strategy.find_game_process(game_name)
            self.logger.info(f"找到游戏进程: {game_path}")

            # 创建快捷方式
            shortcut_path = self.strategy.create_shortcut(
                game_path,
                "-window-mode exclusive 5",
                "CODM全屏独占模式"
            )

            self.logger.success(f"快捷方式创建成功: {shortcut_path}")
            return shortcut_path

        except GameProcessNotFoundError:
            self.logger.error(f"未找到运行中的游戏进程: {game_name}")
            raise
        except ShortcutCreationError as e:
            self.logger.error(f"快捷方式创建失败: {str(e)}")
            raise
