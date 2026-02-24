import pytest
from app.models.feature_extractor import FeatureExtractor, _shannon_entropy


@pytest.fixture
def extractor() -> FeatureExtractor:
    return FeatureExtractor()


def test_basic_url_features(extractor: FeatureExtractor) -> None:
    features = extractor.extract("https://google.com/search?q=test")
    assert features["url_length"] > 0
    assert features["has_https"] == 1
    assert features["has_ip_address"] == 0
    assert features["num_question_marks"] == 1


def test_ip_address_detection(extractor: FeatureExtractor) -> None:
    features = extractor.extract("http://192.168.1.1/admin")
    assert features["has_ip_address"] == 1


def test_at_symbol_detection(extractor: FeatureExtractor) -> None:
    features = extractor.extract("http://legit.com@evil.com/phish")
    assert features["num_at_symbols"] >= 1


def test_suspicious_words(extractor: FeatureExtractor) -> None:
    features = extractor.extract("http://secure-login-bank.xyz/verify")
    assert features["suspicious_words"] == 1


def test_no_suspicious_words(extractor: FeatureExtractor) -> None:
    features = extractor.extract("https://github.com/repos/list")
    assert features["suspicious_words"] == 0


def test_shortened_url(extractor: FeatureExtractor) -> None:
    features = extractor.extract("http://bit.ly/abc123")
    assert features["is_shortened"] == 1


def test_https_in_hostname(extractor: FeatureExtractor) -> None:
    features = extractor.extract("http://https-secure-bank.xyz/login")
    assert features["https_in_hostname"] == 1


def test_very_long_url(extractor: FeatureExtractor) -> None:
    long_url = "http://evil.xyz/" + "a" * 500
    features = extractor.extract(long_url)
    assert features["url_length"] > 500


def test_unicode_url(extractor: FeatureExtractor) -> None:
    # Should not raise an exception
    features = extractor.extract("http://xn--nxasmq6b.com/path")
    assert isinstance(features, dict)


def test_feature_vector_length(extractor: FeatureExtractor) -> None:
    features = extractor.extract("https://example.com")
    vector = extractor.to_feature_vector(features)
    assert len(vector) == len(extractor._feature_names())


def test_shannon_entropy() -> None:
    assert _shannon_entropy("") == 0.0
    # Uniform string has higher entropy than constant
    high = _shannon_entropy("abcdefgh")
    low = _shannon_entropy("aaaaaaaa")
    assert high > low


def test_brand_impersonation(extractor: FeatureExtractor) -> None:
    features = extractor.extract("http://paypa1.evil.xyz/login")
    assert features["brand_impersonation"] == 1


def test_port_detection(extractor: FeatureExtractor) -> None:
    features = extractor.extract("http://evil.com:8080/admin")
    assert features["has_port"] == 1


def test_redirection_count(extractor: FeatureExtractor) -> None:
    features = extractor.extract("http://evil.com//redirect//admin")
    assert features["redirection_count"] >= 1


def test_url_depth(extractor: FeatureExtractor) -> None:
    features = extractor.extract("http://evil.com/a/b/c/d")
    assert features["url_depth"] >= 4
