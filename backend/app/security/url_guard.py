"""
Ultron URL Guard (Phase 4 — SSRF prevention)

Rejects outbound HTTP(S) requests to private/loopback/link-local/metadata
addresses (SSRF). A URL is safe only if it is http(s) and its resolved IP is
public. This prevents tools from hitting 127.0.0.1, the cloud metadata service
(169.254.169.254), or internal networks from a tool-call.
"""

import ipaddress
import socket
from urllib.parse import urlparse

# Hostnames that are always local/metadata, blocked regardless of resolution.
_BLOCKED_HOSTNAMES = {
    "localhost", "metadata", "metadata.google.internal",
    "169.254.169.254",
}

# Maximum accepted download size (bytes): 50 MB.
MAX_DOWNLOAD_BYTES = 50 * 1024 * 1024


def validate_public_url(url: str):
    """Return (ok: bool, reason: str | None)."""
    if not url or not url.lower().startswith(("http://", "https://")):
        return False, "URL must be http(s)"
    try:
        host = urlparse(url).hostname
    except Exception:
        return False, "malformed URL"
    if not host:
        return False, "URL has no host"

    host_lower = host.lower().rstrip(".")
    if host_lower in _BLOCKED_HOSTNAMES:
        return False, f"local/metadata host blocked: {host}"

    # Resolve and reject private / loopback / link-local / reserved addresses.
    try:
        infos = socket.getaddrinfo(host_lower, None)
    except socket.gaierror:
        return False, "host does not resolve"
    except Exception:
        return False, "address lookup failed"

    if not infos:
        return False, "host did not resolve to an address"

    for info in infos:
        ip = info[4][0]
        try:
            obj = ipaddress.ip_address(ip)
        except ValueError:
            continue
        if (obj.is_private or obj.is_loopback or obj.is_link_local
                or obj.is_reserved or obj.is_multicast):
            return False, f"non-public address blocked: {ip}"

    return True, None
