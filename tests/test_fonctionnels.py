import html

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