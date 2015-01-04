import requests
import random
from dbtestcase import DbTestCase, DB_ROOT

class Item:
  def __init__(self, id = None):
    self.id = id if id is not None else random.randint(0, 2**32)
    self.url = "%s/%s" % (DB_ROOT, self.id)

class KeyValueTests(DbTestCase):

  def test_values_are_empty_initially(self):
    read = requests.get(Item().url)
    assert read.status_code == 404

  def test_inserts_are_successful(self):
    write = requests.post(Item().url, "1")
    assert write.status_code == 201

  def test_insert_then_read_gets_inserted_value(self):
    item, value = Item(), "1"
    
    requests.post(item.url, value)
    read = requests.get(item.url)

    self.assertReturns(read, 1)

  def test_insert_different_items_stores_separate_values(self):
    item1, value1 = Item(), 1
    item2, value2 = Item(), 2

    requests.post(item1.url, str(value1))
    requests.post(item2.url, str(value2))
    read1 = requests.get(item1.url)
    read2 = requests.get(item2.url)

    self.assertReturns(read1, value1)
    self.assertReturns(read2, value2)

  def test_insert_then_update_then_read_gets_2nd_value(self):
    item, value1, value2 = Item(), 1, 2

    requests.post(item.url, str(value1))
    requests.post(item.url, str(value2))
    read = requests.get(item.url)

    self.assertReturns(read, value2)
