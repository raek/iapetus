import pytest

from iapetus.url import normalize_url, host_port_pair_from_url, NormalizationError, NonGeminiUrlError


# References
#
# * [URI] https://datatracker.ietf.org/doc/html/rfc3986
# * [GEMINI] https://gemini.circumlunar.space/docs/specification.gmi


def test_all_parts_simple_example():
    s = "gemini://example.com:5691/one/two?three#four"
    assert normalize_url(s) == s


def test_non_gemini_scheme():
    with pytest.raises(NonGeminiUrlError):
        normalize_url("https://example.com/")


# [URI] 6.2.2.1.  Case Normalization
def test_scheme_case_lowered():
    assert normalize_url("GEMINI://example.com/") == "gemini://example.com/"


# [GEMINI] 1.2 Gemini URI scheme
def test_netloc_required():
    with pytest.raises(NormalizationError):
        normalize_url("gemini:///")


# [GEMINI] 1.2 Gemini URI scheme
def test_userinfo_not_allowed():
    with pytest.raises(NormalizationError):
        normalize_url("gemini://user:pass@example.com/")


# [URI] 6.2.3.  Scheme-Based Normalization
# [GEMINI] 1.2 Gemini URI scheme
def test_non_standard_port():
    assert normalize_url("gemini://example.com:5691/") == "gemini://example.com:5691/"


# [URI] 6.2.3.  Scheme-Based Normalization
# [GEMINI] 1.2 Gemini URI scheme
def test_standard_port_removed():
    assert normalize_url("gemini://example.com:1965/") == "gemini://example.com/"


# [URI] 6.2.3.  Scheme-Based Normalization
# [GEMINI] 1.2 Gemini URI scheme
def test_empty_port_removed():
    assert normalize_url("gemini://example.com:/") == "gemini://example.com/"


# [URI] 6.2.2.1.  Case Normalization
def test_domain_name_case_lowered():
    assert normalize_url("gemini://EXAMPLE.COM/") == "gemini://example.com/"


# [URI] 3.2.2.  Host
def test_domain_name_idna_encoded():
    assert normalize_url("gemini://exämple.com/") == "gemini://xn--exmple-cua.com/"


# [URI] 3.2.2.  Host
def test_percent_encoded_domain_name_idna_encoded():
    assert normalize_url("gemini://ex%C3%A4mple.com/") == "gemini://xn--exmple-cua.com/"


# [URI] 6.2.3.  Scheme-Based Normalization
# [GEMINI] 1.2 Gemini URI scheme
def test_empty_path_changed_into_slash():
    assert normalize_url("gemini://example.com") == "gemini://example.com/"


def test_single_slash_remains():
    assert normalize_url("gemini://example.com/") == "gemini://example.com/"


# [URI] 6.2.2.2.  Percent-Encoding Normalization
def test_path_percent_encoded_reserved_remains():
    assert normalize_url("gemini://example.com/%2F") == "gemini://example.com/%2F"


# [URI] 6.2.2.2.  Percent-Encoding Normalization
def test_path_percent_encoded_unreserved_decoded():
    assert normalize_url("gemini://example.com/%61") == "gemini://example.com/a"


# [URI] 6.2.2.2.  Percent-Encoding Normalization
def test_path_unreserved_remains():
    assert normalize_url("gemini://example.com/a") == "gemini://example.com/a"


# [URI] 6.2.2.2.  Percent-Encoding Normalization
def test_path_reserved_percent_encoded():
    assert normalize_url("gemini://example.com/:") == "gemini://example.com/%3A"


# [URI] 6.2.2.2.  Percent-Encoding Normalization
# [GEMINI] 1.2 Gemini URI scheme
def test_path_space_is_percent_encoded():
    assert normalize_url("gemini://example.com/ ") == "gemini://example.com/%20"


# [URI] 6.2.2.1.  Case Normalization
def test_path_percent_encoding_case_uppered():
    assert normalize_url("gemini://example.com/%c3%a4") == "gemini://example.com/%C3%A4"


# [URI] 5.2.4.  Remove Dot Segments
def test_path_dot_segment():
    assert normalize_url("gemini://example.com/a/./b") == "gemini://example.com/a/b"


# [URI] 5.2.4.  Remove Dot Segments
def test_path_double_dot_segment():
    assert normalize_url("gemini://example.com/a/../b") == "gemini://example.com/b"


# [URI] 5.2.4.  Remove Dot Segments
# NOTE: in RFC 1808 (which RFC 3986 replaces) the .. segment used to be kept instead
def test_path_double_dot_past_root():
    assert normalize_url("gemini://example.com/../b") == "gemini://example.com/b"


# [URI] 3.4.  Query
def test_query_part_is_accepted():
    assert normalize_url("gemini://example.com/?query") == "gemini://example.com/?query"


# [URI] 6.2.2.2.  Percent-Encoding Normalization
def test_query_percent_encoded_reserved_remains():
    assert normalize_url("gemini://example.com/?%3A") == "gemini://example.com/?%3A"


# [URI] 6.2.2.2.  Percent-Encoding Normalization
def test_query_percent_encoded_unreserved_decoded():
    assert normalize_url("gemini://example.com/?%61") == "gemini://example.com/?a"


# [URI] 6.2.2.2.  Percent-Encoding Normalization
def test_query_unreserved_remains():
    assert normalize_url("gemini://example.com/?a") == "gemini://example.com/?a"


# [URI] 6.2.2.2.  Percent-Encoding Normalization
def test_query_reserved_percent_encoded():
    assert normalize_url("gemini://example.com/?:") == "gemini://example.com/?%3A"


# [URI] 6.3.  Component Recomposition
def test_empty_query_distinct_from_no_query():
    assert normalize_url("gemini://example.com/?") == "gemini://example.com/?"


# [URI] 3.5.  Fragment
def test_fragment_part_is_accepted():
    assert normalize_url("gemini://example.com/#fragment") == "gemini://example.com/#fragment"


# [URI] 6.2.2.2.  Percent-Encoding Normalization
def test_fragment_percent_encoded_reserved_remains():
    assert normalize_url("gemini://example.com/#%3A") == "gemini://example.com/#%3A"


# [URI] 6.2.2.2.  Percent-Encoding Normalization
def test_fragment_percent_encoded_unreserved_decoded():
    assert normalize_url("gemini://example.com/#%61") == "gemini://example.com/#a"


# [URI] 6.2.2.2.  Percent-Encoding Normalization
def test_fragment_unreserved_remains():
    assert normalize_url("gemini://example.com/#a") == "gemini://example.com/#a"


# [URI] 6.2.2.2.  Percent-Encoding Normalization
def test_fragment_reserved_percent_encoded():
    assert normalize_url("gemini://example.com/#:") == "gemini://example.com/#%3A"


# [URI] 6.3.  Component Recomposition
def test_empty_fragment_distinct_from_no_fragment():
    assert normalize_url("gemini://example.com/#") == "gemini://example.com/#"


def test_host_port_pair_no_port():
    assert host_port_pair_from_url("gemini://example.com/") == ("example.com", 1965)


def test_host_port_pair_with_port():
    assert host_port_pair_from_url("gemini://example.com:5691/") == ("example.com", 5691)
