resource "aws_db_instance" "semantic_search_db" {
  identifier             = "semantic-search-db"
  engine                 = "postgres"
  engine_version         = "15.3"
  instance_class         = var.db_instance_class
  allocated_storage      = 20
  storage_type           = "gp2"
  db_name                = "semanticsearch"
  username               = "semanticadmin"
  password               = random_password.db_password.result
  parameter_group_name   = aws_db_parameter_group.pgvector.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot    = true
  publicly_accessible    = true # For demo purposes only
}

resource "random_password" "db_password" {
  length  = 16
  special = false
}

resource "aws_db_parameter_group" "pgvector" {
  name   = "pgvector-parameters"
  family = "postgres15"

  parameter {
    name  = "shared_preload_libraries"
    value = "pgvector"
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "rds_sg"
  description = "Allow inbound access to RDS"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Restrict this in production
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}