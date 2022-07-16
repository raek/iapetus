from enum import Enum
from hashlib import sha256
from pathlib import Path
import ssl
import socket

import cryptography.x509 as x509
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from appdirs import user_config_dir


class KeyMismatchError(Exception):
    pass


class VerificationResult(Enum):
    FIRST = 0
    MATCH = 1
    MISMATCH = 2


class KeyMismatchBehavior(Enum):
    ERROR = 0
    IGNORE = 1
    REPLACE = 2


class Client:
    def __init__(self):
        self.ssl_context = make_ssl_context()
        self.trust_db = TrustDb()

    def fetch(self, address, on_key_mismatch=KeyMismatchBehavior.ERROR):
        host, port = address
        with socket.create_connection(address) as s:
            with self.ssl_context.wrap_socket(s, server_hostname=host) as ss:
                der_cert = ss.getpeercert(binary_form=True)
                peer_key_hash = public_key_hash(der_cert)
                result = verify_cert(self.trust_db, address, peer_key_hash)
                if result == VerificationResult.MISMATCH:
                    perform_key_mismatch_behaior(self.trust_db, on_key_mismatch)


def make_ssl_context():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    return ctx


def public_key_hash(der_cert):
    """Certificate in DER format to SHA256 sum (as hex) of public key part"""
    cert = x509.load_der_x509_certificate(der_cert)
    public_key = cert.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    return sha256(public_key).hexdigest()


def verify_cert(trust_db, address, peer_key_hash):
    stored_key_hash = trust_db.lookup_key_hash(address)
    if stored_key_hash is not None:
        if peer_key_hash == stored_key_hash:
            return VerificationResult.MATCH
        else:
            return VerificationResult.MISMATCH
    else:
        trust_db.store_key_hash(address, peer_key_hash)
        return VerificationResult.FIRST


def perform_key_mismatch_behaior(trust_db, on_key_mismatch):
    if on_key_mismatch == KeyMismatchBehavior.ERROR:
        raise KeyMismatchError()
    elif on_key_mismatch == KeyMismatchBehavior.IGNORE:
        return
    elif on_key_mismatch == KeyMismatchBehavior.REPLACE:
        self.trust_db.forget_key_hash(address)
        self.trust_db.store_key_hash(address, peer_key_hash)


class TrustDb:
    def __init__(self):
        config_dir = Path(user_config_dir("iapetus"))
        # This creates parents of the config dir too, but with the
        # default mode (see Path.mkdir docs).
        config_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.known_hosts_dir = config_dir / "known_hosts"
        self.known_hosts_dir.mkdir(mode=0o700, exist_ok=True)

    def lookup_key_hash(self, address):
        path = self._address_to_path(address)
        if path.exists():
            return path.read_text(encoding="us-ascii")
        else:
            return None

    def forget_key_hash(self, address):
        self._address_to_path(address).unlink(missing_ok=True)

    def store_key_hash(self, address, key_hash):
        self._address_to_path(address).write_text(key_hash, encoding="us-ascii")

    def _address_to_path(self, address):
        host, port = address
        return self.known_hosts_dir / f"{host}:{port}"
