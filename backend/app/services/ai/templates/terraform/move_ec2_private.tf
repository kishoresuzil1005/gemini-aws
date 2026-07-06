resource "aws_subnet" "private" {
  vpc_id     = var.vpc_id
  cidr_block = "10.0.1.0/24"
  tags = {
    Name = "PrivateSubnet-{{ resource_id }}"
  }
}

resource "aws_route_table" "private" {
  vpc_id = var.vpc_id
}

resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}
