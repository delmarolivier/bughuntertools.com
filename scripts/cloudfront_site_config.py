"""
cloudfront_site_config.py — CloudFront + S3 Static Site Configuration Generator

Generates validated CloudFront distribution config JSON and the URL rewrite
CloudFront Function for new static sites at ClawWorks.

Features baked in:
  - HTTPS-only via ACM certificate
  - Directory index rewrite (CloudFront Function: viewer-request)
  - Compression enabled
  - Custom error handling (403/404 → index.html for SPA fallback)
  - Optional www redirect alias

Usage:
    python3 cloudfront_site_config.py --domain example.com \
        --bucket example.com \
        --cert-arn arn:aws:acm:us-east-1:...:certificate/... \
        [--include-www] \
        [--out-config cf-config.json] \
        [--out-function url-rewrite.js]
"""
import argparse
import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class CloudFrontSiteParams:
    domain: str
    bucket: str
    cert_arn: str
    region: str = "us-east-1"
    include_www: bool = False
    # Placeholder for the CloudFront function ARN after creation
    function_arn: Optional[str] = None


def validate_params(params: CloudFrontSiteParams) -> None:
    """
    Validate site configuration parameters.

    Raises:
        ValueError: with descriptive message if any param is invalid.
    """
    if not params.domain:
        raise ValueError("domain is required and cannot be empty")

    if not params.bucket:
        raise ValueError("bucket is required and cannot be empty")

    if not params.cert_arn:
        raise ValueError("cert_arn is required and cannot be empty")

    # Must be a valid ARN
    arn_pattern = r"^arn:aws:acm:[^:]+:\d+:certificate/.+"
    if not re.match(arn_pattern, params.cert_arn):
        raise ValueError(
            f"cert_arn must be a valid ACM ARN (arn:aws:acm:...:certificate/...), got: {params.cert_arn!r}"
        )

    # ACM certs for CloudFront MUST be in us-east-1
    if ":acm:us-east-1:" not in params.cert_arn:
        raise ValueError(
            "cert_arn must be in us-east-1 — CloudFront requires ACM certificates in us-east-1 "
            f"regardless of the site's origin region. Got: {params.cert_arn!r}"
        )


def generate_url_rewrite_function() -> str:
    """
    Return the CloudFront Function JS code for directory index rewrite.

    Handles two cases:
      1. URI ends with '/' → append 'index.html'
      2. URI has no file extension → append '/index.html'

    Returns:
        str: Valid CloudFront Function JavaScript code.
    """
    return """\
function handler(event) {
    var request = event.request;
    var uri = request.uri;

    // If URI ends with '/', serve index.html in that directory
    if (uri.endsWith('/')) {
        request.uri += 'index.html';
    }
    // If URI has no file extension, treat as a directory route
    else if (!uri.includes('.')) {
        request.uri += '/index.html';
    }

    return request;
}"""


def generate_distribution_config(params: CloudFrontSiteParams) -> Dict[str, Any]:
    """
    Generate a CloudFront distribution config dict.

    Args:
        params: Validated site parameters.

    Returns:
        Distribution config dict suitable for JSON serialisation and
        passing to `aws cloudfront create-distribution --distribution-config`.
    """
    # Build aliases
    aliases = [params.domain]
    if params.include_www:
        aliases.append(f"www.{params.domain}")

    # Origin domain: S3 REST endpoint (not website endpoint — we use OAC/OAI or public bucket)
    origin_domain = f"{params.bucket}.s3.{params.region}.amazonaws.com"

    # Function associations — viewer-request for directory index rewrite
    function_associations: Dict[str, Any] = {"Quantity": 0, "Items": []}
    if params.function_arn:
        function_associations = {
            "Quantity": 1,
            "Items": [
                {
                    "FunctionARN": params.function_arn,
                    "EventType": "viewer-request",
                }
            ],
        }
    else:
        # Placeholder — the shell script creates the function and then fills this in
        function_associations = {
            "Quantity": 1,
            "Items": [
                {
                    "FunctionARN": "REPLACE_WITH_FUNCTION_ARN",
                    "EventType": "viewer-request",
                }
            ],
        }

    config: Dict[str, Any] = {
        "CallerReference": f"{params.domain}-{params.region}",
        "Comment": f"{params.domain} static site — CloudFront + S3",
        "Enabled": True,
        "DefaultRootObject": "index.html",
        "Origins": {
            "Quantity": 1,
            "Items": [
                {
                    "Id": f"S3-{params.bucket}",
                    "DomainName": origin_domain,
                    "S3OriginConfig": {
                        "OriginAccessIdentity": "",
                    },
                }
            ],
        },
        "DefaultCacheBehavior": {
            "TargetOriginId": f"S3-{params.bucket}",
            "ViewerProtocolPolicy": "redirect-to-https",
            "AllowedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"],
                "CachedMethods": {
                    "Quantity": 2,
                    "Items": ["GET", "HEAD"],
                },
            },
            "Compress": True,
            "ForwardedValues": {
                "QueryString": False,
                "Cookies": {"Forward": "none"},
            },
            "MinTTL": 0,
            "DefaultTTL": 3600,
            "MaxTTL": 86400,
            "FunctionAssociations": function_associations,
        },
        "Aliases": {
            "Quantity": len(aliases),
            "Items": aliases,
        },
        "ViewerCertificate": {
            "ACMCertificateArn": params.cert_arn,
            "SSLSupportMethod": "sni-only",
            "MinimumProtocolVersion": "TLSv1.2_2021",
        },
        "CustomErrorResponses": {
            "Quantity": 2,
            "Items": [
                {
                    "ErrorCode": 403,
                    "ResponsePagePath": "/index.html",
                    "ResponseCode": "200",
                    "ErrorCachingMinTTL": 300,
                },
                {
                    "ErrorCode": 404,
                    "ResponsePagePath": "/index.html",
                    "ResponseCode": "200",
                    "ErrorCachingMinTTL": 300,
                },
            ],
        },
        "PriceClass": "PriceClass_100",  # US+Europe only — cheapest that covers our audience
        "HttpVersion": "http2and3",
    }

    return config


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate CloudFront + S3 static site configuration"
    )
    parser.add_argument("--domain", required=True, help="Root domain (e.g. example.com)")
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--cert-arn", required=True, help="ACM cert ARN (must be us-east-1)")
    parser.add_argument("--region", default="us-east-1", help="AWS region (default: us-east-1)")
    parser.add_argument("--include-www", action="store_true", help="Add www.domain alias")
    parser.add_argument("--out-config", default="cf-dist-config.json", help="Output config JSON path")
    parser.add_argument("--out-function", default="cloudfront-function-url-rewrite.js", help="Output function JS path")
    args = parser.parse_args()

    params = CloudFrontSiteParams(
        domain=args.domain,
        bucket=args.bucket,
        cert_arn=args.cert_arn,
        region=args.region,
        include_www=args.include_www,
    )

    validate_params(params)

    # Write distribution config
    config = generate_distribution_config(params)
    with open(args.out_config, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ Distribution config written: {args.out_config}")
    print(f"   ⚠️  Replace REPLACE_WITH_FUNCTION_ARN with the ARN after creating the function")

    # Write function code
    function_code = generate_url_rewrite_function()
    with open(args.out_function, "w") as f:
        f.write(function_code)
    print(f"✅ URL rewrite function written: {args.out_function}")

    print()
    print("Next steps:")
    print(f"  1. aws cloudfront create-function --name {args.domain.replace('.', '-')}-url-rewrite \\")
    print(f"       --function-config '{{\"Comment\":\"Directory index rewrite\",\"Runtime\":\"cloudfront-js-2.0\"}}' \\")
    print(f"       --function-code fileb://{args.out_function}")
    print(f"  2. Note the FunctionARN from the output above")
    print(f"  3. Replace REPLACE_WITH_FUNCTION_ARN in {args.out_config}")
    print(f"  4. aws cloudfront create-distribution --distribution-config file://{args.out_config}")


if __name__ == "__main__":
    main()
