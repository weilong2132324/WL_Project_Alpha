variable "aws_region" {
  description = "AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "db_username" {
  description = "Database master username."
  type        = string
}

variable "db_password" {
  description = "Database master password."
  type        = string
  sensitive   = true
}
