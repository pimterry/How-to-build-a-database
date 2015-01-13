import requests, random, json, time, tempfile, pickle
from dbtestcase import DbTestCase, DB_ROOT

class Item:
    def __init__(self, id = None):
        self.id = id if id is not None else random.randint(0, 2**32)
        self.url = "%s/%s" % (DB_ROOT, self.id)

class DurabilityTests(DbTestCase):

    def setUp(self):
        DbTestCase.stopServer()
        self.db_file = tempfile.NamedTemporaryFile()

    def tearDown(self):
        self.db_file.close()

    def saveDbFile(self, data):
        pickle.dump(data, self.db_file)
        self.db_file.flush()

    def test_can_load_database_with_empty_file(self):
        self.saveDbFile({})

        DbTestCase.startServer(self.db_file.name)
        read = requests.get(Item(0).url)

        self.assertEqual(404, read.status_code)

    def test_can_load_database_from_saved_data(self):
        self.saveDbFile({0: "test-data"})

        DbTestCase.startServer(self.db_file.name)
        read = requests.get(Item(0).url)

        self.assertReturns(read, "test-data")