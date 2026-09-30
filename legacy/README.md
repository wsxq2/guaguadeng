# 旧版实现

此目录保留迁移前的源码、Qt Designer 文件、依赖清单和原始需求。
源码未作逻辑修改；其行为不一定符合最新的 `../Rules.md`。

从项目根目录运行：

```bash
python legacy/game_cli.py
python -m pip install -r legacy/requirements.txt
python legacy/game_gui.py
```

CLI 无第三方依赖；GUI 需要 PySide6。直接执行脚本可保持旧版同目录导入方式。
GUI 日志 `game_gui.log` 写入启动时的工作目录，已由 Git 忽略。
不要使用 `python -m legacy.game_gui` 启动旧版。
