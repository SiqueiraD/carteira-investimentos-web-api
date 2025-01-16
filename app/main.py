from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from . import models, schemas, auth
from .database import usuarios, acoes, carteiras, transacoes, notificacoes, relatorios, precos_referencia, init_db
from .config import get_settings
from typing import List
from bson import ObjectId
from contextlib import asynccontextmanager
from datetime import datetime

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
        "tipo_usuario": user["tipo_usuario"]
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

@app.post("/api/acoes/cadastrar", response_model=models.Acao)
async def cadastrar_acoes(acao: schemas.AcaoCreate, user: dict = Depends(get_current_user)):
    # Criar ação
    user_tipo = user["tipo_usuario"]
    if(user_tipo != "admin" and user_tipo != "bot"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    acao_dict = acao.model_dump()
    resultado = await acoes.insert_one(acao_dict)
    acao_criada = await acoes.find_one({"_id": resultado.inserted_id})
    if not acao_criada:
        raise HTTPException(status_code=500, detail="Erro ao cadastrar ação")
    return models.Acao(
        _id=str(acao_criada["_id"]),
        nome=acao_criada["nome"],
        preco=acao_criada["preco"],
        qtd=acao_criada["qtd"]
    )

@app.patch("/api/acoes/{acao_id}", response_model=models.Acao)
async def atualizar_acoes(acao_id: str, acao: schemas.AcaoUpdate, user: dict = Depends(get_current_user)):
    # Alterar ação
    user_tipo = user["tipo_usuario"]
    if(user_tipo != "admin" and user_tipo != "bot"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    acao_dict = acao.model_dump()
    resultado = await acoes.update_one({"_id": ObjectId(acao_id)}, {"$set": acao_dict})
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Ação não encontrada")
    acao_atualizada = await acoes.find_one({"_id": ObjectId(acao_id)})
    if not acao_atualizada:
        raise HTTPException(status_code=500, detail="Erro ao atualizar ação")
    return models.Acao(
        _id=str(acao_atualizada["_id"]),
        nome=acao_atualizada["nome"],
        preco=acao_atualizada["preco"],
        qtd=acao_atualizada["qtd"]
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

@app.put("/api/usuarios/atualizar-nome")
async def atualizar_nome_usuario(
    dados: schemas.UsuarioUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Atualiza o nome do usuário no banco de dados
        resultado = await usuarios.update_one(
            {"email": current_user.get("email")},
            {"$set": {"nome": dados.nome}}
        )
        
        if resultado.modified_count == 0:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
        return {"mensagem": "Nome atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rotas de preços de referência
@app.post("/api/precos/cadastrar", response_model=schemas.PrecoReferenciaResponse)
async def cadastrar_preco_referencia(
    preco: schemas.PrecoReferenciaCreate,
    current_user: dict = Depends(get_current_user)
):
    # Verificar permissão
    if current_user["tipo_usuario"] not in ["admin", "bot"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Verificar se a ação existe
    acao = await acoes.find_one({"_id": ObjectId(preco.acao_id)})
    if not acao:
        raise HTTPException(status_code=404, detail="Ação não encontrada")
    
    # Criar preço de referência
    preco_dict = {
        "acao_id": preco.acao_id,
        "preco_referencia": preco.preco_referencia,
        "data_atualizacao": datetime.utcnow(),
        "atualizado_por": current_user["email"]
    }
    
    try:
        resultado = await precos_referencia.insert_one(preco_dict)
        preco_criado = await precos_referencia.find_one({"_id": resultado.inserted_id})
        return {
            "id": str(preco_criado["_id"]),
            "acao_id": preco_criado["acao_id"],
            "preco_referencia": preco_criado["preco_referencia"],
            "data_atualizacao": preco_criado["data_atualizacao"],
            "atualizado_por": preco_criado["atualizado_por"]
        }
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Já existe um preço de referência para esta ação")

@app.put("/api/precos/{acao_id}", response_model=schemas.PrecoReferenciaResponse)
async def atualizar_preco_referencia(
    acao_id: str,
    preco: schemas.PrecoReferenciaUpdate,
    current_user: dict = Depends(get_current_user)
):
    # Verificar permissão
    if current_user["tipo_usuario"] not in ["admin", "bot"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Atualizar preço
    resultado = await precos_referencia.find_one_and_update(
        {"acao_id": acao_id},
        {
            "$set": {
                "preco_referencia": preco.preco_referencia,
                "data_atualizacao": datetime.utcnow(),
                "atualizado_por": current_user["email"]
            }
        },
        return_document=True
    )
    
    if not resultado:
        raise HTTPException(status_code=404, detail="Preço de referência não encontrado")
    
    return {
        "id": str(resultado["_id"]),
        "acao_id": resultado["acao_id"],
        "preco_referencia": resultado["preco_referencia"],
        "data_atualizacao": resultado["data_atualizacao"],
        "atualizado_por": resultado["atualizado_por"]
    }

@app.get("/api/precos", response_model=List[schemas.PrecoReferenciaResponse])
async def listar_precos_referencia(_: dict = Depends(get_current_user)):
    cursor = precos_referencia.find()
    precos_list = await cursor.to_list(length=100)
    return [
        {
            "id": str(preco["_id"]),
            "acao_id": preco["acao_id"],
            "preco_referencia": preco["preco_referencia"],
            "data_atualizacao": preco["data_atualizacao"],
            "atualizado_por": preco["atualizado_por"]
        }
        for preco in precos_list
    ]

@app.get("/api/precos/{acao_id}", response_model=schemas.PrecoReferenciaResponse)
async def obter_preco_referencia(acao_id: str, _: dict = Depends(get_current_user)):
    preco = await precos_referencia.find_one({"acao_id": acao_id})
    if not preco:
        raise HTTPException(status_code=404, detail="Preço de referência não encontrado")
    
    return {
        "id": str(preco["_id"]),
        "acao_id": preco["acao_id"],
        "preco_referencia": preco["preco_referencia"],
        "data_atualizacao": preco["data_atualizacao"],
        "atualizado_por": preco["atualizado_por"]
    }

@app.patch("/api/carteira/nivel-risco/{usuario_id}")
async def atualizar_nivel_risco_carteira(usuario_id: str, nivel_risco: int, current_user: dict = Depends(get_current_user)):
    if current_user["tipo_usuario"] != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem alterar o nível de risco")
    
    if nivel_risco < 1 or nivel_risco > 5:
        raise HTTPException(status_code=400, detail="Nível de risco deve estar entre 1 e 5")
    
    resultado = await carteiras.update_one(
        {"usuario_id": ObjectId(usuario_id)},
        {"$set": {"nivel_risco": nivel_risco}}
    )
    
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")
    
    carteira_atualizada = await carteiras.find_one({"usuario_id": ObjectId(usuario_id)})
    return models.Carteira(**carteira_atualizada)

@app.post("/api/carteira/comprar")
async def comprar_acao(compra: schemas.CompraAcao, usuario: dict = Depends(get_current_user)):
    # Verificar se a ação existe
    acao = await acoes.find_one({"_id": ObjectId(compra.acao_id)})
    if not acao:
        raise HTTPException(status_code=404, detail="Ação não encontrada")
    
    # Verificar quantidade disponível
    if acao["qtd"] < compra.quantidade:
        raise HTTPException(status_code=400, detail="Quantidade indisponível")
    
    # Obter carteira do usuário
    carteira = await carteiras.find_one({"usuario_id": ObjectId(usuario["_id"])})
    if not carteira:
        carteira = {
            "usuario_id": ObjectId(usuario["_id"]),
            "acoes": [],
            "saldo": 0.0,
            "qtd_max_acoes": 100,
            "qtd_max_valor": 100000.0,
            "nivel_risco": 1  # Nível de risco padrão
        }
        resultado = await carteiras.insert_one(carteira)
        carteira["_id"] = resultado.inserted_id
    
    # Verificar nível de risco
    if acao.get("risco", 1) > carteira.get("nivel_risco", 1):
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível comprar esta ação. Seu nível de risco ({carteira.get('nivel_risco', 1)}) é menor que o risco da ação ({acao.get('risco', 1)})"
        )
    
    # Continuar com o resto da lógica de compra...