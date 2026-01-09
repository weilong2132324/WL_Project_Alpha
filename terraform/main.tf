provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.0"

  name = "go-web-init-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
}

module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "6.3.0"

  identifier = "go-web-init-db"
  engine     = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  name     = "gowebinitdb"
  username = var.db_username
  password = var.db_password
  subnet_ids = module.vpc.private_subnets
  vpc_security_group_ids = [module.vpc.default_security_group_id]
  publicly_accessible = false
  skip_final_snapshot = true
}

module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "9.6.0"

  name = "go-web-init-alb"
  load_balancer_type = "application"
  vpc_id = module.vpc.vpc_id
  subnets = module.vpc.public_subnets
  security_groups = [module.vpc.default_security_group_id]
}

module "asg" {
  source  = "terraform-aws-modules/autoscaling/aws"
  version = "7.4.0"

  name = "go-web-init-asg"
  vpc_zone_identifier = module.vpc.public_subnets
  min_size = 2
  max_size = 4
  desired_capacity = 2
  launch_template_name = aws_launch_template.web_lt.name
}

resource "aws_launch_template" "web_lt" {
  name_prefix   = "go-web-init-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  user_data     = base64encode(file("${path.module}/user_data.sh"))
  vpc_security_group_ids = [module.vpc.default_security_group_id]
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_s3_bucket" "static" {
  bucket = "go-web-init-static-${random_id.suffix.hex}"
  acl    = "private"
}

resource "random_id" "suffix" {
  byte_length = 4
}
