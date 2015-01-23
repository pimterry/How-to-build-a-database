from dbtestcase import DbTestCase
from timeout_decorator import timeout
import requests, json, time

class DocumentTest(DbTestCase):
    def test_can_write_and_read_document(self):
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

    def test_can_quickly_query_by_field(self):
        data = { i: { "name": "Employee %s" % i, "age": 100 }
                 for i in range(0, 10000)}
        requests.post("http://localhost:8080", json.dumps(data))

        start = time.time()
        read = requests.get("http://localhost:8080/by/name/Employee 9999")
        query_millis = time.time() - start

        self.assertReturns(read, { "name": "Employee 9999", "age": 100 })
        self.assertLess(query_millis, 0.01)

