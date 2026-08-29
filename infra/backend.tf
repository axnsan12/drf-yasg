terraform {
  backend "s3" {
    bucket = "elixir-drf-yasg-terraform-backend"
    key    = "terraform"
    region = "eu-west-2"
  }
}
