#!python
import glob
import os.path

import cherrypy
from cherrypy.lib.static import serve_file


class Root:
    def index(self, directory="."):
        html = """<html><body><h2>Here are the files in the selected directory:</h2>
        <a href="index?directory=%s">Up</a><br />
        """ % os.path.dirname(os.path.abspath(directory))

        for filename in glob.glob(directory + '/*'):
            absPath = os.path.abspath(filename)
            if os.path.isdir(absPath):
                html += '<a href="/index?directory=' + absPath + '">' + os.path.basename(filename) + "</a> <br />"
            else:
                html += '<a href="/download/?filepath=' + absPath + '">' + os.path.basename(filename) + "</a> <br />"

        html += """</body></html>"""
        return html
    index.exposed = True

class Download:

    def index(self, filepath):        
        return serve_file(filepath, "application/x-download", "attachment")
    index.exposed = True

tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    root = Root()
    root.download = Download()
    cherrypy.quickstart(root, config=tutconf)
