import sys
import types
pyperclip = types.SimpleNamespace(paste=lambda: "", copy=lambda x: None)
sys.modules.setdefault("pyperclip", pyperclip)

# Ensure real webio module is loaded
sys.modules.pop('webio', None)

selenium = types.ModuleType('selenium')
webdriver_mod = types.ModuleType('webdriver')
webdriver_mod.Chrome = lambda *a, **k: None
chrome_mod = types.ModuleType('chrome')
service_mod = types.ModuleType('service')
service_mod.Service = object
wcm_mod = types.ModuleType('wcm')
wcm_mod.ChromeDriverManager = object
sys.modules['selenium'] = selenium
sys.modules['selenium.webdriver'] = webdriver_mod
sys.modules['selenium.webdriver.chrome'] = chrome_mod
sys.modules['selenium.webdriver.chrome.service'] = service_mod
sys.modules['webdriver_manager.chrome'] = wcm_mod

import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import importlib
webio = importlib.import_module('webio')
from unittest.mock import MagicMock, patch


def test_load_speakers_text():
    driver = MagicMock()
    with patch('pyperclip.paste', return_value='csvdata'):
        result = webio.load_speakers_text(driver, 'http://site')
    driver.get.assert_called_with('http://site/tab/speaker/')
    driver.find_element.assert_called()
    assert result == 'csvdata'


def test_load_teams_ranks_text():
    driver = MagicMock()
    with patch('pyperclip.paste', return_value='csv'):
        result = webio.load_teams_ranks_text(driver, 'u', '1')
    driver.get.assert_called()
    assert result == 'csv'


def test_load_teams_debates_text():
    driver = MagicMock()
    with patch('pyperclip.paste', return_value='csv'):
        result = webio.load_teams_debates_text(driver, 'u', '1')
    driver.get.assert_called()
    assert result == 'csv'


def test_export_file(tmp_path):
    file = tmp_path / 'f.txt'
    webio.export_file(str(file), 'hello')
    assert file.read_text(encoding='utf-8') == 'hello'


def test_download_whole_tournament(monkeypatch):
    mock_driver = MagicMock()
    monkeypatch.setattr(webio, 'webdriver', MagicMock(Chrome=MagicMock(return_value=mock_driver)))
    monkeypatch.setattr(webio, 'load_speakers_text', lambda d,u: 'spk')
    monkeypatch.setattr(webio, 'load_teams_ranks_text', lambda d,u,r: 'rank')
    monkeypatch.setattr(webio, 'load_teams_debates_text', lambda d,u,r: 'deb')
    exports = []
    monkeypatch.setattr(webio, 'export_file', lambda n,c: exports.append((n,c)))
    webio.download_whole_tournament('url', br_rundi=1)
    assert ('tournament_files/speakers.csv', 'spk') in exports
