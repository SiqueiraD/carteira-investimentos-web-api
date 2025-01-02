from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioBase(BaseModel):
    email: EmailStr
    nome: str

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str
    tipo_usuario: str = "comum"

class CompraAcao(BaseModel):
    acao_id: str
    quantidade: int

class CarteiraLimites(BaseModel):
    qtd_max_acoes: Optional[int] = None
    qtd_max_valor: Optional[float] = None

class RelatorioResponse(BaseModel):
    mensagem: str
    relatorio_id: str
    total_investido: float
