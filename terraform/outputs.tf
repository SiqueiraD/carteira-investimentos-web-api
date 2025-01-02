output "web_app_name" {
  value = azurerm_linux_web_app.web_app.name
  description = "Nome do App Service"
}

output "web_app_url" {
  value = azurerm_linux_web_app.web_app.default_hostname
  description = "URL do App Service"
}

output "mongodb_connection_string" {
  value     = azurerm_cosmosdb_account.mongodb.connection_strings[0]
  sensitive = true
}