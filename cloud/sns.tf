resource "aws_sns_topic" "costs" {
  name = "drf-yasg-cost-alerts"
  tags = local.tags
}

resource "aws_sns_topic_subscription" "costs" {
  topic_arn = aws_sns_topic.costs.arn
  protocol  = "email"
  endpoint  = "joel@smoothycode.com"
}
