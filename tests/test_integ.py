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
