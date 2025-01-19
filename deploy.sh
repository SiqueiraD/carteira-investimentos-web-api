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

# Criar arquivo .env para produção
cat > .env.prod << EOL
ENVIRONMENT=prod
MONGODB_URL=mongodb://$COSMOS_ACCOUNT:$COSMOS_KEY@$COSMOS_ACCOUNT.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000
JWT_SECRET=$(openssl rand -hex 32)
LOG_LEVEL=INFO
EOL

# Configurar as variáveis de ambiente no Web App
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings @.env.prod \
    WEBSITES_PORT=8000 \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    PYTHON_ENABLE_GUNICORN_MULTIWORKERS=1 \
    PYTHONPATH="/home/site/wwwroot"

# Configurar o Python runtime e startup file
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "startup.sh" \
    --linux-fx-version "PYTHON|3.10"

# Inicializar repositório git local se não existir
if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial commit"
fi

# Obter as credenciais de publicação
CREDS=$(az webapp deployment list-publishing-credentials \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "[?name=='web'].{url:url, username:username, password:password}[0]" \
    --output json)

GIT_URL=$(echo $CREDS | jq -r '.url')
GIT_USERNAME=$(echo $CREDS | jq -r '.username')
GIT_PASSWORD=$(echo $CREDS | jq -r '.password')

# Configurar remote do Azure se não existir
if ! git remote | grep -q "azure"; then
    git remote add azure "https://$GIT_USERNAME:$GIT_PASSWORD@$APP_NAME.scm.azurewebsites.net/$APP_NAME.git"
fi

# Deploy para o Azure Web App
echo "Iniciando deploy para $APP_NAME..."
git add .
git commit -m "Deploy update $(date)"
git push azure master --force

# Limpar arquivo de ambiente
rm .env.prod

echo "Deploy concluído!"

# Reiniciar a aplicação
echo "Reiniciando a aplicação..."
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

echo "Processo de deploy finalizado com sucesso!"
