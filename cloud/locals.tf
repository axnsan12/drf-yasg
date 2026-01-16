locals {
  tags = {
    group = "drf-yasg"
  }

  certificate = one([
    for dvo in aws_acm_certificate.app.domain_validation_options
    : {
      name    = dvo.resource_record_name
      type    = dvo.resource_record_type
      records = [dvo.resource_record_value]
    }
    if dvo.domain_name == aws_route53_zone.drf_yasg.name
  ])

  demo_validation = {
    for record in aws_apprunner_custom_domain_association.demo.certificate_validation_records
    : record.name => record
  }
}
