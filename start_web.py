#!/usr/bin/env python3
"""
AI虚拟伴侣系统启动脚本
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        sys.exit(1)

def check_dependencies():
    """检查并安装依赖"""
    web_requirements = Path(__file__).parent / "requirements.txt"

    if web_requirements.exists():
        print("正在检查Web应用依赖...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(web_requirements)
            ], check=True, capture_output=True)
            print("Web应用依赖检查完成")
        except subprocess.CalledProcessError as e:
            print(f"安装Web应用依赖失败: {e}")
            return False
    return True

def start_web_app():
    """启动Web应用"""
    web_dir = Path(__file__).parent
    app_path = web_dir / "start.py"

    if not app_path.exists():
        print(f"错误: 找不到Web应用文件 {app_path}")
        return False

    print("正在启动AI虚拟伴侣Web应用...")
    print("Web应用地址: http://localhost:5000")
    print("聊天界面地址: http://localhost:5000/chat")
    print("=" * 50)

    try:
        # 切换到core目录并启动应用
        os.chdir(web_dir)
        subprocess.run([sys.executable, "start.py"])
    except KeyboardInterrupt:
        print("\n应用已停止")
    except Exception as e:
        print(f"启动Web应用失败: {e}")
        return False

    return True

def show_banner():
    """显示启动横幅"""
    banner = """
    ========================================================
                    AI虚拟伴侣系统
                   智能对话 - 情感交互
    ========================================================
    特性:
    - 基于大语言模型的智能对话
    - 多种人格状态系统
    - Web界面实时交互
    - 情感状态动态变化
    
    默认状态: 温柔模式 (轻微依赖等级1)
    ========================================================
    """
    print(banner)

def main():
    """主函数"""
    show_banner()

    # 检查Python版本
    check_python_version()

    # 检查依赖
    print("正在检查系统依赖...")
    if not check_dependencies():
        print("依赖检查失败，请手动安装依赖")
        sys.exit(1)

    # 启动Web应用
    try:
        start_web_app()
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()