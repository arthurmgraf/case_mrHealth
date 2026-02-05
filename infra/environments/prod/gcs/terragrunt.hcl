###############################################################################
# MR. HEALTH Data Platform - GCS Data Lake Bucket (Prod)
# Bucket: mrhealth-datalake-485810
###############################################################################

include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

include "env" {
  path   = "${get_parent_terragrunt_dir()}/prod/terragrunt.hcl"
  expose = true
}

terraform {
  source = "../../../modules/gcs"
}

inputs = {
  project_id = include.env.locals.project_id

  bucket_name        = "mrhealth-datalake-485810"
  location           = "US"
  storage_class      = "STANDARD"
  versioning_enabled = false

  common_labels = include.env.locals.common_labels

  # ---------------------------------------------------------------------------
  # Lifecycle Rules
  # ---------------------------------------------------------------------------
  lifecycle_rules = [
    {
      # Delete raw CSV files after 90 days (already ingested to Bronze)
      action_type = "Delete"
      age_days    = 90
      prefix      = "raw/"
      with_state  = "ANY"
    },
    {
      # Delete quarantine files after 30 days
      action_type = "Delete"
      age_days    = 30
      prefix      = "quarantine/"
      with_state  = "ANY"
    }
  ]
}
