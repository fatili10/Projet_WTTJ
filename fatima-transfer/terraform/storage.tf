# =============================================================================
# Storage Accounts Configuration
# =============================================================================

# -----------------------------------------------------------------------------
# Storage Account ADLS Gen2 (Data Lake)
# Utilisé pour les données Data Lake avec Hierarchical Namespace activé
# -----------------------------------------------------------------------------

resource "azurerm_storage_account" "adls" {
  name                     = var.adls_storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = var.adls_replication_type
  account_kind             = "StorageV2"

  # ADLS Gen2 - Hierarchical Namespace activé
  is_hns_enabled = true

  # Configuration de sécurité
  min_tls_version                  = "TLS1_2"
  allow_nested_items_to_be_public  = false
  cross_tenant_replication_enabled = false
  shared_access_key_enabled        = true
  public_network_access_enabled    = true
  https_traffic_only_enabled       = true

  # Tier d'accès
  access_tier = "Hot"

  # Large file shares
  large_file_share_enabled = true

  # Configuration réseau
  network_rules {
    default_action = "Allow"
    bypass         = ["AzureServices"]
  }

  # Encryption
  blob_properties {
    versioning_enabled = false
  }

  tags = var.tags
}

# Containers ADLS
resource "azurerm_storage_container" "adls_containers" {
  for_each              = toset(var.adls_containers)
  name                  = each.value
  storage_account_name  = azurerm_storage_account.adls.name
  container_access_type = "private"
}

# -----------------------------------------------------------------------------
# Storage Account Blob Standard
# Utilisé pour le stockage Blob classique sans HNS
# -----------------------------------------------------------------------------

resource "azurerm_storage_account" "blob" {
  name                     = var.blob_storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = var.blob_replication_type
  account_kind             = "StorageV2"

  # Pas de Hierarchical Namespace (Blob standard)
  is_hns_enabled = false

  # Configuration de sécurité
  min_tls_version                  = "TLS1_2"
  allow_nested_items_to_be_public  = false
  cross_tenant_replication_enabled = false
  shared_access_key_enabled        = true
  public_network_access_enabled    = true
  https_traffic_only_enabled       = true

  # Tier d'accès
  access_tier = "Hot"

  # Large file shares
  large_file_share_enabled = true

  # Configuration réseau
  network_rules {
    default_action = "Allow"
    bypass         = ["AzureServices"]
  }

  tags = var.tags
}

# Containers Blob
resource "azurerm_storage_container" "blob_containers" {
  for_each              = toset(var.blob_containers)
  name                  = each.value
  storage_account_name  = azurerm_storage_account.blob.name
  container_access_type = "private"
}
