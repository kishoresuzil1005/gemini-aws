resource "aws_db_instance" "default" {
  identifier          = "{{ resource_id }}"
  publicly_accessible = false
  # Apply immediately to remove public exposure
  apply_immediately   = true
}
