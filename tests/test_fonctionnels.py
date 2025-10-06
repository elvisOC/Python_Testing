import html

def test_club_table_page(client):
    c, clubs, competitions = client
    response = c.get("/club_table")
    
    assert response.status_code == 200
    
    html_content = response.get_data(as_text=True)
    
    for club in clubs:
        assert club["name"] in html_content
    
    for comp in competitions:
        assert comp["name"] in html_content
