###############################################################################
# MR. HEALTH Data Platform - Prod Environment Configuration
# Project: sixth-foundry-485810-e5
###############################################################################

locals {
  environment = "prod"
  project_id  = "sixth-foundry-485810-e5"
  region      = "us-central1"

  common_labels = {
    project     = "mrhealth"
    environment = local.environment
    managed_by  = "terraform"
    team        = "data-lakers"
  }
}
