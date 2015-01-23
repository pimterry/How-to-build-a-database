from dbtestcase import DbTestCase
from timeout_decorator import timeout
import requests, json

class DocumentTest(DbTestCase):
    def test_can_write_and_read_document(self):
        value = { "name": "Tim Perry", "company": "Softwire" }
        requests.post("http://localhost:8080/1", json.dumps(value))

        read = requests.get("http://localhost:8080/1")

        self.assertReturns(read, value)