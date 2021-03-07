#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# GUI module generated by PAGE version 6.0.1
#  in conjunction with Tcl version 8.6
#    Feb 7, 2021 14:06:42 PM +0200  platform: Windows NT

import sys

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

import signup_support


def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    top = SIGNUP (root)
    signup_support.init(root, top)
    root.mainloop()


w = None


def create_SIGNUP(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_SIGNUP(root, *args, **kwargs)' .'''
    global w, w_win, root
    #rt = root
    root = rt
    w = tk.Toplevel (root)
    top = SIGNUP (w)
    signup_support.init(w, top, *args, **kwargs)
    return (w, top)


def destroy_SIGNUP():
    global w
    w.destroy()
    w = None


class SIGNUP:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.configure('.',font="TkDefaultFont")
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        top.geometry("600x450+660+210")
        top.minsize(120, 1)
        top.maxsize(1924, 1061)
        top.resizable(1,  1)
        top.title("Sign Up")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")

        self.TITLE = tk.Message(top)
        self.TITLE.place(relx=0.0, rely=0.133, relheight=0.189, relwidth=0.998)
        self.TITLE.configure(background="#fd8285")
        self.TITLE.configure(font="-family {Segoe UI} -size 24 -weight bold")
        self.TITLE.configure(foreground="#000000")
        self.TITLE.configure(highlightbackground="#d9d9d9")
        self.TITLE.configure(highlightcolor="black")
        self.TITLE.configure(text='''creat a new account''')
        self.TITLE.configure(width=599)

        self.USERNAME = tk.Label(top)
        self.USERNAME.place(relx=0.167, rely=0.467, height=23, width=167)
        self.USERNAME.configure(activebackground="#f9f9f9")
        self.USERNAME.configure(activeforeground="black")
        self.USERNAME.configure(background="#d9d9d9")
        self.USERNAME.configure(disabledforeground="#a3a3a3")
        self.USERNAME.configure(font="-family {Segoe UI} -size 14 -weight bold")
        self.USERNAME.configure(foreground="#000000")
        self.USERNAME.configure(highlightbackground="#d9d9d9")
        self.USERNAME.configure(highlightcolor="black")
        self.USERNAME.configure(text='''enter username:''')

        self.Entry_username = tk.Entry(top)
        self.Entry_username.place(relx=0.55, rely=0.467, height=21
                , relwidth=0.24)
        self.Entry_username.configure(background="white")
        self.Entry_username.configure(disabledforeground="#a3a3a3")
        self.Entry_username.configure(font="TkFixedFont")
        self.Entry_username.configure(foreground="#000000")
        self.Entry_username.configure(highlightbackground="#d9d9d9")
        self.Entry_username.configure(highlightcolor="black")
        self.Entry_username.configure(insertbackground="black")
        self.Entry_username.configure(selectbackground="blue")
        self.Entry_username.configure(selectforeground="white")

        self.menubar = tk.Menu(top,font="TkMenuFont",bg=_bgcolor,fg=_fgcolor)
        top.configure(menu = self.menubar)

        self.PASSWORD = tk.Label(top)
        self.PASSWORD.place(relx=0.167, rely=0.644, height=23, width=167)
        self.PASSWORD.configure(activebackground="#f9f9f9")
        self.PASSWORD.configure(activeforeground="black")
        self.PASSWORD.configure(background="#d9d9d9")
        self.PASSWORD.configure(disabledforeground="#a3a3a3")
        self.PASSWORD.configure(font="-family {Segoe UI} -size 14 -weight bold")
        self.PASSWORD.configure(foreground="#000000")
        self.PASSWORD.configure(highlightbackground="#d9d9d9")
        self.PASSWORD.configure(highlightcolor="black")
        self.PASSWORD.configure(text='''enter password:''')

        self.Entry_password = tk.Entry(top)
        self.Entry_password.place(relx=0.55, rely=0.644, height=21
                                  , relwidth=0.24)
        self.Entry_password.configure(background="white")
        self.Entry_password.configure(disabledforeground="#a3a3a3")
        self.Entry_password.configure(font="TkFixedFont")
        self.Entry_password.configure(foreground="#000000")
        self.Entry_password.configure(highlightbackground="#d9d9d9")
        self.Entry_password.configure(highlightcolor="black")
        self.Entry_password.configure(insertbackground="black")
        self.Entry_password.configure(selectbackground="blue")
        self.Entry_password.configure(selectforeground="white")

        self.CANCEL = ttk.Button(top)
        self.CANCEL.place(relx=0.183, rely=0.8, height=27, width=87)
        self.CANCEL.configure(takefocus="")
        self.CANCEL.configure(text='''cancel''')
        self.CANCEL.configure(command=signup_support.cancel_startMenu)

        self.error_label = tk.Label(top)
        self.error_label.place(relx=0.083, rely=0.378, height=23, width=467)
        self.error_label.configure(activebackground="#d9d9d9")
        self.error_label.configure(activeforeground="black")
        self.error_label.configure(background="#d9d9d9")
        self.error_label.configure(disabledforeground="#a3a3a3")
        self.error_label.configure(font="-family {Tw Cen MT} -size 14 -weight bold")
        self.error_label.configure(foreground="red")
        self.error_label.configure(highlightbackground="#d9d9d9")
        self.error_label.configure(highlightcolor="black")
        self.error_label.configure(text="")

        self.SIGNUPBUTTON = tk.Button(top)
        self.SIGNUPBUTTON.place(relx=0.433, rely=0.778, height=48, width=168)
        self.SIGNUPBUTTON.configure(activebackground="#ececec")
        self.SIGNUPBUTTON.configure(activeforeground="#000000")
        self.SIGNUPBUTTON.configure(background="#fd8285")
        self.SIGNUPBUTTON.configure(disabledforeground="#a3a3a3")
        self.SIGNUPBUTTON.configure(font="-family {Segoe UI} -size 14 -weight bold")
        self.SIGNUPBUTTON.configure(foreground="#000000")
        self.SIGNUPBUTTON.configure(highlightbackground="#d9d9d9")
        self.SIGNUPBUTTON.configure(highlightcolor="black")
        self.SIGNUPBUTTON.configure(pady="0")
        self.SIGNUPBUTTON.configure(text='''sign up''')
        self.SIGNUPBUTTON.configure(command=signup_support.register)


if __name__ == '__main__':
    vp_start_gui()




