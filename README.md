# 刮刮登

四人纸牌游戏，使用四种花色的 1～10 点牌，共 40 张。
游戏的完整规则见 [Rules.md](Rules.md)。

项目正在重写：旧版 CLI 和 PySide6 界面已归档，新实现目前仅建立包结构，尚无可运行的新游戏入口。
旧版行为不完全符合最新规则。

## 目录

```text
guaguadeng/
├── Rules.md                 # 游戏规则
├── README.md
├── pyproject.toml           # 新包配置
├── src/
│   └── guaguadeng/          # 新实现
├── tests/                  # 新实现的测试
├── docs/
│   └── development.md      # 职责规划与后续步骤
└── legacy/                 # 旧源码、UI 文件、依赖和历史需求
```

## 运行旧版

以下命令均在项目根目录执行：

```bash
# CLI：无需第三方依赖
python legacy/game_cli.py

# GUI：安装旧版依赖后启动
python -m pip install -r legacy/requirements.txt
python legacy/game_gui.py
```

也可使用已有虚拟环境中的 `.venv/bin/python` 替代 `python`。
旧版具体说明见 [legacy/README.md](legacy/README.md)。

## 开发新实现

新实现使用 Python 3.10 及以上版本，核心暂不引入第三方运行依赖。
在虚拟环境中安装为可编辑包：

```bash
python -m pip install -e .
python -c "import guaguadeng; print(guaguadeng.__file__)"
```

此命令只安装新包，不安装旧版或启动游戏。新界面的技术和依赖尚未确定。
目前还没有自动化测试；后续计划见 [开发说明](docs/development.md)。
