# Ansible Integration

This directory contains Ansible playbooks for automating tasks related to this project.

## Playbooks

### provision_docker.yml
- Provisions an Nginx Docker container
- Copies your web/index.html into the container
- Reloads Nginx to serve the new file

## Getting Started

1. Install Ansible and Docker on your system.
2. Install required Ansible collections:
   ```sh
   ansible-galaxy collection install -r requirements.yml
   ```
3. Run the playbook:
   ```sh
   ansible-playbook provision_docker.yml
   ```

## Customization
- Edit variables in the playbook to change image, ports, or files.
- Extend with more tasks as needed.
