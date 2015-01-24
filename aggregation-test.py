from dbtestcase import DbTestCase
from timeout_decorator import timeout
import requests, json, time

class AggregationTest(DbTestCase):
    def test_can_sum_values_in_db(self):
        requests.post("http://localhost:8080/1", json.dumps({"cost": 1}))
        requests.post("http://localhost:8080/2", json.dumps({"cost": 2}))
        requests.post("http://localhost:8080/3", json.dumps({"cost": 3}))

        read = requests.get("http://localhost:8080/sum/cost")

        self.assertReturns(read, 6)

    def test_can_quickly_sum_values(self):
        row = { x: x for x in range(0, 100) }
        row['cost'] = 1

        requests.post("http://localhost:8080/", json.dumps({i: row for i in range(0,10000)}))

        start = time.time()
        for i in range(0, 50):
            read = requests.get("http://localhost:8080/sum/cost")
        query_seconds = (time.time() - start) / 50

        self.assertLess(query_seconds, 0.01)
        self.assertReturns(read, 10000)