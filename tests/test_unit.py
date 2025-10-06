import pytest
from server import showSummary, clubs, competitions, purchasePlaces
from flask import Flask

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