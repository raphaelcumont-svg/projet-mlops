terraform {
  required_version = ">= 1.6.0"

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

module "security_groups" {
  source = "./modules/security-groups"
}

module "ec2_instance" {
  source                 = "./modules/ec2-instance"
  instance_name          = "Terraform-101"
  key_name               = "myKey"
  vpc_security_group_ids = module.security_groups.security_group_ids
}
