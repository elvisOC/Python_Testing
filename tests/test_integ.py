from datetime import datetime, timedelta
import html


def test_full_flow_with_past_competition(client):
    c, clubs, competitions = client
    competitions[0]["date"] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    response_index = c.get("/")
    assert response_index.status_code == 200

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
