import motor.motor_asyncio
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from .config import get_settings

settings = get_settings()

# Configuração do MongoDB
if settings.ENVIRONMENT == "prod" and settings.KEY_VAULT_URL:
    # Em produção, tenta obter a string de conexão do Key Vault
    try:
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=settings.KEY_VAULT_URL, credential=credential)
        MONGODB_URL = secret_client.get_secret("mongodb-connection-string").value
    except Exception as e:
        print(f"Erro ao obter segredo do Key Vault: {e}")
        MONGODB_URL = settings.MONGODB_URL
else:
    # Em desenvolvimento local, usa a URL do MongoDB local
    MONGODB_URL = settings.MONGODB_URL

# Cliente MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
database = client[settings.DATABASE_NAME]

# Coleções
usuarios = database.usuarios
acoes = database.acoes
carteiras = database.carteiras
transacoes = database.transacoes
notificacoes = database.notificacoes
relatorios = database.relatorios

# Função para inicializar dados de exemplo em ambiente local
async def init_db():
    if settings.ENVIRONMENT == "local":
        # Verifica se já existem dados
        if await acoes.count_documents({}) == 0:
            # Insere algumas ações de exemplo
            await acoes.insert_many([
                {"nome": "AAPL", "preco": 150.0, "qtd": 1000},
                {"nome": "GOOGL", "preco": 2800.0, "qtd": 500},
                {"nome": "MSFT", "preco": 300.0, "qtd": 800},
                {"nome": "AMZN", "preco": 3300.0, "qtd": 300},
            ])
            print("Dados de exemplo inseridos com sucesso!")
