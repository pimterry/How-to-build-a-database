import requests, random, json, time
from dbtestcase import DbTestCase, DB_ROOT

class Item:
  def __init__(self, id = None):
    self.id = id if id is not None else random.randint(0, 2**32)
    self.url = "%s/%s" % (DB_ROOT, self.id)

class Query:
  def __init__(self, field, value):
    self.url = "%s/by/%s/%s" % (DB_ROOT, field, json.dumps(value))

class DocumentTests(DbTestCase):

  def test_can_insert_document(self):
    requests.post(Item(0).url, json.dumps({"name": "Tim Perry"}))

    read = requests.get(Item(0).url)

    self.assertReturns(read, {"name": "Tim Perry"})

  def test_can_query_for_document_by_field(self):
    clareDoc = {"id": 0, "name": "Clare", "students": 655}
    requests.post(Item().url, json.dumps(clareDoc))
    requests.post(Item().url, json.dumps({"id": 1, "name": "Pembroke", "students": 597}))

    read = requests.get(Query("name", "Clare").url)

    self.assertReturns(read, clareDoc)

  def test_query_returns_nothing_for_items_with_incorrect_values(self):
    requests.post(Item().url, json.dumps({"id": 0, "name": "Trinity", "students": 1030}))

    read = requests.get(Query("name", "Clare").url)

    self.assertEquals(404, read.status_code)

  def test_query_returns_nothing_for_items_without_the_field(self):
    requests.post(Item().url, json.dumps({"id": 0, "city": "London"}))

    read = requests.get(Query("name", "Clare").url)

    self.assertEquals(404, read.status_code)

  def test_can_quickly_query_by_field(self):
    data = json.dumps([(i, {'id': i, 'name': 'Item %s' % i}) for i in range(0, 10000)])
    requests.post(DB_ROOT, data)

    start = time.time()
    read = requests.get(Query("name", "Item 9999").url)
    query_millis = time.time() - start

    self.assertLess(query_millis, 0.01)
    self.assertReturns(read, {'id': 9999, 'name': 'Item 9999'})

  def test_updates_index_after_changes(self):
    requests.post(Item(0).url, json.dumps({"id": 0, "name": "Name1"}))
    requests.post(Item(0).url, json.dumps({"id": 0, "name": "Name2"}))

    read1 = requests.get(Query("name", "Name1").url)
    read2 = requests.get(Query("name", "Name2").url)

    self.assertEquals(404, read1.status_code)
    self.assertReturns(read2, { 'id': 0, 'name': 'Name2' })
