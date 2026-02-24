import math
import re
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any
import tldextract

from app.utils.url_parser import is_ip_address, extract_hostname

SHORTENED_DOMAINS = {
    "bit.ly", "tinyurl.com", "goo.gl", "ow.ly", "t.co", "is.gd",
    "buff.ly", "adf.ly", "short.link", "rebrand.ly", "tiny.cc",
    "cutt.ly", "v.gd", "bl.ink", "shorturl.at",
}

PHISHING_WORDS = {
    "login", "secure", "bank", "update", "verify", "account", "confirm",
    "password", "paypal", "signin", "wallet", "ebay", "amazon", "alert",
    "suspended", "urgent", "limited", "validate", "credential", "webscr",
}

BRAND_KEYWORDS = {
    "paypal", "google", "facebook", "apple", "amazon", "microsoft",
    "netflix", "instagram", "twitter", "linkedin", "dropbox", "chase",
    "wellsfargo", "citibank", "bankofamerica",
}

SUSPICIOUS_BRAND_SUBS = {
    "paypa1", "g00gle", "g0ogle", "amaz0n", "micros0ft", "netfl1x",
    "facebok", "faceb00k", "appleid", "lnstagram", "tw1tter",
}


def _shannon_entropy(s: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not s:
        return 0.0
    freq: Dict[str, int] = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    entropy = 0.0
    length = len(s)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


class FeatureExtractor:
    """Extracts features from a URL for phishing detection."""

    def extract(self, url: str) -> Dict[str, Any]:
        """Extract all features from the URL. Returns a flat dict."""
        features: Dict[str, Any] = {}
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        path = parsed.path or ""
        query = parsed.query or ""
        fragment = parsed.fragment or ""
        full_url = url

        ext = tldextract.extract(url)
        subdomain = ext.subdomain
        domain = ext.domain
        suffix = ext.suffix
        registered_domain = f"{domain}.{suffix}" if domain and suffix else ""

        # --- URL length features ---
        features["url_length"] = len(full_url)
        features["hostname_length"] = len(hostname)
        features["path_length"] = len(path)
        features["query_length"] = len(query)

        # --- Character count features ---
        features["num_dots"] = full_url.count(".")
        features["num_hyphens"] = full_url.count("-")
        features["num_underscores"] = full_url.count("_")
        features["num_slashes"] = full_url.count("/")
        features["num_question_marks"] = full_url.count("?")
        features["num_at_symbols"] = full_url.count("@")
        features["num_equals"] = full_url.count("=")
        features["num_ampersands"] = full_url.count("&")
        features["num_percent"] = full_url.count("%")
        features["num_hash"] = full_url.count("#")

        # --- Domain features ---
        digits_in_domain = sum(c.isdigit() for c in hostname)
        features["num_digits_in_domain"] = digits_in_domain
        features["num_subdomains"] = len(subdomain.split(".")) if subdomain else 0

        # --- Boolean indicator features ---
        features["has_ip_address"] = int(is_ip_address(hostname))
        features["has_https"] = int(parsed.scheme == "https")
        features["https_in_hostname"] = int("https" in hostname.lower())
        features["has_port"] = int(parsed.port is not None)

        # --- Entropy and ratio features ---
        features["path_entropy"] = round(_shannon_entropy(path), 4)
        total_len = len(full_url) if full_url else 1
        special_chars = sum(not c.isalnum() for c in full_url)
        features["special_char_ratio"] = round(special_chars / total_len, 4)
        digit_count = sum(c.isdigit() for c in full_url)
        features["digit_ratio"] = round(digit_count / total_len, 4)
        letter_count = sum(c.isalpha() for c in full_url)
        features["letter_ratio"] = round(letter_count / total_len, 4)

        # --- Suspicious indicators ---
        features["is_shortened"] = int(registered_domain in SHORTENED_DOMAINS)
        lower_url = full_url.lower()
        features["suspicious_words"] = int(
            any(word in lower_url for word in PHISHING_WORDS)
        )
        features["brand_impersonation"] = int(
            any(sub in lower_url for sub in SUSPICIOUS_BRAND_SUBS)
        )

        # --- URL structure features ---
        features["url_depth"] = path.count("/") if path else 0
        features["redirection_count"] = max(0, full_url.count("//") - 1)
        features["query_param_count"] = len(parse_qs(query))
        features["fragment_length"] = len(fragment)

        # --- TLD features ---
        features["tld_length"] = len(suffix) if suffix else 0
        features["domain_length"] = len(domain) if domain else 0

        # --- Placeholder features (filled by services) ---
        features["domain_age_days"] = -1
        features["domain_registration_length"] = -1
        features["has_valid_ssl"] = 0
        features["ssl_issuer_is_trusted"] = 0
        features["ssl_days_remaining"] = -1
        features["is_blacklisted"] = 0
        features["html_form_count"] = 0
        features["external_link_ratio"] = 0.0
        features["null_hyperlinks"] = 0
        features["iframe_count"] = 0
        features["javascript_obfuscated"] = 0
        features["favicon_from_external"] = 0
        features["meta_refresh"] = 0
        features["right_click_disabled"] = 0

        return features

    def update_with_service_features(
        self,
        features: Dict[str, Any],
        service_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge features obtained from external services."""
        features.update(service_data)
        return features

    def to_feature_vector(self, features: Dict[str, Any]) -> list:
        """Return ordered feature values for ML model input."""
        return [features.get(k, 0) for k in self._feature_names()]

    def _feature_names(self) -> list:
        return [
            "url_length", "hostname_length", "path_length", "query_length",
            "num_dots", "num_hyphens", "num_underscores", "num_slashes",
            "num_question_marks", "num_at_symbols", "num_equals",
            "num_ampersands", "num_percent", "num_hash",
            "num_digits_in_domain", "num_subdomains",
            "has_ip_address", "has_https", "https_in_hostname", "has_port",
            "path_entropy", "special_char_ratio", "digit_ratio", "letter_ratio",
            "is_shortened", "suspicious_words", "brand_impersonation",
            "url_depth", "redirection_count", "query_param_count",
            "fragment_length", "tld_length", "domain_length",
            "domain_age_days", "domain_registration_length",
            "has_valid_ssl", "ssl_issuer_is_trusted", "ssl_days_remaining",
            "is_blacklisted", "html_form_count", "external_link_ratio",
            "null_hyperlinks", "iframe_count", "javascript_obfuscated",
            "favicon_from_external", "meta_refresh", "right_click_disabled",
        ]
