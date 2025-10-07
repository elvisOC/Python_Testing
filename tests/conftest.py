# conftest.py
import pytest
import copy
from flask import Flask
from server import app
import io
import json

@pytest.fixture
def fake_clubs():
    return [
        {"name": "Test Club", "email": "test@club.com", "points": "15"},
        {"name": "Other Club", "email": "other@club.com", "points": "5"}
    ]

@pytest.fixture
def fake_competitions():
    return [
        {"name": "Spring Festival", "date": "2099-01-01 10:00:00", "numberOfPlaces": "20"}
    ]

@pytest.fixture(autouse=True)
def disable_json_writes(monkeypatch):
    monkeypatch.setattr("server.saveClubs", lambda data: None)
    monkeypatch.setattr("server.saveCompetitions", lambda data: None)


@pytest.fixture
def client(monkeypatch, fake_clubs, fake_competitions):
    clubs_copy = copy.deepcopy(fake_clubs)
    comps_copy = copy.deepcopy(fake_competitions)

    monkeypatch.setattr("server.clubs", clubs_copy)
    monkeypatch.setattr("server.competitions", comps_copy)

    def fake_render_template(template_name, **context):
        return f"{template_name} - {context}"
    monkeypatch.setattr("server.render_template", fake_render_template)

    app.testing = True
    with app.test_client() as c:
        yield c, clubs_copy, comps_copy


@pytest.fixture
def unit_test_env(monkeypatch):
    clubs = [{"name": "Unit Club", "email": "unit@club.com", "points": "15"}]
    competitions = [{"name": "Unit Comp", "date": "2099-01-01 10:00:00", "numberOfPlaces": "10"}]

    monkeypatch.setattr("server.clubs", copy.deepcopy(clubs))
    monkeypatch.setattr("server.competitions", copy.deepcopy(competitions))

    def fake_render_template(template_name, **context):
        return {"template": template_name, "context": context}

    monkeypatch.setattr("server.render_template", fake_render_template)
    return copy.deepcopy(clubs), copy.deepcopy(competitions)


class NonClosingStringIO(io.StringIO):
    def close(self):
        pass 

@pytest.fixture
def fake_open(monkeypatch):
    buffers = {}

    def _fake_open(file, mode='r', encoding=None):
        buf = NonClosingStringIO()
        buffers[file] = buf
        return buf

    monkeypatch.setattr("builtins.open", _fake_open)
    return buffers
