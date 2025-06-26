output "s3_bucket_name" {
  value = module.storage.bucket_name
}

output "api_endpoint" {
  value = module.search_api.api_endpoint
}

output "db_endpoint" {
  value = module.database.db_host
}