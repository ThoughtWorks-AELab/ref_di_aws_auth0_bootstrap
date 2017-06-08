import json
import socketserver
from http.server import SimpleHTTPRequestHandler

UI_PORT = 8000
BACKEND_PORT = 8001

 environment = {
     "host": os.environ['AUTH0_HOST'] + ".auth0.com",
     "connection": "preproduction-connection",
     "client_id": os.environ['AUTH0_CLIENT_ID']
 }

def env():
    return json.dumps(environment)


class BackendHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/env"):
            response = bytearray(env(), "utf-8")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
        elif self.path.startswith("/callback"):
            response = bytearray(self.path, "utf-8")
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
        else:
            super().do_GET()


with socketserver.TCPServer(("", UI_PORT), BackendHandler) as ui_server:
    print("serving ui at port", UI_PORT)
    ui_server.serve_forever()
