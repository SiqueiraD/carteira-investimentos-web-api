import pymongo
from .config import get_settings
import logging
import sys

# Configurar logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Configuração do MongoDB
MONGODB_URL = settings.MONGODB_URL

logger.info(f"Ambiente: {settings.ENVIRONMENT}")
logger.info("Tentando conectar ao MongoDB...")

try:
    # Cliente MongoDB com configurações simplificadas
    client = pymongo.MongoClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000,
        tlsAllowInvalidCertificates=True  # Necessário para alguns ambientes Azure
    )
    database = client[settings.DATABASE_NAME]
    # Testar a conexão
    client.admin.command('ping')
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
precos_referencia = database.precos_referencia

def init_db():
    """Initialize database with required collections"""
    try:
        # Lista de coleções necessárias
        collections = ["usuarios", "acoes", "carteiras", "transacoes", "notificacoes", "relatorios", "precos_referencia"]
        
        # Criar coleções se não existirem
        existing_collections = database.list_collection_names()
        for collection in collections:
            if collection not in existing_collections:
                database.create_collection(collection)
                logger.info(f"Coleção {collection} criada com sucesso!")
        
        # Criar índices necessários
        usuarios.create_index("email", unique=True)
        acoes.create_index("nome", unique=True)
        
        logger.info("Inicialização do banco de dados concluída!")
    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {e}")
        # Não levanta a exceção para permitir que a aplicação continue mesmo se houver erro na inicialização

# Inicializar o banco de dados
init_db()
