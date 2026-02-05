###############################################################################
# MR. HEALTH Data Platform - Cloud Scheduler Module Outputs
###############################################################################

output "job_names" {
  description = "Map of scheduler job keys to their names"
  value = {
    for key, job in google_cloud_scheduler_job.jobs :
    key => job.name
  }
}

output "job_ids" {
  description = "Map of scheduler job keys to their IDs"
  value = {
    for key, job in google_cloud_scheduler_job.jobs :
    key => job.id
  }
}
