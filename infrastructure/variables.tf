variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "docker_image" {
  description = "Docker image to deploy"
  type        = string
  default     = "sorennielsen599/chat-server:latest"
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
  default     = "chat-app"
}
