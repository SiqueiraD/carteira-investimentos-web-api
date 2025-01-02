from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
