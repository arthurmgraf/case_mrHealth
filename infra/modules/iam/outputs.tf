###############################################################################
# MR. HEALTH Data Platform - IAM Module Outputs
###############################################################################

output "service_account_emails" {
  description = "Map of service account keys to their email addresses"
  value = {
    for key, sa in google_service_account.accounts :
    key => sa.email
  }
}

output "service_account_ids" {
  description = "Map of service account keys to their unique IDs"
  value = {
    for key, sa in google_service_account.accounts :
    key => sa.unique_id
  }
}

output "service_account_names" {
  description = "Map of service account keys to their fully-qualified names"
  value = {
    for key, sa in google_service_account.accounts :
    key => sa.name
  }
}

output "wif_pool_name" {
  description = "Workload Identity Pool name (if created)"
  value       = var.wif_config != null ? google_iam_workload_identity_pool.github[0].name : null
}

output "wif_provider_name" {
  description = "Workload Identity Pool Provider name (if created)"
  value       = var.wif_config != null ? google_iam_workload_identity_pool_provider.github[0].name : null
}
