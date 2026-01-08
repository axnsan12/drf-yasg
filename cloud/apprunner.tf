resource "aws_apprunner_auto_scaling_configuration_version" "demo" {
  auto_scaling_configuration_name = "drf-yasg-demo-scaling"

  max_concurrency = 10
  max_size        = 1

  tags = local.tags
}

resource "aws_apprunner_service" "demo" {
  service_name = "drf-yasg-demo"

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.service.arn
    }

    image_repository {
      image_repository_type = "ECR"
      image_identifier      = data.aws_ecr_image.demo.image_uri

      image_configuration {
        port = "80"

        runtime_environment_variables = {
          DJANGO_SETTINGS_MODULE      = "testproj.settings.prod"
          DJANGO_SECRET_KEY           = random_password.django_secret_key.result
          DJANGO_HOST_DOMAIN          = aws_route53_zone.drf_yasg.name
          DJANGO_HOST_URL             = "https://${aws_route53_zone.drf_yasg.name}"
        }
      }
    }
  }

  instance_configuration {
    cpu    = "256"
    memory = "512"
  }

  auto_scaling_configuration_arn = aws_apprunner_auto_scaling_configuration_version.demo.arn

  tags = local.tags
}

resource "aws_apprunner_custom_domain_association" "demo" {
  domain_name = aws_route53_zone.drf_yasg.name
  service_arn = aws_apprunner_service.demo.arn

  enable_www_subdomain = true
}
