data "aws_ecr_image" "demo_latest" {
  repository_name = aws_ecr_repository.demo.name
  most_recent     = true
}

data "aws_region" "current" {}
