import hashlib
import os,binascii
import db_handler

def for_encrypt_pass(passwd):
    encrypted = hashlib.md5(passwd).hexdigest()
    return encrypted

def get_aggre_key(group):
    rstring = binascii.b2a_hex(os.urandom(15))
    users = db_handler.share_to_group(group)
    enc_group = for_encrypt_pass(str(group))
    a=[]
    a.append(rstring)
    for u in users.keys():
        a.append(u+rstring+enc_group)
    return a

def get_d_aggre_key(user,rstring,group):
    enc_group = for_encrypt_pass(group)
    u = ''.join(user)
    out = []
    out.append(u)
    out.append(rstring)
    out.append(enc_group)
    a = ''.join(out)
    a = a.replace(' ','')
    return a



