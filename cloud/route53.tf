resource "aws_route53_record" "certificate" {
  zone_id = aws_route53_zone.drf_yasg.zone_id

  name    = local.certificate.name
  type    = local.certificate.type
  records = local.certificate.records

  ttl = 300

  allow_overwrite = true
}

resource "aws_route53_record" "demo" {
  zone_id = aws_route53_zone.drf_yasg.zone_id

  name = aws_route53_zone.drf_yasg.name
  type = "A"

  alias {
    name                   = aws_apprunner_service.demo.service_url
    zone_id                = data.aws_apprunner_hosted_zone_id.current.id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "demo_validation" {
  for_each = local.demo_validation

  zone_id = aws_route53_zone.drf_yasg.zone_id

  name    = each.value.name
  type    = each.value.type
  records = [each.value.value]

  ttl = 300

  allow_overwrite = true
}

resource "aws_route53_zone" "drf_yasg" {
  name = "drf-yasg.com"
  tags = local.tags
}
