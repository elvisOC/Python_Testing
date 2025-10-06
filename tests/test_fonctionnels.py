import html

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