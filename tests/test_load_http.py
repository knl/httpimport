import httpimport
from tests import (
    HttpImportTest,
    PYTHON,
    URLS,
    ZIP_PASSWORD,
    servers)



class TestLoadHttp(HttpImportTest):

    def setUp(self):
        # Initialize Content Server and Proxy
        servers.init('httpd')
        self.URL = URLS['web_dir'] % servers.port_for('httpd')
        # Allow plaintext (HTTP) for all test communications
        httpimport.set_profile('''[{url}]
allow-plaintext: yes
        '''.format(url=self.URL))

    def test_load_http(self):
        pack = httpimport.load('test_package', self.URL)
        self.assertTrue(pack)

    def test_load_relative_fail(self):
        try:
            pack = httpimport.load('test_package.b', self.URL)
        except ImportError:
            ''' Fails as 'load()' does not import modules in 'sys.modules'
            but relative imports rely on them
            '''
            self.assertTrue(True)

    def test_dependent_load(self):
        pack = httpimport.load('dependent_package', self.URL)
        self.assertTrue(pack)
