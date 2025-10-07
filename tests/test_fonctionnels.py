import html
from datetime import datetime, timedelta


def test_show_summary_unknown_email_returns_400(client):
    c, _, _ = client
    response = c.post("/showSummary", data={"email": "invalid@example.com"})
    assert response.status_code == 400
    decoded = html.unescape(response.get_data(as_text=True))
    assert "Sorry" in decoded 


def test_show_summary_known_email_returns_200(client):
    c, clubs, _ = client
    response = c.post("/showSummary", data={"email": clubs[0]["email"]})
    assert response.status_code == 200
    decoded = html.unescape(response.get_data(as_text=True))
    assert "Welcome" in decoded 


def test_booking_more_than_points_returns_400(client):
    c, clubs, competitions = client
    data = {"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "20"}
    response = c.post("/purchasePlaces", data=data)
    assert response.status_code == 400
    decoded = html.unescape(response.get_data(as_text=True))
    assert "pas assez de points" in decoded 


def test_booking_valid_points_reduces_club_points(client):
    c, clubs, competitions = client
    initial_points = int(clubs[0]["points"])

    data = {"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "5"}
    response = c.post("/purchasePlaces", data=data)
    assert response.status_code == 200

    assert int(clubs[0]["points"]) == initial_points - 5
    decoded = html.unescape(response.get_data(as_text=True))
    assert "Great" in decoded 


def test_booking_more_than_12_places_returns_400(client):
    c, clubs, competitions = client
    data = {"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "13"}
    response = c.post("/purchasePlaces", data=data)
    assert response.status_code == 400
    decoded = html.unescape(response.get_data(as_text=True))
    assert "12 places" in decoded


def test_booking_12_places_ok(client):
    c, clubs, competitions = client
    data = {"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "12"}
    response = c.post("/purchasePlaces", data=data)
    assert response.status_code == 200
    decoded = html.unescape(response.get_data(as_text=True))
    assert "Great-booking" in decoded 


def test_booking_past_competition_returns_400(client):
    c, clubs, competitions = client
    competitions[0]["date"] = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "club": clubs[0]["name"],
        "competition": competitions[0]["name"],
        "places": "2",
    }
    response = c.post("/purchasePlaces", data=data)
    decoded = html.unescape(response.get_data(as_text=True))

    assert response.status_code == 400
    assert "terminée" in decoded 


def test_booking_future_competition_returns_200(client):
    c, clubs, competitions = client
    competitions[0]["date"] = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "club": clubs[0]["name"],
        "competition": competitions[0]["name"],
        "places": "3",
    }
    response = c.post("/purchasePlaces", data=data)
    decoded = html.unescape(response.get_data(as_text=True))

    assert response.status_code == 200
    assert "Great-booking complete" in decoded 


def test_purchasePlaces_calls_save_functions(client, monkeypatch):
    c, clubs, competitions = client
    called = {"clubs": False, "competitions": False}

    def fake_saveClubs(_):
        called["clubs"] = True

    def fake_saveCompetitions(_):
        called["competitions"] = True

    monkeypatch.setattr("server.saveClubs", fake_saveClubs)
    monkeypatch.setattr("server.saveCompetitions", fake_saveCompetitions)

    response = c.post("/purchasePlaces", data={
        "club": clubs[0]["name"],
        "competition": competitions[0]["name"],
        "places": "3"
    })

    assert response.status_code == 200
    assert b"Great-booking complete" in response.data
    assert called["clubs"]
    assert called["competitions"]


def test_purchasePlaces_overbook_returns_400(client):
    c, clubs, competitions = client
    response = c.post("/purchasePlaces", data={
        "club": clubs[0]["name"],
        "competition": competitions[0]["name"],
        "places": "25"
    })
    assert response.status_code == 400
    decoded = response.get_data(as_text=True)
    assert "pas assez de points" in decoded


def test_club_table_page_displays_clubs_and_competitions(client):
    c, clubs, competitions = client
    response = c.get("/club_table")
    assert response.status_code == 200

    html_content = response.get_data(as_text=True)

    for club in clubs:
        assert club["name"] in html_content
        assert str(club["points"]) in html_content

    for comp in competitions:
        assert comp["name"] in html_content
