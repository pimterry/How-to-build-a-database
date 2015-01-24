import requests, time, json, unittest
from dbtestcase import DbTestCase
from multiprocessing.pool import ThreadPool
from mitm_tcp_proxy import start_proxy

def proxy_port(i):
    return 9090 + i

def server_port(i):
    return 8080 + i

class Server:
    def __init__(self, server_num):
        self.port = server_port(server_num)

    def item(self, id = None):
        return "%s/%s" % (self.root(), id)

    def range(self, start, end):
        return "%s/range?start=%s&end=%s" % (self.root(), start, end)

    def root(self):
        return "http://localhost:%s/" % self.port

class DistributedTests(DbTestCase):

    def setUp(self):
        DbTestCase.stop_server()

        self.servers = []
        self.proxies = []

        whole_cluster = [proxy_port(i) for i in range(3)]

        for i in range(3):
            rest_of_cluster = ["http://localhost:%s" % c for c in whole_cluster if c != proxy_port(i)]

            self.servers.append(DbTestCase.start_and_return_server(port=server_port(i), cluster=rest_of_cluster))
            self.proxies.append(start_proxy(proxy_port(i), server_port(i)))

    def tearDown(self):
        for server in self.servers:
            server.terminate()
        self.disconnect_everything()

    def set_delay(self, delay):
        for proxy in self.proxies:
            proxy.set_delay(delay)

    def make_reachable(self, proxy_num):
        self.proxies[proxy_num] = start_proxy(proxy_port(proxy_num), server_port(proxy_num))

    def start_all_proxies(self):
        for i in range(3):
            self.proxies[i] = start_proxy(proxy_port(i), server_port(i))

    def make_unreachable(self, proxy_num):
        self.proxies[proxy_num].terminate()
        self.proxies[proxy_num] = None

    def disconnect_everything(self):
        for proxy in self.proxies:
            if proxy is not None:
                proxy.terminate()
        self.proxies.clear()

    def test_data_is_available_everywhere(self):
        requests.post(Server(0).item(0), "5")

        read1 = requests.get(Server(1).item(0))
        read2 = requests.get(Server(2).item(0))

        self.assertReturns(read1, 5)
        self.assertReturns(read2, 5)

    def test_replicates_after_outages(self):
        self.make_unreachable(1)
        requests.post(Server(0).item(0), "10")

        self.make_reachable(1)
        time.sleep(1)
        read1 = requests.get(Server(1).item(0))

        self.assertReturns(read1, 10)