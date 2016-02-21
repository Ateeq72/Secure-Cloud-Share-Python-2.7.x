import hashlib
import os,binascii
import db_handler

def for_encrypt_pass(passwd):
    encrypted = hashlib.md5(passwd).hexdigest()
    return encrypted

def get_aggre_key(group,a = {}):
    rstring = binascii.b2a_hex(os.urandom(15))
    users = db_handler.share_to_group(group)
    enc_group = for_encrypt_pass(str(group))
    a.setdefault(rstring,[])
    for u,g in users.iteritems():
        a[rstring].append(u+rstring+enc_group)
        return a

def get_d_aggre_key(user,rstring,group):
    enc_group = for_encrypt_pass(group)
    return user+rstring+enc_group



