"""Android 验证版打包入口；使用当前 Python 环境，无需修改系统 Java 默认值。"""
import argparse
import configparser
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'build' / 'android-preview'
NON_PROXY = 'localhost|127.*|[::1]|10.*|192.168.*|' + '|'.join(f'172.{i}.*' for i in range(16, 32))


def configure_proxy(path, proxy=None, disabled=False):
    """保留其他 Gradle 设置；自动模式已有代理时不覆盖。"""
    text = path.read_text() if path.exists() else ''
    pattern = r'^\s*systemProp\.(?:http|https)\.(?:proxyHost|proxyPort|nonProxyHosts)\s*[=:].*$'
    if proxy is None and not disabled:
        if re.search(r'^\s*systemProp\.(?:http|https)\.proxyHost\s*[=:]', text, re.M):
            return False
        proxy = os.environ.get('https_proxy') or os.environ.get('HTTPS_PROXY') or os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY')
        if not proxy:
            return False
    lines = []
    if not disabled:
        url = urlsplit(proxy if '://' in proxy else 'http://' + proxy)
        if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password:
            raise ValueError('代理必须为无账号密码的 HTTP(S) 地址，例如 http://172.18.208.1:7890')
        port = url.port or (443 if url.scheme == 'https' else 80)
        lines = [f'systemProp.{scheme}.proxy{key}={value}'
                 for scheme in ('http', 'https')
                 for key, value in (('Host', url.hostname), ('Port', port))]
        lines.append(f'systemProp.http.nonProxyHosts={NON_PROXY}')
    updated = re.sub(pattern, '', text, flags=re.M).rstrip() + '\n'
    updated += '\n'.join(lines) + ('\n' if lines else '')
    if updated == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.with_name(path.name + '.before-guaguadeng').write_text(text)
    path.write_text(updated)
    return True


def patch_spec(path, sdk, ndk, orientation):
    config = configparser.ConfigParser(interpolation=None)
    config.read(path)
    for section in ('app', 'buildozer'):
        if not config.has_section(section):
            config.add_section(section)
    config['app']['requirements'] = 'python3==3.11.9,hostpython3==3.11.9,shiboken6,PySide6'
    config['app']['orientation'] = orientation
    config['app']['android.sdk_path'] = str(sdk)
    config['app']['android.ndk_path'] = str(ndk)
    # 不把日志、部署 recipes 或旧构建目录复制进应用资源。
    excluded = config['app'].get('source.exclude_dirs', '').split(',')
    config['app']['source.exclude_dirs'] = ','.join(dict.fromkeys(
        x.strip() for x in excluded + ['deployment', '.buildozer', '.buildozer-py311'] if x.strip()))
    config['buildozer']['build_dir'] = '.buildozer-py311'
    with path.open('w') as stream:
        config.write(stream)


def java17(explicit):
    candidates = [explicit, os.environ.get('JAVA_HOME'), '/usr/lib/jvm/java-17-openjdk-amd64']
    candidates += [str(p) for p in Path('/usr/lib/jvm').glob('*17*')]
    for candidate in candidates:
        if not candidate:
            continue
        home = Path(candidate)
        if not (home / 'bin' / 'javac').is_file():
            continue
        output = subprocess.run([str(home / 'bin' / 'java'), '-version'], capture_output=True, text=True)
        if output.returncode == 0 and re.search(r'version "17(?:\.|\")', output.stderr + output.stdout):
            return home
    raise ValueError('未找到 JDK 17。请先安装 openjdk-17-jdk，或用 --java-home 指定路径。')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java-home')
    parser.add_argument('--sdk', type=Path, default=Path.home()/'.pyside6_android_deploy/android-sdk')
    parser.add_argument('--ndk', type=Path, default=Path.home()/'.pyside6_android_deploy/android-ndk/android-ndk-r27c')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--proxy', help='明确设置/更新 Gradle HTTP(S) 代理；默认保留已有设置，否则从环境变量读取')
    group.add_argument('--no-proxy', action='store_true', help='移除 Gradle HTTP(S) 代理设置')
    parser.add_argument('--orientation', choices=('landscape,portrait', 'landscape', 'portrait'), default='landscape,portrait')
    parser.add_argument('--prepare-only', action='store_true', help='准备和修正配置，不执行 APK 编译')
    args = parser.parse_args()
    try:
        home = java17(args.java_home)
        if not (args.sdk/'platform-tools/adb').is_file():
            raise ValueError('SDK 无效或缺少 platform-tools，请检查 --sdk')
        if not (args.ndk/'toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-readobj').is_file():
            raise ValueError('NDK 无效，请检查 --ndk（当前脚本面向 Linux/WSL）')
        env = os.environ.copy()
        env['JAVA_HOME'] = str(home)
        env['PATH'] = str(home/'bin') + os.pathsep + env.get('PATH', '')
        # 固定同一个解释器环境的工具，避免调用用户目录中的另一套 PySide6。
        env['PATH'] = str(Path(sys.executable).parent) + os.pathsep + env['PATH']
        props = Path(env.get('GRADLE_USER_HOME', str(Path.home()/'.gradle'))) / 'gradle.properties'
        changed = configure_proxy(props, args.proxy, args.no_proxy)
        print(f'JDK: {home}\nGradle 配置: {props}（{"已更新" if changed else "保留原配置"}）', flush=True)
        subprocess.run([sys.executable, str(ROOT/'tools/prepare_android.py')], check=True)
        spec = TARGET/'buildozer.spec'
        recipes = TARGET/'deployment/recipes'
        if not spec.exists() or not (recipes/'PySide6/__init__.py').exists() or not (recipes/'shiboken6/__init__.py').exists():
            wheels = ROOT/'android-deploy'
            pyside = wheels/'PySide6-6.10.1-6.10.1-cp311-cp311-android_aarch64.whl'
            shiboken = wheels/'shiboken6-6.10.1-6.10.1-cp311-cp311-android_aarch64.whl'
            if not pyside.exists() or not shiboken.exists():
                raise ValueError('首次初始化需要 android-deploy/ 下的两份 6.10.1 Android ARM64 wheels')
            subprocess.run([sys.executable, '-m', 'PySide6.scripts.android_deploy', '--init', '--keep-deployment-files',
                            '--name', 'GuaguadengPreview', '--wheel-pyside', str(pyside),
                            '--wheel-shiboken', str(shiboken), '--ndk-path', str(args.ndk),
                            '--sdk-path', str(args.sdk)], cwd=TARGET, env=env, check=True)
        if not spec.exists() or not (recipes/'PySide6/__init__.py').exists():
            raise ValueError('部署初始化未生成完整配置，请检查上方日志')
        patch_spec(spec, args.sdk.resolve(), args.ndk.resolve(), args.orientation)
        if args.prepare_only:
            print('准备完成，未执行 APK 编译。')
            return 0
        log = TARGET/'deploy-script.log'
        with log.open('w') as stream:
            process = subprocess.Popen([sys.executable, '-m', 'buildozer', 'android', 'debug'],
                                       cwd=TARGET, env=env, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True, errors='replace')
            try:
                for line in process.stdout:
                    print(line, end='', flush=True)
                    stream.write(line)
                    stream.flush()
                code = process.wait()
            except KeyboardInterrupt:
                process.terminate()
                process.wait()
                return 130
        print(f'构建退出码: {code}；日志: {log}')
        if code == 0:
            for apk in TARGET.glob('*.apk'):
                print(f'APK: {apk}')
        return code
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'打包失败: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
