#!/bin/bash

# Garantir que estamos no diretório correto
cd /home/site/wwwroot

# Dar permissões de execução ao script
chmod +x startup.sh

# Configurar ambiente Python
export PYTHONPATH=/home/site/wwwroot
export PORT=8000

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
export ENVIRONMENT="prod"
export MONGODB_URL="mongodb://localhost:27017"

# Iniciar a aplicação com Gunicorn
exec gunicorn app.main:app --bind=0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker --timeout 600