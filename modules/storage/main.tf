resource "aws_s3_bucket" "documents_bucket" {
  bucket = "semantic-search-documents-${random_id.bucket_suffix.hex}"
  force_destroy = true
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}