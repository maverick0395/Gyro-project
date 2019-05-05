#!/usr/bin/python
import web
import urllib2
from urllib2  import URLError
from subprocess import check_output

urls = (
'/', 'index'
)

class index:
    def GET(self):
        file = open('/home/pi/results/result.txt','r')
        return file
        file.close()
if __name__ == "__main__":
    try:
        app = web.application(urls, globals())
        app.run()
    except (OSError,IOError) as e:
        check_output('sudo lsof -t -i tcp:8080 | xargs kill -9', shell = True)
        app = web.application(urls, globals())
        app.run()
