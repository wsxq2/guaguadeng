# 刮刮登

四人纸牌游戏，使用四种花色的 1～10 点牌，共 40 张。
游戏的完整规则见 [Rules.md](Rules.md)。

项目正在重写：旧版 CLI 和 PySide6 界面已归档，新实现已完成无界面游戏核心，可通过 Python API 完成连续对局；已新增正式 QML 牌桌，支持真人对战三个随机 AI、结算和连续对局。
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

此命令只安装新包，不安装旧版或启动游戏。新界面已确定采用 PySide6 + QML / Qt Quick，可通过 `python -m pip install -e ".[ui]"` 安装可选界面依赖。
运行测试（标准库 unittest，无额外依赖）：

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

测试覆盖与约定见 [测试说明](tests/README.md)，后续计划见 [开发说明](docs/development.md)。

## 使用新核心

安装可编辑包后，可以用随机合法出牌运行一局（采用基础随机策略，不包含智能评估）：

```python
import random
from guaguadeng.engine import GameEngine
from guaguadeng.domain.state import Phase
from guaguadeng.domain.rules import legal_plays
from guaguadeng.domain.observation import observe
from guaguadeng.strategies import RandomStrategy

engine = GameEngine(random.Random(42))
engine.start_next_game()
strategies = [RandomStrategy(random.Random(i)) for i in range(4)]
while engine.snapshot().phase is Phase.PLAYING:
    state = engine.snapshot()
    player_id = state.round.next_player_id
    observation = observe(state, player_id)
    choices = legal_plays(observation.hand, observation.current_round)
    chosen = strategies[player_id].choose_play(observation, choices)
    result = engine.submit_play(player_id, chosen)
    assert result.is_valid

print([(p.name, p.score) for p in engine.snapshot().players])
```

`engine.start_next_game()` 保留积分并轮庄；`engine.end_session()` 结束本场；
`engine.start_session()` 开始全新一场，积分重置。接口约定见 [开发说明](docs/development.md)。

## QML 牌桌 / Android

```bash
PYTHONPATH=src python -m guaguadeng.ui.app
```

需安装 UI 可选依赖。点击开始游戏，你位于南侧，其他三人为随机 AI；可选牌、提示、出牌、续局及结束本场。窄屏或低高度下可滚动牌桌，手牌可左右滑动。原选牌验证页仍可通过 `python -m guaguadeng.ui.preview` 启动。Android 打包见 [Android 说明](docs/android.md)；验证页已真机通过，正式牌桌尚待重新打包验收。
