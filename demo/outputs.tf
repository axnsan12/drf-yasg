output "apprunner_default_domain" {
  description = "Default domain URL for the App Runner service"
  value       = aws_apprunner_service.demo.service_url
}
