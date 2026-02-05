###############################################################################
# MR. HEALTH Data Platform - Root Terragrunt Configuration
# Shared configuration inherited by all environments
###############################################################################

# ---------------------------------------------------------------------------
# Remote State: GCS Backend
# ---------------------------------------------------------------------------
remote_state {
  backend = "gcs"
  config = {
    bucket   = "mrhealth-terraform-state"
    prefix   = "${path_relative_to_include()}/terraform.tfstate"
    project  = "sixth-foundry-485810-e5"
    location = "us-central1"
  }
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
}

# ---------------------------------------------------------------------------
# Provider Generation
# ---------------------------------------------------------------------------
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<-EOF
    # Provider configured via Terragrunt inputs.
    # project_id and region variables are declared in each module's variables.tf.
    provider "google" {
      project = var.project_id
    }
  EOF
}

# ---------------------------------------------------------------------------
# Terraform Version Constraint
# ---------------------------------------------------------------------------
generate "versions" {
  path      = "versions.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<-EOF
    terraform {
      required_version = ">= 1.5"
      required_providers {
        google = {
          source  = "hashicorp/google"
          version = "~> 5.0"
        }
      }
    }
  EOF
}
