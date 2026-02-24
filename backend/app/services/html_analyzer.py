import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.utils.logger import get_logger

logger = get_logger(__name__)

OBFUSCATION_PATTERNS = [
    re.compile(r"eval\(", re.IGNORECASE),
    re.compile(r"unescape\(", re.IGNORECASE),
    re.compile(r"fromCharCode", re.IGNORECASE),
    re.compile(r"\\x[0-9a-fA-F]{2}", re.IGNORECASE),
]


async def analyze_html(url: str, timeout: int = 10) -> Dict[str, Any]:
    """Download and analyze HTML content of a URL."""
    features: Dict[str, Any] = {
        "html_form_count": 0,
        "external_link_ratio": 0.0,
        "null_hyperlinks": 0,
        "iframe_count": 0,
        "javascript_obfuscated": 0,
        "favicon_from_external": 0,
        "meta_refresh": 0,
        "right_click_disabled": 0,
    }
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=timeout,
            verify=False,
        ) as client:
            response = await client.get(url)
            html = response.text
    except Exception as exc:
        logger.debug({"msg": "HTML fetch failed", "url": url, "error": str(exc)})
        return features

    try:
        soup = BeautifulSoup(html, "html.parser")
        parsed_url = urlparse(url)
        base_domain = parsed_url.netloc.lower()

        # Form count
        features["html_form_count"] = len(soup.find_all("form"))

        # Links analysis
        all_links = soup.find_all("a", href=True)
        null_count = 0
        external_count = 0
        for link in all_links:
            href = link["href"]
            if href in ("#", "", "javascript:void(0)", "javascript:;"):
                null_count += 1
            elif href.startswith("http"):
                link_domain = urlparse(href).netloc.lower()
                if link_domain and link_domain != base_domain:
                    external_count += 1
        features["null_hyperlinks"] = null_count
        features["external_link_ratio"] = (
            round(external_count / len(all_links), 4) if all_links else 0.0
        )

        # iframes
        features["iframe_count"] = len(soup.find_all("iframe"))

        # JavaScript obfuscation
        scripts = soup.find_all("script")
        script_content = " ".join(s.get_text() for s in scripts)
        features["javascript_obfuscated"] = int(
            any(p.search(script_content) for p in OBFUSCATION_PATTERNS)
        )

        # Favicon from external domain
        favicon_tag = soup.find("link", rel=lambda r: r and "icon" in r)
        if favicon_tag and favicon_tag.get("href", "").startswith("http"):
            fav_domain = urlparse(favicon_tag["href"]).netloc.lower()
            features["favicon_from_external"] = int(
                fav_domain != "" and fav_domain != base_domain
            )

        # Meta refresh
        meta_refresh = soup.find("meta", attrs={"http-equiv": re.compile("refresh", re.I)})
        features["meta_refresh"] = int(meta_refresh is not None)

        # Right-click disabled
        features["right_click_disabled"] = int(
            "contextmenu" in html.lower() and "return false" in html.lower()
        )

    except Exception as exc:
        logger.debug({"msg": "HTML parse failed", "url": url, "error": str(exc)})

    return features
