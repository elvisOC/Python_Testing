from server import app

def test_purchasePlaces_overbook(client):
    c, clubs, competitions = client
    response = c.post("/purchasePlaces", data={
        "club": clubs[0]["name"],
        "competition": competitions[0]["name"],
        "places": "25"  
    })
    assert response.status_code == 400
    decoded = response.get_data(as_text=True)
    assert "Le nombre de places de la compétition ne peut pas être inférieur à zéro" in decoded

