"""Explicit byte profiles; formatting differences remain separate contracts."""
import hashlib
import json


def compact_json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def pretty_json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def raw_sha256(value):
    return hashlib.sha256(value).hexdigest()
