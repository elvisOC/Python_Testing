import json

def test_full_booking_flow_with_save(monkeypatch, client):
    c, clubs, competitions = client
    saved_data = {}

    def fake_saveClubs(data):
        saved_data["clubs"] = data

    def fake_saveCompetitions(data):
        saved_data["competitions"] = data

    monkeypatch.setattr("server.saveClubs", fake_saveClubs)
    monkeypatch.setattr("server.saveCompetitions", fake_saveCompetitions)

    original_places = int(competitions[0]["numberOfPlaces"])

    response = c.post("/purchasePlaces", data={
        "club": clubs[0]["name"],
        "competition": competitions[0]["name"],
        "places": "5"
    })

    assert response.status_code == 200
    assert b"Great-booking complete" in response.data

    assert int(competitions[0]["numberOfPlaces"]) == original_places - 5

    assert "clubs" in saved_data
    assert "competitions" in saved_data
    assert saved_data["competitions"][0]["numberOfPlaces"] == original_places - 5


