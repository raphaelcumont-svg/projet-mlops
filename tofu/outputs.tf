output "ec2_public_ip" {
  value = module.ec2_instance.public_ip
}

output "ec2_private_ip" {
  value = module.ec2_instance.private_ip
}

output "ec2_instance_id" {
  value = module.ec2_instance.instance_id
}

output "ami_id_used" {
  value = module.ec2_instance.ami_id
}

output "security_groups" {
  value = module.security_groups.security_group_ids
}
