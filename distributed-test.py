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
                proxy = None

    def set_delay(self, delay):
        for proxy in self.proxies:
            proxy.set_delay(delay)

    def test_data_is_available_from_all_servers(self):
        requests.post(Server(0).item(0), "5")
        time.sleep(1)

        read1 = requests.get(Server(1).item(0))
        read2 = requests.get(Server(2).item(0))

        self.assertReturns(read1, 5)
        self.assertReturns(read2, 5)

    @unittest.skip
    def test_cluster_replicate_despite_individual_outages(self):
        self.make_unreachable(1)
        requests.post(Server(0).item(0), "1")

        read2 = requests.get(Server(2).item(0))

        self.assertReturns(read2, 1)

    @unittest.skip
    def test_cluster_replicates_missed_writes_to_servers_after_outages(self):
        self.make_unreachable(1)
        requests.post(Server(0).item(0), "2")

        self.make_reachable(1)
        time.sleep(0.5)
        read1 = requests.get(Server(1).item(0))

        self.assertReturns(read1, 2)

    @unittest.skip
    def test_changes_are_synchronized_both_ways_after_outages(self):
        requests.post(Server(0).root(), json.dumps([(0, 100), (1, 100)]))
        self.disconnect_everything()

        requests.post(Server(0).item(0), "0")
        requests.post(Server(1).item(1), "1")
        self.start_all_proxies()
        time.sleep(0.5)

        read0 = requests.get(Server(0).range(0, 1))
        read1 = requests.get(Server(1).range(0, 1))
        self.assertReturns(read0, [0, 1])
        self.assertReturns(read1, [0, 1])

    def test_reads_always_return_the_most_recently_written_value(self):
        for i in range(10):
            requests.post(Server(0).item(i), str(i))

            read = requests.get(Server(1).item(i))
            self.assertReturns(read, i)

    def test_cluster_refuses_writes_which_cannot_be_consistent(self):
        self.disconnect_everything()

        try:
            requests.post(Server(0).item(0), "0", timeout=1)
            self.fail("Should not successfully write when network is disconnected")
        except requests.exceptions.Timeout:
            pass

    def test_concurrent_changes_dont_deadlock(self):
        self.set_delay(0.1)

        def try_and_write(i):
            result = requests.post(Server(0).item(i % 3), str(i), timeout=5)
            self.assertIn(result.status_code, [201, 503])

        threads = ThreadPool(processes=4).map_async(try_and_write, range(20))

        try:
            threads.get()
        except requests.exceptions.Timeout:
            self.fail("Request deadlocked and timed out")