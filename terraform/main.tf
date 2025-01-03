resource "azurerm_resource_group" "rg" {
  name     = "rg-investimentos-api-003"
  location = "eastus2"
  
  tags = {
    environment = "development"
    managed-by  = "terraform"
  }
}

# Virtual Network
resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-investimentos-api-003"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  address_space       = ["10.0.0.0/16"]

  tags = {
    environment = "development"
    managed-by  = "terraform"
  }
}

# Subnet for Web App
resource "azurerm_subnet" "webapp_subnet" {
  name                 = "snet-webapp-investimentos-api-003"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
  delegation {
    name = "webapp-delegation"
    service_delegation {
      name    = "Microsoft.Web/serverFarms"
      actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
    }
  }
}

# Subnet for Cosmos DB
resource "azurerm_subnet" "cosmos_subnet" {
  name                 = "snet-cosmos-investimentos-api-003"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.2.0/24"]
  service_endpoints    = ["Microsoft.AzureCosmosDB"]
}

resource "azurerm_service_plan" "app_service_plan" {
  name                = "asp-investimentos-api-003"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type            = "Linux"
  sku_name           = "B1"  # Changed to B1 to support VNet integration

  tags = {
    environment = "development"
    managed-by  = "terraform"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "azurerm_linux_web_app" "web_app" {
  name                = "webapp-investimentos-api-003"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  service_plan_id     = azurerm_service_plan.app_service_plan.id

  depends_on = [
    azurerm_service_plan.app_service_plan
  ]

  site_config {
    application_stack {
      python_version = "3.10"
    }
    always_on = true  # Changed to true for better reliability
  }

  app_settings = {
    "WEBSITE_RUN_FROM_PACKAGE" = "1"
    "WEBSITES_PORT"            = "8000"
    "ENVIRONMENT"             = "prod"
  }

  tags = {
    environment = "development"
    managed-by  = "terraform"
  }
}

# Web App VNet Integration
resource "azurerm_app_service_virtual_network_swift_connection" "vnet_integration" {
  app_service_id = azurerm_linux_web_app.web_app.id
  subnet_id      = azurerm_subnet.webapp_subnet.id
}

# Cosmos DB Account
resource "azurerm_cosmosdb_account" "mongodb" {
  name                = "investimentos-api-003"  # Changed to match the hostname in connection string
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  offer_type         = "Standard"
  kind               = "MongoDB"

  capabilities {
    name = "EnableMongo"
  }

  capabilities {
    name = "EnableServerless"
  }

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = azurerm_resource_group.rg.location
    failover_priority = 0
  }

  # Enable virtual network filtering
  is_virtual_network_filter_enabled = true
  
  # Virtual Network Rules
  virtual_network_rule {
    id = azurerm_subnet.cosmos_subnet.id
  }

  # IP Range Filter - Allow Azure services and resources
  ip_range_filter = "0.0.0.0"

  tags = {
    environment = "development"
    managed-by  = "terraform"
  }
}

# Cosmos DB Database
resource "azurerm_cosmosdb_mongo_database" "mongodb" {
  name                = "investimentos"
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.mongodb.name
}