###############################################################################
# MR. HEALTH Data Platform - BigQuery Module Variables
###############################################################################

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "location" {
  description = "BigQuery dataset location"
  type        = string
  default     = "US"
}

variable "common_labels" {
  description = "Labels applied to all resources for tracking"
  type        = map(string)
  default     = {}
}

variable "datasets" {
  description = "Map of BigQuery datasets to create"
  type = map(object({
    id            = string
    friendly_name = string
    description   = string
  }))
}

variable "bronze_tables" {
  description = "Map of Bronze layer tables to create (key = table name)"
  type = map(object({
    partition_field = string
  }))
}

variable "monitoring_tables" {
  description = "Map of Monitoring layer tables to create (key = table name)"
  type = map(object({
    partition_field = string
  }))
}
