import requests, random, json, time
from dbtestcase import DbTestCase, DB_ROOT

def item(id = None):
    id = id if id is not None else random.randint(0, 2**32)
    return "%s/%s" % (DB_ROOT, id)

def query(field, value):
    return "%s/by/%s/%s" % (DB_ROOT, field, json.dumps(value))

class DocumentTests(DbTestCase):

  def test_can_insert_document(self):
    requests.post(item(0), json.dumps({"name": "Tim Perry"}))

    read = requests.get(item(0))

    self.assertReturns(read, {"name": "Tim Perry"})

  def test_can_query_for_document_by_field(self):
    clareDoc = {"id": 0, "name": "Clare", "students": 655}
    requests.post(item(), json.dumps(clareDoc))
    requests.post(item(), json.dumps({"id": 1, "name": "Pembroke", "students": 597}))

    read = requests.get(query("name", "Clare"))

    self.assertReturns(read, clareDoc)

  def test_query_returns_nothing_for_items_with_incorrect_values(self):
    requests.post(item(), json.dumps({"id": 0, "name": "Trinity", "students": 1030}))

    read = requests.get(query("name", "Clare"))

    self.assertEquals(404, read.status_code)

  def test_query_returns_nothing_for_items_without_the_field(self):
    requests.post(item(), json.dumps({"id": 0, "city": "London"}))

    read = requests.get(query("name", "Clare"))

    self.assertEquals(404, read.status_code)

  def test_can_quickly_query_by_field(self):
    data = json.dumps([(i, {'id': i, 'name': 'Item %s' % i}) for i in range(0, 10000)])
    requests.post(DB_ROOT, data)

    start = time.time()
    read = requests.get(query("name", "Item 9999"))
    query_millis = time.time() - start

    self.assertLess(query_millis, 0.01)
    self.assertReturns(read, {'id': 9999, 'name': 'Item 9999'})

  def test_updates_index_after_changes(self):
    requests.post(item(0), json.dumps({"id": 0, "name": "Name1"}))
    requests.post(item(0), json.dumps({"id": 0, "name": "Name2"}))

    read1 = requests.get(query("name", "Name1"))
    read2 = requests.get(query("name", "Name2"))

    self.assertEquals(404, read1.status_code)
    self.assertReturns(read2, { 'id': 0, 'name': 'Name2' })
