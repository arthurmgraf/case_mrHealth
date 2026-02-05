###############################################################################
# MR. HEALTH Data Platform - Cloud Functions Module Variables
###############################################################################

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Functions"
  type        = string
}

variable "common_labels" {
  description = "Labels applied to all resources for tracking"
  type        = map(string)
  default     = {}
}

variable "functions" {
  description = "Map of Cloud Functions to create"
  type = map(object({
    name                  = string
    runtime               = string
    entry_point           = string
    memory                = string
    timeout_seconds       = number
    max_instances         = number
    min_instances         = number
    source_bucket         = string
    source_object         = string
    service_account_email = string
    environment_variables = map(string)

    secret_env_vars = list(object({
      env_var     = string
      secret_name = string
      version     = string
    }))

    event_trigger = optional(object({
      event_type   = string
      retry_policy = string
      event_filters = list(object({
        attribute = string
        value     = string
        operator  = optional(string)
      }))
    }))
  }))
}
