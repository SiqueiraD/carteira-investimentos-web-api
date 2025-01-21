import requests
import json
from typing import Dict
from pymongo import MongoClient
from app.auth import get_password_hash

# Obter URL base do ambiente
BASE_URL = "http://localhost:8000"

def limpar_banco():
    """Limpa todas as coleções do banco de dados"""
    print("\n0. Limpando banco de dados...")
    # Obter URL do MongoDB do ambiente
    client = MongoClient('mongodb://localhost:27017/')
    db = client['investimentos']
    
    # Lista de coleções para limpar
    colecoes = ['usuarios', 'acoes', 'carteiras', 'transacoes', 'notificacoes', 'relatorios', 'depositos']
    
    for colecao in colecoes:
        result = db[colecao].delete_many({})
        print(f"Removidos {result.deleted_count} documentos da coleção {colecao}")
    
    # Criar usuário admin diretamente no banco
    db.usuarios.insert_one({
        'email': 'admin@example.com',
        'senha': get_password_hash('string'),
        'nome': 'Admin',
        'tipo_usuario': 'admin'
    })
    print("Usuário admin criado com sucesso")

def registrar_usuario_comum():
    """Registra o usuário comum usando o endpoint de registro"""
    print("\n1. Registrando usuário comum...")
    data = {
        "email": "user@example.com",
        "senha": "string",
        "nome": "User",
        "tipo_usuario": "comum"
    }
    response = requests.post(f"{BASE_URL}/api/usuarios/registrar", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

class TestAPI:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.deposito_id = None
        self.acao_id = None

    def get_headers(self, token: str) -> Dict:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def login_admin(self):
        print("\n2. Login como admin...")
        data = {
            "email": "admin@example.com",
            "senha": "string"
        }
        response = requests.post(f"{BASE_URL}/api/usuarios/login", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        self.admin_token = response.json()["access_token"]
        return response.json()

    def login_user(self):
        print("\n3. Login como usuário comum...")
        data = {
            "email": "user@example.com",
            "senha": "string"
        }
        response = requests.post(f"{BASE_URL}/api/usuarios/login", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        self.user_token = response.json()["access_token"]
        return response.json()

    def solicitar_deposito(self):
        print("\n4. Solicitando depósito como usuário comum...")
        data = {
            "valor": 1000.0,
            "descricao": "Depósito inicial"
        }
        response = requests.post(
            f"{BASE_URL}/api/carteira/deposito",
            headers=self.get_headers(self.user_token),
            json=data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        self.deposito_id = response.json()["id"]
        return response.json()

    def verificar_notificacoes_admin(self):
        print("\n5. Verificando notificações como admin...")
        response = requests.get(
            f"{BASE_URL}/api/notificacoes",
            headers=self.get_headers(self.admin_token)
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()

    def aprovar_deposito(self):
        print("\n6. Aprovando depósito como admin...")
        data = {
            "aprovado": True
        }
        response = requests.post(
            f"{BASE_URL}/api/carteira/deposito/{self.deposito_id}/aprovar",
            headers=self.get_headers(self.admin_token),
            json=data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()

    def cadastrar_acao(self):
        print("\n7. Cadastrando ação como admin...")
        data = {
            "nome": "TESTE4",
            "preco": 50.0,
            "qtd": 1000,
            "risco": 1
        }
        response = requests.post(
            f"{BASE_URL}/api/acoes/cadastrar",
            headers=self.get_headers(self.admin_token),
            json=data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        self.acao_id = response.json()["_id"]
        return response.json()

    def tentar_compra_fora_limites(self):
        print("\n8. Tentando compra fora dos limites como usuário comum...")
        data = {
            "acao_id": self.acao_id,
            "quantidade": 1000  # Quantidade alta para exceder limites
        }
        response = requests.post(
            f"{BASE_URL}/api/carteira/comprar",
            headers=self.get_headers(self.user_token),
            json=data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code != 422 else response.text}")
        return response

    def comprar_acao_sucesso(self):
        print("\n9. Comprando ação com sucesso como usuário comum...")
        data = {
            "acao_id": self.acao_id,
            "quantidade": 1
        }
        response = requests.post(
            f"{BASE_URL}/api/carteira/comprar",
            headers=self.get_headers(self.user_token),
            json=data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()

    def testar_endpoints_seguros(self):
        print("\n10. Testando endpoints seguros como usuário comum...")
        # Tentar cadastrar ação
        data = {
            "nome": "TESTE5",
            "preco": 50.0
        }
        response = requests.post(
            f"{BASE_URL}/api/acoes/cadastrar",
            headers=self.get_headers(self.user_token),
            json=data
        )
        print(f"Tentativa de cadastrar ação - Status: {response.status_code}")
        
        # Tentar alterar limites
        data = {
            "nivel_risco": 2
        }
        response = requests.put(
            f"{BASE_URL}/api/carteira/limites/123",
            headers=self.get_headers(self.user_token),
            json=data
        )
        print(f"Tentativa de alterar limites - Status: {response.status_code}")

    def obter_carteira(self):
        print("\n11. Obtendo carteira como usuário comum...")
        response = requests.get(
            f"{BASE_URL}/api/carteira",
            headers=self.get_headers(self.user_token)
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()

    def alterar_limites_carteira(self):
        print("\n12. Alterando limites da carteira como admin...")
        # Primeiro obtém o ID do usuário comum
        response = requests.get(
            f"{BASE_URL}/api/carteira",
            headers=self.get_headers(self.user_token)
        )
        usuario_id = response.json()["usuario_id"]
        
        data = {
            "nivel_risco": 2,
            "qtd_max_acoes": 50,
            "qtd_max_valor": 5000.0
        }
        response = requests.patch(
            f"{BASE_URL}/api/carteiras/{usuario_id}/limites",
            headers=self.get_headers(self.admin_token),
            json=data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()

    def alterar_acao(self):
        print("\n13. Alterando valores da ação como admin...")
        data = {
            "preco": 55.0,
            "qtd": 900,
            "risco": 2
        }
        response = requests.patch(
            f"{BASE_URL}/api/acoes/{self.acao_id}",
            headers=self.get_headers(self.admin_token),
            json=data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()

def main():
    limpar_banco()
    tester = TestAPI()
    registrar_usuario_comum()
    
    # Fluxo de depósito
    tester.login_user()
    tester.solicitar_deposito()
    tester.login_admin()
    tester.verificar_notificacoes_admin()
    tester.aprovar_deposito()
    
    # Testes com usuário comum
    tester.cadastrar_acao()  # Precisa criar a ação primeiro
    tester.login_user()  # Volta para usuário comum
    tester.tentar_compra_fora_limites()
    tester.comprar_acao_sucesso()
    tester.testar_endpoints_seguros()
    tester.obter_carteira()
    
    # Testes com admin
    tester.login_admin()
    tester.alterar_limites_carteira()
    tester.alterar_acao()

if __name__ == "__main__":
    main()
