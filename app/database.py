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
depositos = database.depositos

def init_db():
    """Initialize database with required collections and indexes"""
    try:
        # Lista de coleções necessárias
        collections = ["usuarios", "acoes", "carteiras", "transacoes", "notificacoes", "relatorios", "depositos"]
        
        # Criar coleções se não existirem
        existing_collections = database.list_collection_names()
        for collection in collections:
            if collection not in existing_collections:
                database.create_collection(collection)
                logger.info(f"Coleção {collection} criada com sucesso!")
        
        # Índices para usuários
        usuarios.create_index("email", unique=True)
        
        # Índices para carteiras
        carteiras.create_index("usuario_id", unique=True)
        
        # Índices para transações
        transacoes.create_index([("usuario_id", 1), ("data", -1)])
        transacoes.create_index("acao_id")
        
        # Índices para notificações
        notificacoes.create_index("data")  # Índice simples para ordenação por data
        notificacoes.create_index("usuario_id")  # Índice para filtrar por usuário
        notificacoes.create_index("tipo")  # Índice para filtrar por tipo
        
        # Índices para depósitos
        depositos.create_index([("usuario_id", 1), ("status", 1), ("data_solicitacao", -1)])
        
        logger.info("Inicialização do banco de dados concluída!")
    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {e}")
        # Não levanta a exceção para permitir que a aplicação continue mesmo se houver erro na inicialização

# Inicializar o banco de dados
init_db()
