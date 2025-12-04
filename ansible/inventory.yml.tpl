all:
  vars:
    ansible_user: ubuntu
    ansible_ssh_private_key_file: {ssh_private_key_path}
  children:
    api:
      hosts:
        api-server:
          ansible_host: {api_public_ip}
    monitoring:
      hosts:
        monitoring-server:
          ansible_host: {monitoring_public_ip}
