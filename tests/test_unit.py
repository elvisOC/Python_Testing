import io
import json
import pytest
from server import saveClubs, saveCompetitions

class NonClosingStringIO(io.StringIO):
    def close(self):
        pass 

def test_saveClubs_writes_correct_json(monkeypatch):
    clubs = [{"name": "Test Club", "email": "test@club.com", "points": "10"}]
    buffer = NonClosingStringIO()

    def fake_open(file, mode='r', encoding=None):
        assert file == 'clubs.json'
        assert mode == 'w'
        return buffer

    monkeypatch.setattr("builtins.open", fake_open)

    saveClubs(clubs)
    buffer.seek(0)
    data = json.loads(buffer.getvalue())
    assert "clubs" in data
    assert data["clubs"][0]["name"] == "Test Club"

def test_saveCompetitions_writes_correct_json(monkeypatch):
    competitions = [{"name": "Test Comp", "numberOfPlaces": "20"}]
    buffer = NonClosingStringIO()

    def fake_open(file, mode='r', encoding=None):
        assert file == 'competitions.json'
        assert mode == 'w'
        return buffer

    monkeypatch.setattr("builtins.open", fake_open)

    saveCompetitions(competitions)
    buffer.seek(0)
    data = json.loads(buffer.getvalue())
    assert "competitions" in data
    assert data["competitions"][0]["numberOfPlaces"] == "20"
