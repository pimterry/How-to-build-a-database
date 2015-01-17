import unittest, time, requests, json, logging
from multiprocessing import Process
from main import build_app, run_server

DB_ROOT = "http://localhost:8080"

logging.getLogger("requests.packages.urllib3").setLevel(logging.WARN)

def instance_starter(db_file):
    def start_instance():
        run_server(build_app(db_file))
    return start_instance

class DbTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        DbTestCase.startServer()

    @classmethod
    def tearDownClass(cls):
        DbTestCase.stopServer()

    @classmethod
    def startServer(cls, db_file=None):
        DbTestCase.server = Process(target=instance_starter(db_file))
        DbTestCase.server.start()
        time.sleep(0.1)

    @classmethod
    def stopServer(cls):
        DbTestCase.server.terminate()

    def setUp(self):
        if not DbTestCase.server.is_alive():
            DbTestCase.startServer()

        requests.post(DB_ROOT + "/reset")

    def assertReturns(self, request, data):
        self.assertIn(request.status_code, range(200, 300))

        try:
            content = json.loads(request.text)
        except Exception as e:
            self.fail("Failed to parse response JSON:\n%s\n%s" % (request.text, e))

        self.assertEqual(content, data)