#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# GUI module generated by PAGE version 6.0.1
#  in conjunction with Tcl version 8.6
#    Feb 6, 2021 18:47:51 AM +0200  platform: Windows NT

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

import start_menu_support


def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    top = myProject (root)
    start_menu_support.init(root, top)
    root.mainloop()


w = None


def create_myProject(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_myProject(root, *args, **kwargs)' .'''
    global w, w_win, root
    #rt = root
    root = rt
    w = tk.Toplevel (root)
    top = myProject (w)
    start_menu_support.init(w, top, *args, **kwargs)
    return (w, top)


def destroy_myProject():
    global w
    w.destroy()
    w = None


class myProject:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'

        top.geometry("600x450+409+183")
        top.minsize(120, 1)
        top.maxsize(1924, 1061)
        top.resizable(1,  1)
        top.title("start menu")
        top.configure(background="#eaeaea")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")

        self.SIGNUP = tk.Button(top)
        self.SIGNUP.place(relx=0.067, rely=0.689, height=78, width=238)
        self.SIGNUP.configure(activebackground="#ececec")
        self.SIGNUP.configure(activeforeground="#000000")
        self.SIGNUP.configure(background="#fd8285")
        self.SIGNUP.configure(command=start_menu_support.startSigninPage)
        self.SIGNUP.configure(disabledforeground="#a3a3a3")
        self.SIGNUP.configure(font="-family {Segoe UI} -size 19 -weight bold")
        self.SIGNUP.configure(foreground="#000000")
        self.SIGNUP.configure(highlightbackground="#d9d9d9")
        self.SIGNUP.configure(highlightcolor="black")
        self.SIGNUP.configure(pady="0")
        self.SIGNUP.configure(text='''sign up''')

        self.LOGIN = tk.Button(top)
        self.LOGIN.place(relx=0.483, rely=0.689, height=78, width=258)
        self.LOGIN.configure(activebackground="#ececec")
        self.LOGIN.configure(activeforeground="#000000")
        self.LOGIN.configure(background="#ffcecf")
        self.LOGIN.configure(command=start_menu_support.startLoginPage)
        self.LOGIN.configure(disabledforeground="#a3a3a3")
        self.LOGIN.configure(font="-family {Segoe UI} -size 19")
        self.LOGIN.configure(foreground="#000000")
        self.LOGIN.configure(highlightbackground="#d9d9d9")
        self.LOGIN.configure(highlightcolor="black")
        self.LOGIN.configure(pady="0")
        self.LOGIN.configure(text='''log in''')

        @staticmethod
        def popup1(event, *args, **kwargs):
            Popupmenu1 = tk.Menu(root, tearoff=0)
            Popupmenu1.configure(activebackground="#f9f9f9")
            Popupmenu1.configure(activeborderwidth="1")
            Popupmenu1.configure(activeforeground="black")
            Popupmenu1.configure(background="#d9d9d9")
            Popupmenu1.configure(borderwidth="1")
            Popupmenu1.configure(disabledforeground="#a3a3a3")
            Popupmenu1.configure(font="-family {Segoe UI} -size 9")
            Popupmenu1.configure(foreground="black")
            Popupmenu1.post(event.x_root, event.y_root)


        self.menubar = tk.Menu(top,font="TkMenuFont",bg=_bgcolor,fg=_fgcolor)
        top.configure(menu = self.menubar)

        self.Frame1 = tk.Frame(top)
        self.Frame1.place(relx=0.133, rely=0.089, relheight=0.522
                , relwidth=0.692)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(background="#c9c9c9")
        self.Frame1.configure(highlightbackground="#dcdcdc")
        self.Frame1.configure(highlightcolor="black")

        self.TITLE = tk.Message(self.Frame1)
        self.TITLE.place(relx=0.133, rely=0.153, relheight=0.345, relwidth=0.747)

        self.TITLE.configure(background="#c9c9c9")
        self.TITLE.configure(font="-family {Arial} -size 24 -weight bold -slant italic")
        self.TITLE.configure(foreground="#2c9ffe")
        self.TITLE.configure(highlightbackground="#d9d9d9")
        self.TITLE.configure(highlightcolor="black")
        self.TITLE.configure(text='''ZOOM''')
        self.TITLE.configure(width=235)

        self.ABOUT = tk.Button(self.Frame1)
        self.ABOUT.place(relx=0.267, rely=0.617, height=48, width=188)
        self.ABOUT.configure(activebackground="#ececec")
        self.ABOUT.configure(activeforeground="#000000")
        self.ABOUT.configure(background="#82bdff")
        self.ABOUT.configure(disabledforeground="#a3a3a3")
        self.ABOUT.configure(font="-family {Segoe UI} -size 15")
        self.ABOUT.configure(foreground="#000000")
        self.ABOUT.configure(highlightbackground="#d9d9d9")
        self.ABOUT.configure(highlightcolor="black")
        self.ABOUT.configure(pady="0")
        self.ABOUT.configure(text='''about section''')


if __name__ == '__main__':
    vp_start_gui()




