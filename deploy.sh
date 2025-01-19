#!/bin/bash

# Configurações
RESOURCE_GROUP="rg-investimentos-api-003"
APP_NAME="webapp-investimentos-api-003"
COSMOS_ACCOUNT="investimentos-api-003"
DEPLOYMENT_SOURCE="."

# Obter a chave primária do Cosmos DB
COSMOS_KEY=$(az cosmosdb keys list \
    --name $COSMOS_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --query primaryMasterKey \
    --output tsv)

# Configurar as variáveis de ambiente no Web App
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    ENVIRONMENT="prod" \
    MONGODB_URL="mongodb://$COSMOS_ACCOUNT:$COSMOS_KEY@$COSMOS_ACCOUNT.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000" \
    JWT_SECRET="fixed-secret2" \
    LOG_LEVEL="INFO" \
    WEBSITES_PORT="8000" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    PYTHON_ENABLE_GUNICORN_MULTIWORKERS="1" \
    PYTHONPATH="/home/site/wwwroot"

# Configurar o Python runtime e startup file
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "startup.sh" \
    --linux-fx-version "PYTHON|3.10"

# Criar arquivo __init__.py no diretório config se não existir
mkdir -p app/config
touch app/config/__init__.py

# Compactar a aplicação excluindo arquivos desnecessários
echo "Compactando arquivos para deploy..."
zip -r deployment.zip . \
    -x "*.git*" \
    -x "*.env*" \
    -x "*venv*" \
    -x "*__pycache__*" \
    -x "*.pytest_cache*" \
    -x "deployment.zip" \
    -x "*.pyc" \
    -x "tests/*" \
    -x "terraform/*" \
    -x "banco-de-dados/*" \
    -x "casos-de-uso/*" \
    -x "descricao-api/*"

# Deploy usando o novo comando az webapp deploy
echo "Iniciando deploy para $APP_NAME..."
az webapp deploy \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --src-path deployment.zip \
    --type zip \
    --async false

# Limpar arquivos temporários
rm deployment.zip

echo "Deploy concluído!"

# Reiniciar a aplicação
echo "Reiniciando a aplicação..."
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

echo "Processo de deploy finalizado com sucesso!"
