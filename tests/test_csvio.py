import types, sys
def transl(s, lang="sr"):
    mapping = {"Н":"N","н":"n","и":"i","к":"k","о":"o","л":"l","а":"a","ћ":"c","č":"c"}
    return "".join(mapping.get(ch,ch) for ch in s)
cyr=types.SimpleNamespace(to_latin=transl)
sys.modules.setdefault("cyrtranslit", cyr)
import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import csvio
import os


def test_clean_name():
    assert csvio.clean_name('Никола Николић') == 'nikola nikolic'


def test_load_debater_elo(tmp_path):
    file = tmp_path / 'elo.csv'
    file.write_text('John_Doe 1200 3\nJane_Smith 1100 4\n', encoding='utf-8')
    result = csvio.load_debater_elo(str(file))
    assert result['john_doe'] == (1200.0, 3)
    assert result['jane_smith'] == (1100.0, 4)


def test_load_debater_elo_alt(tmp_path):
    file = tmp_path / 'elo_alt.csv'
    file.write_text('John Doe 1200 3\nJane Smith 1100 4\n', encoding='utf-8')
    result = csvio.load_debater_elo(str(file), alt_mod=True)
    assert result['john doe'] == (1200.0, 3)
    assert result['jane smith'] == (1100.0, 4)


def test_load_teams_participants(tmp_path):
    file = tmp_path / 'teams.csv'
    row = '\t'.join(['1', 'John Doe', 'TeamA'] + ['x'] * 8) + '\n'
    file.write_text('header\n' + row, encoding='utf-8')
    result = csvio.load_teams_participants(str(file), speaker_csv_mode=True)
    assert result['john doe'] == 'TeamA'


def test_load_team_ranks(tmp_path):
    file = tmp_path / 'ranks.csv'
    file.write_text('header\nTeamA\tCollege\t1st\n', encoding='utf-8')
    result = csvio.load_team_ranks(str(file))
    assert result['TeamA'] == 1


def test_convert_rank():
    assert csvio.convert_rank('3rd') == 3


def test_load_debates(tmp_path):
    file = tmp_path / 'debates.csv'
    file.write_text('header\n1\tTeamA\tTeamB\tTeamC\tTeamD\n', encoding='utf-8')
    result = csvio.load_debates(str(file))
    assert {'TeamA', 'TeamB', 'TeamC', 'TeamD'} in result


def test_export_debater_elo(tmp_path):
    data = {'john': (1000.0, 1)}
    file = tmp_path / 'out.csv'
    csvio.export_debater_elo(data, str(file))
    content = file.read_text(encoding='utf-8').strip()
    assert content == 'john 1000.0 1'


def test_uvezi_spikere(tmp_path):
    file = tmp_path / 'spk.csv'
    row = ['1', 'John Doe', 'x', 'TeamA'] + ['70'] * 5 + ['75']
    file.write_text('header\n' + '\t'.join(row) + '\n', encoding='utf-8')
    result = csvio.uvezi_spikere(str(file), no_of_rounds=5)
    assert result['john doe'][0] == 'TeamA'
    assert result['john doe'][1] == [70] * 5
    assert result['john doe'][2] == 75.0


def test_add_debaters(tmp_path):
    data = {}
    file = tmp_path / 'add.csv'
    file.write_text('header\n1\tJohn Doe\tTeamA\n', encoding='utf-8')
    csvio.add_debaters(data, str(file))
    assert 'john doe' in data
    assert data['john doe'] == (1000, 0)
