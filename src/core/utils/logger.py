import logging
import sys
import re
import os
from datetime import datetime
import colorama
from colorama import Fore
from typing import Optional

# 初始化colorama
colorama.init()

# 确保在 Windows 上启用 ANSI 转义序列支持
if sys.platform.startswith('win'):
    os.system('')  # 启用 Windows ANSI 支持


class Style:
    """ANSI 样式常量"""
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    RESET_UNDERLINE = '\033[24m'


# 添加 SUCCESS 日志级别 (25)
SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")


# 创建自定义 Logger 类解决代码补全问题
class EnhancedLogger(logging.Logger):
    """支持 success 方法和输入功能的日志记录器类"""

    def success(self, msg, *args, **kwargs):
        """
        记录 SUCCESS 级别的日志

        :param msg: 日志消息
        :param args: 格式化参数
        :param kwargs: 额外参数
        """
        if self.isEnabledFor(SUCCESS_LEVEL):
            self._log(SUCCESS_LEVEL, msg, args, **kwargs)

    def input(self, prompt: str, color: Optional[str] = None) -> str:
        """
        在日志系统中显示带颜色的输入提示并获取用户输入

        :param prompt: 输入提示文本
        :param color: 可选的颜色名称（如 'red', 'green', 'yellow' 等）
        :return: 用户输入的字符串
        """
        # 首先应用颜色标签
        prompt = apply_color_tags(prompt)

        # 如果指定了整体颜色，则应用整体颜色
        if color:
            color_code = COLORS.get(color.lower(), COLORS["DEFAULT"])
            prompt = f"{color_code}{prompt}{COLORS['DEFAULT']}"

        # 打印提示（不带换行）
        print(prompt, end='', flush=True)

        try:
            # 获取用户输入
            user_input = sys.stdin.readline().rstrip('\n')
        except KeyboardInterrupt:
            # 处理 Ctrl+C
            print()  # 移动到新行
            raise

        return user_input


# 设置自定义 Logger 类
logging.setLoggerClass(EnhancedLogger)

# 颜色配置
COLORS = {
    # 日志级别颜色
    "SUCCESS": Fore.GREEN,
    "INFO": Fore.CYAN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.RED + '\033[1m',

    # 特殊部分颜色
    "TIME": Fore.GREEN,
    "MODULE_NAME": Fore.LIGHTGREEN_EX,
    "MODULE_UNDERLINE": Style.UNDERLINE,
    "DEFAULT": Fore.WHITE,

    # 颜色别名
    "red": Fore.RED,
    "green": Fore.GREEN,
    "yellow": Fore.YELLOW,
    "blue": Fore.BLUE,
    "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN,
    "white": Fore.WHITE,
    "lightred": Fore.LIGHTRED_EX,
    "lightgreen": Fore.LIGHTGREEN_EX,
    "lightyellow": Fore.LIGHTYELLOW_EX,
    "lightblue": Fore.LIGHTBLUE_EX,
    "lightmagenta": Fore.LIGHTMAGENTA_EX,
    "lightcyan": Fore.LIGHTCYAN_EX,
    "lightwhite": Fore.LIGHTWHITE_EX,
}

# 颜色标签处理的正则表达式
COLOR_TAG_PATTERN = re.compile(r'\{color:([a-z_]+)\}(.*?)\{/color\}', re.IGNORECASE)


def apply_color_tags(message: str) -> str:
    """处理消息中的自定义着色标签"""

    def replace_color_tag(match):
        color_name = match.group(1).lower()
        content = match.group(2)
        color = COLORS.get(color_name, COLORS["DEFAULT"])
        return color + content + COLORS["DEFAULT"]

    return COLOR_TAG_PATTERN.sub(replace_color_tag, message)


class EnhancedFormatter(logging.Formatter):
    """支持彩色输出的日志格式化器"""

    def __init__(self, show_time=True):
        super().__init__()
        self.show_time = show_time

    def format(self, record):
        levelname = record.levelname
        module = record.name if record.name else "system"
        message = record.getMessage()

        # 构建时间部分（如果启用）
        if self.show_time:
            current_time = datetime.now().strftime("%m-%d %H:%M:%S")
            time_part = COLORS["TIME"] + current_time + " "  # 时间后面添加空格
        else:
            time_part = ""

        # 构建级别部分 - 不再添加前导空格
        level_color = COLORS.get(levelname, COLORS["DEFAULT"])
        level_part = level_color + f"[{levelname}]"  # 移除前面的空格

        # 构建模块部分
        module_part = (
                COLORS["MODULE_NAME"] + " " +
                COLORS["MODULE_UNDERLINE"] + module +
                Style.RESET_UNDERLINE
        )

        separator = COLORS["DEFAULT"] + " |"
        colored_message = apply_color_tags(message)

        # 组合所有部分
        return f"{time_part}{level_part}{module_part}{separator} {colored_message}{Style.RESET}"


class LoggerManager:
    """集中管理日志记录器的类"""

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str, level: int = logging.DEBUG, show_time: bool = True) -> EnhancedLogger:
        """
        获取或创建指定名称的日志记录器

        :param name: 日志记录器名称
        :param level: 日志级别 (默认DEBUG)
        :param show_time: 是否显示时间戳 (默认True)
        :return: 配置好的Logger实例
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)

        # 确保日志记录器是我们自定义类的实例
        if not isinstance(logger, EnhancedLogger):
            logger.__class__ = EnhancedLogger

        logger.setLevel(level)

        # 避免重复添加处理器
        if not logger.handlers:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(EnhancedFormatter(show_time=show_time))
            logger.addHandler(console_handler)

        # 禁用传播到根日志记录器
        logger.propagate = False

        cls._loggers[name] = logger
        return logger

    @classmethod
    def set_global_level(cls, level: int):
        """设置所有日志记录器的全局级别"""
        for logger in cls._loggers.values():
            logger.setLevel(level)
