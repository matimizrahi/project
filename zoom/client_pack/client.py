from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from threading import Thread, enumerate, active_count
import time
from winsound import PlaySound, SND_LOOP, SND_ASYNC, SND_PURGE
from client_pack.gui_methods import center_window, pop_up_message
from client_pack import clients_server
from client_pack.audio_client import Audio


# creates the pages and shows them
class App(Tk):
    background = r"..\media\background.png"

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title('computer call')
        # Setup Frame
        self.container = Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.username = ''
        self.target = ''
        self.user_called = ''
        self.frames = {}
        self.sp_background = PhotoImage(file=App.background)

        # self.threading_state() # used for debugging
        self.create_frames()
        center_window(self)
        self.show_frame(StartPage)
        # The following three commands are needed so the window pops
        # up on top on Windows...
        self.iconify()
        self.update()
        self.deiconify()

    def create_frames(self):
        for F in (StartPage, Login, Register, Main, Ringing, Dialing, Call):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, context):
        frame = self.frames[context]
        frame.tkraise()

    def threading_state(self, wait=8000):
        threads = [thread.getName() for thread in enumerate() if thread.getName() != 'MainThread']
        if threads:
            print('threads num:', active_count() - 1)
            print(threads)
        self.after(wait, self.threading_state)


# call page
class Call(Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.client = Audio()
        self.controller = controller
        self.msg = Label(self, font=('Ariel', 20), foreground='green')
        self.msg.pack()
        Button(self, text='end call', command=self.stop_call).pack()

    def stop_call(self):
        clients_server.stop(self.controller.username, 'call')

    def start_call(self):
        user = self.controller.target
        if not user:
            user = self.controller.user_called
        self.msg['text'] = f'In a call with {user}'
        Thread(target=self.call_ended, name='call_ended', daemon=True).start()
        self.client.start()

    def call_ended(self):
        time.sleep(2)
        while True:
            time.sleep(1)
            if not clients_server.is_in_call(self.controller.username):
                self.client.end()
                self.controller.show_frame(Main)
                time.sleep(0.4)
                self.controller.frames[Dialing].start_checking()
                break


# main page- after login
class Main(Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.users = Listbox(self, fg='green', font=('Ariel', 12))
        self.target_name = Entry(self, font=('Ariel', 12))
        self.controller = controller
        self.set()
        self.set_users_list()

    def set(self):
        Label(self, text='Call to', font=('Ariel', 20), foreground='magenta').pack(side=TOP)
        self.target_name.pack()
        Button(self, text='Call', command=self.pre_call).pack()
        Label(self, text='Users', font=('Ariel', 18), foreground='blue').pack()
        self.users.pack()
        self.users.bind('<<ListboxSelect>>', self.to_entry)
        self.bind('<Return>', self.pre_call)
        self.target_name.focus_set()

    # create list of users
    def set_users_list(self):
        self.users.delete(0, END)
        users = clients_server.user_lists()
        for user in users:
            if user != self.controller.username:
                self.users.insert(END, user)
        if self.users.size() < 10:
            self.users.configure(height=self.users.size())
        self.after(5000, self.set_users_list)

    # put a user in entry
    def to_entry(self, event=None):
        index = self.users.curselection()
        name = self.users.get(index)
        self.target_name.delete(0, END)
        self.target_name.insert(0, name)

    # checks if name valid, if so runs call

    def pre_call(self, event=None):
        target = self.target_name.get()
        self.target_name.delete(0, END)
        if len(target) > 2 and target != self.controller.username:
            if clients_server.is_user(target):  # checks if the user exists
                self.controller.target = target
                self.controller.show_frame(Ringing)
                self.controller.frames[Ringing].call()
            else:
                pop_up_message(f"sorry, the user '{target}' is not registered yet")
        elif len(target) < 3:
            pop_up_message('sorry, the name is too short, at least 3 characters')
        else:
            pop_up_message("you can't call yourself")


'''
    # create list of users
    def set_users_list(self):
        self.active_users.delete(0, END)
        users = clients_server.user_lists()
        for user in users:
            if user != self.controller.username:
                self.active_users.insert(END, user)
        if self.active_users.size() < 10:
            self.active_users.configure(height=self.active_users.size())
        self.after(5000, self.set_active_users_list)


    # put a user in entry
    def to_entry(self, event=None):
        index = self.active_users.curselection()
        name = self.active_users.get(index)
        self.target_name.delete(0, END)
        self.target_name.insert(0, name)
'''


# waiting for a call to be answered page
class Ringing(Frame):
    ring = r"..\media\calling_ring.wav"

    # ring = r"C:\PycharmProjects\project\zoom\media\phone_ring.mp3"

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.cancel = False
        self.label = Label(self, font=('Ariel', 20), foreground='magenta')
        self.label.pack()
        Button(self, text='Cancel Call', command=self.stop_calling).pack()

    def call(self):
        # print(f'ringing {self.controller.target}')
        self.label['text'] = f'Calling {self.controller.target}...'
        Thread(target=self.ringing, name='ringing', daemon=True).start()

    # cancels call
    def stop_calling(self):
        clients_server.stop(self.controller.username, 'ringing')
        self.cancel = True

    # checks if target agreed to chat
    def answer(self, timeout=1):
        max_time = time.time() + 60 * timeout  # 1 minutes from now
        # check if 'ringing' changed to 'call'
        PlaySound(Ringing.ring, SND_LOOP + SND_ASYNC)
        while True:
            time.sleep(1)
            if self.cancel:
                result = 'canceled'
                # print(result)
                break
            if time.time() > max_time:
                result = 'timed_out'
                break
            if clients_server.is_in_call(self.controller.username):
                result = 'accepted'
                break
            if not clients_server.not_rejected(self.controller.username, self.controller.target):
                result = 'rejected'
                break
        PlaySound(None, SND_PURGE)
        return result

    # calls and handle the call
    def ringing(self):
        is_posted = clients_server.call(self.controller.username, self.controller.target)
        if is_posted:
            # print('call posted')
            result = self.answer(1)
            if result == 'accepted':
                # print('call accepted')
                self.controller.show_frame(Call)
                self.controller.frames[Call].start_call()
            else:
                self.controller.show_frame(Main)
                if result == 'timed_out':  # waited too long for response from the call target
                    pop_up_message("call canceled, didn't receive answer in time")
                    # print("call canceled, didn't receive answer in time")
                elif result == 'canceled':
                    self.cancel = False
                elif result == 'rejected':
                    pop_up_message("call rejected")
                    # print("call canceled")

        else:  # error, call already exists, handling
            # print('error')
            clients_server.stop(self.controller.username, 'ringing')
            self.ringing()


# receiving a call page
class Dialing(Frame):
    sound = r"..\media\called_ring.wav"

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.text1 = Label(self, font=('Ariel', 20), foreground='magenta')
        self.text1.pack()
        self.bind('<Return>', self.yes)
        yes = Button(self, text='yes', command=self.yes)
        yes.focus_set()
        yes.pack()
        Button(self, text='no', command=self.no).pack()

    def start_checking(self):
        Thread(target=self.dialing, name='dialing', daemon=True).start()

    def dialing(self):
        # print(f'hi {self.controller.username}, waiting for a call')
        while True:
            if clients_server.look_for_call(self.controller.username):
                self.controller.show_frame(Dialing)
                user = clients_server.get_src_name(self.controller.username)
                self.controller.user_called = user
                # print(f'{user} dialing')
                self.text1['text'] = f'you got a call from {user}\ndo you want to answer'
                PlaySound(Dialing.sound, SND_LOOP + SND_ASYNC)
                break
            if clients_server.is_in_call(self.controller.username):  # when ringing and call was approved
                break
            time.sleep(1)

    def yes(self):
        PlaySound(None, SND_PURGE)
        successful = clients_server.accept(self.controller.user_called, self.controller.username)
        if successful == 'True':
            time.sleep(0.5)
            self.controller.show_frame(Call)
            self.controller.frames[Call].start_call()
        else:
            pop_up_message('call was canceled')
            # print('call was canceled')
            clients_server.stop(self.controller.username, 'ringing')
            self.controller.show_frame(Main)
            self.start_checking()

    def no(self):
        """ is this how i wanna handle that? the caller doesn't check if we canceled"""
        PlaySound(None, SND_PURGE)
        clients_server.stop(self.controller.username, 'ringing')
        self.controller.show_frame(Main)
        self.start_checking()


# front page of the app
class StartPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        background_label = Label(self, image=controller.sp_background)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        Label(self, text='Welcome to my program!',
              font="-family {Segoe UI} -size 30 -weight bold", foreground='black').place(x=160, y=90)
        Label(self, text='log in or sign up in order to continue',
              font="-family {Segoe UI} -size 20", foreground='black').place(x=180, y=200)
        Button(self, text='login', width=30, command=lambda: controller.show_frame(Login)).place(x=180, y=350)
        Button(self, text='sign up',width=30, command=lambda: controller.show_frame(Register)).place(x=400, y=350)


# login page
class Login(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        background_label = Label(self, image=controller.sp_background)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.controller = controller
        Label(self, text='this is the login page', font="-family {Segoe UI} -size 20 -weight bold", foreground='black').place(x=220, y=100)
        Label(self, text='enter your username and password', font="-family {Segoe UI} -size 20", foreground='black').place(x=150, y=150)
        self.entry_name = Entry(self)
        self.entry_passW = Entry(self, show='*')
        name = Label(self, text='Name', font="-family {Segoe UI} -size 12")
        passW = Label(self, text='Password', font="-family {Segoe UI} -size 12")
        enter = Button(self, text='Enter', command=self.collect)
        cancel = Button(self, text='Cancel', command=self.cancel)
        self.bind('<Return>', self.collect)
        self.entry_name.focus_set()
        # grid & pack
        name.grid(row=0, sticky=E)
        name.place(x=300, y=258)
        passW.grid(row=1, sticky=E)
        passW.place(x=270, y=298)
        self.entry_name.grid(row=0, column=1)
        self.entry_name.place(x=350, y=260)
        self.entry_passW.grid(row=1, column=1)
        self.entry_passW.place(x=350, y=300)
        enter.grid()
        enter.place(x=330, y=410)
        cancel.grid()
        cancel.place(x=330, y=450)

    def enter(self, name, passW):
        is_connected = clients_server.login(name, passW)
        if is_connected:
            self.controller.username = name
            pop_up_message(f"you're in, {name}")
            self.controller.create_frames()
            self.controller.show_frame(Main)
            self.controller.frames[Dialing].start_checking()
        else:
            self.entry_name.delete(0, END)
            self.entry_passW.delete(0, END)
            pop_up_message("name or password is incorrect")

    def collect(self):
        name = self.entry_name.get()
        passW = self.entry_passW.get()
        self.enter(name, passW)

    def cancel(self):
        self.controller.show_frame(StartPage)


# register page
class Register(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        background_label = Label(self, image=controller.sp_background)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.controller = controller
        Label(self, text='this is the registration page', font="-family {Segoe UI} -size 20 -weight bold", foreground='black').place(x=220, y=100)
        Label(self, text='enter your desired username and password and enter your email',
              font="-family {Segoe UI} -size 20", foreground='black').place(x=20, y=150)
        self.entry_name = Entry(self)
        self.entry_password = Entry(self)
        self.entry_email = Entry(self)
        name = Label(self, text='Name', font="-family {Segoe UI} -size 12")
        passW = Label(self, text='Password', font="-family {Segoe UI} -size 12")
        email = Label(self, text='email', font="-family {Segoe UI} -size 12")
        enter = Button(self, text='Register', command=self.handle)
        cancel = Button(self, text='Cancel', command=self.cancel)
        self.bind('<Return>', self.handle)
        self.entry_name.focus_set()

        # grid & pack
        name.grid(row=0, sticky=E)
        name.place(x=300, y=258)
        passW.grid(row=1, sticky=E)
        passW.place(x=270, y=298)
        email.grid(row=2, sticky=E)
        email.place(x=300, y=338)
        self.entry_name.grid(row=0, column=1)
        self.entry_name.place(x=350, y=260)
        self.entry_password.grid(row=1, column=1)
        self.entry_password.place(x=350, y=300)
        self.entry_email.grid(row=2, column=1)
        self.entry_email.place(x=350, y=340)
        enter.grid()
        enter.place(x=330, y=410)
        enter.place(x=330, y=410)
        cancel.grid()
        cancel.place(x=330, y=450)

    def handle(self, event=None):
        # acquire args
        name = self.entry_name.get()
        passW = self.entry_password.get()
        email = self.entry_email.get()
        self.entry_name.delete(0, END)
        self.entry_password.delete(0, END)
        self.entry_email.delete(0, END)
        # checks if valid
        if len(name) < 3 or len(passW) < 3 or str(email[-10:]) != "@gmail.com":
            pop_up_message('name and password must be at least 3 characters and email address must end with @gmail.com')
        # add to database unless name is already used
        else:
            success = clients_server.register(name, passW, email)
            if success:
                # pop_up_message('added to database')
                self.controller.frames[Login].enter(name, passW, email)
            else:
                pop_up_message('username already used')

    def cancel(self):
        self.controller.show_frame(StartPage)


if __name__ == '__main__':
    app = App()
    app.mainloop()
