from dbtestcase import DbTestCase
import requests

class KeyValueTest(DbTestCase):
    def test_database_is_initially_empty(self):
        read = requests.get("http://localhost:8080/1")

        self.assertEquals(404, read.status_code)

    def test_write_can_be_read(self):
        requests.post("http://localhost:8080/5", "100")

        read = requests.get("http://localhost:8080/5")

        self.assertReturns(read, 100)

    def test_data_can_be_updated(self):
        requests.post("http://localhost:8080/10", "1")
        requests.post("http://localhost:8080/10", "2")

        read = requests.get("http://localhost:8080/10")

        self.assertReturns(read, 2)