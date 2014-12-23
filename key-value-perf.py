import requests
import unittest
import random
import time
from multiprocessing import Process
from main import build_app, run_server
from locust import TaskSet, HttpLocust, task, events

class Item:
  def __init__(self):
    self.id = random.randint(0, 100000)
    self.path = "%s" % (self.id,)

class KeyValueTasks(TaskSet):
  @task
  def read_random_item(self):
    with self.client.get(Item().path, catch_response=True, name="Read") as response:
      if response.status_code == 404:
          response.success()

  @task
  def write_random_item(self):
    value = random.randint(0, 1000)
    self.client.post(Item().path, str(value), name="Write")

class KeyValueUser(HttpLocust):
  min_wait = 0
  max_wait = 0
  host = "http://localhost:8080/"
  task_set = KeyValueTasks
