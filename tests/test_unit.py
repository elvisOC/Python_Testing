import pytest
from server import purchasePlaces
from flask import Flask


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
