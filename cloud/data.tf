data "aws_apprunner_hosted_zone_id" "current" {}

data "aws_ecr_image" "demo" {
  repository_name = aws_ecr_repository.demo.name
  most_recent     = true
}

data "aws_region" "current" {}
