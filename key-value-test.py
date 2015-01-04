import requests
import unittest
import random
import time
from multiprocessing import Process
from main import build_app, run_server

class Item:
  def __init__(self):
    self.id = random.randint(0, 2**32)
    self.url = "http://localhost:8080/%s" % (self.id,)

def start_instance():
  run_server(build_app())

class KeyValueTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.server = Process(target=start_instance)
    cls.server.start()
    time.sleep(0.1)

  @classmethod
  def tearDownClass(cls):
    cls.server.terminate()

  def setUp(self):
    requests.post("http://localhost:8080/reset")

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

    assert read.status_code, read.text == (200, value)

  def test_insert_different_items_stores_separate_values(self):
    item1, value1 = Item(), "1"
    item2, value2 = Item(), "2"

    requests.post(item1.url, value1)
    requests.post(item2.url, value2)
    read1 = requests.get(item1.url)
    read2 = requests.get(item2.url)

    assert read1.status_code, read1.text == (200, value1)
    assert read2.status_code, read2.text == (200, value2)


  def test_insert_then_update_then_read_gets_2nd_value(self):
    item, value1, value2 = Item(), "1", "2"

    requests.post(item.url, value1)
    requests.post(item.url, value2)
    read = requests.get(item.url)

    assert read.status_code, read.text == (200, value2)
