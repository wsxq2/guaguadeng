# Android 最小验证版

目标：用同一份 Python 核心和 QML 页面验证显示卡牌、触摸选牌、调用领牌规则。
当前页面不执行完整对局。桌面无显示测试通过，不代表 Android 真机已验证。

## 桌面运行

```bash
python -m pip install -e '.[ui]'
python -m guaguadeng.ui.preview
```

使用已有虚拟环境，无需先安装项目：

```bash
PYTHONPATH=src .venv/bin/python -m guaguadeng.ui.preview
```

选择两张 6 后验证应通过；再选择 7 后应提示点数必须相同。
卡牌支持点击取消，手牌区域在窄屏时可以横向滑动。

## 准备 Android 部署目录

在项目根目录执行：

```bash
python tools/prepare_android.py
cd build/android-preview
```

脚本仅复制新包和 QML，生成部署工具要求的 `main.py`，不复制旧版、测试或虚拟环境。
重跑会刷新该目录中的 `guaguadeng/` 包。生成的构建目录不提交版本库。

## 已验证的构建环境

2026-09-30，用户确认最小验证版 Android 构建成功。构建成功与真机运行验收分开记录，当前尚未收到真机验收结果。

本次构建相关版本与配置：

- Windows + WSL2，Ubuntu 22.04。
- 主机构建环境为项目 `.venv`，Python 3.10、PySide6 6.10.1。
- Android wheels：PySide6 / Shiboken6 6.10.1，`cp311`、`android_aarch64`；目标端使用 CPython 3.11，不等于主机虚拟环境版本。
- NDK：r27c；SDK 由对应版本的 Qt 下载脚本准备。
- JDK：由 11 切换到 17，解决 Android Gradle 插件的版本要求。
- 构建日志中的 Gradle 为 8.14.3，Android Gradle 插件为 8.11.0。

部署工具的一般用法参见 [Qt 官方 Android 部署说明](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-android-deploy.html)。以下记录本次成功流程，不代表任意版本组合均兼容。

## 准备 SDK、NDK 和 Android wheels

在已激活项目虚拟环境的终端中，克隆并切换到匹配的 Qt for Python 版本：

```bash
cd ~
git clone https://code.qt.io/pyside/pyside-setup
cd pyside-setup
git switch --detach v6.10.1
python -m pip install -r tools/cross_compile_android/requirements.txt
pip install -r /home/wsxq2/guaguadeng/.venv/lib/python3.10/site-packages/PySide6/scripts/requirements-android.txt
python tools/cross_compile_android/main.py \
  --download-only \
  --skip-update \
  --auto-accept-license
```

已有仓库时跳过克隆。`--detach` 检出版本标签是正常状态。最后一个参数会自动接受下载工具链所需的许可。

本次路径为：

```text
~/.pyside6_android_deploy/android-sdk
~/.pyside6_android_deploy/android-ndk/android-ndk-r27c
```

将以下两个文件保存到项目根目录的 `android-deploy/` 中：

- [PySide6 Android ARM64 wheel](https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.10.1-6.10.1-cp311-cp311-android_aarch64.whl)
- [Shiboken6 Android ARM64 wheel](https://download.qt.io/official_releases/QtForPython/shiboken6/shiboken6-6.10.1-6.10.1-cp311-cp311-android_aarch64.whl)

`.whl` 是已构建的 Python 发行包，`src` 目录提供的是源码。wheel 链接在官方目录的文件列表中，不在 `src` 子目录内。直接下载无需 `qtpip`；这些 Android 包交给部署工具处理，不要安装到 Linux 虚拟环境中，也不能替换为桌面 wheel。

## 配置 JDK 17

```bash
sudo apt update
sudo apt install openjdk-17-jdk

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH="$JAVA_HOME/bin:$PATH"
java -version
javac -version
```

确认两者显示 17，然后在同一终端构建。这些环境变量只影响当前终端及其子进程，不必卸载 Java 11。新开终端时需重新设置，或自行纳入构建环境配置。

## Gradle 代理

本次还为 Gradle 设置了代理。需要代理时，建议把下面配置合并到 WSL 用户目录的 `~/.gradle/gradle.properties`，不要覆盖文件中已有的其他配置。该位置影响当前用户的其他 Gradle 项目；配置项已存在时更新原值，避免重复。

```ini
systemProp.http.proxyHost=172.18.208.1
systemProp.http.proxyPort=7890
systemProp.https.proxyHost=172.18.208.1
systemProp.https.proxyPort=7890
systemProp.http.nonProxyHosts=localhost|127.*|[::1]|10.*|192.168.*|172.16.*|172.17.*|172.18.*|172.19.*|172.20.*|172.21.*|172.22.*|172.23.*|172.24.*|172.25.*|172.26.*|172.27.*|172.28.*|172.29.*|172.30.*|172.31.*
```

这是用户本次使用的配置；原始配置文件位置未记录，上述用户级路径为后续复现建议。`172.18.208.1:7890` 是本次环境的代理地址，不是通用固定值。WSL 网络变化或代理服务更换后，需要检查并更新地址，确保 WSL 能访问该端口。`nonProxyHosts` 列出无需代理的本机和内网目标。

不要仅凭终端已设置 `http_proxy` / `https_proxy` 就假定 Gradle 也使用了同一代理；本次对 Gradle 单独配置。无需代理的环境可省略此步骤。

## 执行部署并保存日志

先按前文生成 `build/android-preview/`，激活项目虚拟环境并配置 JDK 17，然后在部署目录执行：

```bash
cd /home/wsxq2/guaguadeng/build/android-preview
set -o pipefail
pyside6-android-deploy \
  --name GuaguadengPreview \
  --wheel-pyside ../../android-deploy/PySide6-6.10.1-6.10.1-cp311-cp311-android_aarch64.whl \
  --wheel-shiboken ../../android-deploy/shiboken6-6.10.1-6.10.1-cp311-cp311-android_aarch64.whl \
  --ndk-path /home/wsxq2/.pyside6_android_deploy/android-ndk/android-ndk-r27c \
  --sdk-path /home/wsxq2/.pyside6_android_deploy/android-sdk \
  2>&1 | tee deploy.log
```

换机器时调整绝对路径。`pipefail` 避免管道只反映 `tee` 的退出状态；同时仍应检查日志末尾和实际 APK 产物。生成的 `pysidedeploy.spec` 可保留复用。运行成功不代表 QML 资源和所有插件在真机上一定正常，需继续安装测试。

## 本次排错记录

| 现象 | 原因与处理 |
| --- | --- |
| `No module named jinja2` | 安装 `tools/cross_compile_android/requirements.txt` |
| `No module named packaging` | 子目录清单未包含该导入所需依赖，另执行 `python -m pip install packaging` |
| 部署工具提示缺少 `pkginfo` | 按工具提示安装当前 PySide6 所附的 `requirements-android.txt`，补齐部署工具依赖 |
| pip 提示 `generate-parameter-library-py` 缺少其他依赖 | 是已有环境的依赖冲突提示；本次日志同时显示目标依赖安装成功，不等于下载脚本依赖安装失败 |
| `qtpip: command not found` | 它是独立工具，本次通过直接下载 Android wheels 绕过 |
| `NoneType` 与字符串不能进行 `/` 路径拼接 | 本地部署工具读取已有配置时可能跳过 NDK 初始化；NDK 实际存在，显式传 `--ndk-path` 绕过，无需重下 |
| `Android Gradle plugin requires Java 17 ... using Java 11` | 安装 JDK 17，并在部署终端设置 `JAVA_HOME` 和 `PATH` |
| `No project file found` | 当前没有 Qt 项目文件，工具继续部署；不是本次失败根因 |
| `No setup.py/pyproject.toml used` | 当前使用复制源码的部署目录，并非该提示导致失败 |
| `CalledProcessError` / `gradlew failed` | 是子命令失败汇总；向前查找 `What went wrong` 才能定位原因 |

Gradle 开头的“Java 24 support”只是版本特性介绍，不表示当前使用 Java 24。“不兼容 Gradle 9.0”是未来升级警告，不是本次 Java 11 错误的原因。

## 下载量和构建资源

首次部署会下载 SDK/NDK、Gradle、Android 插件与传递依赖、Python 构建组件等，大量下载是正常的。下载量不等于 APK 大小；后续构建通常可复用缓存，不要为了普通重试删除工具链或构建缓存。

本次机器 CPU 和内存较紧张，用户关闭飞书、Chrome、Docker Desktop 等应用后再构建，以释放资源。

用户观察到：直接在独立 WSL2 终端中执行，似乎比在 VS Code 集成终端中更快。这是本次环境的体验，尚未进行相同条件下的计时对比；VS Code 的 WSL 终端也可能运行在同一个 WSL2 环境，不能据此认定终端类型本身决定构建性能。资源紧张时可先关闭不必要应用，使用独立 WSL 终端进行构建。

## 验证进度与后续

- 桌面 PySide6 6.10.1：选牌和规则桥接测试通过。
- 无显示测试检查了 840×480、360×640、640×360，未产生 QML 警告。
- 用户已确认 Android 构建成功；不再将 SDK/NDK、wheels 或 JDK 配置列为未解决阻塞。
- 待真机验收：安装启动、中文和花色、横竖屏、触摸与滑动、系统安全区域、后台恢复。
- 本页面不执行完整对局，没有持续 AI 定时任务和存档；这些属于完整界面阶段。
