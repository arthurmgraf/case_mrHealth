###############################################################################
# MR. HEALTH Data Platform - Secret Manager Module Variables
###############################################################################

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "common_labels" {
  description = "Labels applied to all resources for tracking"
  type        = map(string)
  default     = {}
}

variable "secrets" {
  description = "Map of secrets to create in Secret Manager"
  type = map(object({
    id               = string
    purpose          = string
    accessor_members = list(string)
  }))
}
