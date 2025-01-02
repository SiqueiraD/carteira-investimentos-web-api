import motor.motor_asyncio
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from .config import get_settings
import logging
import sys

# Configurar logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Configuração do MongoDB
if settings.ENVIRONMENT == "prod" and settings.KEY_VAULT_URL:
    # Em produção, tenta obter a string de conexão do Key Vault
    try:
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=settings.KEY_VAULT_URL, credential=credential)
        MONGODB_URL = secret_client.get_secret("mongodb-connection-string").value
    except Exception as e:
        logger.error(f"Erro ao obter segredo do Key Vault: {e}")
        MONGODB_URL = settings.MONGODB_URL
else:
    # Em desenvolvimento local, usa a URL do MongoDB local
    MONGODB_URL = settings.MONGODB_URL

logger.info(f"Ambiente: {settings.ENVIRONMENT}")
logger.info("Tentando conectar ao MongoDB...")

try:
    # Cliente MongoDB com configurações otimizadas para Cosmos DB
    client = motor.motor_asyncio.AsyncIOMotorClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        socketTimeoutMS=20000,
        maxPoolSize=1,
        retryWrites=False,
        ssl=True
    )
    database = client[settings.DATABASE_NAME]
    logger.info("Conexão com MongoDB estabelecida com sucesso!")
except Exception as e:
    logger.error(f"Erro ao conectar ao MongoDB: {e}")
    raise

# Coleções
usuarios = database.usuarios
acoes = database.acoes
carteiras = database.carteiras
transacoes = database.transacoes
notificacoes = database.notificacoes
relatorios = database.relatorios

# Função para inicializar o banco de dados
async def init_db():
    try:
        # Testar a conexão
        await client.admin.command('ping')
        logger.info("Ping ao MongoDB realizado com sucesso!")
        
        # Criar índices necessários
        await usuarios.create_index("email", unique=True)
        await acoes.create_index("nome", unique=True)
        logger.info("Índices criados com sucesso!")
        
        # Em ambiente local, inserir dados de exemplo
        if settings.ENVIRONMENT == "local":
            if await acoes.count_documents({}) == 0:
                await acoes.insert_many([
                    {"nome": "AAPL", "preco": 150.0, "qtd": 1000},
                    {"nome": "GOOGL", "preco": 2800.0, "qtd": 500},
                    {"nome": "MSFT", "preco": 300.0, "qtd": 800},
                    {"nome": "AMZN", "preco": 3300.0, "qtd": 300},
                ])
                logger.info("Dados de exemplo inseridos com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        # Não levanta a exceção para permitir que a aplicação continue mesmo se houver erro na inicialização
