output "db_host" {
  value = aws_db_instance.semantic_search_db.address
}

output "db_name" {
  value = aws_db_instance.semantic_search_db.db_name
}

output "db_username" {
  value = aws_db_instance.semantic_search_db.username
}

output "db_password" {
  value     = aws_db_instance.semantic_search_db.password
  sensitive = true
}

output "db_security_group_id" {
  value = aws_security_group.rds_sg.id
}