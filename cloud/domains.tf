resource "aws_route53domains_registered_domain" "drf_yasg" {
  domain_name = aws_route53_zone.drf_yasg.name

  dynamic "name_server" {
    for_each = aws_route53_zone.drf_yasg.name_servers

    content {
      name = name_server.value
    }
  }

  transfer_lock = true
  auto_renew    = true

  lifecycle {
    prevent_destroy = true
  }

  tags = local.tags
}
