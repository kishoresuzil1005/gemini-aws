resource "aws_lambda_function" "example" {
  function_name = "{{ resource_id }}"
  vpc_config {
    subnet_ids         = ["<subnet-id-1>", "<subnet-id-2>"]
    security_group_ids = ["<sg-id>"]
  }
}
