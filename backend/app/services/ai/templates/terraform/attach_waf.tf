resource "aws_wafv2_web_acl" "example" {
  name        = "waf-{{ resource_id }}"
  description = "WAF for {{ resource_id }}"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "waf-{{ resource_id }}"
    sampled_requests_enabled   = true
  }
}

resource "aws_wafv2_web_acl_association" "example" {
  resource_arn = "{{ resource_arn }}"
  web_acl_arn  = aws_wafv2_web_acl.example.arn
}
