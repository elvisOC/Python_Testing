from datetime import datetime, timedelta
import html


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
