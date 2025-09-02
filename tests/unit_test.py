from fastapi.testclient import TestClient
from src.app.api.main import app  

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "Document Portal" in response.text