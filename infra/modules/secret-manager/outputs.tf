###############################################################################
# MR. HEALTH Data Platform - Secret Manager Module Outputs
###############################################################################

output "secret_ids" {
  description = "Map of secret keys to their fully-qualified IDs"
  value = {
    for key, secret in google_secret_manager_secret.secrets :
    key => secret.id
  }
}

output "secret_names" {
  description = "Map of secret keys to their secret_id (name)"
  value = {
    for key, secret in google_secret_manager_secret.secrets :
    key => secret.secret_id
  }
}
