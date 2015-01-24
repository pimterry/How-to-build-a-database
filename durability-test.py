from dbtestcase import DbTestCase
from timeout_decorator import timeout
import requests, json, time, tempfile, pickle

class DurabilityTest(DbTestCase):
    def setUp(self):
        DbTestCase.stop_server()
        self.db_file = tempfile.NamedTemporaryFile()

    def tearDown(self):
        DbTestCase.stop_server()
        self.db_file.close()

    def saveDbFile(self, data):
        pickle.dump(data, self.db_file)
        self.db_file.flush()

    def test_can_load_database_from_file(self):
        self.saveDbFile({ 0: "hello /dev/winter" })

        DbTestCase.start_server(db_filename=self.db_file.name)
        read = requests.get("http://localhost:8080/0")

        self.assertReturns(read, "hello /dev/winter")

    def test_database_persists_over_restart(self):
        DbTestCase.start_server(db_filename=self.db_file.name)

        requests.post("http://localhost:8080/123", "4")
        time.sleep(0.1)
        DbTestCase.stop_server()
        DbTestCase.start_server(db_filename=self.db_file.name)
        read = requests.get("http://localhost:8080/123")

        self.assertReturns(read, 4)

    def test_runs_quickly_with_persistence(self):
        DbTestCase.start_server(db_filename=self.db_file.name)

        start_time = time.time()
        data = json.dumps({i: i for i in range(0, 1000)})
        requests.post("http://localhost:8080", data)
        query_seconds = time.time() - start_time

        self.assertLess(query_seconds, 0.1)
