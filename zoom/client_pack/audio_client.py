import socket
import pyaudio
from threading import Thread
from client_pack import clients_server

# record
CHUNK = 1024  # 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 20000
# socket
SERVER_PORT = 50000
SERVER_IP = clients_server.HOST_IP

#לקוח המקליט ומשמיע קול
class Audio:
    # connect to server and start stream
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("socket initiated")
        self.stop = False
        p = pyaudio.PyAudio()
        try:
            self.send_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        except:
            print("microphone is not connected")
        try:
            self.receive_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True,
                                         frames_per_buffer=CHUNK)
        except:
            print("speaker is not connected")

    def receive_data(self):
        while not self.stop:
            try:
                data = self.s.recv(1024)
                self.receive_stream.write(data)
            except:
                pass

    def send_data(self):
        while not self.stop:
            try:
                data = self.send_stream.read(CHUNK)
                self.s.send(data)
            except:
                pass

    def start(self):
        self.conn(SERVER_IP, SERVER_PORT)
        recv = Thread(target=self.receive_data, name='receive_data', daemon=True)
        send = Thread(target=self.send_data, name='send_data', daemon=True)
        recv.start()
        send.start()

    def conn(self, server_ip, server_port):
        self.s.connect((server_ip, server_port))
        print("voice call connected")

    def end(self):
        self.stop = True
        self.s.close()
        self.stop = False
        # print('Voice chat closed')