resource "aws_ecr_lifecycle_policy" "delete_images" {
  repository = aws_ecr_repository.demo.name

  policy = jsonencode({
    rules = [
      for i, selection in [
        {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        },
        {
          tagStatus      = "tagged"
          tagPatternList = ["*"]
          countType      = "imageCountMoreThan"
          countNumber    = 5
        }
      ]
      : {
        rulePriority = i + 1
        selection    = selection
        action = {
          type = "expire"
        }
      }
    ]
  })
}

resource "aws_ecr_repository" "demo" {
  name = "drf-yasg-demo"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.tags
}
