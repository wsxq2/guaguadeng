#!/usr/bin/env python3
"""
刮刮登纸牌游戏 - 启动器
让用户选择CLI或GUI版本
"""

import sys
import os

def show_menu():
    """显示菜单"""
    print("=" * 50)
    print("🎮 欢迎来到刮刮登纸牌游戏！")
    print("=" * 50)
    print()
    print("请选择游戏版本：")
    print("1. 命令行版本 (CLI)")
    print("2. 图形界面版本 (GUI)")
    print("3. 退出")
    print()

def main():
    """主函数"""
    while True:
        show_menu()
        try:
            choice = input("请输入您的选择 (1-3): ").strip()
            
            if choice == '1':
                print("\n启动命令行版本...")
                os.system(f"{sys.executable} game_cli.py")
                
            elif choice == '2':
                print("\n启动图形界面版本...")
                try:
                    import PySide6
                    os.system(f"{sys.executable} game_gui.py")
                except ImportError:
                    print("❌ 错误：未安装PySide6，无法启动GUI版本")
                    print("请运行: pip install PySide6")
                    input("\n按回车键继续...")
                    
            elif choice == '3':
                print("\n谢谢游玩！再见！ 👋")
                break
                
            else:
                print("\n❌ 无效选择，请输入 1、2 或 3")
                input("按回车键继续...")
                
        except KeyboardInterrupt:
            print("\n\n谢谢游玩！再见！ 👋")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            input("按回车键继续...")

if __name__ == "__main__":
    main()