from tkinter import *
from tkinter import ttk


class BrainAligner:

    def __init__(self, master):

        self.label = ttk.Label(master, text="First")
        self.label.grid(row=0, column=0, columnspan=2)

        self.button = ttk.Button(master, text="Italian")
        self.button.grid()
        button.pack()


def main():
    root = Tk()
    app = BrainAligner(root)
    root.mainloop()

if __name__ == "__main__": main()
