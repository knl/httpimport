import httpimport
from tests import (
    HttpImportTest,
    PYTHON,
    URLS,
    ZIP_PASSWORD,
    servers)


class TestArchiveFiles(HttpImportTest):

    def setUp(self):
        # Initialize Content Server and Proxy
        servers.init('httpd')
        servers.init('httpd_to_login')
        self.URL = URLS['web_dir'] % servers.port_for('httpd')
        # Allow plaintext (HTTP) for all test communications
        httpimport.set_profile('''[DEFAULT]
allow-plaintext: yes
        ''')

    def test_tarbz2_import(self, url=None):
        if url is None:
            url = URLS['tar_bz'] % servers.port_for('httpd')
        with httpimport.remote_repo(url):
            import test_package
        self.assertTrue(test_package)

    def test_autodetect_corrupt_file(self, url=None):
        if url is None:
            url = URLS['tar_corrupt'] % servers.port_for('httpd')
        try:
            with httpimport.remote_repo(url):
                import test_package
        except (ImportError, KeyError) as e:
            self.assertTrue(e)

    def test_tarxz_import(self, url=None):
        if url is None:
            url = URLS['tar_xz'] % servers.port_for('httpd')
        # Pass the test in IronPython, which does not support tar.xz lzma
        if PYTHON == "ironpython":
            self.assertTrue(True)
            return
        with httpimport.remote_repo(url):
            import test_package
        self.assertTrue(test_package)

    def test_targz_import(self, url=None):
        if url is None:
            url = URLS['tar_gz'] % servers.port_for('httpd')
        with httpimport.remote_repo(url):
            import test_package

        self.assertTrue(test_package)

    def test_targz_import_with_redirect_to_login(self, url=None):
        """This test should fail, as returned value is not an archive."""
        if url is None:
            url = URLS['tar_gz'] % servers.port_for('httpd_to_login')
        try:
            with httpimport.remote_repo(url):
                import test_package
        except (ImportError, SyntaxError) as e:
            self.assertTrue(e)

    def test_tar_import(self, url=None):
        if url is None:
            url = URLS['tar'] % servers.port_for('httpd')
        with httpimport.remote_repo(url):
            import test_package

        self.assertTrue(test_package)

    def test_zip_import(self, url=None):
        if url is None:
            url = URLS['zip'] % servers.port_for('httpd')
        with httpimport.remote_repo(url):
            import test_package

        self.assertTrue(test_package)

    # Correct Password for 'test_package.enc.zip' - 'P@ssw0rd!'
    def test_zip_import_w_pwd(self, url=None):
        if url is None:
            url = URLS['zip_encrypt'] % servers.port_for('httpd')
        httpimport.set_profile("""[{url}]
zip-password: {password}
        """.format(url=url, password=ZIP_PASSWORD))
        with httpimport.remote_repo(url):
            import test_package

        self.assertTrue(test_package)

    def test_zip_import_w_pwd_wrong(self, url=None):
        if url is None:
            url = URLS['zip_encrypt'] % servers.port_for('httpd')
        httpimport.set_profile("""[{url}]
# wrong password!
zip-password: XXXXXXXX
        """.format(url=url))
        try:
            with httpimport.remote_repo(url):
                import test_package

        except RuntimeError:
            self.assertTrue(True)
