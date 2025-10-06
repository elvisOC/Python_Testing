import html


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
