import pytest
from server import showSummary, clubs, competitions, purchasePlaces
from flask import Flask
from flask import Flask
from server import showSummary, purchasePlaces


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
