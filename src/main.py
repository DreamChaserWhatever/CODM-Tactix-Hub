import ctypes
import os
import re
import winreg
import argparse
from enum import Enum, auto

from src.bootstrap import initialize_app
from src.core.di.provider import DependencyProvider
from src.core.exceptions.exceptions import RegistryOperationError
from src.core.utils.logger import LoggerManager
from src.modules.reg_unlock_fps import RegUnlockFPSService
from src.modules.zero_sensitivity import ZeroSensitivityService
from src.modules.game_shortcut import GameShortcutService
from src.modules.reg_unlock_fov import RegUnlockFOVService

# 配置正则表达式模式
SENSITIVITY_PATTERN = re.compile(
    r"^CODM_\d+_"
    r"iMSDK_CN_"
    r"(PVE|PVP|TD|Br|PVEFiring|PVPFiring|TDFiring|BrFiring)"
    r"(_(?:RotateSensitive|AimRotate|ReddotHolo|Sniper|Free|ACOG|[\dX]+|SkyVehicle|GroundVehicle|Vertical|Ult).*?)?"
    r"_h\d+$",
    re.IGNORECASE
)

FPS_UNLOCK_PATTERN = re.compile(
    r"^CODM_\d+_"
    r"iMSDK_CN_"
    r"(EnableFramerateCustomize|FramerateCustomizeValue)"
    r"_h\d+$",
    re.IGNORECASE
)

FOV_UNLOCK_PATTERN = re.compile(
    r"^CODM_\d+_"
    r"iMSDK_CN_"
    r"(BRWeaponFov|MPWeaponFov)"
    r"_h\d+$",
    re.IGNORECASE
)


class MenuOption(Enum):
    """主菜单选项枚举"""
    EXIT = auto()
    OPTIMIZE = auto()  # 默认优化（灵敏度 + 帧率解锁）
    CREATE_SHORTCUT = auto()
    UNLOCK_FOV = auto()

    @classmethod
    def from_input(cls, value: str):
        """从用户输入解析为枚举值"""
        try:
            num = int(value)
            if num == 0:
                return cls.EXIT
            elif num == 1:
                return cls.OPTIMIZE
            elif num == 2:
                return cls.CREATE_SHORTCUT
            elif num == 3:
                return cls.UNLOCK_FOV
        except ValueError:
            pass
        return None


class RegistryOperation(Enum):
    """注册表操作类型枚举"""
    SENSITIVITY = auto()
    FPS_UNLOCK = auto()
    FOV_UNLOCK = auto()


def process_codm_registry(operation: RegistryOperation, fov_value: int = 0xFF):
    """处理CODM注册表键值"""
    logger = LoggerManager.get_logger("RegistryProcessor", show_time=False)
    root_key = winreg.HKEY_CURRENT_USER
    sub_key = r"SOFTWARE\Tencent\Call-of-Duty"

    # 验证FOV值范围
    if operation == RegistryOperation.FOV_UNLOCK and not (0 <= fov_value <= 255):
        logger.error(f"错误：FOV值 {fov_value} 超出范围 (0-255)")
        return

    try:
        # 获取服务实例
        fps_service = DependencyProvider.get(RegUnlockFPSService)
        sensitivity_service = DependencyProvider.get(ZeroSensitivityService)
        fov_service = DependencyProvider.get(RegUnlockFOVService)

        # 打开注册表键
        with winreg.OpenKey(
                root_key, sub_key, 0, winreg.KEY_READ | winreg.KEY_WRITE
        ) as key:
            logger.info(f"成功打开注册表路径: HKEY_CURRENT_USER\\{sub_key}")

            i = 0
            while True:
                try:
                    # 枚举所有键值
                    name, value, value_type = winreg.EnumValue(key, i)

                    # 根据操作类型处理注册表项
                    if operation == RegistryOperation.SENSITIVITY and SENSITIVITY_PATTERN.match(name):
                        try:
                            sensitivity_service.apply_zero_sensitivity(root_key, sub_key, name)
                        except RegistryOperationError as e:
                            logger.error(f"灵敏度设置失败: {str(e)}")

                    elif operation == RegistryOperation.FPS_UNLOCK and FPS_UNLOCK_PATTERN.match(name):
                        try:
                            fps_service.apply_reg_unlock(root_key, sub_key, name)
                        except RegistryOperationError as e:
                            logger.error(f"帧率解锁失败: {str(e)}")

                    elif operation == RegistryOperation.FOV_UNLOCK and FOV_UNLOCK_PATTERN.match(name):
                        try:
                            fov_service.apply_reg_unlock(root_key, sub_key, name, fov_value)
                        except RegistryOperationError as e:
                            logger.error(f"FOV设置失败: {str(e)}")

                    i += 1
                except OSError:
                    logger.info("注册表处理完成")
                    break

    except FileNotFoundError:
        logger.error(f"注册表路径不存在: HKEY_CURRENT_USER\\{sub_key}")
    except Exception as e:
        logger.critical(f"处理注册表时发生未知错误: {str(e)}")


def create_exclusive_shortcut():
    """创建全屏独占模式快捷方式"""
    logger = LoggerManager.get_logger("ShortcutCreator", show_time=False)
    try:
        # 获取服务实例
        shortcut_service = DependencyProvider.get(GameShortcutService)

        # 创建快捷方式
        shortcut_path = shortcut_service.create_exclusive_shortcut()
        logger.success(f"全屏独占模式快捷方式已创建到桌面: {os.path.basename(shortcut_path)}")
        return True
    except Exception as e:
        logger.error(f"创建快捷方式失败: {str(e)}")
        return False


def logger_banner(logger):
    """显示横幅信息"""
    logger.info("{color:yellow}CODM Tactix Hub{/color} - 注册表优化工具")
    logger.info("仅供学习交流,开源免费工具")
    logger.info("{color:yellow}开发者{/color}: DC随便")
    logger.info("{color:yellow}UID{/color}: 3493117248407780")
    logger.info("{color:yellow}Bilibili{/color}: https://space.bilibili.com/3493117248407780")
    logger.info("{color:yellow}GitHub{/color}: https://github.com/DreamChaserWhatever")


def check_admin_privileges():
    """检查管理员权限"""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("[错误] 请以管理员身份运行此程序！")
        return False
    return True


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='CODM Tactix Hub - 注册表优化工具',
    )

    # 添加命令行选项
    parser.add_argument(
        '--sensitivity',
        action='store_true',
        help='应用灵敏度优化'
    )
    parser.add_argument(
        '--fps-unlock',
        action='store_true',
        help='解锁帧率限制'
    )
    parser.add_argument(
        '--fov-unlock',
        action='store_true',
        help='解锁FOV设置 (默认值: 0xFF)'
    )
    parser.add_argument(
        '--create-shortcut',
        action='store_true',
        help='创建全屏独占模式快捷方式'
    )
    parser.add_argument(
        '--fov-value',
        type=lambda x: int(x, 0),  # 支持十六进制输入 (0xFF格式)
        default=0xFF,
        help='自定义FOV值 (0-255, 十六进制, 默认0xFF)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='执行所有优化操作 (灵敏度 + 帧率解锁 + FOV解锁)'
    )

    return parser.parse_args()


def run_from_command_line(args, logger):
    """根据命令行参数执行操作"""
    # 执行所有操作
    if args.all:
        logger.info("执行所有优化操作...")
        process_codm_registry(RegistryOperation.SENSITIVITY)
        process_codm_registry(RegistryOperation.FPS_UNLOCK)
        process_codm_registry(RegistryOperation.FOV_UNLOCK, args.fov_value)
        if create_exclusive_shortcut():
            logger.info("快捷方式创建成功")
        logger.info("所有操作已完成!")
        return True

    # 执行单个操作
    executed = False

    if args.sensitivity:
        logger.info("应用灵敏度优化...")
        process_codm_registry(RegistryOperation.SENSITIVITY)
        executed = True

    if args.fps_unlock:
        logger.info("解锁帧率限制...")
        process_codm_registry(RegistryOperation.FPS_UNLOCK)
        executed = True

    if args.fov_unlock:
        logger.info(f"解锁FOV设置 (值: 0x{args.fov_value:02X})...")
        process_codm_registry(RegistryOperation.FOV_UNLOCK, args.fov_value)
        executed = True

    if args.create_shortcut:
        logger.info("创建全屏独占模式快捷方式...")
        if create_exclusive_shortcut():
            logger.info("快捷方式创建成功")
        executed = True

    return executed


def get_valid_fov_input(logger):
    """获取有效的FOV输入值"""
    while True:
        try:
            input_str = logger.input(">>>{color:yellow}请输入FOV值 (0-255, 十六进制加0x前缀): {/color}",
                                     color="lightcyan")

            # 尝试解析十六进制输入
            if input_str.startswith("0x"):
                fov_value = int(input_str, 16)
            else:
                fov_value = int(input_str)

            if 0 <= fov_value <= 255:
                return fov_value
            else:
                logger.error("FOV值必须在0到255之间！")
        except ValueError:
            logger.error("输入无效，请输入一个有效的整数（十进制或十六进制）")


def main():
    # 1. 检查管理员权限
    is_admin = check_admin_privileges()
    if not is_admin:
        return

    initialize_app()
    logger = LoggerManager.get_logger("Main", show_time=False)

    try:
        # 解析命令行参数
        args = parse_arguments()

        # 检查是否有真正的操作标志被设置
        operation_flags = ['sensitivity', 'fps_unlock', 'fov_unlock', 'create_shortcut', 'all']
        has_operation = any(getattr(args, flag) for flag in operation_flags)
        has_operation = has_operation or (args.fov_value != 0xFF and args.fov_unlock)

        # 如果有命令行参数，则执行对应操作
        if has_operation:
            # 命令行模式显示横幅
            logger_banner(logger)
            run_from_command_line(args, logger)
            return
        else:

            while True:
                # 显示横幅
                logger_banner(logger)

                # 显示菜单选项
                logger.info(f"0. 退出程序")
                logger.info(f"1. 默认优化 (ZeroSensitivity + RegUnlockFPS)")
                logger.info(f"2. 创建全屏独占快捷方式")
                logger.info(f"3. 解锁FOV (可自定义值)")

                user_input = logger.input(">>>{color:yellow}请输入功能选项: {/color}", color="lightcyan")
                option = MenuOption.from_input(user_input)

                if option is None:
                    logger.error("无效选项，请重新输入")
                    input("按Enter键继续...")
                    os.system('cls')  # 清屏
                    continue

                if option == MenuOption.EXIT:
                    return

                elif option == MenuOption.OPTIMIZE:
                    # 执行灵敏度优化和帧率解锁
                    process_codm_registry(RegistryOperation.SENSITIVITY)
                    process_codm_registry(RegistryOperation.FPS_UNLOCK)
                    logger.info("优化操作成功完成!")
                    input("按Enter键返回主菜单...")
                    os.system('cls')  # 清屏
                    continue

                elif option == MenuOption.CREATE_SHORTCUT:
                    if create_exclusive_shortcut():
                        logger.info("快捷方式创建成功!")
                    input("按Enter键返回主菜单...")
                    os.system('cls')  # 清屏
                    continue

                elif option == MenuOption.UNLOCK_FOV:
                    # 获取用户输入的FOV值
                    fov_value = get_valid_fov_input(logger)
                    process_codm_registry(RegistryOperation.FOV_UNLOCK, fov_value)
                    logger.info(f"FOV解锁成功! (值: 0x{fov_value:02X})")
                    input("按Enter键返回主菜单...")
                    os.system('cls')  # 清屏
                    continue

    except Exception as e:
        logger.critical(f"程序运行时发生严重错误: {str(e)}")
    finally:
        input("按Enter键退出程序...")


if __name__ == "__main__":
    main()
