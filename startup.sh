#!/bin/bash

# Navegar para o diretório do aplicativo
cd /home/site/wwwroot

# Configurar variáveis de ambiente
export PYTHONPATH=/home/site/wwwroot
export PORT=8000

# Criar e ativar ambiente virtual
python -m venv antenv
source antenv/bin/activate

# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt

# Iniciar a aplicação com Gunicorn
exec gunicorn app.main:app --bind=0.0.0.0:8000 --timeout 600 --worker-class uvicorn.workers.UvicornWorker