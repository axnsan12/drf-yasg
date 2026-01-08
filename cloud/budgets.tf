resource "aws_ce_cost_allocation_tag" "group" {
  tag_key = "group"
  status  = "Active"
}

resource "aws_budgets_budget" "costs" {
  name = "drf-yasg-monthly-budget"

  time_unit    = "MONTHLY"
  budget_type  = "COST"
  limit_amount = "5"
  limit_unit   = "USD"

  cost_filter {
    name   = "TagKeyValue"
    values = ["group$drf-yasg"]
  }

  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_sns_topic_arns = [aws_sns_topic.costs.arn]
  }

  depends_on = [aws_ce_cost_allocation_tag.group]

  tags = local.tags
}
