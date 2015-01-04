import requests, random, unittest
from timeout_decorator import timeout
from dbtestcase import DbTestCase, DB_ROOT

class Item:
  def __init__(self, id = None):
    self.id = id if id != None else random.randint(0, 2**32)
    self.url = "%s/%s" % (DB_ROOT, self.id)

class Range:
  def __init__(self, start_id = None, end_id = None):
    self.start_id, self.end_id = start_id, end_id
    self.url = "%s/range?start=%s&end=%s" % (DB_ROOT, self.start_id, self.end_id)

class RangeTests(DbTestCase):

  def test_can_get_two_value_range(self):
    requests.post(Item(0).url, "0")
    requests.post(Item(1).url, "1")

    read = requests.get(Range(0, 1).url)

    self.assertReturns(read, [0, 1])

  def test_can_get_single_value_range(self):
    requests.post(Item(10).url, "123")

    read = requests.get(Range(10, 10).url)

    self.assertReturns(read, [123])

  def test_doesnt_include_values_after_range(self):
    requests.post(Item(0).url, "0")
    requests.post(Item(1).url, "1")
    requests.post(Item(2).url, "2")

    read = requests.get(Range(0, 1).url)

    self.assertReturns(read, [0, 1])

  def test_doesnt_include_values_before_range(self):
    requests.post(Item(0).url, "0")
    requests.post(Item(1).url, "1")
    requests.post(Item(2).url, "2")

    read = requests.get(Range(1, 2).url)

    self.assertReturns(read, [1, 2])

  def test_skips_missing_values(self):
    requests.post(Item(0).url, "0")
    requests.post(Item(2).url, "2")

    read = requests.get(Range(0, 2).url)

    self.assertReturns(read, [0, 2])

  def test_handles_empty_ranges(self):
    read = requests.get(Range(0, 2).url)

    self.assertReturns(read, [])

  @timeout(1)
  def test_with_large_empty_range(self):
    read = requests.get(Range(0, 100000000).url)

    self.assertReturns(read, [])
