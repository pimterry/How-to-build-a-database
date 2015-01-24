from dbtestcase import DbTestCase
import requests

class KeyValueTest(DbTestCase):
    def test_database_is_initally_empty(self):
        read = requests.get("http://localhost:8080/123")

        self.assertEquals(read.status_code, 404)
