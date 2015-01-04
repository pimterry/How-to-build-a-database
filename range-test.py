import requests, unittest, random, time, json
from multiprocessing import Process
from main import build_app, run_server

class Item:
  def __init__(self, id = None):
    self.id = id if id != None else random.randint(0, 2**32)
    self.url = "http://localhost:8080/%s" % (self.id,)

class Range:
  def __init__(self, start_id = None, end_id = None):
    self.start_id, self.end_id = start_id, end_id
    self.url = "http://localhost:8080/range?start=%s&end=%s" % (self.start_id, self.end_id)

def start_instance():
  run_server(build_app())

class RangeTests(unittest.TestCase):
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

  def test_can_get_two_value_range(self):
    requests.post(Item(0).url, "1")
    requests.post(Item(1).url, "2")

    read = requests.get(Range(0, 1).url)

    self.assertEqual(200, read.status_code)
    self.assertEqual([1, 2], json.loads(read.text))

  def test_can_get_single_value_range(self):
    requests.post(Item(10).url, "0")

    read = requests.get(Range(10, 10).url)

    self.assertEqual(200, read.status_code)
    self.assertEqual([0], json.loads(read.text))

  def test_skips_missing_values(self):
    requests.post(Item(0).url, "0")
    requests.post(Item(2).url, "2")

    read = requests.get(Range(0, 2).url)

    self.assertEqual(200, read.status_code)
    self.assertEqual([0, 2], json.loads(read.text))

  def test_handles_empty_ranges(self):
    read = requests.get(Range(0, 2).url)

    self.assertEqual(200, read.status_code)
    self.assertEqual([], json.loads(read.text))