terraform {
  backend "s3" {
    bucket = "elixir-drf-yasg-backend"
    key    = "terraform"
    region = "eu-west-2"
  }
}
