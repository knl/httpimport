import requests

import os
from http.server import HTTPServer as BaseHTTPServer
from http.server import SimpleHTTPRequestHandler
import ssl
from threading import Thread
from time import sleep
from tests import (
    SERVER_HOST,
    BASIC_AUTH_CREDS,
    HTTPS_CERT,
    PROXY_TLS_CERT,
    PROXY_HEADER,
    WEB_DIRECTORY)

# Taken from:
# https://stackoverflow.com/questions/39801718/how-to-run-a-http-server-which-serve-a-specific-path


class HTTPHandler(SimpleHTTPRequestHandler):
    """This handler uses server.base_path instead of always using os.getcwd()"""

    def translate_path(self, path):
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath


class HTTPHandlerToLogin(HTTPHandler):
    """This handler always redirects to the login/signin page."""

    def do_GET(self):
        if self.path.endswith('signin.html'):
            return HTTPHandler.do_GET(self)

        self.send_response(302)
        self.send_header('Location', '/signin.html')
        self.end_headers()


# Taken from:
# https://github.com/operatorequals/httpimport/pull/42


class ProxyHandler(SimpleHTTPRequestHandler):
    def do_GET(self, head=False):
        try:
            resp = requests.get(self.path)
            code = resp.status_code
        except requests.HTTPError as he:
            code = he.status_code
        self.send_response(code)
        self.send_header(PROXY_HEADER[0], PROXY_HEADER[1])
        self.end_headers()
        if code == 200 and not head:
            self.copyfile(resp, self.wfile)

    def do_HEAD(self):
        self.do_GET(head=True)

# Taken from:
# https://gist.github.com/mauler/593caee043f5fe4623732b4db5145a82


class HTTPBasicAuthHandler(HTTPHandler):
    _auth = BASIC_AUTH_CREDS

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="HttpImport Test"')
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self, onauth=HTTPHandler.do_GET):
        """ Present frontpage with user authentication. """
        if self.headers.get("Authorization") is None:
            self.do_AUTHHEAD()
            self.wfile.write(b"no auth header received")
        elif self.headers.get("Authorization") == "Basic " + self._auth:
            onauth(self)
        else:
            self.do_AUTHHEAD()
            self.wfile.write(b"not authenticated")


class HTTPBasicAuthProxyHandler(HTTPBasicAuthHandler):
    _auth = BASIC_AUTH_CREDS

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="HttpImport Test"')
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        """ Do HTTP Proxy on Auth Success. """
        HTTPBasicAuthHandler.do_GET(self, onauth=ProxyHandler.do_GET)


class HTTPServer(BaseHTTPServer):
    def __init__(self, base_path, server_address,
                 RequestHandlerClass=HTTPHandler):
        self.base_path = base_path
        BaseHTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.port = self.socket.getsockname()[1]

########### Globals ###########


__SERVERS = {
    'httpd': HTTPServer(
        WEB_DIRECTORY,
        (SERVER_HOST, 0),
        RequestHandlerClass=HTTPHandler),
    'httpd_to_login': HTTPServer(
        WEB_DIRECTORY,
        (SERVER_HOST, 0),
        RequestHandlerClass=HTTPHandlerToLogin),
    'httpd_proxy': HTTPServer(
        WEB_DIRECTORY,
        (SERVER_HOST, 0),
        RequestHandlerClass=ProxyHandler),
    'httpd_basic_auth': HTTPServer(
        WEB_DIRECTORY,
        (SERVER_HOST, 0),
        RequestHandlerClass=HTTPBasicAuthHandler),
    'httpd_basic_auth_proxy': HTTPServer(
        WEB_DIRECTORY,
        (SERVER_HOST, 0),
        RequestHandlerClass=HTTPBasicAuthProxyHandler),
    'httpd_tls': HTTPServer(
        WEB_DIRECTORY,
        (SERVER_HOST, 0),
        RequestHandlerClass=HTTPHandler),
    'httpd_proxy_tls': HTTPServer(
        WEB_DIRECTORY,
        (SERVER_HOST, 0),
        RequestHandlerClass=ProxyHandler),
}

__SERVERS['httpd_tls'].socket = ssl.wrap_socket (__SERVERS['httpd_tls'].socket, certfile=HTTPS_CERT, server_side=True)
__SERVERS['httpd_proxy_tls'].socket = ssl.wrap_socket (__SERVERS['httpd_proxy_tls'].socket, certfile=PROXY_TLS_CERT, server_side=True)
__SERVER_THREADS = {}

RUNNING = {
    'httpd': False,
    'httpd_proxy': False,
    'httpd_basic_auth': False,
    'httpd_basic_auth_proxy': False,
    'httpd_tls': False,
    'httpd_proxy_tls': False,
}


def init(server_name=None):
    global RUNNING, __SERVER_THREADS, __SERVERS

    if RUNNING.get(server_name, False):
        return

    if server_name is not None:
        servers = {server_name: __SERVERS[server_name]}
    else:
        servers = __SERVERS

    for server_name, server in servers.items():
        print("'%s' at port %d" % (server_name, server.port))
        __SERVER_THREADS[server_name] = Thread(target=server.serve_forever, )
        __SERVER_THREADS[server_name].daemon = True
        __SERVER_THREADS[server_name].start()
        RUNNING[server_name] = True

    # Wait for everything to hopefully setup
    sleep(1)


def port_for(server_name):
    global RUNNING, __SERVERS

    if server_name is None:
        raise ValueError("Server name must be provided")
    if server_name not in RUNNING:
        return ValueError("Server {} is not running yet".format(server_name))
    if server_name not in __SERVERS:
        return ValueError("Unknown server {}".format(server_name))

    return __SERVERS[server_name].port
