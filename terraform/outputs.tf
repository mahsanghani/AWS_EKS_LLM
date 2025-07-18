output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = aws_eks_cluster.main.vpc_config[0].cluster_security_group_id
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.main.name
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.llm_api.repository_url
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}
