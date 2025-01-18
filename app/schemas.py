from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
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
    nivel_risco: Optional[int] = Field(default=None, ge=1, le=5)
    qtd_max_acoes: Optional[int] = Field(default=None, ge=1)
    qtd_max_valor: Optional[float] = Field(default=None, ge=0.0)

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

class CarteiraAcao(BaseModel):
    pass

class CarteiraComUsuario(BaseModel):
    id: str = Field(alias="_id")
    usuario_id: str
    usuario_nome: str
    usuario_email: str
    acoes: List[CarteiraAcao] = []
    saldo: float = 0.0
    qtd_max_acoes: int = 100
    qtd_max_valor: float = 100000.0
    nivel_risco: int = Field(default=1, ge=1, le=5)

    class Config:
        populate_by_name = True
