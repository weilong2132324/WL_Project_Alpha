#!/bin/bash
# Install and start a simple web server
yum update -y
yum install -y httpd
systemctl enable httpd
systemctl start httpd
echo "Hello from go-web-init EC2!" > /var/www/html/index.html
