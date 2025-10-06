import html


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
