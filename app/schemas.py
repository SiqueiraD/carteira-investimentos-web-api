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
    tipo_usuario: str

class CompraAcao(BaseModel):
    acao_id: str
    quantidade: int

class AcaoCreate(BaseModel):
    nome: str
    preco: float
    qtd: int
    risco: int

class AcaoUpdate(BaseModel):
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

class SolicitacaoDeposito(BaseModel):
    valor: float = Field(..., gt=0)
    descricao: Optional[str] = None

class SolicitacaoDepositoResponse(BaseModel):
    id: str
    usuario_id: str
    valor: float
    descricao: Optional[str]
    status: str  # pendente, aprovado, rejeitado
    data_solicitacao: datetime
    data_aprovacao: Optional[datetime] = None
    aprovado_por: Optional[str] = None

class AprovarDeposito(BaseModel):
    aprovado: bool
    motivo_rejeicao: Optional[str] = None

class Notificacao(BaseModel):
    id: str
    tipo: str  # deposito_pendente, deposito_aprovado, deposito_rejeitado
    usuario_id: Optional[str] = None  # None para notificações de admin
    mensagem: str
    data: datetime
    lida: bool = False
    dados: Optional[dict] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DepositoPendente(BaseModel):
    id: str
    usuario_id: str
    valor: float
    descricao: str
    data_solicitacao: datetime
    status: str
    nome_usuario: Optional[str] = None

class TransacaoResponse(BaseModel):
    id: str
    usuario_id: str
    acao_id: str
    tipo: str  # compra, venda, deposito
    qtd: Optional[int]
    valor: float
    preco_unitario: Optional[float]
    data: datetime
