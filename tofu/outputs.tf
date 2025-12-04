output "api_public_ip" {
  value = aws_instance.api.public_ip
}

output "monitoring_public_ip" {
  value = aws_instance.monitoring.public_ip
}

output "api_url" {
  value = "http://${aws_instance.api.public_ip}:${var.api_port}"
}

output "grafana_url" {
  value = "http://${aws_instance.monitoring.public_ip}:3000"
}
