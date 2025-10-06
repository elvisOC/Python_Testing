import html
from datetime import datetime, timedelta
import json

def test_full_login_flow_with_unknown_email(client):
    c, _, _ = client

    response_index = c.get("/")
    assert response_index.status_code == 200

    response_summary = c.post("/showSummary", data={"email": "notfound@club.com"})
    assert response_summary.status_code == 400
    decoded = html.unescape(response_summary.get_data(as_text=True))
    assert "Sorry, that email wasn't found" in decoded

def test_full_login_flow_with_valid_email(client):
    c, clubs_list, _ = client


def test_full_flow_with_past_competition(client):
    c, clubs, competitions = client
    competitions[0]["date"] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    response_index = c.get("/")
    assert response_index.status_code == 200

    response_summary = c.post("/showSummary", data={"email": clubs_list[0]["email"]})
    assert response_summary.status_code == 200
    decoded = html.unescape(response_summary.get_data(as_text=True))
    assert "Bienvenue" in decoded
    
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

def test_full_booking_flow_with_valid_email_and_valid_places(client):
    c, clubs, competitions = client

    response_summary = c.post("/showSummary", data={"email": clubs[0]["email"]})
    assert response_summary.status_code == 200

    response_booking = c.post("/purchasePlaces", data={"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "10"})
    assert response_booking.status_code == 200
    decoded = html.unescape(response_booking.get_data(as_text=True))
    assert "Great-booking" in decoded or "welcome" in decoded


def test_full_booking_flow_more_than_12_places_fails(client):
    c, clubs, competitions = client

    c.post("/showSummary", data={"email": clubs[0]["email"]})
    response_booking = c.post("/purchasePlaces", data={"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "13"})
    assert response_booking.status_code == 400
    decoded = html.unescape(response_booking.get_data(as_text=True))
    assert "12 places" in decoded
    response_login = c.post("/showSummary", data={"email": clubs[0]["email"]})
    assert response_login.status_code == 200

    data = {
        "club": clubs[0]["name"],
        "competition": competitions[0]["name"],
        "places": "2",
    }
    response_booking = c.post("/purchasePlaces", data=data)
    decoded = html.unescape(response_booking.get_data(as_text=True))
    assert response_booking.status_code == 400
    assert "terminée" in decoded

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

def test_overbooking_flow(client):
    c, clubs, competitions = client

    response_overbook = c.post("/purchasePlaces", data={
        "club": clubs[0]["name"],
        "competition": competitions[0]["name"],
        "places": "30"
    })
    assert response_overbook.status_code == 400
    decoded = response_overbook.get_data(as_text=True)
    assert "Le nombre de places de la compétition ne peut pas être inférieur à zéro" in decoded
def test_club_table_integration_flow(client):
    c, clubs, competitions = client
    
    login_response = c.post("/showSummary", data={"email": clubs[0]["email"]})
    assert login_response.status_code == 200
    
    table_response = c.get("/club_table")
    assert table_response.status_code == 200
    
    html_content = table_response.get_data(as_text=True)
    
    for club in clubs:
        assert club["name"] in html_content
        assert str(club["points"]) in html_content
    
    for comp in competitions:
        assert comp["name"] in html_content
