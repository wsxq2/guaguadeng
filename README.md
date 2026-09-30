# 刮刮登

四人纸牌游戏，使用四种花色的 1～10 点牌，共 40 张。
游戏的完整规则见 [Rules.md](Rules.md)。

项目正在重写：旧版 CLI 和 PySide6 界面已归档，新实现已完成无界面游戏核心，可通过 Python API 完成连续对局；新 GUI 和交互式启动入口尚未实现。
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
运行测试（标准库 unittest，无额外依赖）：

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

测试覆盖与约定见 [测试说明](tests/README.md)，后续计划见 [开发说明](docs/development.md)。

## 使用新核心

安装可编辑包后，可以用随机合法出牌运行一局（仅演示 API，不是 AI 策略）：

```python
import random
from guaguadeng.engine import GameEngine
from guaguadeng.domain.state import Phase
from guaguadeng.domain.rules import legal_plays

engine = GameEngine(random.Random(42))
engine.start_next_game()
choice_rng = random.Random(7)
while engine.snapshot().phase is Phase.PLAYING:
    state = engine.snapshot()
    player_id = state.round.next_player_id
    choices = legal_plays(state.players[player_id].hand, state.round)
    result = engine.submit_play(player_id, choice_rng.choice(choices))
    assert result.is_valid

print([(p.name, p.score) for p in engine.snapshot().players])
```

`engine.start_next_game()` 保留积分并轮庄；`engine.end_session()` 结束本场；
`engine.start_session()` 开始全新一场，积分重置。接口约定见 [开发说明](docs/development.md)。
