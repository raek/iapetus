import argparse
import sys

from .url import normalize_url, host_port_pair_from_url, NormalizationError
from .client import Client, KeyMismatchBehavior, KeyMismatchError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--on-key-mismatch", default="error",
                        choices=[m.name.lower() for m in KeyMismatchBehavior])
    parser.add_argument("url")
    args = parser.parse_args()
    on_key_mismatch = KeyMismatchBehavior[args.on_key_mismatch.upper()]
    try:
        url = normalize_url(args.url)
    except NormalizationError as e:
        sys.stderr.write(f"Invalid URL \"{args.url}\": {e.args[0]}\n")
        sys.exit(1)
    client = Client()
    try:
        page = client.fetch(host_port_pair_from_url(url), on_key_mismatch)
        print(page)
    except KeyMismatchError:
        sys.stderr.write("ERROR: The host public key has changed!\n")
        sys.stderr.write("It is possible that someone is doing something nasty!\n")
        sys.stderr.write("Someone could be eavesdropping on you right now (man-in-the-middle attack)!\n")
        sys.stderr.write("\n")
        sys.stderr.write("It is also possible that a host key has just been changed.\n")
        sys.stderr.write("Add --on-key-mismatch=ignore to allow the new key for this request\n")
        sys.stderr.write("or --on-key-mismatch=replace to forget the old key and start using the new key.\n")
        sys.exit(1)
