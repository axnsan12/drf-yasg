resource "aws_route53_record" "certificate" {
  zone_id = aws_route53_zone.drf_yasg.zone_id

  name    = local.certificate.name
  type    = local.certificate.type
  records = local.certificate.records

  ttl = 300

  allow_overwrite = true
}

resource "aws_route53_zone" "drf_yasg" {
  name = "drf-yasg.com"
  tags = local.tags
}
