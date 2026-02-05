###############################################################################
# MR. HEALTH Data Platform - GCS Module Variables
###############################################################################

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "bucket_name" {
  description = "Name of the GCS bucket"
  type        = string
}

variable "location" {
  description = "Bucket location"
  type        = string
  default     = "US"
}

variable "storage_class" {
  description = "Default storage class"
  type        = string
  default     = "STANDARD"
}

variable "versioning_enabled" {
  description = "Enable object versioning"
  type        = bool
  default     = false
}

variable "lifecycle_rules" {
  description = "List of lifecycle rules for the bucket"
  type = list(object({
    action_type        = string
    storage_class      = optional(string)
    age_days           = optional(number)
    prefix             = optional(string)
    with_state         = optional(string, "ANY")
    num_newer_versions = optional(number)
  }))
  default = []
}

variable "common_labels" {
  description = "Labels applied to all resources for tracking"
  type        = map(string)
  default     = {}
}
