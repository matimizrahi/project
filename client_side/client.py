from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from threading import Thread, enumerate, active_count
import time
from winsound import PlaySound, SND_LOOP, SND_ASYNC, SND_PURGE
from client_side.gui_methods import center_window, pop_up_message
from client_side import chat_call_server
from client_side.connect_call_server import Audio

username = '*'


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        app.destroy()
        chat_call_server.user_left(username)


class App(Tk):
    background = r"..\client_side\background.png"

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title('computer call')
        # Setup Frame
        self.container = Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.username = '*'
        self.target = ''
        self.user_called = ''
        self.frames = {}
        self.sp_background = PhotoImage(file=App.background)
        self.create_frames()
        center_window(self)
        self.show_frame(StartPage)
        # The following three commands are needed so the window pops
        # up on top on Windows...
        self.iconify()
        self.update()
        self.deiconify()

    def create_frames(self):
        for F in (StartPage, Login, Register, Main, Dialing, Ringing, Call):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, context):
        frame = self.frames[context]
        frame.tkraise()
    # creates the pages and shows them


# call page
class Call(Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        background_label = Label(self, image=controller.sp_background)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.msg = Label(self, font=('Ariel', 20), foreground='black')
        self.msg.pack()
        Button(self, text='end call', command=self.stop_call).pack()

    def stop_call(self):
        chat_call_server.stop(self.controller.username, 'call')

    def start_call(self):
        self.client = Audio()  # i have to start it here because i want to create a new socket when a call is made
        # otherwise i will be trying to connect to a closed socket
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
            if not chat_call_server.is_in_call(self.controller.username):
                self.client.end()
                self.controller.show_frame(Main)
                time.sleep(0.4)
                self.controller.frames[Ringing].start_checking()
                break


# main page- after login
class Main(Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        background_label = Label(self, image=controller.sp_background)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.users = Listbox(self, fg='black', font=('Ariel', 12))
        self.target_name = Entry(self, font=('Ariel', 12))
        self.controller = controller
        #        self.set()
        self.set_users_list()
        self.users.place(x=50, y=90)
        self.target_name.place(x=470, y=230)

        #    def set(self):
        Label(self, text='Call to', font=('Ariel', 20), foreground='black').place(x=520, y=170)
        # self.target_name.pack()
        Button(self, text='Call', command=self.pre_call).place(x=520, y=280)
        Label(self, text='Users', font=('Ariel', 18), foreground='black').place(x=100, y=50)
        # self.users.pack()
        self.users.bind('<<ListboxSelect>>', self.to_entry)
        self.bind('<Return>', self.pre_call)
        self.target_name.focus_set()

    # create list of users
    def set_users_list(self):
        self.users.delete(0, END)
        users = chat_call_server.active_user_lists()
        for user in users:
            if user != self.controller.username:
                self.users.insert(END, user)
        if self.users.size() < 20:
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
            if not chat_call_server.is_user(target, "Active"):
                pop_up_message(f"sorry, the user {target} is not active right now")
            elif chat_call_server.is_user(target, "User"):  # checks if the user exists
                self.controller.target = target
                self.controller.show_frame(Dialing)
                self.controller.frames[Dialing].call()
            else:
                pop_up_message(f"sorry, the user {target} is not registered yet")
        elif len(target) < 3:
            pop_up_message('sorry, the name is too short, at least 3 characters')
        else:
            pop_up_message("you can't call yourself")


# waiting for a call to be answered page
class Dialing(Frame):
    ring = r"..\client_side\dialing.wav"

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.cancel = False
        background_label = Label(self, image=controller.sp_background)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.label = Label(self, font=('Ariel', 20), foreground='black')
        self.label.pack()
        Button(self, text='Cancel Call', command=self.stop_calling).pack()

    def call(self):
        self.label['text'] = f'Calling {self.controller.target}...'
        Thread(target=self.dialing, name='dialing', daemon=True).start()

    # cancels call
    def stop_calling(self):
        chat_call_server.stop(self.controller.username, 'dialing')
        self.cancel = True

    # checks if target agreed to chat
    def answer(self, timeout=1):
        max_time = time.time() + 60 * timeout  # 1 minutes from now
        # check if 'dialing' changed to 'call'
        PlaySound(Dialing.ring, SND_LOOP + SND_ASYNC)
        while True:
            time.sleep(1)
            if self.cancel:
                result = 'canceled'
                break
            if time.time() > max_time:
                result = 'timed_out'
                break
            if chat_call_server.is_in_call(self.controller.username):
                result = 'accepted'
                break
            if not chat_call_server.not_rejected(self.controller.username, self.controller.target):
                result = 'rejected'
                break
        PlaySound(None, SND_PURGE)
        return result

    # calls and handle the call
    def dialing(self):
        is_posted = chat_call_server.call(self.controller.username, self.controller.target)
        if is_posted:
            result = self.answer(1)
            if result == 'accepted':
                self.controller.show_frame(Call)
                self.controller.frames[Call].start_call()
            else:
                self.controller.show_frame(Main)
                if result == 'timed_out':  # waited too long for response from the call target
                    pop_up_message("call canceled, didn't receive answer in time")
                elif result == 'canceled':
                    self.cancel = False
                elif result == 'rejected':
                    pop_up_message("call rejected")

        else:  # error, call already exists, handling
            chat_call_server.stop(self.controller.username, 'dialing')
            self.dialing()


# receiving a call page
class Ringing(Frame):
    sound = r"..\client_side\ring.wav"

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        background_label = Label(self, image=controller.sp_background)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.text1 = Label(self, font=('Ariel', 20), foreground='black')
        self.text1.pack()
        self.bind('<Return>', self.yes)
        yes = Button(self, text='yes', command=self.yes)
        yes.focus_set()
        yes.pack()
        Button(self, text='no', command=self.no).pack()

    def start_checking(self):
        Thread(target=self.ringing, name='ringing', daemon=True).start()

    def ringing(self):
        while True:
            if chat_call_server.look_for_call(self.controller.username):
                self.controller.show_frame(Ringing)
                user = chat_call_server.get_src_name(self.controller.username)
                self.controller.user_called = user
                self.text1['text'] = f'you got a call from {user}\ndo you want to answer'
                PlaySound(Ringing.sound, SND_LOOP + SND_ASYNC)
                break
            if chat_call_server.is_in_call(self.controller.username):  # when dialing and call was approved
                break
            time.sleep(1)

    def yes(self):
        PlaySound(None, SND_PURGE)
        successful = chat_call_server.accept(self.controller.user_called, self.controller.username)
        if successful == 'True':
            time.sleep(0.5)
            self.controller.show_frame(Call)
            self.controller.frames[Call].start_call()
        else:
            pop_up_message('call was canceled')
            chat_call_server.stop(self.controller.username, 'dialing')
            self.controller.show_frame(Main)
            self.start_checking()

    def no(self):
        """ is this how i wanna handle that? the caller doesn't check if we canceled"""
        # if clients_server.get_call_list.query.filter_by(src=self.controller.username).first():
        PlaySound(None, SND_PURGE)
        chat_call_server.stop(self.controller.username, 'dialing')
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
        Button(self, text='sign up', width=30, command=lambda: controller.show_frame(Register)).place(x=400, y=350)


# login page
class Login(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        background_label = Label(self, image=controller.sp_background)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.controller = controller
        Label(self, text='this is the login page', font="-family {Segoe UI} -size 20 -weight bold",
              foreground='black').place(x=220, y=100)
        Label(self, text='enter your username and password', font="-family {Segoe UI} -size 20",
              foreground='black').place(x=150, y=150)
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

    def enter(self, name, passW, is_login):
        is_connected = chat_call_server.login(name, passW)
        if is_connected == 'True':
            self.controller.username = name
            global username
            username = name
            if is_login:
                pop_up_message(f"welcome back, {name}")
            else:
                pop_up_message(f"welcome, {name}")
            self.controller.create_frames()
            self.controller.show_frame(Main)
            self.controller.frames[Ringing].start_checking()
        elif is_connected == 'False':
            self.entry_name.delete(0, END)
            self.entry_passW.delete(0, END)
            pop_up_message("name or password is incorrect")
        else:
            self.entry_name.delete(0, END)
            self.entry_passW.delete(0, END)
            pop_up_message("the user that goes by that username is already connected")

    def collect(self):
        name = self.entry_name.get()
        passW = self.entry_passW.get()
        self.enter(name, passW, True)

    def cancel(self):
        self.controller.show_frame(StartPage)


# register page
class Register(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        background_label = Label(self, image=controller.sp_background)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.controller = controller
        Label(self, text='this is the registration page', font="-family {Segoe UI} -size 20 -weight bold",
              foreground='black').place(x=220, y=100)
        Label(self, text='enter your desired username and password and enter your email',
              font="-family {Segoe UI} -size 20", foreground='black').place(x=20, y=150)
        self.entry_name = Entry(self)
        self.entry_password = Entry(self)
        self.entry_email = Entry(self)
        name = Label(self, text='Name', font="-family {Segoe UI} -size 12")
        passW = Label(self, text='Password', font="-family {Segoe UI} -size 12")
        email = Label(self, text='email', font="-family {Segoe UI} -size 12")
        enter = Button(self, text='Register', command=self.handle)
        cancel = Button(self, text='Cancel', command=self.controller.frames[Login].cancel)
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

    #   checks if yhe entered values are valid and calls for clients_server.register to enter into the database
    def handle(self, event=None):
        name = self.entry_name.get()
        pass_w = self.entry_password.get()
        email = self.entry_email.get()
        self.entry_name.delete(0, END)
        self.entry_password.delete(0, END)
        self.entry_email.delete(0, END)
        # checks if valid
        if len(name) < 3 or len(pass_w) < 3 or str(email[-10:]) != "@gmail.com":
            pop_up_message('name and password must be at least 3 characters and email address must end with @gmail.com')
        # add to database unless name is already used
        else:
            success = chat_call_server.register(name, pass_w, email)
            if success:
                # pop_up_message('added to database')
                self.controller.frames[Login].enter(name, pass_w, False)
            else:
                pop_up_message('username already used')


if __name__ == '__main__':
    app = App()
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()
