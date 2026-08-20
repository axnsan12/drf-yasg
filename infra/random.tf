resource "random_password" "django_secret_key" {
  length  = 50
  special = true
}
