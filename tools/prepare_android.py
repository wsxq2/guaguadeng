"""生成独立部署目录，避免将 legacy、测试和虚拟环境打入 APK。"""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
target = root / 'build' / 'android-preview'
target.mkdir(parents=True, exist_ok=True)
package = target / 'guaguadeng'
if package.exists():
    shutil.rmtree(package)
shutil.copytree(root / 'src' / 'guaguadeng', package,
                ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
(target / 'main.py').write_text(
    'from guaguadeng.ui.preview import main\n\n'
    'if __name__ == "__main__":\n    raise SystemExit(main())\n', encoding='utf-8')
print(target)
