variable "bucket_name" {
  description = "Name of the S3 bucket for static website hosting"
  type        = string
  default     = "care-circles-website"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]*[a-z0-9]$", var.bucket_name))
    error_message = "Bucket name must be lowercase alphanumeric with hyphens, and cannot start or end with a hyphen."
  }
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g., production, staging, development)"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name for resource tagging"
  type        = string
  default     = "care-circles"
}

variable "cloudfront_price_class" {
  description = "CloudFront price class (PriceClass_All, PriceClass_200, PriceClass_100)"
  type        = string
  default     = "PriceClass_100" # US, Canada, Europe

  validation {
    condition     = contains(["PriceClass_All", "PriceClass_200", "PriceClass_100"], var.cloudfront_price_class)
    error_message = "Price class must be one of: PriceClass_All, PriceClass_200, PriceClass_100."
  }
}
