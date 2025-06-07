import ctypes
import os
import re
import winreg
from src.bootstrap import initialize_app
from src.core.di.provider import DependencyProvider
from src.core.exceptions.exceptions import RegistryOperationError
from src.core.utils.logger import LoggerManager
from src.modules.reg_unlock_fps import RegUnlockFPSService
from src.modules.zero_sensitivity import ZeroSensitivityService
from src.modules.game_shortcut import GameShortcutService


# 配置正则表达式模式
SENSITIVITY_PATTERN = re.compile(
    r"^CODM_\d+_"  # 动态前缀
    r"iMSDK_CN_"  # 固定模块标识
    r"(PVE|PVP|TD|Br|PVEFiring|PVPFiring|TDFiring|BrFiring)"  # 扩展模式部分
    r"(_(?:RotateSensitive|AimRotate|ReddotHolo|Sniper|Free|ACOG|[\dX]+|SkyVehicle|GroundVehicle|Vertical|Ult).*?)?"  # 动态描述部分
    r"_h\d+$",  # 固定后缀哈希值
    re.IGNORECASE
)

FPS_UNLOCK_PATTERN = re.compile(
    r"^CODM_\d+_"  # 动态前缀
    r"iMSDK_CN_"  # 固定模块标识
    r"(EnableFramerateCustomize|FramerateCustomizeValue)"  # 关键部分
    r"_h\d+$",  # 固定后缀哈希值
    re.IGNORECASE
)


def process_codm_registry():
    """处理CODM注册表键值"""
    logger = LoggerManager.get_logger("RegistryProcessor", show_time=False)
    root_key = winreg.HKEY_CURRENT_USER
    sub_key = r"SOFTWARE\Tencent\Call-of-Duty"

    try:
        # 获取服务实例
        fps_service = DependencyProvider.get(RegUnlockFPSService)
        sensitivity_service = DependencyProvider.get(ZeroSensitivityService)  # 假设你也有这个服务

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

                    # 处理灵敏度设置
                    if SENSITIVITY_PATTERN.match(name) and value_type == winreg.REG_DWORD:
                        try:
                            sensitivity_service.apply_zero_sensitivity(root_key, sub_key, name)
                            pass
                        except RegistryOperationError as e:
                            logger.error(f"灵敏度设置失败: {str(e)}")

                    # 处理帧率解锁
                    elif FPS_UNLOCK_PATTERN.match(name) and value_type == winreg.REG_DWORD:
                        try:
                            fps_service.apply_reg_unlock(root_key, sub_key, name)
                        except RegistryOperationError as e:
                            logger.error(f"帧率解锁失败: {str(e)}")

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


def logger_banner():
    logger = LoggerManager.get_logger("Banner", show_time=False)
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


def main():
    """程序主入口"""
    logger = LoggerManager.get_logger("Main", show_time=False)
    logger_banner()

    if not check_admin_privileges():
        input("按Enter键继续...")  # 按任意键继续
        return

    try:
        # 初始化应用
        initialize_app()
        logger.info(f"0.退出程序")
        logger.info(f"1.默认ZeroSensitivity, RegUnlockFPS")
        logger.info(f"2.创建全屏独占方式于桌面")
        while True:
            function = logger.input(">>>{color:yellow}请输入功能: {/color}", color="lightcyan")
            # 处理注册表
            if function == str(0):
                return
            elif function == str(1):
                process_codm_registry()
                return
            elif function == str(2):
                if create_exclusive_shortcut():
                    logger.info("操作成功完成!")
                return
            else:
                logger.error("请输入有效的功能")

    except Exception as e:
        logger.critical(f"程序运行时发生严重错误: {str(e)}")
    finally:
        input("按Enter键继续...")  # 按任意键继续


if __name__ == "__main__":
    main()
