from dbtestcase import DbTestCase
from timeout_decorator import timeout
import requests

class RangeTest(DbTestCase):
    def test_can_query_for_range_of_values(self):
        requests.post("http://localhost:8080/1", "1")
        requests.post("http://localhost:8080/2", "2")
        requests.post("http://localhost:8080/3", "3")

        read = requests.get("http://localhost:8080/range?start=2&end=3")

        self.assertReturns(read, [2, 3])

    @timeout(1)
    def test_can_query_for_range_of_values_quickly(self):
        read = requests.get("http://localhost:8080/range?start=0&end=100000000")

        self.assertReturns(read, [])