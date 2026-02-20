# =============================================================================
# Configuration Terraform pour Azure
# Reproduction du Resource Group RG_FELJATTIOUI
# =============================================================================

terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  # Backend pour stocker l'état Terraform (à configurer selon votre environnement)
  # backend "azurerm" {
  #   resource_group_name  = "rg-terraform-state"
  #   storage_account_name = "tfstate"
  #   container_name       = "tfstate"
  #   key                  = "feljattioui.tfstate"
  # }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }

  # Abonnement Azure Student
  subscription_id = "1b55917c-0cca-4c14-b10d-af1f0c872568"
}

# -----------------------------------------------------------------------------
# Resource Group
# -----------------------------------------------------------------------------

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}
