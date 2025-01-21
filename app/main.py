from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app import models, schemas, auth
from app.database import usuarios, acoes, carteiras, transacoes, notificacoes, relatorios, depositos, init_db
from app.config import get_settings
from typing import List
from bson import ObjectId
from datetime import datetime

# Configuração do FastAPI
app = FastAPI(
    title="API de Investimentos",
    description="API para gerenciamento de investimentos em ações",
    version="1.0.0"
)

# Inicializar o banco de dados durante a inicialização
init_db()

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
def read_root():
    return {"message": "Bem-vindo à API de Investimentos"}

# Middleware de autenticação
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return auth.get_current_user(credentials.credentials, credentials_exception)

# Rotas de autenticação
@app.post("/api/usuarios/registrar", response_model=schemas.Token, tags=["Autenticação"])
def registrar_usuario(usuario: schemas.UsuarioCreate):
    # Verificar se o email já existe
    if usuarios.find_one({"email": usuario.email}):
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    # Criar usuário
    usuario_dict = usuario.model_dump()
    usuario_dict["senha"] = auth.get_password_hash(usuario_dict["senha"])
    resultado = usuarios.insert_one(usuario_dict)
    
    # Gerar token
    token = auth.create_access_token(data={"sub": usuario.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "tipo_usuario": usuario.tipo_usuario
    }

@app.post("/api/usuarios/login", response_model=schemas.Token, tags=["Autenticação"])
def login(usuario: schemas.UsuarioLogin):
    user = auth.autenticar_usuario(usuario.email, usuario.senha)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth.create_access_token(data={"sub": usuario.email, "tipo_usuario": user["tipo_usuario"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "tipo_usuario": user["tipo_usuario"]
    }

# Rotas de ações
@app.get("/api/acoes", response_model=List[models.Acao], tags=["Ações"])
def listar_acoes(_: dict = Depends(get_current_user)):
    cursor = acoes.find()
    acoes_list = list(cursor)
    return [
        models.Acao(
            _id=str(acao["_id"]),
            nome=acao["nome"],
            preco=acao["preco"],
            qtd=acao["qtd"],
            risco=acao.get("risco", 1)  # Valor padrão 1 se não existir
        )
        for acao in acoes_list
    ]

@app.get("/api/acoes/{acao_id}", response_model=models.Acao, tags=["Ações"])
def obter_acao(acao_id: str, _: dict = Depends(get_current_user)):
    acao = acoes.find_one({"_id": ObjectId(acao_id)})
    if not acao:
        raise HTTPException(status_code=404, detail="Ação não encontrada")
    return models.Acao(
        _id=str(acao["_id"]),
        nome=acao["nome"],
        preco=acao["preco"],
        qtd=acao["qtd"],
        risco=acao.get("risco", 1)
    )

@app.post("/api/acoes/cadastrar", response_model=models.Acao, tags=["Ações"])
def cadastrar_acoes(acao: schemas.AcaoCreate, user: dict = Depends(get_current_user)):
    # Verificar permissões
    if user["tipo_usuario"] != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Criar ação
    acao_dict = acao.model_dump()
    resultado = acoes.insert_one(acao_dict)
    acao_criada = acoes.find_one({"_id": resultado.inserted_id})
    if not acao_criada:
        raise HTTPException(status_code=500, detail="Erro ao cadastrar ação")
    
    return models.Acao(
        _id=str(acao_criada["_id"]),
        nome=acao_criada["nome"],
        preco=acao_criada["preco"],
        qtd=acao_criada.get("qtd", 0),
        risco=acao_criada.get("risco", 1)
    )

@app.patch("/api/acoes/{acao_id}", response_model=models.Acao, tags=["Ações"])
def atualizar_acoes(acao_id: str, acao: schemas.AcaoUpdate, user: dict = Depends(get_current_user)):
    # Verificar permissões
    if user["tipo_usuario"] != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Verificar se a ação existe
    acao_atual = acoes.find_one({"_id": ObjectId(acao_id)})
    if not acao_atual:
        raise HTTPException(status_code=404, detail="Ação não encontrada")
    
    # Criar dicionário com os campos a serem atualizados
    atualizacao = {}
    if acao.preco is not None:
        atualizacao["preco"] = acao.preco
    if acao.qtd is not None:
        atualizacao["qtd"] = acao.qtd
    if acao.risco is not None:
        atualizacao["risco"] = acao.risco
    
    if not atualizacao:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    # Atualizar ação
    resultado = acoes.find_one_and_update(
        {"_id": ObjectId(acao_id)},
        {"$set": atualizacao},
        return_document=True
    )
    
    if not resultado:
        raise HTTPException(status_code=500, detail="Erro ao atualizar ação")
    
    return models.Acao(
        _id=str(resultado["_id"]),
        nome=resultado["nome"],
        preco=resultado["preco"],
        qtd=resultado.get("qtd", 0),
        risco=resultado.get("risco", 1)
    )

# Rotas de carteira
@app.get("/api/carteira", response_model=models.Carteira, tags=["Carteira"])
def obter_carteira(usuario: dict = Depends(get_current_user)):
    carteira = carteiras.find_one({"usuario_id": ObjectId(usuario["_id"])})
    if not carteira:
        # Criar carteira vazia se não existir
        carteira = {
            "usuario_id": ObjectId(usuario["_id"]),
            "acoes": [],
            "saldo": 0.0,
            "qtd_max_acoes": 100,
            "qtd_max_valor": 100000.0,
            "nivel_risco": 1
        }
        resultado = carteiras.insert_one(carteira)
        carteira["_id"] = resultado.inserted_id
    
    return models.Carteira(
        _id=str(carteira["_id"]),
        usuario_id=str(carteira["usuario_id"]),
        acoes=[
            models.CarteiraAcao(
                acao_id=str(acao["acao_id"]),
                qtd=acao["qtd"],
                preco_compra=acao.get("preco_compra", 0.0)
            )
            for acao in carteira["acoes"]
        ],
        saldo=carteira.get("saldo", 0.0),
        qtd_max_acoes=carteira.get("qtd_max_acoes", 100),
        qtd_max_valor=carteira.get("qtd_max_valor", 100000.0),
        nivel_risco=carteira.get("nivel_risco", 1)
    )

@app.post("/api/carteira/deposito", response_model=schemas.SolicitacaoDepositoResponse, tags=["Carteira"])
def solicitar_deposito(
    deposito: schemas.SolicitacaoDeposito,
    usuario: dict = Depends(get_current_user)
):
    # Criar solicitação de depósito
    deposito_dict = {
        "usuario_id": ObjectId(usuario["_id"]),
        "valor": deposito.valor,
        "descricao": deposito.descricao,
        "status": "pendente",
        "data_solicitacao": datetime.utcnow()
    }
    
    resultado = depositos.insert_one(deposito_dict)
    
    # Criar notificação para admins
    notificacao = {
        "tipo": "deposito_pendente",
        "usuario_id": None,  # None indica que é para todos os admins
        "mensagem": f"Nova solicitação de depósito de R$ {deposito.valor:.2f} do usuário {usuario['email']}",
        "data": datetime.utcnow(),
        "lida": False,
        "dados": {
            "deposito_id": str(resultado.inserted_id),
            "valor": deposito.valor,
            "usuario_email": usuario["email"]
        }
    }
    notificacoes.insert_one(notificacao)
    
    deposito_criado = depositos.find_one({"_id": resultado.inserted_id})
    return schemas.SolicitacaoDepositoResponse(
        id=str(deposito_criado["_id"]),
        usuario_id=str(deposito_criado["usuario_id"]),
        valor=deposito_criado["valor"],
        descricao=deposito_criado.get("descricao"),
        status=deposito_criado["status"],
        data_solicitacao=deposito_criado["data_solicitacao"],
        data_aprovacao=deposito_criado.get("data_aprovacao"),
        aprovado_por=deposito_criado.get("aprovado_por")
    )

@app.post("/api/carteira/deposito/{deposito_id}/aprovar", response_model=schemas.SolicitacaoDepositoResponse, tags=["Carteira"])
def aprovar_deposito(
    deposito_id: str,
    aprovacao: schemas.AprovarDeposito,
    current_user: dict = Depends(get_current_user)
):
    # Verificar permissão
    if current_user["tipo_usuario"] != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem aprovar depósitos")
    
    # Buscar depósito
    deposito = depositos.find_one({"_id": ObjectId(deposito_id)})
    if not deposito:
        raise HTTPException(status_code=404, detail="Depósito não encontrado")
    
    if deposito["status"] != "pendente":
        raise HTTPException(status_code=400, detail="Este depósito já foi processado")
    
    agora = datetime.utcnow()
    
    if aprovacao.aprovado:
        # Atualizar status do depósito
        depositos.update_one(
            {"_id": ObjectId(deposito_id)},
            {
                "$set": {
                    "status": "aprovado",
                    "data_aprovacao": agora,
                    "aprovado_por": current_user["email"]
                }
            }
        )
        
        # Atualizar saldo da carteira
        carteira = carteiras.find_one({"usuario_id": ObjectId(deposito["usuario_id"])})
        if not carteira:
            # Criar carteira se não existir
            carteira = {
                "usuario_id": ObjectId(deposito["usuario_id"]),
                "saldo": 0,
                "acoes": [],
                "qtd_max_acoes": 100,
                "qtd_max_valor": 100000.0,
                "nivel_risco": 1
            }
            carteiras.insert_one(carteira)
        
        # Atualizar saldo
        carteiras.update_one(
            {"usuario_id": ObjectId(deposito["usuario_id"])},
            {"$inc": {"saldo": deposito["valor"]}}
        )
        
        # Registrar transação
        transacao = {
            "usuario_id": ObjectId(deposito["usuario_id"]),
            "tipo": "deposito",
            "valor": deposito["valor"],
            "data": agora
        }
        transacoes.insert_one(transacao)
        
        # Criar notificação para o usuário
        notificacao = {
            "tipo": "deposito_aprovado",
            "usuario_id": str(deposito["usuario_id"]),
            "mensagem": f"Seu depósito de R$ {deposito['valor']:.2f} foi aprovado",
            "data": agora,
            "lida": False,
            "dados": {
                "deposito_id": deposito_id,
                "valor": deposito["valor"]
            }
        }
    else:
        # Atualizar status do depósito como rejeitado
        depositos.update_one(
            {"_id": ObjectId(deposito_id)},
            {
                "$set": {
                    "status": "rejeitado",
                    "data_aprovacao": agora,
                    "aprovado_por": current_user["email"],
                    "motivo_rejeicao": aprovacao.motivo_rejeicao
                }
            }
        )
        
        # Criar notificação para o usuário
        notificacao = {
            "tipo": "deposito_rejeitado",
            "usuario_id": str(deposito["usuario_id"]),
            "mensagem": f"Seu depósito de R$ {deposito['valor']:.2f} foi rejeitado. Motivo: {aprovacao.motivo_rejeicao}",
            "data": agora,
            "lida": False,
            "dados": {
                "deposito_id": deposito_id,
                "valor": deposito["valor"],
                "motivo": aprovacao.motivo_rejeicao
            }
        }
    
    notificacoes.insert_one(notificacao)
    
    deposito_atualizado = depositos.find_one({"_id": ObjectId(deposito_id)})
    return schemas.SolicitacaoDepositoResponse(
        id=str(deposito_atualizado["_id"]),
        usuario_id=str(deposito_atualizado["usuario_id"]),
        valor=deposito_atualizado["valor"],
        descricao=deposito_atualizado.get("descricao"),
        status=deposito_atualizado["status"],
        data_solicitacao=deposito_atualizado["data_solicitacao"],
        data_aprovacao=deposito_atualizado.get("data_aprovacao"),
        aprovado_por=deposito_atualizado.get("aprovado_por")
    )

@app.get("/api/depositos/pendentes", response_model=list[schemas.DepositoPendente])
def listar_depositos_pendentes(current_user: dict = Depends(get_current_user)):
    # Verificar se o usuário é admin
    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem visualizar depósitos pendentes"
        )

    try:
        # Buscar depósitos pendentes sem ordenação no banco
        depositos_temp = list(depositos.find({"status": "pendente"}))
        
        if not depositos_temp:
            return []
        
        # Criar um conjunto de IDs de usuário únicos
        user_ids = {dep["usuario_id"] for dep in depositos_temp}
        
        # Buscar informações dos usuários de uma vez
        usuarios_info = {
            str(u["_id"]): u["nome"] 
            for u in usuarios.find({"_id": {"$in": list(user_ids)}})
        }
        
        # Processar os depósitos com as informações dos usuários
        depositos_list = []
        for dep in depositos_temp:
            deposito_dict = {
                "id": str(dep["_id"]),
                "usuario_id": str(dep["usuario_id"]),
                "valor": dep["valor"],
                "descricao": dep["descricao"],
                "data_solicitacao": dep["data_solicitacao"],
                "status": dep["status"],
                "nome_usuario": usuarios_info.get(str(dep["usuario_id"]))
            }
            depositos_list.append(deposito_dict)
        
        # Ordenar a lista em memória por data_solicitacao (mais recentes primeiro)
        depositos_list.sort(key=lambda x: x["data_solicitacao"], reverse=True)
        
        return depositos_list
        
    except Exception as e:
        print(f"Erro ao listar depósitos pendentes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao listar depósitos pendentes"
        )

@app.post("/api/carteira/comprar", response_model=models.Carteira, tags=["Carteira"])
def comprar_acao(compra: schemas.CompraAcao, usuario: dict = Depends(get_current_user)):
    # Verificar se a ação existe
    acao = acoes.find_one({"_id": ObjectId(compra.acao_id)})
    if not acao:
        raise HTTPException(status_code=404, detail="Ação não encontrada")
    
    # Verificar quantidade disponível
    if acao["qtd"] < compra.quantidade:
        raise HTTPException(status_code=400, detail="Quantidade indisponível")
    
    # Obter carteira do usuário
    carteira = carteiras.find_one({"usuario_id": ObjectId(usuario["_id"])})
    if not carteira:
        carteira = {
            "usuario_id": ObjectId(usuario["_id"]),
            "acoes": [],
            "saldo": 0.0,
            "qtd_max_acoes": 100,
            "qtd_max_valor": 100000.0,
            "nivel_risco": 1
        }
        resultado = carteiras.insert_one(carteira)
        carteira["_id"] = resultado.inserted_id
    
    # Calcular valor total da compra
    valor_total = acao["preco"] * compra.quantidade
    
    # Verificar se há saldo suficiente
    if carteira["saldo"] < valor_total:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")
    
    # Verificar nível de risco
    if acao.get("risco", 1) > carteira.get("nivel_risco", 1):
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível comprar esta ação. Seu nível de risco ({carteira.get('nivel_risco', 1)}) é menor que o risco da ação ({acao.get('risco', 1)})"
        )
    
    # Verificar limites da carteira
    if len(carteira["acoes"]) >= carteira["qtd_max_acoes"]:
        raise HTTPException(status_code=400, detail="Limite de ações atingido")
    
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
            "qtd": compra.quantidade,
            "preco_compra": acao["preco"]  # Registrar preço de compra
        })
    
    # Atualizar saldo da carteira
    carteira["saldo"] -= valor_total
    
    # Atualizar banco de dados
    carteiras.update_one(
        {"_id": carteira["_id"]},
        {"$set": carteira}
    )
    
    acoes.update_one(
        {"_id": ObjectId(compra.acao_id)},
        {"$inc": {"qtd": -compra.quantidade}}
    )
    
    # Registrar transação
    transacao = {
        "usuario_id": ObjectId(usuario["_id"]),
        "acao_id": ObjectId(compra.acao_id),
        "tipo": "compra",
        "qtd": compra.quantidade,
        "valor": valor_total,
        "preco_unitario": acao["preco"],
        "data": datetime.utcnow()
    }
    transacoes.insert_one(transacao)
    
    # Retornar carteira atualizada com preços de compra
    carteira_atualizada = carteiras.find_one({"_id": carteira["_id"]})
    return models.Carteira(
        _id=str(carteira_atualizada["_id"]),
        usuario_id=str(carteira_atualizada["usuario_id"]),
        acoes=[
            models.CarteiraAcao(
                acao_id=str(acao["acao_id"]),
                qtd=acao["qtd"],
                preco_compra=acao.get("preco_compra", 0.0)
            )
            for acao in carteira_atualizada["acoes"]
        ],
        saldo=carteira_atualizada["saldo"],
        qtd_max_acoes=carteira_atualizada.get("qtd_max_acoes", 100),
        qtd_max_valor=carteira_atualizada.get("qtd_max_valor", 100000.0),
        nivel_risco=carteira_atualizada.get("nivel_risco", 1)
    )

@app.patch("/api/carteiras/{usuario_id}/limites", response_model=models.Carteira, tags=["Carteira"])
def atualizar_limites_carteira(
    usuario_id: str,
    limites: schemas.CarteiraLimites,
    current_user: dict = Depends(get_current_user)
):
    # Verificar permissões
    if current_user["tipo_usuario"] != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem alterar os limites da carteira")
    
    # Criar dicionário com os campos a serem atualizados
    updates = {}
    if limites.nivel_risco is not None:
        updates["nivel_risco"] = limites.nivel_risco
    if limites.qtd_max_acoes is not None:
        updates["qtd_max_acoes"] = limites.qtd_max_acoes
    if limites.qtd_max_valor is not None:
        updates["qtd_max_valor"] = limites.qtd_max_valor
    
    if not updates:
        raise HTTPException(status_code=400, detail="Nenhum limite para atualizar foi fornecido")
    
    # Atualizar limites
    resultado = carteiras.update_one(
        {"usuario_id": ObjectId(usuario_id)},
        {"$set": updates}
    )
    
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")
    
    # Retornar carteira atualizada
    carteira_atualizada = carteiras.find_one({"usuario_id": ObjectId(usuario_id)})
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
        qtd_max_valor=carteira_atualizada.get("qtd_max_valor", 100000.0),
        nivel_risco=carteira_atualizada.get("nivel_risco", 1)
    )

@app.get("/api/carteiras", response_model=List[schemas.CarteiraComUsuario], tags=["Carteira"])
def listar_carteiras(current_user: dict = Depends(get_current_user)):
    # Verificar permissões
    if current_user.get("tipo_usuario") not in ["admin", "bot"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Buscar todas as carteiras
    cursor = carteiras.find()
    carteiras_list = list(cursor)
    
    # Para cada carteira, buscar informações do usuário
    resultado = []
    for carteira in carteiras_list:
        usuario = usuarios.find_one({"_id": carteira["usuario_id"]})
        if usuario:
            resultado.append({
                "_id": str(carteira["_id"]),
                "usuario_id": str(carteira["usuario_id"]),
                "usuario_nome": usuario["nome"],
                "usuario_email": usuario["email"],
                "acoes": [
                    {
                        "acao_id": str(acao["acao_id"]),
                        "qtd": acao["qtd"]
                    }
                    for acao in carteira["acoes"]
                ],
                "saldo": carteira.get("saldo", 0.0),
                "qtd_max_acoes": carteira.get("qtd_max_acoes", 100),
                "qtd_max_valor": carteira.get("qtd_max_valor", 100000.0),
                "nivel_risco": carteira.get("nivel_risco", 1)
            })
    
    return resultado

@app.get("/api/carteiras/{usuario_id}", response_model=models.Carteira, tags=["Carteira"])
def buscar_carteira_por_usuario(usuario_id: str, current_user: dict = Depends(get_current_user)):
    # Verificar se o usuário existe
    usuario = usuarios.find_one({"_id": ObjectId(usuario_id)})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar permissões (apenas admin/bot ou o próprio usuário pode ver a carteira)
    if current_user.get("tipo_usuario") not in ["admin", "bot"] and str(current_user["_id"]) != usuario_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Buscar carteira
    carteira = carteiras.find_one({"usuario_id": ObjectId(usuario_id)})
    if not carteira:
        # Criar carteira vazia se não existir
        carteira = {
            "usuario_id": ObjectId(usuario_id),
            "acoes": [],
            "saldo": 0.0,
            "qtd_max_acoes": 100,
            "qtd_max_valor": 100000.0,
            "nivel_risco": 1
        }
        resultado = carteiras.insert_one(carteira)
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
        qtd_max_valor=carteira.get("qtd_max_valor", 100000.0),
        nivel_risco=carteira.get("nivel_risco", 1)
    )