#!/usr/bin/env python
from flup.server.fcgi import WSGIServer
from refdesk import app 

if __name__ == '__main__':
    WSGIServer(app, bindAddress='/var/flup/refdesk-fcgi.sock').run()
