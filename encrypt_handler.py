import hashlib
import os,binascii
import db_handler


def for_encrypt_pass(passwd):
    encrypted = hashlib.md5(passwd).hexdigest()
    return encrypted

def get_aggre_key(group):
    rstring = binascii.b2a_hex(os.urandom(15))
    users = db_handler.get_users()
    for u,p in users.iteritems():
        return dict(u.join(rstring).join(group).join(p)), rstring



