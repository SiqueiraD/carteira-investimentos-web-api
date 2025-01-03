from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from . import models, schemas, auth
from .database import usuarios, acoes, carteiras, transacoes, notificacoes, relatorios, init_db
from .config import get_settings
from typing import List
from bson import ObjectId
from contextlib import asynccontextmanager

# Configuração do FastAPI
app = FastAPI(
    title="API de Investimentos",
    description="API para gerenciamento de investimentos em ações",
    version="1.0.0"
)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

# Atualizar a configuração do FastAPI
app.lifespan_context = lifespan

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de segurança
security = HTTPBearer()

# Root route
@app.get("/")
async def read_root():
    return {"message": "Bem-vindo à API de Investimentos"}

# Rotas de autenticação
@app.post("/api/usuarios/registrar", response_model=schemas.Token)
async def registrar_usuario(usuario: schemas.UsuarioCreate):
    # Verificar se o email já existe
    if await usuarios.find_one({"email": usuario.email}):
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    # Criar usuário
    usuario_dict = usuario.model_dump()
    usuario_dict["senha"] = auth.get_password_hash(usuario_dict["senha"])
    resultado = await usuarios.insert_one(usuario_dict)
    
    # Gerar token
    token = auth.create_access_token(data={"sub": usuario.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "tipo_usuario": "comum"
    }

@app.post("/api/usuarios/login", response_model=schemas.Token)
async def login(usuario: schemas.UsuarioLogin):
    user = await auth.autenticar_usuario(usuario.email, usuario.senha)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth.create_access_token(data={"sub": user["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "tipo_usuario": user.get("tipo_usuario", "comum")
    }

# Rotas protegidas
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return await auth.get_current_user(credentials.credentials, credentials_exception)

# Rotas de ações
@app.get("/api/acoes", response_model=List[models.Acao])
async def listar_acoes(_: dict = Depends(get_current_user)):
    cursor = acoes.find()
    acoes_list = await cursor.to_list(length=100)
    return [
        models.Acao(
            _id=str(acao["_id"]),
            nome=acao["nome"],
            preco=acao["preco"],
            qtd=acao["qtd"]
        )
        for acao in acoes_list
    ]

@app.get("/api/acoes/{acao_id}", response_model=models.Acao)
async def obter_acao(acao_id: str, _: dict = Depends(get_current_user)):
    acao = await acoes.find_one({"_id": ObjectId(acao_id)})
    if not acao:
        raise HTTPException(status_code=404, detail="Ação não encontrada")
    return models.Acao(
        _id=str(acao["_id"]),
        nome=acao["nome"],
        preco=acao["preco"],
        qtd=acao["qtd"]
    )

# Rotas de carteira
@app.get("/api/carteira", response_model=models.Carteira)
async def obter_carteira(usuario: dict = Depends(get_current_user)):
    carteira = await carteiras.find_one({"usuario_id": ObjectId(usuario["_id"])})
    if not carteira:
        # Criar carteira vazia se não existir
        carteira = {
            "usuario_id": ObjectId(usuario["_id"]),
            "acoes": [],
            "saldo": 0.0,
            "qtd_max_acoes": 100,
            "qtd_max_valor": 100000.0
        }
        resultado = await carteiras.insert_one(carteira)
        carteira["_id"] = resultado.inserted_id
    
    return models.Carteira(
        _id=str(carteira["_id"]),
        usuario_id=str(carteira["usuario_id"]),
        acoes=[
            models.CarteiraAcao(
                acao_id=str(acao["acao_id"]),
                qtd=acao["qtd"]
            )
            for acao in carteira["acoes"]
        ],
        saldo=carteira.get("saldo", 0.0),
        qtd_max_acoes=carteira.get("qtd_max_acoes", 100),
        qtd_max_valor=carteira.get("qtd_max_valor", 100000.0)
    )

@app.post("/api/carteira/comprar", response_model=models.Carteira)
async def comprar_acao(compra: schemas.CompraAcao, usuario: dict = Depends(get_current_user)):
    # Verificar se a ação existe
    acao = await acoes.find_one({"_id": ObjectId(compra.acao_id)})
    if not acao:
        raise HTTPException(status_code=404, detail="Ação não encontrada")
    
    # Verificar quantidade disponível
    if acao["qtd"] < compra.quantidade:
        raise HTTPException(status_code=400, detail="Quantidade indisponível")
    
    # Atualizar carteira
    carteira = await carteiras.find_one({"usuario_id": ObjectId(usuario["_id"])})
    if not carteira:
        carteira = {
            "usuario_id": ObjectId(usuario["_id"]),
            "acoes": [],
            "saldo": 0.0,
            "qtd_max_acoes": 100,
            "qtd_max_valor": 100000.0
        }
        resultado = await carteiras.insert_one(carteira)
        carteira["_id"] = resultado.inserted_id
    
    # Verificar limites da carteira
    if len(carteira["acoes"]) >= carteira["qtd_max_acoes"]:
        raise HTTPException(status_code=400, detail="Limite de ações atingido")
    
    valor_total = acao["preco"] * compra.quantidade
    if valor_total > carteira["qtd_max_valor"]:
        raise HTTPException(status_code=400, detail="Limite de valor atingido")
    
    # Atualizar quantidade de ações
    acao_carteira = None
    for a in carteira["acoes"]:
        if str(a["acao_id"]) == compra.acao_id:
            acao_carteira = a
            break
    
    if acao_carteira:
        acao_carteira["qtd"] += compra.quantidade
    else:
        carteira["acoes"].append({
            "acao_id": ObjectId(compra.acao_id),
            "qtd": compra.quantidade
        })
    
    # Atualizar banco de dados
    await carteiras.update_one(
        {"_id": carteira["_id"]},
        {"$set": carteira}
    )
    
    await acoes.update_one(
        {"_id": ObjectId(compra.acao_id)},
        {"$inc": {"qtd": -compra.quantidade}}
    )
    
    # Registrar transação
    transacao = {
        "usuario_id": ObjectId(usuario["_id"]),
        "acao_id": ObjectId(compra.acao_id),
        "tipo": "compra",
        "qtd": compra.quantidade
    }
    await transacoes.insert_one(transacao)
    
    # Retornar carteira atualizada
    carteira_atualizada = await carteiras.find_one({"_id": carteira["_id"]})
    return models.Carteira(
        _id=str(carteira_atualizada["_id"]),
        usuario_id=str(carteira_atualizada["usuario_id"]),
        acoes=[
            models.CarteiraAcao(
                acao_id=str(acao["acao_id"]),
                qtd=acao["qtd"]
            )
            for acao in carteira_atualizada["acoes"]
        ],
        saldo=carteira_atualizada.get("saldo", 0.0),
        qtd_max_acoes=carteira_atualizada.get("qtd_max_acoes", 100),
        qtd_max_valor=carteira_atualizada.get("qtd_max_valor", 100000.0)
    )
