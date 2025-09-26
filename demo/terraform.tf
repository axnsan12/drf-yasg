terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "elixir-drf-yasg-backend"
    key    = "terraform"
    region = "eu-west-2"
  }
}
