# =============================================================================
# Variables Terraform pour le déploiement des ressources Azure
# Resource Group: RG_FELJATTIOUI (source)
# =============================================================================

# -----------------------------------------------------------------------------
# Configuration générale
# -----------------------------------------------------------------------------

variable "resource_group_name" {
  description = "Nom du resource group à créer"
  type        = string
  default     = "RG_FELJATTIOUI"
}

variable "location" {
  description = "Région Azure pour le déploiement"
  type        = string
  default     = "francecentral"
}

variable "tags" {
  description = "Tags à appliquer aux ressources"
  type        = map(string)
  default     = {}
}

# -----------------------------------------------------------------------------
# Storage Account ADLS Gen2 (Data Lake)
# -----------------------------------------------------------------------------

variable "adls_storage_account_name" {
  description = "Nom du storage account ADLS Gen2 (doit être unique globalement)"
  type        = string
  default     = "adlseljattioui"
}

variable "adls_replication_type" {
  description = "Type de réplication pour le storage ADLS"
  type        = string
  default     = "RAGRS"
}

variable "adls_containers" {
  description = "Liste des containers à créer dans le storage ADLS"
  type        = list(string)
  default     = ["insights-logs-auditevent", "logs", "nyc-taxi", "wttj"]
}

# -----------------------------------------------------------------------------
# Storage Account Blob Standard
# -----------------------------------------------------------------------------

variable "blob_storage_account_name" {
  description = "Nom du storage account Blob (doit être unique globalement)"
  type        = string
  default     = "blobfeljattioui"
}

variable "blob_replication_type" {
  description = "Type de réplication pour le storage Blob"
  type        = string
  default     = "LRS"
}

variable "blob_containers" {
  description = "Liste des containers à créer dans le storage Blob"
  type        = list(string)
  default     = ["amazon", "api", "students"]
}

# -----------------------------------------------------------------------------
# SQL Server
# -----------------------------------------------------------------------------

variable "sql_server_name" {
  description = "Nom du serveur SQL (doit être unique globalement)"
  type        = string
  default     = "fatiserveur"
}

variable "sql_admin_login" {
  description = "Login administrateur du serveur SQL"
  type        = string
  default     = "fatima"
}

variable "sql_admin_password" {
  description = "Mot de passe administrateur du serveur SQL"
  type        = string
  sensitive   = true
}

# -----------------------------------------------------------------------------
# SQL Database
# -----------------------------------------------------------------------------

variable "sql_database_name" {
  description = "Nom de la base de données SQL"
  type        = string
  default     = "wttj"
}

variable "sql_database_max_size_gb" {
  description = "Taille maximale de la base de données en GB"
  type        = number
  default     = 32
}

variable "sql_database_sku_name" {
  description = "SKU de la base de données (serverless Gen5)"
  type        = string
  default     = "GP_S_Gen5_1"
}

variable "sql_database_min_capacity" {
  description = "Capacité minimale vCores (serverless)"
  type        = number
  default     = 0.5
}

variable "sql_database_auto_pause_delay" {
  description = "Délai avant pause automatique en minutes (-1 = désactivé)"
  type        = number
  default     = 60
}

# -----------------------------------------------------------------------------
# SQL Firewall Rules
# -----------------------------------------------------------------------------

variable "sql_firewall_rules" {
  description = "Règles de firewall pour le serveur SQL"
  type = list(object({
    name             = string
    start_ip_address = string
    end_ip_address   = string
  }))
  default = [
    {
      name             = "ClientIP_1"
      start_ip_address = "90.39.20.177"
      end_ip_address   = "90.39.20.177"
    },
    {
      name             = "ClientIP_2"
      start_ip_address = "185.39.171.242"
      end_ip_address   = "185.39.171.242"
    }
  ]
}

variable "allow_azure_services" {
  description = "Autoriser les services Azure à accéder au serveur SQL"
  type        = bool
  default     = true
}
