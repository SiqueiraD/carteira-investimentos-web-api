# API de Investimentos

API para gerenciamento de investimentos em ações, desenvolvida com FastAPI e MongoDB.

## Requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- MongoDB
- Git

## Configuração do Ambiente Local

1. **Clone o repositório**
   ```bash
   git clone [URL_DO_REPOSITORIO]
   cd investimentos-web-dev
   ```

2. **Crie e ative um ambiente virtual**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/MacOS
   python -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   - Crie um arquivo `.env` na raiz do projeto
   - Adicione as seguintes variáveis:
     ```env
     MONGODB_URL=sua_url_do_mongodb
     SECRET_KEY=sua_chave_secreta
     ```

## Executando a Aplicação

1. **Inicie o servidor de desenvolvimento**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Acesse a documentação da API**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Executando os Testes

```bash
# Executar todos os testes
pytest tests --doctest-modules --junitxml=junit/test-results.xml --cov=. --cov-report=xml

# Executar testes específicos
pytest tests/test_main.py -v
```

## Deploy no Azure

O projeto pode ser implantado no Azure usando os recursos criados pelo Terraform.

### Pré-requisitos

1. **Azure CLI** instalado e configurado
2. **WSL Ubuntu** para executar os scripts de deploy
3. **Terraform** para criar os recursos (opcional, se já não estiverem criados)

### Criando os Recursos (opcional)

Se os recursos ainda não existirem, você pode criá-los com o Terraform:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Deploy da Aplicação

1. **Preparar o ambiente WSL**
   ```bash
   # No Windows, abra o WSL Ubuntu
   wsl
   
   # Navegue até o diretório do projeto
   cd /mnt/c/Projetos/CascadeProjects/windsurf-project
   
   # Torne o script de deploy executável
   chmod +x deploy.sh
   ```

2. **Execute o script de deploy**
   ```bash
   ./deploy.sh
   ```

O script irá:
- Obter a chave do Cosmos DB
- Configurar as variáveis de ambiente no Web App
- Criar um arquivo de deploy
- Fazer o upload da aplicação
- Limpar os arquivos temporários

### Verificando o Deploy

1. Acesse a URL da aplicação:
   ```
   https://webapp-investimentos-api-003.azurewebsites.net
   ```

2. Verifique os logs no portal do Azure ou use o comando:
   ```bash
   az webapp log tail --name webapp-investimentos-api-003 --resource-group rg-investimentos-api-003
   ```

### Configuração de Ambiente

A aplicação suporta dois ambientes:

1. **Local**
   - Usa MongoDB local
   - Configurado através do arquivo `.env`
   - Ideal para desenvolvimento

2. **Produção (Azure)**
   - Usa Azure Cosmos DB com API MongoDB
   - Configurado através das variáveis de ambiente do Web App
   - Deploy automático via script

## Como Contribuir

1. **Fork o projeto**
   - Clique no botão "Fork" no canto superior direito da página

2. **Clone seu fork**
   ```bash
   git clone [URL_DO_SEU_FORK]
   ```

3. **Crie uma branch para sua feature**
   ```bash
   git checkout -b feature/nome-da-feature
   ```

4. **Faça suas alterações**
   - Siga o estilo de código do projeto
   - Adicione testes para novas funcionalidades
   - Mantenha a documentação atualizada

5. **Commit suas alterações**
   ```bash
   git commit -m "feat: adiciona nova funcionalidade"
   ```
   > Siga o padrão de commits convencionais:
   > - feat: nova funcionalidade
   > - fix: correção de bug
   > - docs: alteração na documentação
   > - test: adição/modificação de testes
   > - refactor: refatoração de código

6. **Push para seu fork**
   ```bash
   git push origin feature/nome-da-feature
   ```

7. **Crie um Pull Request**
   - Abra um PR do seu fork para o repositório principal
   - Descreva suas alterações detalhadamente
   - Referencie issues relacionadas

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Suporte

- Abra uma issue para reportar bugs ou sugerir melhorias
- Consulte a documentação da API para dúvidas sobre endpoints
- Entre em contato com a equipe de desenvolvimento para questões mais específicas

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

### Testes
- **Pytest**: Framework de testes
- **Requests**: Biblioteca HTTP para Python, utilizada nos testes de integração

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
