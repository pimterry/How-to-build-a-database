import unittest, time, requests, json, logging
from multiprocessing import Process
from main import build_app, run_server

logging.getLogger("requests.packages.urllib3").setLevel(logging.WARN)

def instance_starter(port):
    def start_instance():
        run_server(build_app(), port)
    return start_instance

class DbTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        DbTestCase.start_server()

    def setUp(self):
        if not DbTestCase.server or not DbTestCase.server.is_alive():
            DbTestCase.start_server()

        reset = requests.post("http://localhost:8080/reset")
        reset.raise_for_status()

    @classmethod
    def start_server(cls):
        DbTestCase.server = DbTestCase.start_and_return_server()

    @classmethod
    def start_and_return_server(cls, port=8080):
        process = Process(target=instance_starter(port))
        process.start()
        time.sleep(0.1)
        return process

    @classmethod
    def tearDownClass(cls):
        DbTestCase.stop_server()

    @classmethod
    def stop_server(cls):
        DbTestCase.server.terminate()

    def assertReturns(self, request, data):
        self.assertIn(request.status_code, range(200, 300))

        try:
            content = json.loads(request.text)
        except Exception as e:
            self.fail("Failed to parse response JSON:\n%s\n%s" % (request.text, e))

        self.assertEqual(content, data)