# Terraform AWS Static Website Deployment

This Terraform configuration deploys the Care Circles Vue.js application as a static website on AWS using S3 and CloudFront.

## Architecture

- **S3 Bucket**: Private bucket for storing static files
- **CloudFront CDN**: Global content delivery with HTTPS
- **Origin Access Identity**: Secure S3 access (no public bucket access)

## Prerequisites

1. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```

2. **Terraform** installed (>= 1.0)
   ```bash
   terraform version
   ```

3. **AWS Credentials** with permissions to create:
   - S3 buckets
   - CloudFront distributions
   - IAM policies

## Quick Start

### 1. Configure Variables

Edit the bucket name in `variables.tf` or create a `terraform.tfvars` file:

```hcl
bucket_name  = "care-circles-website-your-unique-name"
aws_region   = "us-east-1"
environment  = "production"
project_name = "care-circles"
```

### 2. Initialize Terraform

```bash
cd terraform
terraform init
```

### 3. Preview Changes

```bash
terraform plan
```

### 4. Deploy Infrastructure

```bash
terraform apply
```

Review the planned changes and type `yes` to confirm.

### 5. Note the Outputs

After deployment, Terraform will output:
- CloudFront URL (your website URL)
- CloudFront Distribution ID (for cache invalidation)
- S3 Bucket Name (for uploading files)

## Deploying Your Application

### Build the Vue.js App

```bash
cd ../www-app
yarn build
```

This creates a `dist/` folder with your compiled static files.

### Upload to S3

```bash
# Replace BUCKET_NAME with the output from Terraform
aws s3 sync ./dist/ s3://BUCKET_NAME/ --delete
```

### Invalidate CloudFront Cache

After uploading new files, clear the CloudFront cache:

```bash
# Replace DISTRIBUTION_ID with the output from Terraform
aws cloudfront create-invalidation \
  --distribution-id DISTRIBUTION_ID \
  --paths "/*"
```

## Accessing Your Website

Visit the CloudFront URL displayed in the Terraform outputs:
```
https://d1234567890abc.cloudfront.net
```

## Configuration Options

### Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `bucket_name` | S3 bucket name (must be globally unique) | `care-circles-website-CHANGE-ME` |
| `aws_region` | AWS region for resources | `us-east-1` |
| `environment` | Environment tag | `production` |
| `project_name` | Project name for tagging | `care-circles` |
| `cloudfront_price_class` | CloudFront edge location coverage | `PriceClass_100` |

### CloudFront Price Classes

- `PriceClass_100`: US, Canada, Europe (lowest cost)
- `PriceClass_200`: Above + Asia, Middle East, Africa
- `PriceClass_All`: All edge locations worldwide

## SPA Support

The CloudFront configuration includes custom error responses to support Vue Router:
- 404 and 403 errors are redirected to `index.html`
- This allows client-side routing to work correctly

## Cost Estimate

Approximate monthly costs for low-to-medium traffic:

- **S3 Storage**: $0.023/GB
- **CloudFront**: 1TB free tier, then ~$0.085/GB
- **S3 Requests**: Minimal (<$0.01/month)

**Total**: ~$1-10/month depending on traffic

## Updating the Infrastructure

To modify the infrastructure:

1. Edit the Terraform files
2. Run `terraform plan` to preview changes
3. Run `terraform apply` to apply changes

## Destroying the Infrastructure

To remove all resources:

```bash
terraform destroy
```

**Warning**: This will delete the S3 bucket and all uploaded files.

## Troubleshooting

### CloudFront showing "Access Denied"

- Ensure files are uploaded to S3
- Wait 5-10 minutes for CloudFront to fully deploy
- Check S3 bucket policy allows CloudFront OAI access

### 404 Errors on Routes

- Verify custom error responses are configured
- Clear CloudFront cache after uploading new files
- Ensure `index.html` exists in the S3 bucket root

### Bucket Name Already Exists

S3 bucket names are globally unique. Change the `bucket_name` variable to something unique.

## Security Features

- ✅ S3 bucket is private (all public access blocked)
- ✅ CloudFront accesses S3 via Origin Access Identity
- ✅ HTTPS enforced (HTTP redirects to HTTPS)
- ✅ Server-side encryption enabled (AES256)
- ✅ Versioning enabled for rollback capability

## Next Steps

- Add custom domain with Route53 and ACM certificate
- Set up CI/CD pipeline for automated deployments
- Configure CloudWatch alarms for monitoring
- Add WAF rules for additional security

## Support

For issues with this Terraform configuration, check:
- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
- [AWS S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
