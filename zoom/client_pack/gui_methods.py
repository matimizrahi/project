from tkinter import *
import time


def pop_up_message(text):
    win = Tk()
    center_window(win, height=100)
    Label(win, text=text).pack()
    win.update()
    time.sleep(1.5)
    win.destroy()


def center_window(root, width=800, height=550):
    # get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))


if __name__ == '__main__':
    pop_up_message('hi')
