# Configurações do MySQL
$MYSQL_ROOT_PASSWORD="root"
$MYSQL_DATABASE="investimentos"
$CONTAINER_NAME="mysql-investimentos"
$HOST_PORT="3306"

# Verifica se o container já existe
$containerExists = docker ps -a --filter "name=$CONTAINER_NAME" --format '{{.Names}}'

if ($containerExists) {
    Write-Host "Removendo container existente..."
    docker rm -f $CONTAINER_NAME
}

# Cria e inicia o container MySQL
Write-Host "Criando novo container MySQL..."
docker run --name $CONTAINER_NAME `
    -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD `
    -e MYSQL_DATABASE=$MYSQL_DATABASE `
    -p ${HOST_PORT}:3306 `
    -d mysql:8.0

# Aguarda o MySQL iniciar completamente
Write-Host "Aguardando MySQL iniciar..."
Start-Sleep -Seconds 30

# Verifica se o container está rodando
$isRunning = docker ps --filter "name=$CONTAINER_NAME" --format '{{.Names}}'
if ($isRunning) {
    Write-Host "MySQL está rodando!"
    Write-Host "Credenciais:"
    Write-Host "Host: localhost"
    Write-Host "Port: $HOST_PORT"
    Write-Host "Database: $MYSQL_DATABASE"
    Write-Host "Username: root"
    Write-Host "Password: $MYSQL_ROOT_PASSWORD"
    Write-Host ""
    Write-Host "Para conectar via linha de comando:"
    Write-Host "docker exec -it $CONTAINER_NAME mysql -uroot -p$MYSQL_ROOT_PASSWORD"
} else {
    Write-Host "Erro: MySQL não está rodando!"
    exit 1
}

# Executa as migrações do Alembic
Write-Host "Executando migrações do banco de dados..."
alembic upgrade head

Write-Host "Configuração completa!"