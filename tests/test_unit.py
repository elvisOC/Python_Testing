import pytest
from flask import Flask
from server import showSummary, purchasePlaces


def fake_render_template(template_name, **context):
    return f"{template_name} - {context}"



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
