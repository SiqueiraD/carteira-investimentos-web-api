from datetime import datetime
from typing import Optional, List, Any, Annotated
from pydantic import BaseModel, Field, EmailStr, ConfigDict, GetJsonSchemaHandler, BeforeValidator
from pydantic.json_schema import JsonSchemaValue
from bson import ObjectId

# Função auxiliar para converter strings em ObjectId
def validate_object_id(v: Any) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str):
        try:
            ObjectId(v)
            return v
        except:
            raise ValueError("Invalid ObjectId format")
    raise ValueError("Invalid ObjectId")

# Tipo personalizado para ObjectId
PyObjectId = Annotated[str, BeforeValidator(validate_object_id)]

class MongoBaseModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")

class Usuario(MongoBaseModel):
    nome: str
    email: EmailStr
    senha: str
    tipo_usuario: str = "comum" or "admin" or "bot"

class Acao(MongoBaseModel):
    nome: str
    preco: float
    qtd: int
    risco: Optional[int] = Field(default=1, ge=1, le=5)

class CarteiraAcao(MongoBaseModel):
    acao_id: PyObjectId
    qtd: int
    preco_compra: float = 0.0

class Carteira(MongoBaseModel):
    usuario_id: PyObjectId
    acoes: List[CarteiraAcao] = []
    qtd_max_acoes: int = 100
    qtd_max_valor: float = 100000.0
    saldo: float = 0.0
    nivel_risco: int = Field(default=1, ge=1, le=5)

class Transacao(MongoBaseModel):
    usuario_id: PyObjectId
    acao_id: PyObjectId
    tipo: str  # compra ou venda
    qtd: int
    data: datetime = Field(default_factory=datetime.utcnow)

class Notificacao(MongoBaseModel):
    usuario_id: PyObjectId
    mensagem: str
    data: datetime = Field(default_factory=datetime.utcnow)

class Relatorio(MongoBaseModel):
    usuario_id: PyObjectId
    data: datetime = Field(default_factory=datetime.utcnow)
    total_investido: float

class PrecoReferencia(MongoBaseModel):
    acao_id: str
    preco_referencia: float
    data_atualizacao: datetime
    atualizado_por: str  # email do usuário que atualizou
