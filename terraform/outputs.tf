output "vpc_id" {
  value = module.vpc.vpc_id
}

output "alb_dns_name" {
  value = module.alb.dns_name
}

output "rds_endpoint" {
  value = module.rds.db_instance_endpoint
}

output "s3_bucket_name" {
  value = aws_s3_bucket.static.bucket
}
