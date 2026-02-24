import re
from urllib.parse import urlparse, urlunparse
from typing import Optional
import tldextract


def normalize_url(url: str) -> str:
    """Normalize URL by adding schema if missing and lowercasing hostname."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    parsed = urlparse(url)
    normalized = parsed._replace(netloc=parsed.netloc.lower())
    return urlunparse(normalized)


def is_valid_url(url: str) -> bool:
    """Check if a URL is syntactically valid."""
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


def extract_domain(url: str) -> str:
    """Extract the registered domain from a URL."""
    extracted = tldextract.extract(url)
    if extracted.domain and extracted.suffix:
        return f"{extracted.domain}.{extracted.suffix}"
    return extracted.domain or ""


def extract_hostname(url: str) -> str:
    """Extract hostname from URL."""
    try:
        return urlparse(url).hostname or ""
    except Exception:
        return ""


def get_url_hash(url: str) -> str:
    """Return SHA256 hash of normalized URL."""
    import hashlib

    return hashlib.sha256(url.encode()).hexdigest()


IP_PATTERN = re.compile(
    r"^(\d{1,3}\.){3}\d{1,3}$"
)


def is_ip_address(hostname: str) -> bool:
    """Check if hostname is an IP address."""
    return bool(IP_PATTERN.match(hostname))


def get_tld(url: str) -> Optional[str]:
    """Get top-level domain from URL."""
    extracted = tldextract.extract(url)
    return extracted.suffix or None
