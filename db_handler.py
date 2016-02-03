import MySQLdb as mysqldb

def connect_logic():     
    return mysqldb.connect("localhost","root","laka","securecloud") 
    
def add_user(username,password):
    db = connect_logic()
    cur = db.cursor()
    cur.execute('create table if not exists users(username varchar(255),password varchar(255))')
    if cur.execute('insert into users (username,password) values (%s,%s)',(username,password)):
        db.commit()
        status = "Success"
        return status
    else:
        db.rollback()
        status = "failed"
        return status
    db.close()
    return status
   
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
        status = "Success"
        return status
    else:
        db.rollback()
        status = "failed"
        return status
    db.close()
    return status
    
    