from tkinter import *
from socket import *
from threading import *
from tkinter.scrolledtext import ScrolledText
from time import sleep
import sqlite3
from queue import Queue

flag = 1
conn_q = Queue()
gui_q = Queue()
isUser = False
printTable = False
afterLogin = False
newUser = False
check_count = 0
need_to_pick_new_name = False  # if a client choses a taken name he needs to choose a diffetent name, only relevent
# once after the name is taken(otherwise it loops)

userName = ''


def sqlCreateUserTable():
    conn = sqlite3.connect('users.db')
    print("Opened database successfully");

    conn.execute('''CREATE TABLE USERS
             (
             username       TEXT PRIMARY KEY   NOT NULL,
             password       TEXT               NOT NULL
             );''')

    print("Table created successfully");
    conn.close()


def check_user(userN, passW):
    conn = sqlite3.connect('users.db')
    print("Opened database successfully")
    exists = False
    cursor = conn.execute("SELECT * from users")
    for row in cursor:

        if userN == row[0] and passW == row[1]:
            exists = True
    print("Operation done successfully")
    conn.close()
    return exists


# checks if the new username from the sign up process is taken
def userN_exists(name):
    conn = sqlite3.connect('users.db')
    print("Opened database successfully")
    exists = False
    cursor = conn.execute("SELECT * from users")
    for row in cursor:

        if name == row[0]:
            exists = True
    print("Operation done successfully")
    conn.close()
    return exists



def check_login(username, password):
    pass




def server_recv():
    global flag
    global newUser
    global userName
    port = 8820
    print("server recv start")
    server_socket = socket()
    server_socket.bind(('0.0.0.0', 8820))

    server_socket.listen(1)

    (client_socket, client_address) = server_socket.accept()
    print("client accept from {0} at port {1}".format(client_address, port))
    client_socket.settimeout(3000)

    flag = 1
    sendThread = Thread(target=server_send, args=(client_socket, client_address))
    sendThread.start()
    global check_count
    client_info = client_socket.recv(1024).decode('latin-1')
    print("server_recv: " + client_info)
    print("4444", current_thread().name)
    gui_q.put(client_info)
    if client_info == "new":
        newUser = True
    sleep(0.5)
    while 1:
        try:
            client_info = client_socket.recv(1024)
        except Exception as e:
            flag = 0
            sleep(0.2)  # let the server_send thread to be close
            print(e)
            client_socket.close()
            (client_socket, client_address) = server_socket.accept()  # be ready for next client
            client_socket.settimeout(3000)
            print("client accept from {0} at port {1}".format(client_address, port))
            flag = 1
            sendThread = Thread(target=server_send, args=(client_socket, client_address))
            sendThread.start()
            continue
        # if the code will not check empty string,then once the client terminate,
        # the server will continusly will get empty string
        if client_info == "":
            flag = 0
            sleep(0.2)  # let the server_send thread to be close
            client_socket.close()
            print("client close the socket")
            (client_socket, client_address) = server_socket.accept()
            print("client accept from {0} at port {1}".format(client_address, port))
            client_socket.settimeout(3000)
            flag = 1
            sendThread = Thread(target=server_send, args=(client_socket, client_address))
            sendThread.start()
            continue

        client_info_str = client_info.decode('latin-1')
        print("server_recv: " + client_info_str)
        print("4444", current_thread().name)
        gui_q.put(client_info_str)
        check_count = check_count + 1
        if newUser and check_count == 1:
            print("newUserChe")
            userName = client_info_str
            if userN_exists(userName):  # user name exists, the client needs to pick a different name
                check_count = 0
                global need_to_pick_new_name
                need_to_pick_new_name = True

        elif newUser and check_count == 2:
            newUserPass = client_info_str
            print(userName + 'new username')
            add = [(userName, newUserPass)]
            conn = sqlite3.connect('users.db')

            add = [(userName, newUserPass)]
            conn.executemany('INSERT INTO  users (username, password) VALUES (?,?)', add)

            print("Records for users created successfully");

            conn.commit()
            conn.close()
            conn_q.put("isUser")
        elif check_count == 1 and not newUser:
            userName = client_info_str
        elif check_count == 2:
            passW = client_info_str
            global isUser
            isUser = check_user(userName, passW)
            global afterLogin
            afterLogin = True
        '''if client_info_str == "send_users":
            send_users()'''


def server_send(client_socket, client_address):
    print("server send start")
    global flag
    while flag == 1:
        if not conn_q.empty():
            data = conn_q.get()
            print("server_send: " + data)
            print("3333", current_thread().name)
            client_socket.sendall(data.encode('latin-1'))
        sleep(0.05)  # sleep a little before check the queue again


def send_users():
    conn = sqlite3.connect('users.db')
    print("Opened database successfully")
    exists = False
    cursor = conn.execute("SELECT * from users")
    conn_q.put('the users are:\n')
    for row in cursor:
        conn_q.put(row[0] + '\n-----------------------')

    global printTable
    printTable = True
    print("Operation done successfully")
    conn.close()


class App(Thread):
    def __init__(self, master):
        commThread = Thread(target=server_recv, args=())
        commThread.start()

        Thread.__init__(self)
        frame = Frame(master)
        frame.pack()
        self.gettext = Text(frame, height=1, width=15, state=NORMAL)
        self.gettext.pack()
        sframe = Frame(frame)
        sframe.pack(anchor='w')
        self.pro = Label(sframe, text="")
        self.sendtext = Entry(sframe, width=15)
        self.sendtext.focus_set()
        self.sendtext.bind(sequence="<Return>", func=self.Send)
        self.pro.pack(side=LEFT)
        self.sendtext.pack(side=LEFT)
        self.gettext.insert(END, 'server is up')
        self.gettext.configure(state=DISABLED)

    def Send(self, args):
        print("2222", current_thread().name)
        self.gettext.configure(state=NORMAL)
        text = self.sendtext.get()
        if text == "": text = " "
        self.gettext.insert(END, 'Me >> %s \n' % text)
        self.sendtext.delete(0, END)
        conn_q.put(text)
        self.sendtext.focus_set()
        self.gettext.configure(state=DISABLED)
        self.gettext.see(END)

    def run(self):
        loggedIn = False
        global need_to_pick_new_name
        global check_count
        while 1:
            global afterLogin
            if need_to_pick_new_name:
                conn_q.put('you chose a name that was already taken, please choose a new name')
                need_to_pick_new_name = False
            if not loggedIn:
                if newUser:
                    loggedIn = True
                elif isUser:
                    self.gettext.configure(state=NORMAL)
                    self.gettext.configure(state=DISABLED)
                    print("the client is a user")
                    loggedIn = True
                    conn_q.put("isUser")
                elif not isUser and afterLogin:
                    self.gettext.configure(state=NORMAL)
                    self.gettext.insert(END, 'the client was not a user\n')
                    conn_q.put('you are not a user, try again')
                    self.gettext.configure(state=DISABLED)
                    afterLogin = False
                    check_count = 0

            if not gui_q.empty():
                text = gui_q.get()
                print("1111", current_thread().name)
                self.gettext.configure(state=NORMAL)
                self.gettext.insert(END, 'client >> %s\n' % text)
                self.gettext.configure(state=DISABLED)
                self.gettext.see(END)
            sleep(0.05)  # sleep a little before check the queue again


def main():
    # sqlCreateUserTable()
    root = Tk()
    root.title('Server')
    app = App(root).start()
    root.mainloop()


if __name__ == "__main__":
    main()