###############################################################################
# MR. HEALTH Data Platform - Cloud Functions Module Outputs
###############################################################################

output "function_uris" {
  description = "Map of function keys to their HTTP URIs"
  value = {
    for key, fn in google_cloudfunctions2_function.functions :
    key => fn.service_config[0].uri
  }
}

output "function_names" {
  description = "Map of function keys to their names"
  value = {
    for key, fn in google_cloudfunctions2_function.functions :
    key => fn.name
  }
}

output "function_states" {
  description = "Map of function keys to their current state"
  value = {
    for key, fn in google_cloudfunctions2_function.functions :
    key => fn.state
  }
}
