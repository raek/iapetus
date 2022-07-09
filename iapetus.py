from urllib.parse import urlsplit, urlunsplit, quote, unquote


DEFAULT_PORT = 1965


def normalize_url(s):
    u = urlsplit(s)
    scheme = u.scheme.lower()
    if u.netloc == "":
        raise ValueError("Gemini URI scheme requires the authority component")
    if u.username or u.password:
        raise ValueError("Gemini URI scheme does not support userinfo components")
    if u.hostname is not None:
        hostname = unquote(u.hostname).encode("idna").decode("us-ascii")
    else:
        hostname = ""
    port = "" if u.port is None or u.port == DEFAULT_PORT else ":" + str(u.port)
    netloc = hostname + port
    assert u.path.startswith("/") or u.path == ""
    if u.path == "":
        path = "/"
    else:
        path_segments = [quote(unquote(p), safe="") for p in u.path[1:].split("/") if p != "."]
        without_double_dots = []
        for segment in path_segments:
            if segment == ".." and without_double_dots:
                without_double_dots.pop()
            elif segment == "..":
                # Extra double dots that go past the root are discarded
                continue
            else:
                without_double_dots.append(segment)
        path = "".join("/" + segment for segment in without_double_dots)
    if path == "":
        path = "/"
    query = u.query
    fragment = u.fragment
    return urlunsplit((scheme, netloc, path, query, fragment))
