from server import app

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
