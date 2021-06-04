import socket
import select
import time

"""connects clients to server"""


class Server:
    def __init__(self):

        self.CONNECTION_LIST = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", 50000))
        self.server_socket.listen(2)

        self.CONNECTION_LIST.append(self.server_socket)
        self.addresses = {}

        print("Server Started!")

    def broadcast(self, sock, data):
        for current_socket in self.CONNECTION_LIST:
            if current_socket != self.server_socket and current_socket != sock:
                try:
                    current_socket.send(data)
                except:
                    pass

    def run(self):
        while True:
            rlist, wlist, xlist = select.select(self.CONNECTION_LIST, [], [])
            for current_socket in rlist:
                if current_socket is self.server_socket:
                    (new_socket, address) = self.server_socket.accept()
                    self.CONNECTION_LIST.append(new_socket)
                    self.addresses[new_socket] = address
                    print(time.strftime("%H:%M:%S", time.localtime()), "%s connected to the server" % str(address))
                else:
                    try:
                        data = current_socket.recv(1024)
                        self.broadcast(current_socket, data)
                    except socket.error:
                        print(time.strftime("%H:%M:%S", time.localtime()), "%s left the server" % str(self.addresses[current_socket]))
                        current_socket.close()
                        self.CONNECTION_LIST.remove(current_socket)


if __name__ == "__main__":
    Server().run()