data "aws_region" "current" {}

data "aws_ecr_image" "demo" {
  repository_name = aws_ecr_repository.demo.name
  most_recent     = true
}
