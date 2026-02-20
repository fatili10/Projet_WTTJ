# =============================================================================
# Outputs Terraform
# =============================================================================

# -----------------------------------------------------------------------------
# Resource Group
# -----------------------------------------------------------------------------

output "resource_group_name" {
  description = "Nom du resource group créé"
  value       = azurerm_resource_group.main.name
}

output "resource_group_id" {
  description = "ID du resource group"
  value       = azurerm_resource_group.main.id
}

# -----------------------------------------------------------------------------
# Storage Account ADLS
# -----------------------------------------------------------------------------

output "adls_storage_account_name" {
  description = "Nom du storage account ADLS Gen2"
  value       = azurerm_storage_account.adls.name
}

output "adls_storage_account_id" {
  description = "ID du storage account ADLS Gen2"
  value       = azurerm_storage_account.adls.id
}

output "adls_primary_blob_endpoint" {
  description = "Endpoint Blob primaire du storage ADLS"
  value       = azurerm_storage_account.adls.primary_blob_endpoint
}

output "adls_primary_dfs_endpoint" {
  description = "Endpoint DFS (Data Lake) primaire"
  value       = azurerm_storage_account.adls.primary_dfs_endpoint
}

output "adls_primary_access_key" {
  description = "Clé d'accès primaire du storage ADLS"
  value       = azurerm_storage_account.adls.primary_access_key
  sensitive   = true
}

# -----------------------------------------------------------------------------
# Storage Account Blob
# -----------------------------------------------------------------------------

output "blob_storage_account_name" {
  description = "Nom du storage account Blob"
  value       = azurerm_storage_account.blob.name
}

output "blob_storage_account_id" {
  description = "ID du storage account Blob"
  value       = azurerm_storage_account.blob.id
}

output "blob_primary_blob_endpoint" {
  description = "Endpoint Blob primaire du storage Blob"
  value       = azurerm_storage_account.blob.primary_blob_endpoint
}

output "blob_primary_access_key" {
  description = "Clé d'accès primaire du storage Blob"
  value       = azurerm_storage_account.blob.primary_access_key
  sensitive   = true
}

# -----------------------------------------------------------------------------
# SQL Server
# -----------------------------------------------------------------------------

output "sql_server_name" {
  description = "Nom du serveur SQL"
  value       = azurerm_mssql_server.main.name
}

output "sql_server_fqdn" {
  description = "FQDN du serveur SQL"
  value       = azurerm_mssql_server.main.fully_qualified_domain_name
}

output "sql_server_id" {
  description = "ID du serveur SQL"
  value       = azurerm_mssql_server.main.id
}

# -----------------------------------------------------------------------------
# SQL Database
# -----------------------------------------------------------------------------

output "sql_database_name" {
  description = "Nom de la base de données SQL"
  value       = azurerm_mssql_database.wttj.name
}

output "sql_database_id" {
  description = "ID de la base de données SQL"
  value       = azurerm_mssql_database.wttj.id
}

output "sql_connection_string" {
  description = "Chaîne de connexion SQL Server (sans mot de passe)"
  value       = "Server=tcp:${azurerm_mssql_server.main.fully_qualified_domain_name},1433;Database=${azurerm_mssql_database.wttj.name};User ID=${var.sql_admin_login};Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"
  sensitive   = false
}
