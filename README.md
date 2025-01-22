# Investimentos Web

Sistema web para gerenciamento de investimentos, permitindo que usuários realizem operações de compra e venda de ações, além de acompanhar seu portfólio.

## Demonstração

Uma versão de demonstração da API está disponível para testes:
- **Documentação Swagger**: [https://webapp-investimentos-api-003.azurewebsites.net/docs](https://webapp-investimentos-api-003.azurewebsites.net/docs)

Para testar a API, você pode:
1. Registrar um novo usuário em `/api/usuarios/registrar`
2. Fazer login em `/api/usuarios/login`
3. Usar o token JWT retornado para acessar os demais endpoints

> **Nota**: Esta é uma versão de demonstração temporária para avaliação.

## Requisitos

- Python 3.11 ou superior
- MongoDB ou Azure Cosmos DB com API do MongoDB
- Variáveis de ambiente configuradas (ver seção de Configuração)

## Configuração

1. Clone o repositório
2. Crie e ative um ambiente virtual Python
3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
# Desenvolvimento
ENVIRONMENT=development
MONGODB_URL=sua_url_mongodb
JWT_SECRET=sua_chave_secreta

# Produção
ENVIRONMENT=production
MONGODB_URL=sua_url_cosmosdb
JWT_SECRET=sua_chave_secreta
API_BASE_URL=sua_url_base
```

## Como Executar

1. Certifique-se que o MongoDB está rodando
2. Execute o servidor:
```bash
uvicorn app.main:app --reload
```

3. Acesse a documentação da API em:
```
http://localhost:8000/docs
```

## Estrutura do Projeto

```
.
├── app/
│   ├── __init__.py
│   ├── main.py          # Endpoints da API
│   ├── auth.py          # Autenticação e autorização
│   ├── database.py      # Configuração do banco de dados
│   ├── models.py        # Modelos de dados
│   └── schemas.py       # Schemas de validação
├── tests/               # Testes da aplicação
├── requirements.txt     # Dependências do projeto
└── README.md           # Este arquivo
```

## Tecnologias Principais

### Backend
- **FastAPI**: Framework web moderno e rápido para construção de APIs com Python
- **PyMongo**: Driver oficial do MongoDB para Python, usado para interação com o banco de dados
- **Python-Jose**: Biblioteca para manipulação de tokens JWT (JSON Web Tokens)
- **Pydantic**: Biblioteca para validação de dados e gerenciamento de configurações
- **Uvicorn**: Servidor ASGI de alta performance para Python

### Banco de Dados
- **MongoDB**: Banco de dados NoSQL utilizado para armazenamento dos dados
- **Azure Cosmos DB API for MongoDB**: Serviço de banco de dados distribuído da Microsoft

### Segurança
- **Passlib**: Biblioteca para hash de senhas
- **Python-Multipart**: Suporte para formulários multipart
- **JWT (JSON Web Tokens)**: Para autenticação e autorização de usuários

## Infraestrutura na Azure

O projeto é hospedado na Azure usando uma arquitetura moderna e escalável:

### Componentes Principais

- **Azure App Service**: Hospeda a API FastAPI em um ambiente gerenciado
  - Configurado com Python 3.11
  - Escalamento automático baseado em carga
  - SSL/TLS habilitado por padrão

- **Azure Cosmos DB**: Banco de dados distribuído
  - API compatível com MongoDB
  - Escalabilidade global
  - Backups automáticos
  - Baixa latência para operações de leitura/escrita

- **Azure Key Vault**: Gerenciamento seguro de segredos
  - Armazena chaves de API e credenciais
  - Rotação automática de segredos
  - Integração com identidades gerenciadas

### Monitoramento e Logging

- **Application Insights**: Telemetria e monitoramento
  - Rastreamento de requisições
  - Métricas de performance
  - Logs de aplicação
  - Alertas configuráveis

- **Azure Monitor**: Monitoramento da infraestrutura
  - Métricas do App Service
  - Uso do Cosmos DB
  - Dashboards personalizados

### Segurança

- **Azure AD**: Gerenciamento de identidades
  - Autenticação de serviços
  - Identidades gerenciadas
  - Controle de acesso baseado em papéis (RBAC)

- **Azure Front Door**: CDN e WAF
  - Proteção contra DDoS
  - SSL/TLS gerenciado
  - Regras de segurança personalizadas

### Diagrama de Arquitetura

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Azure Front   │     │              │     │   Cosmos DB  │
│     Door       │────▶│  App Service  │────▶│  MongoDB API │
└─────────────────┘     │   (FastAPI)  │     └─────────────┘
                        └──────────────┘            ▲
                              │                     │
                              ▼                     │
                        ┌──────────────┐     ┌─────────────┐
                        │   Key Vault  │     │Application  │
                        │             │     │  Insights   │
                        └──────────────┘     └─────────────┘
```

## Funcionalidades

- **Usuários**
  - Registro e autenticação
  - Perfis: admin e comum
  - Gerenciamento de carteira

- **Investimentos**
  - Compra e venda de ações
  - Acompanhamento de carteira
  - Histórico de transações

- **Depósitos**
  - Solicitação de depósitos
  - Aprovação por administradores
  - Controle de limites

## Endpoints da API

### Usuários
- `POST /api/usuarios/registrar`: Registro de novo usuário
- `POST /api/usuarios/login`: Login de usuário

### Carteira
- `GET /api/carteira`: Consulta carteira do usuário
- `POST /api/carteira/comprar`: Compra de ações
- `POST /api/carteira/vender`: Venda de ações
- `POST /api/carteira/deposito`: Solicita depósito

### Ações
- `GET /api/acoes`: Lista ações disponíveis
- `POST /api/acoes/cadastrar`: Cadastra nova ação (admin)

### Depósitos
- `GET /api/depositos/pendentes`: Lista depósitos pendentes (admin)
- `POST /api/carteira/deposito/{id}/aprovar`: Aprova/rejeita depósito (admin)

