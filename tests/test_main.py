import sys
import types
pyperclip = types.SimpleNamespace(paste=lambda: "", copy=lambda x: None)
sys.modules.setdefault("pyperclip", pyperclip)
import types, sys
cyr=types.SimpleNamespace(to_latin=lambda s,lang:s)
service_mod=types.ModuleType("service")
service_mod.Service=object
wcm_mod=types.ModuleType("wcm")
wcm_mod.ChromeDriverManager=object
selenium_mod=types.ModuleType("selenium")
webdriver_mod=types.ModuleType("webdriver")
webdriver_mod.Chrome=lambda *a,**k: None
sys.modules.setdefault("cyrtranslit", cyr)
sys.modules.setdefault("selenium", selenium_mod)
csvio_stub = types.SimpleNamespace(load_debater_elo=lambda f:{}, add_debaters=lambda d,f:None, load_teams_participants=lambda f,no_of_rounds=5:{}, uvezi_spikere=lambda f,no_of_rounds=5:{}, load_team_ranks=lambda f,alt_instit=True:{}, load_debates=lambda f:[], export_debater_elo=lambda data,file:None); sys.modules["csvio"] = csvio_stub
webio_stub = types.SimpleNamespace(download_whole_tournament=lambda url,n:None); sys.modules["webio"] = webio_stub
sys.modules.setdefault("selenium.webdriver", webdriver_mod)
sys.modules.setdefault("selenium.webdriver.chrome", types.ModuleType("chrome"))
sys.modules.setdefault("selenium.webdriver.chrome.service", service_mod)
sys.modules.setdefault("webdriver_manager.chrome", wcm_mod)
import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import main
import csvio


def test_generate_pairs_teams():
    ranks = {'A':1, 'B':2, 'C':3, 'D':4}
    debates = [{'A','B','C','D'}]
    result = main.generate_pairs_teams(ranks, debates)
    assert ('A','B') in result
    assert ('A','C') in result
    assert ('C','D') in result


def test_generate_pairs_debaters():
    pairs = [('A','B')]
    speakers = {'alice':'A','bob':'B'}
    result = main.generate_pairs_debaters(pairs, speakers)
    # expecting four combinations
    assert len(result) == 4


def test_calculate_k_factor():
    assert main.calculate_k_factor((1600,3)) == 60


def test_find_partner():
    speakers = {'alice':('Team', [70],70), 'bob':('Team',[60],60)}
    assert main.find_partner('alice', speakers) == 'bob'


def test_apply_speaker_modifier():
    speakers = {'alice':('Team',[70],70),'bob':('Team',[60],60)}
    assert main.apply_speaker_modifier('alice', speakers, True, 1) > 1


def test_calculate_elo():
    pairs = [('alice','bob')]
    elo = {'alice':(1000,0),'bob':(1000,0)}
    spk = {'alice':('A',[70],70),'bob':('B',[60],60)}
    result = main.calculate_elo(pairs, elo, spk, 1)
    assert result['alice'][0] != 1000


def test_enter_tournament(monkeypatch):
    calls = []
    monkeypatch.setattr(main.webio, 'download_whole_tournament', lambda u,r: calls.append('web'))
    monkeypatch.setattr(main.csvio, 'load_debater_elo', lambda f: {})
    monkeypatch.setattr(main.csvio, 'add_debaters', lambda e,f: calls.append('add'))
    monkeypatch.setattr(main.csvio, 'load_teams_participants', lambda f,no_of_rounds: {'a':'A'})
    monkeypatch.setattr(main.csvio, 'uvezi_spikere', lambda f,no_of_rounds: {'a':('A',[70],70)})
    monkeypatch.setattr(main.csvio, 'load_team_ranks', lambda f,alt_instit=True: {'A':1,'B':2})
    monkeypatch.setattr(main.csvio, 'load_debates', lambda f: [{'A','B'}])
    monkeypatch.setattr(main, 'generate_pairs_teams', lambda ranks,debates: [('A','B')])
    monkeypatch.setattr(main, 'generate_pairs_debaters', lambda pairs,st: [('a','b')])
    monkeypatch.setattr(main, 'calculate_elo', lambda pairs,elo,spk,i: {'a':(1000,1)})
    monkeypatch.setattr(main.csvio, 'export_debater_elo', lambda elo,file: calls.append(file))
    main.enter_tournament('url',num_of_rounds=1, spk_file='spk.csv', new_elo_file='elo.csv')
    assert 'web' in calls
