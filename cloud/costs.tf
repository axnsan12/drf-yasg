resource "aws_ce_anomaly_monitor" "costs" {
  name = "drf-yasg-cost-monitor"

  monitor_type = "CUSTOM"

  monitor_specification = jsonencode({
    And            = null
    CostCategories = null
    Dimensions     = null
    Not            = null
    Or             = null

    Tags = {
      MatchOptions = null

      Key    = "user:group"
      Values = ["drf-yasg"]
    }
  })

  tags = local.tags
}

resource "aws_ce_anomaly_subscription" "costs" {
  name = "drf-yasg-cost-subscription"

  frequency = "IMMEDIATE"

  threshold_expression {
    dimension {
      key           = "ANOMALY_TOTAL_IMPACT_PERCENTAGE"
      match_options = ["GREATER_THAN_OR_EQUAL"]
      values        = ["10"]
    }
  }

  monitor_arn_list = [
    aws_ce_anomaly_monitor.costs.arn
  ]

  subscriber {
    type    = "SNS"
    address = aws_sns_topic.costs.arn
  }

  tags = local.tags
}
