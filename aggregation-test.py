from dbtestcase import DbTestCase
from timeout_decorator import timeout
import requests, json, time

class AggregationTest(DbTestCase):
    def test_can_sum_over_all_values(self):
        requests.post("http://localhost:8080/1", json.dumps({"name": "Product 1", "cost": 1}))
        requests.post("http://localhost:8080/2", json.dumps({"name": "Product 1", "cost": 2}))
        requests.post("http://localhost:8080/3", json.dumps({"name": "Product 1", "cost": 3}))

        read = requests.get("http://localhost:8080/sum/cost")

        self.assertReturns(read, 6)

    def test_can_quickly_sum_over_all_values(self):
        values = { i: { "name": "Product %s" % i, "cost": 1 }
                   for i in range(0, 10000) }
        requests.post("http://localhost:8080", json.dumps(values))

        start = time.time()
        for i in range(0, 50):
            read = requests.get("http://localhost:8080/sum/cost")
        query_seconds = (time.time() - start) / 50

        self.assertReturns(read, 10000)
        self.assertLess(query_seconds, 0.02)