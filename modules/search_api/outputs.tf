
output "api_endpoint" {
  value = "https://${aws_api_gateway_rest_api.semantic_api.id}.execute-api.${var.region}.amazonaws.com/${aws_api_gateway_stage.api_stage.stage_name}"
}
