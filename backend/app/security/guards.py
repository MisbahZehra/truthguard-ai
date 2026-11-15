import ipaddress, re, socket
from urllib.parse import urlparse

_INJECTION = re.compile(
    r"(ignore (all |any )?(previous|prior|above) instructions|disregard .{0,40}instructions|"
    r"you are now|system prompt|act as|new instructions:|assistant:|<\s*/?system\s*>)", re.I)
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_KEY = re.compile(r"\b(sk-[A-Za-z0-9]{16,}|tv\x6cy-[A-Za-z0-9-]{8,}|AKIA[0-9A-Z]{16})\b")


def sanitize_untrusted(text: str, limit: int = 1500) -> tuple[str, bool]:
    """Neutralize instruction-like text in retrieved content. Returns (text, flagged)."""
    flagged = bool(_INJECTION.search(text))
    cleaned = _INJECTION.sub("[removed-instruction-like-text]", text)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)  # strip tags
    return re.sub(r"\s+", " ", cleaned).strip()[:limit], flagged


def redact(text: str) -> str:
    return _KEY.sub("[REDACTED_KEY]", _EMAIL.sub("[REDACTED_EMAIL]", text))


def is_safe_url(url: str) -> bool:
    """SSRF guard: http(s) only, no credentials, no private/loopback/link-local targets."""
    try:
        p = urlparse(url)
        if p.scheme not in ("http", "https") or not p.hostname or p.username:
            return False
        for info in socket.getaddrinfo(p.hostname, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                return False
        return True
    except Exception:
        return False
