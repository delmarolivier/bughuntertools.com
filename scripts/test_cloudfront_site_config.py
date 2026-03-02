"""
TDD tests for cloudfront_site_config.py
Tests written BEFORE implementation.

Validates the CloudFront+S3 site configuration generator that produces
correct distribution config and function code for new static sites.
"""
import json
import pytest

from cloudfront_site_config import (
    generate_distribution_config,
    generate_url_rewrite_function,
    validate_params,
    CloudFrontSiteParams,
)


# ── validate_params tests ───────────────────────────────────────────────────

class TestValidateParams:
    def test_valid_params_does_not_raise(self):
        params = CloudFrontSiteParams(
            domain="example.com",
            bucket="example.com",
            cert_arn="arn:aws:acm:us-east-1:123456789012:certificate/abc123",
            region="us-east-1",
        )
        # Should not raise
        validate_params(params)

    def test_missing_domain_raises(self):
        with pytest.raises(ValueError, match="domain"):
            validate_params(CloudFrontSiteParams(
                domain="",
                bucket="example.com",
                cert_arn="arn:aws:acm:us-east-1:123456789012:certificate/abc123",
                region="us-east-1",
            ))

    def test_missing_bucket_raises(self):
        with pytest.raises(ValueError, match="bucket"):
            validate_params(CloudFrontSiteParams(
                domain="example.com",
                bucket="",
                cert_arn="arn:aws:acm:us-east-1:123456789012:certificate/abc123",
                region="us-east-1",
            ))

    def test_missing_cert_arn_raises(self):
        with pytest.raises(ValueError, match="cert_arn"):
            validate_params(CloudFrontSiteParams(
                domain="example.com",
                bucket="example.com",
                cert_arn="",
                region="us-east-1",
            ))

    def test_invalid_cert_arn_format_raises(self):
        with pytest.raises(ValueError, match="cert_arn"):
            validate_params(CloudFrontSiteParams(
                domain="example.com",
                bucket="example.com",
                cert_arn="not-a-valid-arn",
                region="us-east-1",
            ))

    def test_cert_must_be_us_east_1(self):
        """ACM certs for CloudFront must be in us-east-1."""
        with pytest.raises(ValueError, match="us-east-1"):
            validate_params(CloudFrontSiteParams(
                domain="example.com",
                bucket="example.com",
                cert_arn="arn:aws:acm:eu-west-1:123456789012:certificate/abc123",
                region="us-east-1",
            ))


# ── generate_distribution_config tests ─────────────────────────────────────

class TestGenerateDistributionConfig:
    def _make_params(self, **kwargs):
        defaults = dict(
            domain="example.com",
            bucket="example.com",
            cert_arn="arn:aws:acm:us-east-1:123456789012:certificate/abc123",
            region="us-east-1",
        )
        defaults.update(kwargs)
        return CloudFrontSiteParams(**defaults)

    def test_returns_dict(self):
        config = generate_distribution_config(self._make_params())
        assert isinstance(config, dict)

    def test_is_json_serializable(self):
        config = generate_distribution_config(self._make_params())
        json.dumps(config)  # Should not raise

    def test_contains_domain_alias(self):
        config = generate_distribution_config(self._make_params(domain="mysite.com"))
        aliases = config["Aliases"]["Items"]
        assert "mysite.com" in aliases

    def test_contains_cert_arn(self):
        cert = "arn:aws:acm:us-east-1:123456789012:certificate/abc123"
        config = generate_distribution_config(self._make_params(cert_arn=cert))
        assert config["ViewerCertificate"]["ACMCertificateArn"] == cert

    def test_viewer_protocol_is_redirect_to_https(self):
        config = generate_distribution_config(self._make_params())
        policy = config["DefaultCacheBehavior"]["ViewerProtocolPolicy"]
        assert policy == "redirect-to-https"

    def test_origin_uses_bucket_name(self):
        config = generate_distribution_config(self._make_params(bucket="my-bucket", region="us-east-1"))
        origin = config["Origins"]["Items"][0]
        assert "my-bucket" in origin["DomainName"]

    def test_https_minimum_protocol_version(self):
        config = generate_distribution_config(self._make_params())
        version = config["ViewerCertificate"]["MinimumProtocolVersion"]
        assert version == "TLSv1.2_2021"

    def test_compression_is_enabled(self):
        config = generate_distribution_config(self._make_params())
        assert config["DefaultCacheBehavior"]["Compress"] is True

    def test_custom_error_404_to_index(self):
        """CloudFront S3 returns 403/404 for missing files; we handle both."""
        config = generate_distribution_config(self._make_params())
        error_codes = [e["ErrorCode"] for e in config["CustomErrorResponses"]["Items"]]
        assert 403 in error_codes
        assert 404 in error_codes

    def test_url_rewrite_function_associated(self):
        """The CloudFront function for directory index rewrite must be attached."""
        config = generate_distribution_config(self._make_params())
        functions = config["DefaultCacheBehavior"].get("FunctionAssociations", {})
        items = functions.get("Items", [])
        assert len(items) >= 1
        events = [f["EventType"] for f in items]
        assert "viewer-request" in events

    def test_caller_reference_uses_domain(self):
        config = generate_distribution_config(self._make_params(domain="example.com"))
        assert "example.com" in config["CallerReference"]

    def test_enabled_by_default(self):
        config = generate_distribution_config(self._make_params())
        assert config["Enabled"] is True

    def test_www_alias_included_when_requested(self):
        config = generate_distribution_config(self._make_params(domain="example.com", include_www=True))
        aliases = config["Aliases"]["Items"]
        assert "example.com" in aliases
        assert "www.example.com" in aliases
        assert config["Aliases"]["Quantity"] == 2

    def test_www_alias_not_included_by_default(self):
        config = generate_distribution_config(self._make_params(domain="example.com"))
        aliases = config["Aliases"]["Items"]
        assert "www.example.com" not in aliases


# ── generate_url_rewrite_function tests ────────────────────────────────────

class TestGenerateUrlRewriteFunction:
    def test_returns_string(self):
        code = generate_url_rewrite_function()
        assert isinstance(code, str)

    def test_contains_handler_function(self):
        code = generate_url_rewrite_function()
        assert "function handler" in code

    def test_handles_trailing_slash(self):
        code = generate_url_rewrite_function()
        assert "index.html" in code

    def test_handles_no_extension(self):
        """URIs without extensions should get /index.html appended."""
        code = generate_url_rewrite_function()
        # Should have logic to check for file extension
        assert "includes('.')" in code or "indexOf('.')" in code or "extension" in code.lower()

    def test_is_valid_cloudfront_function_format(self):
        """Must return the event request at the end."""
        code = generate_url_rewrite_function()
        assert "return request" in code

    def test_no_nodejs_import_statements(self):
        """CloudFront Functions (not Lambda) must not use import/require."""
        code = generate_url_rewrite_function()
        assert "require(" not in code
        assert "import " not in code
