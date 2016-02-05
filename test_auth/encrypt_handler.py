import hashlib

def for_encrypt_pass(passwd):
    encrypted = hashlib.md5(passwd).hexdigest()
    return encrypted