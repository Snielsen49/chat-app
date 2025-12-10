terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Data source to get latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security group for chat server
resource "aws_security_group" "chat_server_sg" {
  name        = "chat-server-sg"
  description = "Security group for chat server"

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH access"
  }

  # Chat server port
  ingress {
    from_port   = 1234
    to_port     = 1234
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Chat server port"
  }

  # Outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name    = "chat-server-sg"
    Project = "chat-app"
  }
}

# EC2 instance for chat server
resource "aws_instance" "chat_server" {
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = var.instance_type
  
  vpc_security_group_ids = [aws_security_group.chat_server_sg.id]
  
  # User data script to install Docker and run the chat server
  user_data = templatefile("${path.module}/user-data.sh", {
    docker_image = var.docker_image
  })

  # Enable detailed monitoring
  monitoring = true

  # Root volume configuration
  root_block_device {
    volume_size = 8
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name    = "chat-server"
    Project = "chat-app"
  }

  # Ensure instance is recreated if user data changes
  user_data_replace_on_change = true
}

# Elastic IP for consistent public IP
resource "aws_eip" "chat_server_eip" {
  instance = aws_instance.chat_server.id
  domain   = "vpc"

  tags = {
    Name    = "chat-server-eip"
    Project = "chat-app"
  }
}
