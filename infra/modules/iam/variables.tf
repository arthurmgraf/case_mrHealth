###############################################################################
# MR. HEALTH Data Platform - IAM Module Variables
###############################################################################

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "service_accounts" {
  description = "Map of service accounts to create with their roles"
  type = map(object({
    account_id   = string
    display_name = string
    description  = string
    roles        = list(string)
  }))
}

variable "wif_config" {
  description = "Workload Identity Federation configuration for GitHub Actions"
  type = object({
    pool_id              = string
    pool_display_name    = string
    pool_description     = string
    provider_id          = string
    provider_display_name = string
    github_repo          = string
    service_account_key  = string
  })
  default = null
}
