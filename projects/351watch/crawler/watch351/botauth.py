"""Web Bot Auth: sign AgendaAheadBot's requests so sites behind Cloudflare can verify who we are.

Cloudflare's Verified Bots programme accepts bots that sign each request with an
Ed25519 key published in a key directory (HTTP Message Signatures, RFC 9421, plus
draft-meunier-web-bot-auth-architecture). Our directory is served by the site at
https://agendaahead.vercel.app/.well-known/http-message-signatures-directory
(site/api/key-directory.js), signed with the same key.

The private key is the 32-byte Ed25519 seed, base64url-encoded, in the
WBA_PRIVATE_KEY environment variable (the same value is set on the Vercel
project). Without it the crawler sends unsigned requests exactly as before.

Signing only says who we are. It does not change what we fetch: robots.txt,
the per-host rate limit and every other rule in fetch.py still apply.

CLI:
  python3 -m watch351.botauth keygen KEYFILE   write a new seed (mode 600)
  python3 -m watch351.botauth info             key id and public key from WBA_PRIVATE_KEY
  python3 -m watch351.botauth check-directory [URL]
                                               fetch our key directory and verify its signature
  python3 -m watch351.botauth test [URL]       send one signed request to Cloudflare's test endpoint
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import secrets
import sys
import time
from urllib.parse import urlsplit

KEY_ENV = "WBA_PRIVATE_KEY"
SIGNATURE_AGENT = os.environ.get("WBA_SIGNATURE_AGENT", "https://agendaahead.vercel.app")
DIRECTORY_PATH = "/.well-known/http-message-signatures-directory"
CLOUDFLARE_TEST_URL = "https://crawltest.com/cdn-cgi/web-bot-auth"
SIGNATURE_TTL = 60  # seconds; Cloudflare suggests about a minute


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(text: str) -> bytes:
    text = text.strip()
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def jwk_thumbprint(x: str) -> str:
    """RFC 7638 / RFC 8037 thumbprint of an Ed25519 public key (base64url x)."""
    canonical = json.dumps({"crv": "Ed25519", "kty": "OKP", "x": x}, separators=(",", ":"),
                           sort_keys=True)
    return b64url(hashlib.sha256(canonical.encode("ascii")).digest())


def authority_of(url: str) -> str:
    """RFC 9421 @authority: lowercased host, plus the port only if it isn't the default."""
    parts = urlsplit(url)
    host = (parts.hostname or "").encode("idna").decode("ascii").lower()
    port = parts.port
    if port and not ((parts.scheme == "https" and port == 443) or (parts.scheme == "http" and port == 80)):
        host = f"{host}:{port}"
    return host


class Signer:
    def __init__(self, seed: bytes, agent: str = SIGNATURE_AGENT):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        if len(seed) != 32:
            raise ValueError(f"{KEY_ENV} must decode to a 32-byte Ed25519 seed")
        self._key = Ed25519PrivateKey.from_private_bytes(seed)
        raw_pub = self._key.public_key().public_bytes(serialization.Encoding.Raw,
                                                      serialization.PublicFormat.Raw)
        self.x = b64url(raw_pub)
        self.keyid = jwk_thumbprint(self.x)
        self.agent = agent

    def headers(self, url: str, now: float | None = None) -> dict[str, str]:
        """The three Web Bot Auth headers for one request to `url`."""
        created = int(now if now is not None else time.time())
        agent_field = f'"{self.agent}"'
        nonce = base64.b64encode(secrets.token_bytes(48)).decode("ascii")
        params = (f'("@authority" "signature-agent");created={created};keyid="{self.keyid}";'
                  f'alg="ed25519";expires={created + SIGNATURE_TTL};nonce="{nonce}";tag="web-bot-auth"')
        base = (f'"@authority": {authority_of(url)}\n'
                f'"signature-agent": {agent_field}\n'
                f'"@signature-params": {params}')
        signature = base64.b64encode(self._key.sign(base.encode("ascii"))).decode("ascii")
        return {
            "Signature-Agent": agent_field,
            "Signature-Input": f"sig1={params}",
            "Signature": f"sig1=:{signature}:",
        }


_signer: Signer | None = None
_loaded = False


def signer_from_env() -> Signer | None:
    """The process-wide signer, or None when WBA_PRIVATE_KEY is unset."""
    global _signer, _loaded
    if not _loaded:
        _loaded = True
        value = os.environ.get(KEY_ENV, "").strip()
        if value:
            _signer = Signer(b64url_decode(value))
    return _signer


# ---- checks -----------------------------------------------------------------------

def _parse_signature_input(value: str) -> tuple[str, str]:
    """'sig1=(...);a=b' -> ('sig1', '(...);a=b')."""
    label, _, params = value.partition("=")
    return label.strip(), params.strip()


def verify_directory(url: str) -> dict:
    """Fetch a key directory and check it the way Cloudflare does."""
    import requests
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    r = requests.get(url, headers={"Accept": "application/http-message-signatures-directory+json"},
                     timeout=20)
    result = {"url": url, "status": r.status_code, "content_type": r.headers.get("Content-Type", "")}
    keys = r.json().get("keys", [])
    result["keys"] = [k.get("x") for k in keys]
    label, params = _parse_signature_input(r.headers.get("Signature-Input", ""))
    sig_match = re.search(rf"{re.escape(label)}=:([^:]+):", r.headers.get("Signature", ""))
    result["tag_ok"] = 'tag="http-message-signatures-directory"' in params
    created = int(re.search(r"created=(\d+)", params).group(1)) if "created=" in params else 0
    expires = int(re.search(r"expires=(\d+)", params).group(1)) if "expires=" in params else 0
    result["fresh"] = created <= time.time() + 5 and expires >= time.time()
    keyid = re.search(r'keyid="([^"]+)"', params)
    result["verified"] = False
    if sig_match and keyid:
        base = f'"@authority";req: {authority_of(url)}\n"@signature-params": {params}'
        for k in keys:
            if jwk_thumbprint(k["x"]) == keyid.group(1):
                pub = Ed25519PublicKey.from_public_bytes(b64url_decode(k["x"]))
                try:
                    pub.verify(base64.b64decode(sig_match.group(1)), base.encode("ascii"))
                    result["verified"] = True
                except Exception as e:  # noqa: BLE001 - report, don't raise
                    result["error"] = f"signature did not verify: {e}"
    result["ok"] = (r.status_code == 200 and result["content_type"].startswith(
        "application/http-message-signatures-directory+json") and result["tag_ok"]
        and result["fresh"] and result["verified"])
    return result


def _main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    if cmd == "keygen":
        path = argv[1] if len(argv) > 1 else "wba_private_key.txt"
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(b64url(secrets.token_bytes(32)) + "\n")
        print(f"wrote a new Ed25519 seed to {path} (keep it secret; set it as {KEY_ENV})")
        return 0
    if cmd == "info":
        s = signer_from_env()
        if not s:
            print(f"{KEY_ENV} is not set")
            return 1
        print(json.dumps({"keyid": s.keyid, "x": s.x, "signature_agent": s.agent}, indent=1))
        return 0
    if cmd == "check-directory":
        url = argv[1] if len(argv) > 1 else SIGNATURE_AGENT + DIRECTORY_PATH
        result = verify_directory(url)
        print(json.dumps(result, indent=1))
        return 0 if result["ok"] else 1
    if cmd == "test":
        import requests
        from .fetch import USER_AGENT
        s = signer_from_env()
        if not s:
            print(f"{KEY_ENV} is not set")
            return 1
        url = argv[1] if len(argv) > 1 else CLOUDFLARE_TEST_URL
        r = requests.get(url, headers={"User-Agent": USER_AGENT, **s.headers(url)}, timeout=20)
        meaning = {200: "key known and signature verified", 401: "well formed; key not (yet) known",
                   400: "malformed signature"}.get(r.status_code, "unexpected")
        print(f"{r.status_code} {meaning}")
        return 0 if r.status_code in (200, 401) else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
