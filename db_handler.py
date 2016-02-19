import MySQLdb as mysqldb
import encrypt_handler

def connect_logic():     
    return mysqldb.connect("localhost","root","laka","securecloud") 
    
def add_user(username,password):
    db = connect_logic()
    cur = db.cursor()
    cur.execute('create table if not exists users(username varchar(255),password varchar(255))')
    if cur.execute('select * from users where username = "%s"' % (username)) == 0L:
      if cur.execute('insert into users (username,password) values ("%s","%s")' % (username,password)):
          db.commit()
          status = "Success"
          return status
      else:
          db.rollback()
          status = "failed"
          return status
    return "User Exist"


def register(email,phone,age):
    db = connect_logic()
    cur = db.cursor()
    cur.execute('create table if not exists registered_user(email varchar(255),phone varchar(255), age varchar(255))')
    if cur.execute('insert into registered_user(email,phone,age) values("%s","%s","%s")' % (email,phone,age)):
        db.commit()
        return "Done"
    else:
        return "Failed"

def unregister(email,phone,age):
    db = connect_logic()
    cur = db.cursor()
    cur.execute('create table if not exists registered_user(email varchar(255),phone varchar(255), age varchar(255))')
    if cur.execute('delete from registered_user where email= "%s" and phone = "%s" and age= "%s"' % (email,phone,age)):
        db.commit()
        db.close()
        return "Done"
    else:
        return "Failed"
   
def get_users():
    db = connect_logic()
    cur = db.cursor()
    cur.execute('select username, password from users')
    return dict(cur.fetchall())

def remove_user(user):
    db = connect_logic()
    cur = db.cursor()
    if cur.execute("delete from users where username='%s'" % (user)):
        db.commit()
        db.close()
        status = "Success"
        return status
    else:
        db.rollback()
        status = "failed"
        return status


def get_cur_user():
    db = connect_logic()
    cur = db.cursor()
    cur.execute('create table if not exists cur_user(uname varchar(255))')
    if cur.execute('select uname from cur_user') != 0L:
         cur_user = dict(cur.fetchall())
    else:
         cur_user = {'Not Logged in'}         
    return cur_user

def file_upload(user,file):
    db = connect_logic()
    cur = db.cursor()
    cur.execute('create table if not exists file_upload(user varchar(255),file varchar(255))')
    if cur.execute('select * from file_upload where file = "%s"' % (file)) != 0L:
        return 'File Exists'
    else:
        cur.execute('insert into file_upload (user,file) values("%s","%s")' % (user,file))
        db.commit()
        db.close()
        return 'Upload Successfull'

def file_remove(user,file):
    db = connect_logic()
    cur = db.cursor()
    cur.execute('create table if not exists file_upload(user varchar(255),file varchar(255))')
    if cur.execute('select * from file_upload where file = "%s"' % (file)) != 0L:
        cur.execute('delete from file_upload where user="%s" and file="%s"' % (user,file))
        db.commit()
        db.close()
        return True
    else:
        return False

def find_group(user):
    db = connect_logic()
    cur = db.cursor()
    cur.execute('create table if not exists group_(user_ varchar(255),group_ varchar(255))')
    if cur.execute('select * from group_ where user_="%s"' % (user)) != 0L:
        return dict(cur.fetchall())
    else:
        return None

def insert_to_group(user,group):
    db = connect_logic()
    cur = db.cursor()
    cur.execute('create table if not exists group_(user_ varchar(255), group_ varchar(255))')
    if cur.execute('select * from group_ where user_="%s" and group_="%s"' % (user,group)) == 0L:
        cur.execute('insert into group_ (user_,group_) values ("%s","%s")' % (user,group))
        db.commit()
        db.close()
        return "Added to Group : %s" % group
    else:
        return "Failed! :("

def delete_from_group(user,group):
    db = connect_logic()
    cur = db.cursor()
    cur.execute('create table if not exists group_(user_ varchar(255), group_ varchar(255))')
    if cur.execute('select * from group_ where user_="%s" and group_="%s"' % (user,group)) != 0L:
        cur.execute('delete from group_ where user_="%s" and group_="%s"' % (user,group))
        db.commit()
        db.close()
        return "Removed from Group : %s" % group
    else:
        return "Failed! :("

def file_download(user,file):
    db = connect_logic()
    cur = db.cursor()
    cur.execute('create table if not exists file_upload(user varchar(255),file varchar(255))')
    out = cur.execute('select * from file_upload where file = "%s" and user = "%s" ' % (file,user))
    if out == 0L:
        return False
    else:
        return True

def file_share(user,file,aggre_key,group):
    db = connect_logic()
    cur = db.cursor()
    cur.execute('create table if not exists file_share(user varchar(255),file varchar(255),aggre_key var(255),group varchar(255)')
    if cur.execute('select * from file_share where user = "%s" and file = "%s" and aggre_key = "%s" and group = "%s"' % (user,file,aggre_key,group)) != 0L :
        return "Share Exists!"
    else:
        cur.execute('insert into file_share (user,file,aggre_key,group) values ("%s","%s","%s","%s")' % (user,file,aggre_key,group))
        db.commit()
        db.close()
        return "Share Added"

def file_share_download(user,file,aggre_key,group):
    db = connect_logic()
    cur = db.cursor()
    cur.execute('create table if not exists file_share(user varchar(255),file varchar(255),aggre_key var(255),group varchar(255)')
    if cur.execute('select * from file_share where user = "%s" and file = "%s" and aggre_key = "%s" and group = "%s"' % (user,file,aggre_key,group)) != 0L :
        return True
    else:
        return False

def add_key_share(user,key,group):
    db = connect_logic()
    cur = db.cursor()
    cur.execute('create table if not exists keys_for_share(key varchar(255)')
    if cur.execute('insert into keys_for_share values("%s")' % (key)):
        db.commit()
        db.close()
        return "Done"
    else:
        return "Failed"

def remove_key_share(key):
    db = connect_logic()
    cur = db.cursor()
    cur.execute('create table if not exists keys_for_share(key varchar(255)')
    if cur.execute('delete from keys_for_share where key="%s"' % (key)):
        db.commit()
        return "Done"
    else:
        return "Failed"
