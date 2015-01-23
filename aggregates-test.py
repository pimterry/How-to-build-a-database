import requests, random, json, time
from dbtestcase import DbTestCase, DB_ROOT


def item(id = None):
    id = id if id is not None else random.randint(0, 2**32)
    return "%s/%s" % (DB_ROOT, id)

def sum_query(field):
    return "%s/sum/%s" % (DB_ROOT, field)

class AggregatesTests(DbTestCase):

  def test_can_sum_values(self):
    requests.post(item(), json.dumps({"value": 1}))
    requests.post(item(), json.dumps({"value": 2}))
    requests.post(item(), json.dumps({"value": 3}))

    read = requests.get(sum_query('value'))

    self.assertReturns(read, 6)

  def test_can_sum_values_quickly(self):
    filler_data = {x: x for x in range(0, 100)}
    filler_data['value'] = 1

    requests.post(DB_ROOT, json.dumps([(i, filler_data) for i in range(0, 10000)]))

    start = time.time()
    for i in range(0, 50):
      read = requests.get(sum_query('value'))
    query_seconds = (time.time() - start) / 50

    self.assertLess(query_seconds, 0.03)
    self.assertReturns(read, 10000)

  def test_handles_removal_of_column_indexed_field(self):
    requests.post(item(0), json.dumps({"name": "Tim perry", "value": 1}))
    requests.post(item(0), json.dumps({"name": "Tim perry"}))

    read = requests.get(sum_query('value'))

    self.assertReturns(read, 0)