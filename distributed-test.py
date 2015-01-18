import requests, time, json, unittest
from dbtestcase import DbTestCase
from mitm_tcp_proxy import start_proxy

def proxy_port(i):
    return 9090 + i

def server_port(i):
    return 8080 + i

class Server:
    def __init__(self, server_num, direct=False):
        if direct:
            self.port = server_port(server_num)
        else:
            self.port = proxy_port(server_num)

    def item(self, id = None):
        return "%s/%s" % (self.root(), id)

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
        self.stop_all_proxies()

    def start_proxy(self, proxy_num):
        self.proxies[proxy_num] = start_proxy(proxy_port(proxy_num), server_port(proxy_num))

    def start_all_proxies(self):
        for i in range(3):
            self.proxies[i] = start_proxy(proxy_port(i), server_port(i))

    def stop_proxy(self, proxy_num):
        self.proxies[proxy_num].terminate()
        self.proxies[proxy_num] = None

    def stop_all_proxies(self):
        for proxy in self.proxies:
            if proxy is not None:
                proxy.terminate()

    def test_data_is_available_from_all_servers(self):
        requests.post(Server(0).item(0), "5")
        time.sleep(1)

        read1 = requests.get(Server(1).item(0))
        read2 = requests.get(Server(2).item(0))

        self.assertReturns(read1, 5)
        self.assertReturns(read2, 5)

    def test_cluster_replicate_despite_individual_outages(self):
        self.stop_proxy(1)
        requests.post(Server(0).item(0), "1")

        read2 = requests.get(Server(2).item(0))

        self.assertReturns(read2, 1)