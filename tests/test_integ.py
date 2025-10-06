import json

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



