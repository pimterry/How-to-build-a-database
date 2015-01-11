import requests, random, json
from dbtestcase import DbTestCase, DB_ROOT

class Item:
  def __init__(self, id = None):
    self.id = id if id is not None else random.randint(0, 2**32)
    self.url = "%s/%s" % (DB_ROOT, self.id)

class Sum:
  def __init__(self, field):
    self.url = "%s/sum/%s" % (DB_ROOT, field)

class AggregatesTests(DbTestCase):

  def test_can_sum_values(self):
    requests.post(Item().url, json.dumps({"value": 1}))
    requests.post(Item().url, json.dumps({"value": 2}))
    requests.post(Item().url, json.dumps({"value": 3}))

    read = requests.get(Sum('value').url)

    self.assertReturns(read, 6)