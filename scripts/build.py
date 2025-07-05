import os
import shutil
import subprocess
import sys
from datetime import datetime

# 将项目根目录添加到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def build_executable():
    """构建可执行文件"""
    # 获取项目根目录
    os.chdir(project_root)

    # 配置路径
    entry_point = os.path.join(project_root, "src", "main.py")
    output_name = "CODM_Tactix_Hub"
    resources_dir = os.path.join(project_root, "resources")
    dist_path = os.path.join(project_root, "dist")
    build_path = os.path.join(project_root, "build")
    spec_path = os.path.join(project_root, "build.spec")

    # 清理旧构建
    clean_old_builds(dist_path, build_path, spec_path)

    # 确保输出目录存在
    os.makedirs(dist_path, exist_ok=True)

    # 获取所有需要隐藏导入的模块
    hidden_imports = get_hidden_imports()

    # 构建PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",
        f"--name={output_name}",
        f"--icon={os.path.join(resources_dir, 'icon.ico')}",  # 应用图标
        f"--add-data={resources_dir}{os.pathsep}resources",
        f"--distpath={dist_path}",
        f"--workpath={build_path}",
        f"--specpath={project_root}",
        "--clean",  # 清理临时文件
        "--upx-dir=upx" if os.path.exists("upx") else "",  # UPX压缩
    ]

    # 添加隐藏导入
    for module in hidden_imports:
        cmd.append(f"--hidden-import={module}")

    # 添加主入口文件
    cmd.append(entry_point)

    # 过滤空参数
    cmd = [arg for arg in cmd if arg]

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始构建可执行文件...")
    print("构建命令:", " ".join(cmd))

    # 执行构建命令
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)

        # 检查构建结果
        exe_path = os.path.join(dist_path, f"{output_name}.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 构建成功!")
            print(f"输出文件: {exe_path}")
            print(f"文件大小: {file_size:.2f} MB")

            # 复制配置文件（如果需要）
            copy_config_files(dist_path)
            return True
        else:
            print(f"\n[错误] 未找到输出文件: {exe_path}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"\n[错误] 构建失败!")
        print(f"错误代码: {e.returncode}")
        print(f"错误信息:\n{e.stderr}")
        return False


def clean_old_builds(dist_path, build_path, spec_path):
    """清理旧构建文件"""
    print("清理旧构建文件...")
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)
    if os.path.exists(spec_path):
        os.remove(spec_path)


def get_hidden_imports():
    """获取所有需要隐藏导入的模块"""
    return [
        # 核心模块
        "src.core",
        "src.core.di",
        "src.core.exceptions",
        "src.core.utils",

        # 功能模块
        "src.modules.reg_unlock_fps",
        "src.modules.zero_sensitivity",
        "src.modules.game_shortcut",
        "src.modules.reg_unlock_fov",

        # 其他可能需要的模块
        "win32api",  # Windows API支持
        "win32con",
        "win32gui",
        "colorama",  # 日志颜色支持
        "ctypes",  # 底层API支持
        "re",  # 正则表达式
        "enum",
        "argparse",

    ]


def copy_config_files(dist_path):
    """复制配置文件到输出目录"""
    config_files = [
        "README.md",
        "LICENSE"
    ]

    print("\n复制配置文件...")
    for file in config_files:
        src = os.path.join(project_root, file)
        dst = os.path.join(dist_path, file)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"已复制: {file}")


if __name__ == "__main__":
    # 检查是否在项目根目录运行
    if not os.path.exists("src") or not os.path.exists("resources"):
        print("请在项目根目录运行此脚本!")
        sys.exit(1)

    # 执行构建
    success = build_executable()

    # 等待用户确认
    if success:
        print("\n构建完成! 按 Enter 键退出...")
    else:
        print("\n构建失败! 按 Enter 键退出...")

    input()
