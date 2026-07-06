resource "aws_security_group_rule" "allow_ssh_vpn" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["<your-vpn-cidr>"]
  security_group_id = "{{ resource_id }}"
}
