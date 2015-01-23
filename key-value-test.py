import requests
import random
from dbtestcase import DbTestCase, DB_ROOT

def item(id = None):
    id = id if id is not None else random.randint(0, 2**32)
    return "%s/%s" % (DB_ROOT, id)

class KeyValueTests(DbTestCase):

  def test_values_are_empty_initially(self):
    read = requests.get(item())
    assert read.status_code == 404

  def test_inserts_are_successful(self):
    write = requests.post(item(), "1")
    assert write.status_code == 201

  def test_insert_then_read_gets_inserted_value(self):
    item1, value = item(), "1"
    
    requests.post(item1, value)
    read = requests.get(item1)

    self.assertReturns(read, 1)

  def test_insert_different_items_stores_separate_values(self):
    item1, value1 = item(), 1
    item2, value2 = item(), 2

    requests.post(item1, str(value1))
    requests.post(item2, str(value2))
    read1 = requests.get(item1)
    read2 = requests.get(item2)

    self.assertReturns(read1, value1)
    self.assertReturns(read2, value2)

  def test_insert_then_update_then_read_gets_2nd_value(self):
    item1, value1, value2 = item(), 1, 2

    requests.post(item1, str(value1))
    requests.post(item1, str(value2))
    read = requests.get(item1)

    self.assertReturns(read, value2)
