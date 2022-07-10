import argparse

from .url import normalize_url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()
    print(normalize_url(args.url))
