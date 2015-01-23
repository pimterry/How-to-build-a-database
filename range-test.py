import requests, random, unittest
from timeout_decorator import timeout
from dbtestcase import DbTestCase, DB_ROOT

def item(id = None):
    id = id if id is not None else random.randint(0, 2**32)
    return "%s/%s" % (DB_ROOT, id)

def range_query(start_id, end_id):
    return "%s/range?start=%s&end=%s" % (DB_ROOT, start_id, end_id)

class RangeTests(DbTestCase):

  def test_can_get_two_value_range(self):
    requests.post(item(0), "0")
    requests.post(item(1), "1")

    read = requests.get(range_query(0, 1))

    self.assertReturns(read, [0, 1])

  def test_can_get_single_value_range(self):
    requests.post(item(10), "123")

    read = requests.get(range_query(10, 10))

    self.assertReturns(read, [123])

  def test_doesnt_include_values_after_range(self):
    requests.post(item(0), "0")
    requests.post(item(1), "1")
    requests.post(item(2), "2")

    read = requests.get(range_query(0, 1))

    self.assertReturns(read, [0, 1])

  def test_doesnt_include_values_before_range(self):
    requests.post(item(0), "0")
    requests.post(item(1), "1")
    requests.post(item(2), "2")

    read = requests.get(range_query(1, 2))

    self.assertReturns(read, [1, 2])

  def test_skips_missing_values(self):
    requests.post(item(0), "0")
    requests.post(item(2), "2")

    read = requests.get(range_query(0, 2))

    self.assertReturns(read, [0, 2])

  def test_handles_empty_ranges(self):
    read = requests.get(range_query(0, 2))

    self.assertReturns(read, [])

  @timeout(1)
  def test_with_large_empty_range(self):
    read = requests.get(range_query(0, 100000000))

    self.assertReturns(read, [])
