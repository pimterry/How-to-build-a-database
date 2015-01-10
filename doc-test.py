import requests, random, json
from dbtestcase import DbTestCase, DB_ROOT

class Item:
  def __init__(self, id = None):
    self.id = id if id is not None else random.randint(0, 2**32)
    self.url = "%s/%s" % (DB_ROOT, self.id)

class DocumentTests(DbTestCase):

  def test_can_insert_document(self):
    requests.post(Item(0).url, json.dumps({"name": "Tim Perry"}))

    read = requests.get(Item(0).url)

    self.assertReturns(read, {"name": "Tim Perry"})