import hashlib
import os,binascii
import db_handler

def for_encrypt_pass(passwd):
    encrypted = hashlib.md5(passwd).hexdigest()
    return encrypted

def get_aggre_key(group):
    rstring = binascii.b2a_hex(os.urandom(15))
    users = db_handler.share_to_group(group)
    enc_group = for_encrypt_pass(group)
    a = {}
    a.setdefault(rstring,[])
    for u,g in users.iteritems():
        a[rstring].append(u+rstring+enc_group)
        return a





