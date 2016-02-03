import glob
import os.path
import cgi
import tempfile
import db_handler
from md5 import md5

import cherrypy
from cherrypy.lib.static import serve_file
from cherrypy.lib import auth_digest

header = """<html><title>Secure Cloud Group Share</title>
        <link rel="stylesheet" href="/static/themes/downloaded_style.css" type="text/css" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />      
        </head>
        <body align="center">   
        <div class="wrapper">"""

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
    
    @cherrypy.expose
    def download_view(self, directory="static/download"):
        html = header
        html += """<h2>Here are the files in the selected directory:</h2>
        <h3><a href="/upload_view"> Upload Files </a></h3>
        <table><tr><th>Files Available</th></tr>
        <a href="download_view?directory=%s"> Parent Directory [..] </a></br></br>       
        """ % os.path.dirname(os.path.abspath(directory))

        for filename in glob.glob(directory + '/*'):
            absPath = os.path.abspath(filename)
            if os.path.isdir(absPath):
                html += '<tr><td><a href="/download_view?directory=' + absPath + '">' + os.path.basename(filename) + "/[Dir]</a> </tr></td>"
            else:
                html += '<tr><td><a href="/download/download_view/?filepath=' + absPath + '">' + os.path.basename(filename) + "</a> </tr></td>"

        html += """ </table><br></div></body></html>"""
        return html    
    
    
    @cherrypy.expose    
    def upload_view(self):
        html = header
        html += """      
            <h2>Upload a file</h2>
            <form action="upload_file" method="post" enctype="multipart/form-data">
            filename: <input type="file" name="theFile" /><br />
            <input type="submit" />
            </form>
            <h2>Download a file</h2>
            <a href='download_view'>Go to Downloads</a>
            </div>
        </body></html>
        """    
        return html 


    @cherrypy.expose
    def index(self):
        html = header
        html += """   
            <h2> Welcome to Secure Cloud</h2>
            <table>
            <form method="post" action="validate">
            <tr><td>Login : </td><td><input type="text" name="uname"/></td></tr>
            <tr><td>Password : </td><td><input type="password" name="upasswd"/></td></tr>
            <tr><td></td><td><input type="submit" value="login"></td><td></td><tr>
            </table>
            <h3><a href=register>Register!</a></h3>
            <h3><a href=remove>Remove!</a></h3>
            </div>
        </body></html>"""
        return html
        
    @cherrypy.expose
    def register(self):
        page = header
        page += """   
        <h2> Register</h2><br>
        <form method="post" action="getdata">
        <input type="text" name="uname"/>
        <input type="password" name="upasswd"/>
        <input type="hidden" value="add" name="action"/>
        <input type="submit" value="Register">
        </form></div></body></html>"""
        return page
    
    @cherrypy.expose
    def remove(self):
        page = header
        page += """   
        <h2> Remove</h2><br>
        <form method="post" action="getdata">
        <input type="text" name="uname"/>
        <input type="hidden" value="remove" name="action"/>        
        <input type="hidden" value="" name="upasswd"/>
        <input type="submit" value="Remove">
        </form></div></body></html>"""
        return page
        
    @cherrypy.expose
    def getdata(self,uname,upasswd,action):
        if action == "add":
           adduser = db_handler.add_user(uname,upasswd)
           html = header
           html += """ <h1>Status : %s </h1> """ % (adduser)
           html += "</div></body></html>"
        elif action == "remove":
           adduser = db_handler.remove_user(uname)
           html = header
           html += """ <h1>Status : %s </h1> """ % (adduser)
           html += "</div></body></html>"
        return html
        
    @cherrypy.expose
    def validate(self,uname,upasswd):
        users = db_handler.get_users()  
        print users
        place = header
        for u, p in users.iteritems():        
         if uname == u and upasswd == p:
            place += """<h2>Login Succeeded</h2><br><a href=/download_view>Click to Continue!</a></div></body><html>"""
         else:
            place += """<h2>Login Failed</h2><br><a href=/>Click To Retry</a></div></body><html>"""
        return place 
        

    @cherrypy.expose
    @cherrypy.tools.noBodyProcess()
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
        os.link(theFile.file.name, 'static/download/'+theFile.filename)
        
        return "ok, got it filename='%s'" % theFile.filename        
   
class Download:

    @cherrypy.expose
    def download_view(self, filepath):        
        return serve_file(filepath, "application/x-download", "attachment")     
  


tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    root = Root()
    root.download = Download()
    cherrypy.quickstart(root, config=tutconf)
 