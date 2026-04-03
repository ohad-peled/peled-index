import hashlib


def make_author_id(name: str, institution: str) -> str:
    """Generate a unique author ID as an MD5 hash of 'name_institution'."""
    return hashlib.md5(f"{name}_{institution}".encode()).hexdigest()
