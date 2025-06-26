variable "s3_bucket_name" {
  description = "Name of the S3 bucket for document storage"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of the S3 bucket for document storage"
  type        = string
}

variable "db_host" {
  description = "RDS database host"
  type        = string
}

variable "db_name" {
  description = "RDS database name"
  type        = string
}

variable "db_username" {
  description = "RDS database username"
  type        = string
}

variable "db_password" {
  description = "RDS database password"
  type        = string
  sensitive   = true
}

variable "db_security_group_id" {
  description = "Security group ID for the RDS instance"
  type        = string
}