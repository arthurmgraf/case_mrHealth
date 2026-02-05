###############################################################################
# MR. HEALTH Data Platform - GCS Module Outputs
###############################################################################

output "bucket_name" {
  description = "Name of the created bucket"
  value       = google_storage_bucket.datalake.name
}

output "bucket_url" {
  description = "GCS URL of the bucket"
  value       = google_storage_bucket.datalake.url
}

output "bucket_self_link" {
  description = "Self link of the bucket"
  value       = google_storage_bucket.datalake.self_link
}
