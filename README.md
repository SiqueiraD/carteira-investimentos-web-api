# Investment API

API de gerenciamento de investimentos com suporte para execução local e na nuvem Azure.

## Requisitos

- Python 3.8+
- MongoDB (para desenvolvimento local)
- Azure CLI (para deploy na nuvem)
- Terraform (para infraestrutura na nuvem)

## Configuração do Ambiente

### 1. Ambiente Local

1. Instale o MongoDB Community Edition:
   - Windows: [MongoDB Windows Installation Guide](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/)
   - Inicie o serviço MongoDB

2. Configure o ambiente Python:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente:
   ```bash
   copy .env.example .env
   ```
   - Edite o arquivo `.env` com suas configurações

4. Execute a aplicação:
   ```bash
   python local.py
   ```
   A API estará disponível em `http://localhost:8000`
   Documentação Swagger: `http://localhost:8000/docs`

### 2. Deploy na Azure

1. Login na Azure:
   ```bash
   az login
   ```

2. Configure as credenciais do Terraform:
   ```bash
   az account set --subscription "YOUR_SUBSCRIPTION_ID"
   ```

3. Inicialize e aplique a infraestrutura Terraform:
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

4. Configure as variáveis de ambiente da produção:
   - Copie as variáveis de saída do Terraform
   - Atualize o arquivo `.env` com os valores de produção

5. Deploy da aplicação:
   ```bash
   az functionapp deployment source config-zip -g YOUR_RESOURCE_GROUP -n YOUR_FUNCTION_APP_NAME --src dist/function.zip
   ```

## Estrutura do Projeto

```
.
├── app/
│   ├── __init__.py
│   ├── main.py          # Aplicação FastAPI
│   ├── config.py        # Configurações
│   ├── models.py        # Modelos Pydantic
│   ├── schemas.py       # Schemas de validação
│   ├── database.py      # Conexão MongoDB
│   └── auth.py          # Autenticação JWT
├── terraform/
│   ├── main.tf          # Recursos Azure
│   ├── variables.tf     # Variáveis Terraform
│   └── outputs.tf       # Outputs Terraform
├── requirements.txt     # Dependências Python
├── local.py            # Servidor desenvolvimento
├── function_app.py     # Entrada Azure Functions
└── README.md
```

## Endpoints da API

- `POST /api/usuarios/registrar`: Registro de usuário
- `POST /api/usuarios/login`: Login de usuário
- `GET /api/acoes`: Lista de ações disponíveis
- `POST /api/carteira/comprar`: Compra de ações
- `PATCH /api/carteiras/{usuario_id}/limites`: Atualiza limites da carteira (admin)
- `POST /api/relatorios/gerar`: Gera relatório de investimentos
- `GET /api/relatorios`: Lista relatórios do usuário

## Segurança

- Autenticação JWT
- Azure Key Vault para segredos em produção
- HTTPS em produção
- Validação de dados com Pydantic

## Monitoramento

- Azure Application Insights para logs e métricas
- Monitoramento de performance com Azure Functions
- Logs de transações no MongoDB
