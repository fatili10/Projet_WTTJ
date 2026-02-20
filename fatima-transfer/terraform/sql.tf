# =============================================================================
# SQL Server et Database Configuration
# =============================================================================

# -----------------------------------------------------------------------------
# SQL Server
# -----------------------------------------------------------------------------

resource "azurerm_mssql_server" "main" {
  name                         = var.sql_server_name
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_login
  administrator_login_password = var.sql_admin_password

  # Configuration de sécurité
  minimum_tls_version           = "1.2"
  public_network_access_enabled = true

  tags = var.tags
}

# -----------------------------------------------------------------------------
# SQL Database - Serverless Gen5
# Configuration: GP_S_Gen5_1 (General Purpose Serverless)
# -----------------------------------------------------------------------------

resource "azurerm_mssql_database" "wttj" {
  name                 = var.sql_database_name
  server_id            = azurerm_mssql_server.main.id
  collation            = "SQL_Latin1_General_CP1_CI_AS"
  max_size_gb          = var.sql_database_sku_name == "Basic" ? 2 : var.sql_database_max_size_gb
  sku_name             = var.sql_database_sku_name
  zone_redundant       = false
  read_scale           = false
  storage_account_type = "Local"

  # Configuration Serverless (seulement pour SKU GP_S_*)
  auto_pause_delay_in_minutes = startswith(var.sql_database_sku_name, "GP_S_") ? var.sql_database_auto_pause_delay : null
  min_capacity                = startswith(var.sql_database_sku_name, "GP_S_") ? var.sql_database_min_capacity : null

  tags = var.tags
}

# -----------------------------------------------------------------------------
# SQL Server Firewall Rules
# -----------------------------------------------------------------------------

# Règle pour autoriser les services Azure
resource "azurerm_mssql_firewall_rule" "allow_azure_services" {
  count            = var.allow_azure_services ? 1 : 0
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Règles de firewall personnalisées
resource "azurerm_mssql_firewall_rule" "custom_rules" {
  for_each         = { for rule in var.sql_firewall_rules : rule.name => rule }
  name             = each.value.name
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = each.value.start_ip_address
  end_ip_address   = each.value.end_ip_address
}
