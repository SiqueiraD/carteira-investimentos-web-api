resource "azurerm_resource_group" "rg" {
  name     = "rg-investimentos-api-003"
  location = "eastus2"
  
  tags = {
    environment = "development"
    managed-by  = "terraform"
  }
}

resource "azurerm_service_plan" "app_service_plan" {
  name                = "asp-investimentos-api-003"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type            = "Linux"
  sku_name           = "F1"

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
    always_on = false
  }

  app_settings = {
    "WEBSITE_RUN_FROM_PACKAGE" = "1"
  }

  tags = {
    environment = "development"
    managed-by  = "terraform"
  }
}

# Cosmos DB Account
resource "azurerm_cosmosdb_account" "mongodb" {
  name                = "cosmos-investimentos-api-003"
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