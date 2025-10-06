<<<<<<< HEAD
import pytest
from server import showSummary, clubs, competitions, purchasePlaces, saveClubs, saveCompetitions
from flask import Flask
from datetime import datetime, timedelta
import io
import json

def fake_render_template(template_name, **context):
    return f"{template_name} - {context}"

def test_show_summary_returns_400_for_unknown_email(monkeypatch):
    monkeypatch.setattr("server.clubs", [{"name": "Known", "email": "known@test.com"}])
    monkeypatch.setattr("server.competitions", [{"name": "Comp", "date": "2099-01-01 10:00:00"}])
    monkeypatch.setattr("server.render_template", fake_render_template)

    app = Flask(__name__)
    app.secret_key = "test_secret"

    with app.test_request_context(method="POST", data={"email": "unknown@test.com"}):
        response, status = showSummary()
        assert status == 400
        assert "index.html" in response
        assert "unknown@test.com" not in response

def test_show_summary_returns_200_for_known_email(monkeypatch):
    monkeypatch.setattr("server.clubs", [{"name": "Known", "email": "known@test.com"}])
    monkeypatch.setattr("server.competitions", [{"name": "Comp", "date": "2099-01-01 10:00:00"}])
    monkeypatch.setattr("server.render_template", fake_render_template)

    app = Flask(__name__)
    app.secret_key = "test_secret"

    with app.test_request_context(method="POST", data={"email": "known@test.com"}):
        response = showSummary()
        assert "welcome.html" in response
        assert "Known" in response


@pytest.fixture
def setup_club_comp(monkeypatch):
    clubs = [{"name": "Test Club", "email": "test@club.com", "points": "10"}]
    competitions = [{"name": "Test Competition", "numberOfPlaces": "20"}]
    monkeypatch.setattr("server.clubs", clubs)
    monkeypatch.setattr("server.competitions", competitions)
    monkeypatch.setattr("server.render_template", fake_render_template)
    return clubs, competitions

def test_purchasePlaces_more_than_points_returns_400(setup_club_comp):
    clubs, competitions = setup_club_comp
    app = Flask(__name__)
    app.secret_key = "test_secret"
    with app.test_request_context(method="POST",
                                  data={"club": "Test Club", "competition": "Test Competition", "places": "15"}):
        response, status = purchasePlaces()
        assert status == 400
        assert "Vous n'avez pas assez de points" in response

def test_purchasePlaces_valid_booking(setup_club_comp):
    clubs, competitions = setup_club_comp
    app = Flask(__name__)
    app.secret_key = "test_secret"
    with app.test_request_context(method="POST",
                                  data={"club": "Test Club", "competition": "Test Competition", "places": "5"}):
        response = purchasePlaces()
        assert "welcome.html" in response
        assert int(competitions[0]["numberOfPlaces"]) == 15


@pytest.fixture
def mock_templates(monkeypatch):
    def fake_render_template(template_name, **context):
        return f"Rendered {template_name} with {context}"
    monkeypatch.setattr("server.render_template", fake_render_template)


def test_purchasePlaces_more_than_12_returns_400(client, mock_templates):
    c, clubs, competitions = client
    app = Flask(__name__)
    app.secret_key = "test_secret"

    with app.test_request_context(method="POST", data={"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "13"}):
        response, status = purchasePlaces()
        assert status == 400
        assert "12 places" in response


def test_purchasePlaces_valid_booking(client, mock_templates):
    c, clubs, competitions = client
    app = Flask(__name__)
    app.secret_key = "test_secret"

    with app.test_request_context(method="POST", data={"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "8"}):
        response = purchasePlaces()
        assert "welcome.html" in response
        assert int(competitions[0]["numberOfPlaces"]) == 12


def test_purchasePlaces_already_booked_too_many(client, mock_templates):
    c, clubs, competitions = client
    clubs[0][competitions[0]["name"]] = 11

    app = Flask(__name__)
    app.secret_key = "test_secret"

    with app.test_request_context(method="POST", data={"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "3"}):
        response, status = purchasePlaces()
        assert status == 400
        assert "12 places" in response

def test_purchase_places_in_past_competition_returns_400(client, monkeypatch, mock_templates):
    c, clubs, competitions = client
    competitions[0]["date"] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    app = Flask(__name__)
    app.secret_key = "test_secret"

    with app.test_request_context(method="POST", data={
                                                    "club": clubs[0]["name"],
                                                    "competition": competitions[0]["name"],
                                                    "places": "3",
                                                }):
        response, status = purchasePlaces()
        assert status == 400
        assert "terminée" in response


def test_purchase_places_in_future_competition(client, monkeypatch, mock_templates):
    c, clubs, competitions = client
    competitions[0]["date"] = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")

    app = Flask(__name__)
    app.secret_key = "test_secret"

    with app.test_request_context(method="POST", data={
                                                    "club": clubs[0]["name"],
                                                    "competition": competitions[0]["name"],
                                                    "places": "5",
                                                }):
        response = purchasePlaces()
        assert "welcome.html" in response
        assert int(competitions[0]["numberOfPlaces"]) == 15


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
