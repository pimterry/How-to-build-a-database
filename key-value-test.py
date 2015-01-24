from dbtestcase import DbTestCase
import requests

class KeyValueTest(DbTestCase):
    def test_database_is_initally_empty(self):
        read = requests.get("http://localhost:8080/123")

        self.assertEquals(read.status_code, 404)

    def test_can_read_writes(self):
        requests.post("http://localhost:8080/1", "5")

        read = requests.get("http://localhost:8080/1")

        self.assertReturns(read, 5)
