from dbtestcase import DbTestCase
from timeout_decorator import timeout
import requests, json, time

class DocumentTest(DbTestCase):
    def test_put_and_read_documents(self):
        value = { "name": "Tim Perry", "company": "Softwire" }
        requests.post("http://localhost:8080/1", json.dumps(value))

        read = requests.get("http://localhost:8080/1")

        self.assertReturns(read, value)

    def test_can_query_by_field(self):
        clareDoc = { "name": "Clare", "population": 655 }
        pembrokeDoc = { "name": "Pembroke", "population": 597 }
        requests.post("http://localhost:8080/1", json.dumps(clareDoc))
        requests.post("http://localhost:8080/2", json.dumps(pembrokeDoc))

        read = requests.get("http://localhost:8080/by/name/Clare")

        self.assertReturns(read, clareDoc)

    def test_can_query_quickly(self):
        data = json.dumps({i: { "name": "Item %s" % i, "value": 1 }
                          for i in range(0, 10000)})
        requests.post("http://localhost:8080/", data)

        start = time.time()
        read = requests.get("http://localhost:8080/by/name/Item 9999")
        query_seconds = time.time() - start

        self.assertLess(query_seconds, 0.01)
        self.assertReturns(read, { "name": "Item 9999", "value": 1 })