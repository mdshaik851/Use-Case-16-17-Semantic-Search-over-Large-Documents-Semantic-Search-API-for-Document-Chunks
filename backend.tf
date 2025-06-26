terraform {
  backend "s3" {
    bucket       = "uc-16-17-sematic-search"
    key          = "uc-16-17-sematic-search"
    region       = "us-west-1"
    encrypt      = true
    use_lockfile = true
  }
}
