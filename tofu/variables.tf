variable "aws_region" {
  type    = string
  default = "eu-north-1"
}

variable "ssh_public_key_path" {
  type    = string
  default = "C:/Users/Pablo/.ssh/id_rsa.pub"
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "api_port" {
  type    = number
  default = 5000
}
