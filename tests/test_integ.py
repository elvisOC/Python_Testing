import html

def test_full_booking_flow(client):
    c, clubs, competitions = client
    response = c.post("/showSummary", data={"email": clubs[0]["email"]})
    assert response.status_code == 200


    data = {"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "50"}
    response = c.post("/purchasePlaces", data=data)
    assert response.status_code == 400


    data = {"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "5"}
    response = c.post("/purchasePlaces", data=data)
    assert response.status_code == 200