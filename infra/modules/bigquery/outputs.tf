###############################################################################
# MR. HEALTH Data Platform - BigQuery Module Outputs
###############################################################################

output "dataset_ids" {
  description = "Map of dataset keys to their fully-qualified dataset IDs"
  value = {
    for key, ds in google_bigquery_dataset.datasets :
    key => ds.dataset_id
  }
}

output "dataset_self_links" {
  description = "Map of dataset keys to their self links"
  value = {
    for key, ds in google_bigquery_dataset.datasets :
    key => ds.self_link
  }
}

output "bronze_table_ids" {
  description = "Map of bronze table names to their fully-qualified table IDs"
  value = {
    for key, tbl in google_bigquery_table.bronze_tables :
    key => tbl.table_id
  }
}

output "monitoring_table_ids" {
  description = "Map of monitoring table names to their fully-qualified table IDs"
  value = {
    for key, tbl in google_bigquery_table.monitoring_tables :
    key => tbl.table_id
  }
}
