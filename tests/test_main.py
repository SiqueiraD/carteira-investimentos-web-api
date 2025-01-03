from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

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

@patch('app.main.get_current_user')
@patch('app.main.acoes.insert_one')
@patch('app.main.acoes.find_one')
async def test_cadastrar_acoes(mock_find_one, mock_insert_one, mock_get_current_user):
    # Mock authentication with admin role
    mock_get_current_user.return_value = {
        "email": "test@example.com",
        "role": "admin",
        "tipo_usuario": "admin"  # Adding tipo_usuario for additional authentication
    }
    
    # Mock database operations
    mock_insert_one.return_value.inserted_id = "123"
    mock_find_one.return_value = {
        "_id": "123",
        "nome": "TESTE3",
        "preco": 10.5,
        "qtd": 100
    }
    
    # Test data
    test_acao = {
        "nome": "TESTE3",
        "preco": 10.5,
        "qtd": 100
    }
    
    # Add authorization header
    headers = {"Authorization": "Bearer test-token"}
    
    response = client.post("/api/acoes/cadastrar", json=test_acao, headers=headers)
    assert response.status_code == 200
    assert response.json()["nome"] == "TESTE3"
    assert response.json()["preco"] == 10.5
    assert response.json()["qtd"] == 100
