from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UsuarioBase(BaseModel):
    email: EmailStr
    nome: str
    tipo_usuario: str = "comum"

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class UsuarioUpdate(BaseModel):
    nome: str

class Token(BaseModel):
    access_token: str
    token_type: str
    tipo_usuario: str = "comum"

class CompraAcao(BaseModel):
    acao_id: str
    quantidade: int

class AcaoCreate(BaseModel):
    nome: str
    preco: float
    qtd: int
    risco: int

class AcaoUpdate(BaseModel):
    nome: Optional[str] = None
    preco: Optional[float] = None
    qtd: Optional[int] = None
    risco: Optional[int] = None

class CarteiraLimites(BaseModel):
    qtd_max_acoes: Optional[int] = None
    qtd_max_valor: Optional[float] = None
    nivel_risco: Optional[int] = None

class RelatorioResponse(BaseModel):
    mensagem: str
    relatorio_id: str
    total_investido: float

class PrecoReferenciaCreate(BaseModel):
    acao_id: str
    preco_referencia: float

class PrecoReferenciaUpdate(BaseModel):
    preco_referencia: float

class PrecoReferenciaResponse(BaseModel):
    id: str
    acao_id: str
    preco_referencia: float
    data_atualizacao: datetime
    atualizado_por: str
