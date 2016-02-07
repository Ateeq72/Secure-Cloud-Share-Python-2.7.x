import glob
import os.path
import cgi
import tempfile
import db_handler
import encrypt_handler


import cherrypy
from cherrypy.lib.static import serve_file
from auth import AuthController, require, member_of, name_is


header = """<html><title>Secure Cloud Group Share</title>
        <link rel="stylesheet" href="/static/themes/ateeq.min.css" />
        <link rel="stylesheet" href="/static/themes/ateeq.css" />
	    <link rel="stylesheet" href="/static/themes/jquery.mobile.icons.min.css" />
        <link rel="stylesheet" href="/static/themes/jquery.mobile.structure-1.4.5.min.css" />
        <script src="/static/themes/jquery-1.11.1.min.js"></script>
        <script src="/static/themes/jquery.mobile-1.4.5.min.js"></script>
       
        </head>
        <div data-role="page" data-theme="a">
        <div data-role="header" data-position="inline">
             <h2> Welcome to Secure Cloud</h2></div>
        <body align="center"> 
        <div data-role="content" data-theme="a">
        <div class="wrapper">""" 
        
footer = """</div></div></body></html> """
        
def check_login():
        if cherrypy.session['cur_user'] != "":
            header = """<html><title>Secure Cloud Group Share</title>
            <link rel="stylesheet" href="/static/themes/ateeq.min.css" />
            <link rel="stylesheet" href="/static/themes/ateeq.css" />
	        <link rel="stylesheet" href="/static/themes/jquery.mobile.icons.min.css" />
            <script src="/static/themes/jquery-1.11.1.min.js"></script>
            <script src="/static/themes/jquery.mobile-1.4.5.min.js"></script>
            <meta name="viewport" content="width=device-width, initial-scale=1" />      
            </head>
            <div data-role="page" data-theme="a">
            <div data-role="header" data-position="inline">
             <h2> <a href='/'>Welcome to Secure Cloud</a></h2>
             </div>
            <h4>Welcome %s <a href=/auth/logout>Logout</a>  <a href=/remove>Delete Account</a></h4>
            <body align="center"> 
            <div data-role="content" data-theme="a">
            <div class="wrapper">""" % str(cherrypy.session['cur_user'])
        else:
            header = """<html><title>Secure Cloud Group Share</title>
            <link rel="stylesheet" href="/static/themes/ateeq.min.css" />
            <link rel="stylesheet" href="/static/themes/ateeq.css" />
	        <link rel="stylesheet" href="/static/themes/jquery.mobile.icons.min.css" />
            <script src="http://code.jquery.com/jquery-1.11.1.min.js"></script>
            <script src="http://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.js"></script>
            <meta name="viewport" content="width=device-width, initial-scale=1" />   
            <div data-role="page" data-theme="a">
            <div data-role="header" data-position="inline">
             <h2> Welcome to Secure Cloud</h2></div>
            </head><h4>Welcome Guest <a href='/'>Login</a></h4></div>
            <body align="center">  
            <div data-role="content" data-theme="a">
            <div class="wrapper">""" 
        return header


class myFieldStorage(cgi.FieldStorage):
    """Our version uses a named temporary file instead of the default
    non-named file; keeping it visibile (named), allows us to create a
    2nd link after the upload is done, thus avoiding the overhead of
    making a copy to the destination filename."""
    
    def make_file(self, binary=None):
        return tempfile.NamedTemporaryFile()
    
def noBodyProcess():
    """Sets cherrypy.request.process_request_body = False, giving
    us direct control of the file upload destination. By default
    cherrypy loads it to memory, we are directing it to disk."""
    cherrypy.request.process_request_body = False

cherrypy.tools.noBodyProcess = cherrypy.Tool('before_request_body', noBodyProcess)
    
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
            <form action="/upload_file" method="post" enctype="multipart/form-data">
            filename: <input type="file" name="theFile" /><br />
            <input type="submit" value="Upload" />
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
        <input type="hidden" value="add" name="action"/>
        <input type="submit" value="Register">
        </form></div></body></html>"""
        return page
    
    @cherrypy.expose
    @require()
    def remove(self):
        page = header
        page += """   
        <h2> Remove</h2><br>
        <form method="post" action="getdata">
        Name : <input type="text" name="uname"/><br>
        <input type="hidden" value="remove" name="action"/><br>
        Password : <input type="hidden" value="" name="upasswd"/><br>
        Email : <input type="email" name="email" required="required"/><br>
        Phone No. : <input type="number" name="phno" required="required"/><br>
        Age : <input type="number" name="age" required="required"/><br>
        <input type="submit" value="Remove">
        </form></div></body></html>"""
        return page
        
    @cherrypy.expose    
    def getdata(self,uname,upasswd,action,email,phno,age):
        if action == "add":
           e_pass = encrypt_handler.for_encrypt_pass(upasswd)
           adduser = db_handler.add_user(uname,e_pass)
           register = db_handler.register(email,phno,age)
           html = header
           html += """ <h1>Status : %s <br> %s </h1> """ % (adduser,register)
        elif action == "remove":
           adduser = db_handler.remove_user(uname)
           unregister = db_handler.unregister(email,phno,age)
           html = header
           html += """ <h1>Status : %s <br> %s  </h1> """ % (adduser,unregister)
        html += "<h3><a href=/>Click to continue</a></h3></div></body></html>"
        return html 
   
        

    @cherrypy.expose
    @cherrypy.tools.noBodyProcess()
    @require()
    def upload_file(self, theFile=None):                 
        """upload action
        
        We use our variation of cgi.FieldStorage to parse the MIME
        encoded HTML form data containing the file."""
        
        # the file transfer can take a long time; by default cherrypy
        # limits responses to 300s; we increase it to 1h
        cherrypy.response.timeout = 3600
        
        # convert the header keys to lower case
        lcHDRS = {}
        for key, val in cherrypy.request.headers.iteritems():
            lcHDRS[key.lower()] = val
        
        # at this point we could limit the upload on content-length...
        # incomingBytes = int(lcHDRS['content-length'])
        
        # create our version of cgi.FieldStorage to parse the MIME encoded
        # form data where the file is contained
        formFields = myFieldStorage(fp=cherrypy.request.rfile,
                                    headers=lcHDRS,
                                    environ={'REQUEST_METHOD':'POST'},
                                    keep_blank_values=True)
        
        # we now create a 2nd link to the file, using the submitted
        # filename; if we renamed, there would be a failure because
        # the NamedTemporaryFile, used by our version of cgi.FieldStorage,
        # explicitly deletes the original filename
        theFile = formFields['theFile']
        user = cherrypy.session['cur_user']
        file = theFile.filename

        try:
          out = db_handler.file_upload(user,file)
          os.link(theFile.file.name, 'static/download/'+theFile.filename)
        except OSError,e:
          return 'error occured : %s, %s' % (e, out)
        
        return "ok, got it filename='%s' ,  %s" % (theFile.filename, out)
     
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
          <tr><td><a href=/>Share</a></td><tr><br>""" % (file,response,filepath)
        else:
            html += """ <h2> You are Authorized to do anything with the file! Sorry :( REsponse = %s """ % response
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
 