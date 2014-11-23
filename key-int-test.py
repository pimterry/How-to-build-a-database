import requests
import unittest
import random
from main import build_app, run_server

def itemUrl(item_id):
  return "http://localhost:8080/%s" % (item_id,)

class KeyValueTests(unittest.TestCase):
  def setUp(self):
    self.item_id = random.randint(0, 2 ** 32)

  def itemUrl(self):
    return "http://localhost:8080/%s" % (self.item_id,)

  def test_read_before_write_gets_404(self):
    read = requests.get(url=self.itemUrl())

    assert read.status_code == 404

  def test_inserts_are_successful(self):
    write = requests.post(url=self.itemUrl(), data="500")

    assert write.status_code == 201

  def test_insert_then_read_gets_inserted_value(self):
    test_value = "100"
    requests.post(url=self.itemUrl(), data=test_value)
    read = requests.get(url=self.itemUrl())

    assert read.status_code == 200
    assert read.text == test_value

  def test_insert_then_update_then_read_gets_2nd_value(self):
    first_value, second_value = "100", "200"
    requests.post(url=self.itemUrl(), data=first_value)
    requests.post(url=self.itemUrl(), data=second_value)
    read = requests.get(url=self.itemUrl())

    assert read.status_code == 200
    assert read.text == second_value
