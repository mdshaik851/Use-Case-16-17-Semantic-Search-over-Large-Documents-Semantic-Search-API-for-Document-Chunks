module "storage" {
  source = "./modules/storage"
}

module "database" {
  source = "./modules/database"
}

module "document_processing" {
  source = "./modules/document_processing"

  s3_bucket_name   = module.storage.bucket_name
  s3_bucket_arn    = module.storage.bucket_arn
  db_host          = module.database.db_host
  db_name          = module.database.db_name
  db_username      = module.database.db_username
  db_password      = module.database.db_password
  db_security_group_id = module.database.db_security_group_id
}

module "search_api" {
  source = "./modules/search_api"

  db_host          = module.database.db_host
  db_name          = module.database.db_name
  db_username      = module.database.db_username
  db_password      = module.database.db_password
}