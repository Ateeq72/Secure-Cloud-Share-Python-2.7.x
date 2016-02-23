import glob
import os.path
import cgi
import tempfile
import db_handler
import encrypt_handler
import commands
import send_mail


import cherrypy
from cherrypy.lib.static import serve_file
from auth import AuthController, require, member_of, name_is

groups = 5

header = """<html><title>Secure Cloud Group Share</title>
        <head>
        <link rel="stylesheet" href="/static/themes/downloaded_style.css" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
        </head>
             <h2><a href=/> Welcome to Secure Cloud</h2></a></div>
        <body align="center">
        <div class="wrapper">"""

footer = """</div></body></html> """

def check_login():
        if cherrypy.session['cur_user'] != "":
            header = """<html><title>Secure Cloud Group Share</title>
        <head>
        <link rel="stylesheet" href="/static/themes/downloaded_style.css" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
        </head>
             <h2> <a href=/>Welcome to Secure Cloud</a></h2>
             <h4>Welcome %s, Your Group : %s<br><a href=/auth/logout>Logout</a>  <a href=/remove>Delete Account</a></h4>
            <body align="center">
             <div class="wrapper">
            """ % (str(cherrypy.session['cur_user']),str(cherrypy.session['group']))
        else:
            header = """<html><title>Secure Cloud Group Share</title>
        <head>
        <link rel="stylesheet" href="/static/themes/downloaded_style.css" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
        </head>
             <h2><a href=/> Welcome to Secure Cloud</a></h2>
             <h4>Welcome Guest <br><a href=/auth/login>Login</a> </h4>
            <body align="center">
             <div class="wrapper">"""
        return header


class NamedPart(cherrypy._cpreqbody.Part):

    def make_file(self):
        return tempfile.NamedTemporaryFile()

cherrypy._cpreqbody.Entity.part_class = NamedPart

class Root: 
    
    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True
    }
    
    auth = AuthController()  
    
    
    @cherrypy.expose  
    @require()
    def upload_view(self):
        html = check_login()
        html += """      
            <h2>Upload a file</h2>
            <form action='/upload_file' method='post' enctype='multipart/form-data'>
            File: <input type='file' name='videoFile'/> <br/>
            <input type='submit' value='Upload'/>
            </form>
            <h2>Download a file</h2>
            <a href='/'>Go to Downloads</a>            
        """
        html += footer
        return html          


    @cherrypy.expose  
    @require()
    def index(self, directory="static/download"):
        html = check_login()
        html += """<h2>Here are the files in the selected directory:</h2>
        <h3><a href="/upload_view"> Upload Files </a></h3>
        <table><tr><th>Files Available</th></tr>
        <a href="/?directory=%s"> Parent Directory [..] </a></br></br>
        """ % os.path.dirname(os.path.abspath(directory))

        for filename in glob.glob(directory + '/*'):
            absPath = os.path.abspath(filename)
            if os.path.isdir(absPath):
                html += '<tr><td><a href="/?directory=' + absPath + '">' + os.path.basename(filename) + "/[Dir]</a> </tr></td>"
            else:
                html += '<tr><td><a href="/index_download?filepath=' + absPath + '">' + os.path.basename(filename) + "</a> </tr></td>"

        html += """ </table><br></div></body></html>"""
        return html
        
    @cherrypy.expose
    def register(self):
        page = header
        page += """   
        <h2> Register</h2><br>
        <form method="post" action="getdata">
        Name : <input type="text" name="uname" required="required"/><br>
        Password : <input type="password" name="upasswd" required="required"/><br>
        Email : <input type="email" name="email" required="required"/><br>
        Phone No. : <input type="number" name="phno" required="required"/><br>
        Age : <input type="number" name="age" required="required"/><br>
        Group : <select name="group">   """
        for x in range(1,groups+1):
            page += """ <option value=" """ + str(x) + """" >""" + str(x) + """ </option>"""
        page +="""</select><br>
        <input type="hidden" value="add" name="action"/>
        <input type="submit" value="Register">
        </form></div></body></html>"""
        return page
    
    @cherrypy.expose
    @require()
    def remove(self):
        page = check_login()
        page += """   
        <h2> Remove</h2><br>
        <form method="post" action="getdata">
        Name : <input type="text" name="uname"/><br>
        Password : <input type="password" value="" name="upasswd"/><br>
        Email : <input type="email" name="email" required="required"/><br>
        Phone No. : <input type="number" name="phno" required="required"/><br>
        Age : <input type="number" name="age" required="required"/><br>
        <input type="hidden" value="remove" name="action"/>
        <input type="submit" value="Remove">
        </form></div></body></html>"""
        return page
        
    @cherrypy.expose    
    def getdata(self,uname,upasswd,action,email,phno,age,group):
        if action == "add":
           e_pass = encrypt_handler.for_encrypt_pass(upasswd)
           adduser = db_handler.add_user(uname,e_pass)
           register = db_handler.register(uname,email,phno,age,group)
           group_info = db_handler.insert_to_group(uname,group)
           html = header
           html += """ <h1>Status : %s <br> %s <br> %s</h1> """ % (adduser,register,group_info)
        elif action == "remove":
           adduser = db_handler.remove_user(uname)
           unregister = db_handler.unregister(uname,email,phno,age)
           remove_f_group = db_handler.delete_from_group(uname,group)
           html = header
           html += """ <h1>Status : %s <br> %s <br> %s  </h1> """ % (adduser,unregister,remove_f_group)
        html += "<h3><a href=/>Click to continue</a></h3></div></body></html>"
        return html

    @require()
    @cherrypy.config(**{'response.timeout': 3600}) # default is 300s
    @cherrypy.expose()
    def upload_file(self, videoFile):
       html = check_login()
       assert isinstance(videoFile, cherrypy._cpreqbody.Part)
       user = cherrypy.session['cur_user']
       file = videoFile.filename
       destination = os.path.join('/home/aristocrat/NetBeansProjects/SecureCloudGroupShare/static/download/', videoFile.filename)
       try:

       # Note that original link will be deleted by tempfile.NamedTemporaryFile
          os.link(videoFile.file.name, destination)
          out = db_handler.file_upload(user,file)
       except OSError,e:
           html += 'error occured : %s ' % (e)
           html += footer
           return html
       html += "ok, got it filename='%s' ,  %s" % (videoFile.filename, out)
       html += footer
       return html


    @cherrypy.expose
    @require()
    def index_download(self, filepath):
        user = cherrypy.session['cur_user']
        file = os.path.basename(filepath)
        html = check_login()
        response = db_handler.file_download(user,file)
        if response:
          html += """<h2> What do you wanna do with the file?</h2> <br>
          <h3> %s </h3><br> Response : %s
          <table><tr><td><a href=/download_file?filepath=%s>Download</a></td>
          <tr><td><a href=/delete_file?file=%s>Delete</a></td></tr>
          <tr><td><a href=/share?file=%s>Share</a></td><tr>
          <br>""" % (file,response,filepath,filepath,filepath)
        else:
            html += """ <h2> You are not the uploader!. <br> Hence, you are <b>not</b> authorized to do anything with the file! Sorry :( <br> Response = %s """ % response
        html += footer
        return html

    @cherrypy.expose
    @require()
    def delete_file(self,file):
        html = check_login()
        user = cherrypy.session['cur_user']
        file_name= os.path.basename(file)
        if commands.getoutput('rm -rf %s' % file) == '' and not os.path.isfile(file):
            if db_handler.file_remove(user,file_name):
                html += "<h2> File was deleted and ownership was removed! :)</h2>"
            else:
                html += "<h2> Something went wrong during DB handling! :(</h2>"
        else:
          html += "<h2> Something went wrong during Command execution! :(</h2>"
        html += "<h3><a href=/>Go Back!</a></h3>"
        html += footer
        return html

    @cherrypy.expose
    @require()
    def share(self,file):
        file_name = os.path.basename(file)
        user = cherrypy.session['cur_user']
        group = cherrypy.session['group']
        html = check_login()
        aggre_keys = encrypt_handler.get_aggre_key(group)
        html += """ <h2> File : %s </h2>""" % file_name
        html += """ Select the Group you wanna share the file with <br>
         <form method="post" action=/share_file >
         <input type="hidden" value=" """  + file +""" " name="file">
         Group : <select name="group">"""
        for x in range(1,groups+1):
            html += """ <option value=" """ + str(x) + """ " > """ + str(x) + """ </option>"""
        html +="""</select><br> <input type=submit value="Share"></form>"""
        html += footer
        return html

    @cherrypy.expose
    @require()
    def share_file(self, group, file):
        html = check_login()
        file_name = os.path.basename(file)
        user = cherrypy.session['cur_user']
        uemail = [db_handler.fetch_member_email(group)]
        keys = encrypt_handler.get_aggre_key(group)
        for i,j in zip(range(0,len(uemail[0].keys())),range(1,len(keys))):
           out = db_handler.file_share(uemail[0].keys()[i],file_name,keys[j],group)
        skey = keys[0]
        msg = " %s shared %s with you! key = %s " % (user,file_name,skey)
        if out != "Share Exists!":
         for u in uemail:
                send_mail.send_email(u.values(),msg)
                html += """ File Shared, \nResult : %s """ % out
        else:
                html += """ File Sharing Failed, \nResult : %s """ % out
        html += footer
        return html


    @cherrypy.expose
    @require()
    def download_file(self,filepath):
        return serve_file(filepath, "application/x-download", "attachment")  
    
tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    root = Root()
    cherrypy.quickstart(root, config=tutconf)
