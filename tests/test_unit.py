import pytest
from server import club_table, clubs, competitions

def fake_render_template(template_name, **context):
    return {"template": template_name, "context": context}

def test_club_table_unit(monkeypatch):
    monkeypatch.setattr("server.render_template", fake_render_template)
    
    response = club_table()
    
    assert response["template"] == "/club_table.html"
    assert response["context"]["clubs"] == clubs
    assert response["context"]["competitions"] == competitions
