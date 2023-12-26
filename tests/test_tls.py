import requests
import httpimport
from tests import HttpImportTest, URLS, PROXY_HEADER, HTTPS_CERT
from tests import servers


class TestHttp(HttpImportTest):

    def setUp(self):
        # Initialize Content Server and Proxy
        servers.init('httpd_tls')
        self.URL = (URLS['web_dir'] % servers.port_for('httpd_tls')).replace("http://", "https://")

        # servers.init('httpd_proxy_tls')

    def test_unverified_https_profile(self):
        httpimport.set_profile("""
[no_verify]
ca-verify: false
            """)
        with httpimport.remote_repo(self.URL, profile='no_verify'):
            import test_package
        self.assertTrue(test_package)

    def test_unverified_https_profile_failure(self):
        httpimport.set_profile("""
[verify]
ca-verify: false
            """)
        try:
            with httpimport.remote_repo(self.URL, profile='verify'):
                import test_package
        except requests.exceptions.SSLError:
            self.assertTrue(True)

    def test_unverified_https_failure(self):
        try:
            with httpimport.remote_repo(self.URL):
                import test_package
        except requests.exceptions.SSLError:
            self.assertTrue(True)

    def test_verify_ca(self):
        httpimport.set_profile("""
[verify_cert]
ca-file: {path}
            """.format(path=HTTPS_CERT))
        with httpimport.remote_repo(self.URL, profile='verify_cert'):
            import test_package
        self.assertTrue(test_package)

    def test_invalid_ca(self):
        httpimport.set_profile("""
[invalid_ca_file]
ca-file: /non-existent/
        """)
        try:
            with httpimport.remote_repo(self.URL, profile='invalid_ca_file'):
                import test_package
        except OSError:
            self.assertTrue(True)
