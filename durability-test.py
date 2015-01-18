import requests, random, json, time, tempfile, pickle
from dbtestcase import DbTestCase, DB_ROOT

class Item:
    def __init__(self, id = None):
        self.id = id if id is not None else random.randint(0, 2**32)
        self.url = "%s/%s" % (DB_ROOT, self.id)

class DurabilityTests(DbTestCase):

    def setUp(self):
        DbTestCase.stop_server()
        self.db_file = tempfile.NamedTemporaryFile()

    def tearDown(self):
        DbTestCase.stop_server()
        self.db_file.close()

    def saveDbFile(self, data):
        pickle.dump(data, self.db_file)
        self.db_file.flush()

    def test_can_load_database_with_empty_file(self):
        self.saveDbFile({})

        DbTestCase.start_server(self.db_file.name)
        read = requests.get(Item(0).url)

        self.assertEqual(404, read.status_code)

    def test_can_load_database_from_saved_data(self):
        self.saveDbFile({0: "test-data"})

        DbTestCase.start_server(self.db_file.name)
        read = requests.get(Item(0).url)

        self.assertReturns(read, "test-data")

    def test_persists_changes_over_restart(self):
        DbTestCase.start_server(self.db_file.name)

        requests.post(Item(0).url, "123")
        DbTestCase.stop_server()
        DbTestCase.start_server(self.db_file.name)
        read = requests.get(Item(0).url)

        self.assertReturns(read, 123)

    def test_run_quickly_without_persistence(self):
        DbTestCase.start_server()
        data = json.dumps([(i, i) for i in range(0, 1000)])

        startTime = time.time()
        requests.post(DB_ROOT, data)
        writeTime = time.time() - startTime

        self.assertLess(writeTime, 0.1)

    def test_run_quickly_with_persistence(self):
        DbTestCase.start_server(self.db_file.name)
        data = json.dumps([(i, i) for i in range(0, 1000)])

        startTime = time.time()
        requests.post(DB_ROOT, data)
        writeTime = time.time() - startTime

        self.assertLess(writeTime, 0.2)