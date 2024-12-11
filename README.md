# Cursor Device ID Changer

这是一个简单的脚本工具，用于修改 Cursor 编辑器的设备 ID。当因频繁切换账号导致设备被锁定时，可以使用此脚本重置设备 ID。

## 功能特点

- 自动生成新的随机设备 ID
- 自动备份原配置文件
- 支持自定义设备 ID
- 无需额外依赖，使用系统内置工具

## 使用方法

1. 下载 `Cursor.sh` 脚本

2.放置在自己管理员终端路径下
比如C:\Windows\System32

3.运行脚本：
```bash
查看设备 ID
Python Cursor.py ids
使用自定义设备 ID
Python Cursor.py random-ids
```
重置id
Python Cursor.py reset-ids

## 注意事项

- 脚本会在修改前自动创建配置文件的备份
- 使用前要先删除machineid文件 ~\AppData\Roaming\Cursor下
- 请确保在运行脚本前关闭 Cursor 编辑器
- 仅支持 window 系统




## 免责声明

本脚本仅供学习和研究使用，使用本脚本可能违反 Cursor 的服务条款。请合理使用，风险自负。
