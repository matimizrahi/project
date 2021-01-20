from tkinter import *
from socket import *
from threading import *
from tkinter.scrolledtext import ScrolledText
from time import sleep
import tkinter as tk
from queue import Queue
import cv2

conn_q = Queue()
gui_q = Queue()
isUser = False
rootLog = Tk
root = tk
rootSign = tk


def open_cam():
    cap = cv2.VideoCapture(cv2.CAP_DSHOW)
    print("camara is opening")
    while True:
        ret, frame = cap.read()

        const = 50
        edge = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edge = cv2.Laplacian(frame, cv2.CV_16S, ksize=3)
        cv2.imshow("my camera", frame)
        key = cv2.waitKey(1)
        if key == ord('q'):  # if user presses q key they will exit the program
            cv2.destroyAllWindows()
            break


def view_users():
    pass


def connect():
    pass


def login():
    global rootLog
    global root
    root.destroy()
    rootLog = Tk()
    rootLog.title('log in')
    app = LogIn(rootLog).start()
    rootLog.mainloop()
    print("login done")

    afterLoginTK()


def signup():
    global root
    global rootSign
    root.destroy()
    rootSign = Tk()
    rootSign.title('sign up')
    app = SignUp(rootSign).start()
    rootSign.mainloop()
    afterLoginTK()


def afterLoginTK():
    afterLogin = tk.Tk()
    frame = tk.Frame(afterLogin)
    frame.pack()
    button1 = tk.Button(frame, text="EXIT", fg="green", command=quit)
    button1.pack(side=tk.LEFT)
    button2 = tk.Button(frame, text="view users", fg="black", command=view_users())
    button2.pack(side=tk.LEFT)
    button3 = tk.Button(frame, text="connect me!", fg="black", command=connect())  # only opens camara
    button3.pack(side=tk.LEFT)
    afterLogin.mainloop()


def active_users():
    pass


def client_recv(my_socket):
    global isUser
    while True:
        data = my_socket.recv(1024)
        if data == "":
            print("server close this socket")
            my_socket.close()
            break  # get out from thread
        data = data.decode('latin-1')
        print("client_recv:" + data)
        print("4444", current_thread().name)
        gui_q.put(data)
        if data == "isUser":
           isUser = True
    print("client_recv while done")


def client_send():
    print("start client")
    my_socket = socket()
    my_socket.connect(("127.0.0.1", 8820))

    recvThread = Thread(target=client_recv, args=(my_socket,))
    recvThread.start()

    while True:
        if not conn_q.empty():
            data = conn_q.get()
            print("client_send:" + data)
            print("3333", current_thread().name)
            my_socket.sendall(data.encode('latin-1'))

        sleep(0.05)  # sleep a little before check the queue again


class SignUp(Thread):

    def __init__(self, master):

        commThread = Thread(target=client_send, args=())
        commThread.start()

        Thread.__init__(self)
        frame = Frame(master)
        frame.pack()
        conn_q.put("new")
        self.gettext = ScrolledText(frame, height=10, width=50, background="light green")
        self.gettext.pack()
        self.gettext.insert(END, 'enter your desired username:\n')
        self.gettext.configure(state='disabled')
        sframe = Frame(frame)
        sframe.pack(anchor='w')
        self.pro = Label(sframe, text="")
        self.sendtext = Entry(sframe, width=50)
        self.sendtext.focus_set()
        self.sendtext.bind(sequence="<Return>", func=self.Send)
        self.pro.pack(side=LEFT)
        self.sendtext.pack(side=LEFT)

    def Send(self, args):
        print("2222", current_thread().name)
        self.gettext.configure(state='normal')
        text = self.sendtext.get()
        if text == "": text = " "
        self.gettext.insert(END, '%s\n' % text)
        self.sendtext.delete(0, END)
        conn_q.put(text)

        self.sendtext.focus_set()
        self.gettext.configure(state='disabled')
        self.gettext.see(END)

    def run(self):
        while True:
            if isUser:
                rootSign.destroy()
                break
            if not gui_q.empty():
                text = gui_q.get()
                print("1111", current_thread().name)
                self.gettext.configure(state='normal')
                self.gettext.insert(END, '%s\n' % text)
                self.gettext.configure(state='disabled')
                self.gettext.see(END)
            sleep(0.05)  # sleep a little before check the queue again


class LogIn(Thread):

    def __init__(self, master):

        commThread = Thread(target=client_send, args=())
        commThread.start()

        Thread.__init__(self)
        frame = Frame(master)
        frame.pack()
        self.gettext = ScrolledText(frame, height=10, width=50, background="light gray")
        self.gettext.pack()
        conn_q.put("old")
        self.gettext.insert(END,
                            'in order to log in you need to enter your username and password.\nfirst enter your username and then your password.\n')
        self.gettext.configure(state='disabled')
        sframe = Frame(frame)
        sframe.pack(anchor='w')
        self.pro = Label(sframe, text="");
        self.sendtext = Entry(sframe, width=50)
        self.sendtext.focus_set()
        self.sendtext.bind(sequence="<Return>", func=self.Send)
        self.pro.pack(side=LEFT)
        self.sendtext.pack(side=LEFT)

    def Send(self, args):
        print("2222", current_thread().name)
        self.gettext.configure(state='normal')
        text = self.sendtext.get()
        if text == "": text = " "
        self.gettext.insert(END, '%s\n' % text)
        self.sendtext.delete(0, END)
        conn_q.put(text)

        self.sendtext.focus_set()
        self.gettext.configure(state='disabled')
        self.gettext.see(END)
        print("send")

    def run(self):
        # global rootLog
        while True:
            if isUser:
                rootLog.destroy()
                break
            if not gui_q.empty():
                text = gui_q.get()
                print("1111", current_thread().name)
                self.gettext.configure(state='normal')
                self.gettext.insert(END, 'Server >> %s\n' % text)
                self.gettext.configure(state='disabled')
                self.gettext.see(END)
            sleep(0.05)  # sleep a little before check the queue again
        print("run while done")


def main():
    global root
    root = tk.Tk()
    frame = tk.Frame(root)
    frame.pack()

    button1 = tk.Button(frame, text="EXIT", fg="green", command=quit)
    button1.pack(side=tk.LEFT)
    button2 = tk.Button(frame, text="log in", command=login)
    button2.pack(side=tk.LEFT)
    button3 = tk.Button(frame, text="sign up", command=signup)
    button3.pack(side=tk.LEFT)

    root.mainloop()


if __name__ == "__main__":
    main()
