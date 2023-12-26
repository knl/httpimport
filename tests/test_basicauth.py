import httpimport
from tests import (BASIC_AUTH_CREDS, URLS, servers, HttpImportTest)



class TestBasicAuth(HttpImportTest):

    def setUp(self):
        # Initialize Basic Auth Server
        servers.init('httpd_basic_auth')
        self.URL = URLS['web_dir'] % servers.port_for('httpd_basic_auth')
        # Allow plaintext (HTTP) for all test communications
        httpimport.set_profile('''[{url}]
allow-plaintext: yes
        '''.format(url=self.URL))

    def test_basic_auth_HTTP(self):
        httpimport.set_profile("""[{url}]
headers:
    Authorization: Basic {b64_creds}
        """.format(url=self.URL, b64_creds=BASIC_AUTH_CREDS))
        with httpimport.remote_repo(self.URL):
            import test_package
        self.assertTrue(test_package)

    def test_basic_auth_HTTP_fail(self):
        httpimport.set_profile("""[{url}]
# Wrong Password
headers:
    Authorization: Basic dXNlcm5hbWU6d3JvbmdfcGFzc3dvcmQ=
        """.format(url=self.URL))
        with httpimport.remote_repo(self.URL):
            try:
                import test_package
            except (ImportError, KeyError) as e:
                self.assertTrue(e)
