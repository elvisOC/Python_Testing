import html

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

    response_index = c.get("/")
    assert response_index.status_code == 200

    response_summary = c.post("/showSummary", data={"email": clubs_list[0]["email"]})
    assert response_summary.status_code == 200
    decoded = html.unescape(response_summary.get_data(as_text=True))
    assert "Bienvenue" in decoded