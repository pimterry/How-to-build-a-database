from threading import Thread
import traceback, socket, time


def start_proxy(listen_port, target_port, target_host='localhost'):
    proxy = MitmTcpProxy(listen_port, target_port, target_host)
    proxy.start()
    time.sleep(0.1)
    return proxy


class MitmTcpProxy(Thread):
    def __init__(self, listen_port, target_port, target_host):
        super().__init__()

        self.listen_port = listen_port
        self.target_port = target_port
        self.target_host = target_host

        self.delay = 0

    def run(self):
        self.running = True

        try:
            self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listen_socket.bind(('', self.listen_port))
            self.listen_socket.listen(5)

            while self.running:
                try:
                    client_socket = self.listen_socket.accept()[0]

                    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    server_socket.connect((self.target_host, self.target_port))

                    Thread(target=self.forward, args=(client_socket, server_socket)).start()
                    Thread(target=self.forward, args=(server_socket, client_socket)).start()
                except Exception as e:
                    if self.running:
                        print("Proxy threw an exception: %s" % e)
                        traceback.print_exc()
        except Exception as e:
            print("Proxy setup threw an exception: %s" % e)
            traceback.print_exc()

    def forward(self, source, target):
        data = True

        try:
            while data:
                data = source.recv(1024)
                if data:
                    time.sleep(self.delay)
                    target.sendall(data)
        except: pass

        try: source.shutdown(socket.SHUT_RD)
        except: pass

        try: target.shutdown(socket.SHUT_WR)
        except: pass

    def set_delay(self, delay):
        self.delay = delay

    def terminate(self):
        if not self.running: return

        try:
            self.running = False
            self.listen_socket.shutdown(socket.SHUT_RDWR)
            self.listen_socket.close()
        except Exception as e:
            print("Failed to stop: %s" % e)
            traceback.print_exc()
        self.listen_socket = None

