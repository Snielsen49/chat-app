output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.chat_server.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_eip.chat_server_eip.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.chat_server.public_dns
}

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.chat_server_sg.id
}

output "chat_server_url" {
  description = "URL to connect to chat server"
  value       = "tcp://${aws_eip.chat_server_eip.public_ip}:1234"
}

output "connection_command" {
  description = "Command to connect client to server"
  value       = "CHAT_SERVER_HOST=${aws_eip.chat_server_eip.public_ip} python -m src.client"
}
