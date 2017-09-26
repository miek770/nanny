import SimpleHTTPServer
import SocketServer

class myHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        print self.path
        self.send_response(200, "Hello world!")

PORT = 8000
handler = SocketServer.TCPServer(("", PORT), myHandler)
print "serving at port,", PORT
handler.serve_forever()

