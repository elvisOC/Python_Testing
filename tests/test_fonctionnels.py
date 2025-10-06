import html
from datetime import datetime, timedelta

def test_show_summary_unknown_email_returns_400(client):
    c, _, _ = client
    response = c.post("/showSummary", data={"email": "invalid@example.com"})
    assert response.status_code == 400
    decoded = html.unescape(response.get_data(as_text=True))
    assert "Sorry, that email wasn't found" in decoded

def test_show_summary_known_email_returns_200(client):
    c, clubs_list, _ = client
    response = c.post("/showSummary", data={"email": clubs_list[0]["email"]})
    assert response.status_code == 200
    decoded = html.unescape(response.get_data(as_text=True))
    assert "Bienvenue" in decoded
    
def test_booking_more_than_points(client):
    c, clubs, competitions = client
    data = {"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "20"}
    response = c.post("/purchasePlaces", data=data)
    assert response.status_code == 400
    decoded = html.unescape(response.get_data(as_text=True))
    assert "Vous n'avez pas assez de points" in decoded

def test_booking_valid_points(client):
    c, clubs, competitions = client
    data = {"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "5"}
    response = c.post("/purchasePlaces", data=data)
    assert response.status_code == 200
    assert int(competitions[0]["numberOfPlaces"]) == int(competitions[0]["numberOfPlaces"])

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
    assert "Great-booking" in decoded or "welcome" in decoded


def test_booking_past_competition_returns_error(client):
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


def test_booking_future_competition(client):
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
    assert "Great-booking complete" in decoded or "welcome" in decoded
