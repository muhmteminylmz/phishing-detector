import ssl
import socket
from datetime import datetime, timezone
from typing import Dict, Any

from app.utils.logger import get_logger

logger = get_logger(__name__)

TRUSTED_ISSUERS = {
    "Let's Encrypt", "DigiCert", "Comodo", "GlobalSign", "Sectigo",
    "GeoTrust", "Thawte", "RapidSSL", "Amazon", "Entrust",
}


def check_ssl(hostname: str, port: int = 443, timeout: int = 5) -> Dict[str, Any]:
    """Check SSL certificate for a hostname and return relevant features."""
    result: Dict[str, Any] = {
        "has_valid_ssl": 0,
        "ssl_issuer_is_trusted": 0,
        "ssl_days_remaining": -1,
    }
    if not hostname:
        return result
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                if cert:
                    result["has_valid_ssl"] = 1
                    # Parse expiry
                    not_after = cert.get("notAfter", "")
                    if not_after:
                        expire_dt = datetime.strptime(
                            not_after, "%b %d %H:%M:%S %Y %Z"
                        ).replace(tzinfo=timezone.utc)
                        days_left = (expire_dt - datetime.now(timezone.utc)).days
                        result["ssl_days_remaining"] = max(days_left, 0)
                    # Check issuer
                    issuer = dict(x[0] for x in cert.get("issuer", []))
                    org = issuer.get("organizationName", "")
                    result["ssl_issuer_is_trusted"] = int(
                        any(t in org for t in TRUSTED_ISSUERS)
                    )
    except ssl.SSLCertVerificationError:
        result["has_valid_ssl"] = 0
    except Exception as exc:
        logger.debug({"msg": "SSL check failed", "hostname": hostname, "error": str(exc)})
    return result
