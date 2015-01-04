import unittest, time, requests, json
from multiprocessing import Process
from main import build_app, run_server

DB_ROOT = "http://localhost:8080"

def start_instance():
    run_server(build_app())

class DbTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = Process(target=start_instance)
        cls.server.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()

    def setUp(self):
        requests.post(DB_ROOT + "/reset")

    def assertReturns(self, request, data):
        self.assertIn(request.status_code, range(200, 300))
        self.assertEqual(json.loads(request.text), data)