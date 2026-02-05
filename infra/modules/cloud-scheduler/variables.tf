###############################################################################
# MR. HEALTH Data Platform - Cloud Scheduler Module Variables
###############################################################################

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Scheduler"
  type        = string
}

variable "scheduler_jobs" {
  description = "Map of Cloud Scheduler jobs to create"
  type = map(object({
    name                 = string
    schedule             = string
    timezone             = string
    description          = string
    attempt_deadline     = string
    http_method          = string
    target_uri           = string
    oidc_service_account = optional(string)
    headers              = optional(map(string), {})
    body                 = optional(string)
    retry_count          = optional(number, 1)
    max_retry_duration   = optional(string, "0s")
    min_backoff_duration = optional(string, "5s")
    max_backoff_duration = optional(string, "3600s")
    max_doublings        = optional(number, 5)
  }))
}
