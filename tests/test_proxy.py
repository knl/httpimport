import httpimport
from tests import (BASIC_AUTH_CREDS, URLS, SERVER_HOST, servers, HttpImportTest)



class TestBase(HttpImportTest):

    def setUp(self):
        # Initialize Content Server and Proxy
        servers.init('httpd')
        servers.init('httpd_proxy')
        servers.init('httpd_basic_auth_proxy')
        self.URL = URLS['web_dir'] % servers.port_for('httpd')
        # Allow plaintext (HTTP) for all test communications
        httpimport.set_profile('''[{url}]
allow-plaintext: yes
        '''.format(url=self.URL))

    def test_proxy_simple_HTTP(self):
        httpimport.set_profile("""[{url}]
proxy-url: http://{host}:{port}
        """.format(host=SERVER_HOST, url=self.URL, port=servers.port_for('httpd_proxy')))

        with httpimport.remote_repo(self.URL):
            import test_package

        self.assertTrue(test_package)

    def test_basic_auth_proxy_HTTP(self):
        httpimport.set_profile("""[{url}]
headers:
    Authorization: Basic {b64_creds}

proxy-url: http://{host}:{port}
        """.format(host=SERVER_HOST, url=self.URL, b64_creds=BASIC_AUTH_CREDS, port=servers.port_for('httpd_basic_auth_proxy')))
        with httpimport.remote_repo(self.URL):
            import test_package
        self.assertTrue(test_package)
