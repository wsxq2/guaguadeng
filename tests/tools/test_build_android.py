import configparser
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('android_builder', Path(__file__).resolve().parents[2]/'tools/build_android.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class AndroidBuildTests(unittest.TestCase):
    def test_proxy_preserves_existing_and_explicit_update_backs_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'gradle.properties'
            original = 'org.gradle.jvmargs=-Xmx2g\nsystemProp.http.proxyHost=old\n'
            p.write_text(original)
            with patch.dict('os.environ', {'HTTPS_PROXY': 'http://new:7890'}):
                self.assertFalse(builder.configure_proxy(p))
            self.assertEqual(p.read_text(), original)
            builder.configure_proxy(p, 'http://new:7890')
            self.assertIn('org.gradle.jvmargs=-Xmx2g', p.read_text())
            self.assertIn('systemProp.https.proxyHost=new', p.read_text())
            self.assertEqual(p.with_name(p.name+'.before-guaguadeng').read_text(), original)
            builder.configure_proxy(p, disabled=True)
            self.assertNotIn('proxyHost', p.read_text())
            self.assertIn('org.gradle.jvmargs', p.read_text())

    def test_first_proxy_from_environment_and_reject_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'gradle.properties'
            with patch.dict('os.environ', {'https_proxy': 'http://172.18.208.1:7890'}, clear=True):
                self.assertTrue(builder.configure_proxy(p))
            before = p.read_text()
            with self.assertRaises(ValueError):
                builder.configure_proxy(p, 'http://user:secret@host:7890')
            self.assertEqual(p.read_text(), before)

    def test_spec_pins_versions_and_preserves_other_options(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'buildozer.spec'
            p.write_text('[app]\nrequirements = python3\norientation = portrait\nversion = 0.2\n[buildozer]\n')
            builder.patch_spec(p, Path('/sdk'), Path('/ndk'), 'landscape,portrait')
            first = p.read_text()
            builder.patch_spec(p, Path('/sdk'), Path('/ndk'), 'landscape,portrait')
            self.assertEqual(first, p.read_text())
            config = configparser.ConfigParser()
            config.read(p)
            self.assertIn('hostpython3==3.11.9', config['app']['requirements'])
            self.assertEqual(config['app']['version'], '0.2')
            self.assertEqual(config['buildozer']['build_dir'], '.buildozer-py311')
