import requests, time, unittest
from dbtestcase import DbTestCase
from mitm_tcp_proxy import start_proxy

class Server:
    def __init__(self, server_num):
        self.port = 9090 + server_num

    def item(self, id = None):
        return "http://localhost:%s/%s" % (self.port, id)

class DistributedTests(DbTestCase):

    def setUp(self):
        DbTestCase.stop_server()

        self.servers = []
        self.proxies = []

        whole_cluster = [9090, 9091, 9092]

        for i in range(3):
            server_port = 8080+i
            proxied_server_port = 9090+i
            rest_of_cluster = ["http://localhost:%s" % c for c in whole_cluster if c != proxied_server_port]

            self.servers.append(DbTestCase.start_and_return_server(port=server_port, cluster=rest_of_cluster))
            self.proxies.append(start_proxy(proxied_server_port, server_port))

    def tearDown(self):
        for server in self.servers:
            server.terminate()
        for proxy in self.proxies:
            proxy.terminate()

    def test_data_is_available_from_all_servers(self):
        requests.post(Server(0).item(0), "5")
        time.sleep(1)

        read1 = requests.get(Server(1).item(0))
        read2 = requests.get(Server(2).item(0))

        self.assertReturns(read1, 5)
        self.assertReturns(read2, 5)

    def test_cluster_replicate_despite_individual_outages(self):
        self.proxies[1].terminate()
        requests.post(Server(0).item(0), "1")

        read2 = requests.get(Server(2).item(0))

        self.assertReturns(read2, 1)