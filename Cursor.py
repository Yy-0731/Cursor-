#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time

# 检查 Python 版本
if sys.version_info[0] < 3:
    print("错误: 此脚本需要 Python 3")
    sys.exit(1)

import json
import os
from pathlib import Path
import argparse
import hashlib
import uuid
import random
import string
import subprocess

def get_config_path():
    """根据不同操作系统返回配置文件路径"""
    if sys.platform == "darwin":  # macOS
        base_path = Path("~/Library/Application Support/Cursor/User/globalStorage")
    elif sys.platform == "win32":  # Windows
        base_path = Path(os.environ.get("APPDATA", "")) / "Cursor/User/globalStorage"
    else:  # Linux 和其他类Unix系统
        base_path = Path("~/.config/Cursor/User/globalStorage")
    
    return Path(os.path.expanduser(str(base_path))) / "storage.json"

CONFIG_PATH = get_config_path()

def is_cursor_running():
    """检查 Cursor 是否正在运行（不依赖第三方库）"""
    try:
        if sys.platform == "win32":
            # Windows
            output = subprocess.check_output('tasklist', shell=True, stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
            return any(proc.lower().startswith('cursor') for proc in output.split('\n'))
        else:
            # Unix-like systems (Linux, macOS)
            output = subprocess.check_output(['ps', 'aux'], stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
            return any('cursor' in line.lower() for line in output.split('\n'))
    except subprocess.SubprocessError:
        return False  # 如果执行命令失败，假设进程未运行
    except Exception as e:
        print(f"检查进程时出错: {str(e)}")
        return False

def check_cursor_process(func):
    """装饰器：检查 Cursor 进程"""
    def wrapper(*args, **kwargs):
        if is_cursor_running():
            print("警告: 检测到 Cursor 正在运行！")
            print("请先关闭 Cursor 再执行操作，否则修改可能会被覆盖。")
            choice = input("是否继续？(y/N): ")
            if choice.lower() != 'y':
                return
        return func(*args, **kwargs)
    return wrapper

def show_config():
    """显示当前配置文件的内容"""
    try:
        if not CONFIG_PATH.exists():
            print(f"配置文件不存在: {CONFIG_PATH}")
            return
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"读取配置文件时出错: {str(e)}")

def get_value(key):
    """获取指定键的值"""
    try:
        if not CONFIG_PATH.exists():
            print(f"配置文件不存在: {CONFIG_PATH}")
            return
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            value = data.get(key)
            if value is None:
                print(f"未找到键: {key}")
            else:
                print(json.dumps(value, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"读取配置文件时出错: {str(e)}")

def get_machine_ids():
    """获取机器 ID 信息"""
    try:
        if not CONFIG_PATH.exists():
            print(f"配置文件不存在: {CONFIG_PATH}")
            return
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            mac_id = data.get("telemetry.macMachineId", "未设置")
            machine_id = data.get("telemetry.machineId", "未设置")
            print(f"Mac机器ID: {mac_id}")
            print(f"机器ID: {machine_id}")
    except Exception as e:
        print(f"读取配置文件时出错: {str(e)}")

@check_cursor_process
def set_value(key, value):
    """设置指定键的值"""
    try:
        data = {}
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        # 尝试将输入的值转换为 JSON
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            # 如果不是有效的 JSON，就按字符串处理
            pass
        
        data[key] = value
        
        # 确保目录存在
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"已设置 {key} = {value}")
    except Exception as e:
        print(f"设置值时出错: {str(e)}")

@check_cursor_process
def reset_machine_ids():
    """重置机器 ID"""
    try:
        if not CONFIG_PATH.exists():
            print(f"配置文件不存在: {CONFIG_PATH}")
            return
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 删除遥测 ID
        data.pop("telemetry.macMachineId", None)
        data.pop("telemetry.machineId", None)
        
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("已成功重置机器 ID")
    except Exception as e:
        print(f"重置机器 ID 时出错: {str(e)}")

@check_cursor_process
def generate_random_machine_ids():
    """生成随机的机器 ID"""
    try:
        if not CONFIG_PATH.exists():
            print(f"配置文件不存在: {CONFIG_PATH}")
            return
        
        # 生成随机字符串并计算其哈希值
        def generate_random_hash():
            random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            random_str += str(uuid.uuid4())  # 添加 UUID 增加随机性
            return hashlib.sha256(random_str.encode()).hexdigest()
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 生成新的 ID
        data["telemetry.macMachineId"] = generate_random_hash()
        data["telemetry.machineId"] = generate_random_hash()
        
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("已生成新的机器 ID：")
        print(f"Mac机器ID: {data['telemetry.macMachineId']}")
        print(f"机器ID: {data['telemetry.machineId']}")
    except Exception as e:
        print(f"生成机器 ID 时出错: {str(e)}")

def kill_cursor_processes():
    """终止所有 Cursor 相关进程"""
    try:
        if sys.platform == "win32":
            # Windows
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'Cursor.exe'], 
                             check=False, 
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE)
                subprocess.run(['taskkill', '/F', '/IM', 'cursor.exe'], 
                             check=False,
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE)
            except subprocess.SubprocessError:
                print("无法找到 Cursor 进程或没有权限终止进程")
        else:
            # Unix-like systems (Linux, macOS)
            try:
                # 使用 pgrep 查找进程
                pids = subprocess.check_output(['pgrep', '-i', 'cursor'], 
                                            stderr=subprocess.DEVNULL).decode().split()
                for pid in pids:
                    try:
                        os.kill(int(pid), 15)  # SIGTERM
                        time.sleep(0.1)
                        try:
                            os.kill(int(pid), 0)  # 检查进程是否还存在
                            os.kill(int(pid), 9)  # SIGKILL
                        except ProcessLookupError:
                            pass  # 进程已经终止
                    except ProcessLookupError:
                        continue  # 跳过已经不存在的进程
            except subprocess.CalledProcessError:
                print("未找到 Cursor 进程")
            except PermissionError:
                print("没有权限终止进程")
        
        print("已尝试终止所有 Cursor 进程")
    except Exception as e:
        print(f"终止进程时出错: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='管理 Cursor 配置文件的命令行工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # show 命令
    subparsers.add_parser('show', help='显示当前配置文件的内容')

    # get 命令
    get_parser = subparsers.add_parser('get', help='获取指定键的值')
    get_parser.add_argument('key', help='键名')

    # set 命令
    set_parser = subparsers.add_parser('set', help='设置指定键的值')
    set_parser.add_argument('key', help='键名')
    set_parser.add_argument('value', help='值')

    # 机器 ID 相关命令
    subparsers.add_parser('ids', help='显示机器 ID 信息')
    subparsers.add_parser('reset-ids', help='重置机器 ID')
    subparsers.add_parser('random-ids', help='生成随机机器 ID')

    # 添加 kill 命令
    subparsers.add_parser('kill', help='终止所有 Cursor 进程')

    args = parser.parse_args()

    if args.command == 'show':
        show_config()
    elif args.command == 'get':
        get_value(args.key)
    elif args.command == 'set':
        set_value(args.key, args.value)
    elif args.command == 'ids':
        get_machine_ids()
    elif args.command == 'reset-ids':
        reset_machine_ids()
    elif args.command == 'random-ids':
        generate_random_machine_ids()
    elif args.command == 'kill':
        kill_cursor_processes()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()