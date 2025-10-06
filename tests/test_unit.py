import pytest
from server import purchasePlaces
from flask import Flask
from datetime import datetime, timedelta


@pytest.fixture
def mock_templates(monkeypatch):
    def fake_render_template(template_name, **context):
        return f"Rendered {template_name} with {context}"
    monkeypatch.setattr("server.render_template", fake_render_template)


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
