resource "aws_apprunner_auto_scaling_configuration_version" "demo" {
  auto_scaling_configuration_name = "drf-yasg-demo-scaling"

  max_concurrency = 10
  max_size        = 5

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
      image_identifier      = data.aws_ecr_image.demo_latest.image_uri

      image_configuration {
        port = "80"

        runtime_environment_variables = {
          DJANGO_SETTINGS_MODULE = "testproj.settings.apprunner"
          DJANGO_SECRET_KEY      = random_password.django_secret_key.result
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
