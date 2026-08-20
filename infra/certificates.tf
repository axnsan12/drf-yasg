resource "aws_acm_certificate" "app" {
  provider = aws.us_east_1

  domain_name       = aws_route53_zone.drf_yasg.name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = local.tags
}

resource "aws_acm_certificate_validation" "app" {
  provider = aws.us_east_1

  certificate_arn         = aws_acm_certificate.app.arn
  validation_record_fqdns = [aws_route53_record.certificate.fqdn]

  timeouts {
    create = "5m"
  }
}
