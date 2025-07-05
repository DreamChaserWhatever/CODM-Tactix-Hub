from src.core.utils.logger import LoggerManager
from src.core.di.provider import DependencyProvider
from src.modules.reg_unlock_fps import RegUnlockFPSService
from src.modules.zero_sensitivity import ZeroSensitivityService
from src.modules.game_shortcut import GameShortcutService
from src.modules.reg_unlock_fov import RegUnlockFOVService

# 导入模块接口和实现


def initialize_app():
    """初始化应用依赖"""
    loggers = LoggerManager.get_logger("bootstrap", show_time=False)
    DependencyProvider.register(RegUnlockFPSService, RegUnlockFPSService)
    DependencyProvider.register(ZeroSensitivityService, ZeroSensitivityService)
    DependencyProvider.register(GameShortcutService, GameShortcutService)
    DependencyProvider.register(RegUnlockFOVService, RegUnlockFOVService)
    loggers.success("{color:yellow}RegUnlockFPS{/color}依赖初始化完成")
    loggers.success("{color:yellow}ZeroSensitivity{/color}依赖初始化完成")
    loggers.success("{color:yellow}GameShortcut{/color}依赖初始化完成")
    loggers.success("{color:yellow}RegUnlockFOV{/color}依赖初始化完成")
