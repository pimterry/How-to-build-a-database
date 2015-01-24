from dbtestcase import instance_starter
from multiprocessing import Process

if __name__ == "__main__":
    server_ports = [8080, 8081, 8082]
    for port in server_ports:
        other_servers = ["http://localhost:%s" % other_port
                         for other_port in server_ports
                         if other_port != port]
        print("Starting %s" % port)
        Process(target=instance_starter(port=port, cluster=other_servers)).start()
        print("Started")