from tkinter import *
from tkinter import ttk


class BrainAlignerGUI:

    def __init__(self, root):

        self.root = root

        # Create frames
        self.frame1 = ttk.Frame(root).config(width=1000, height=1000, relief="RIDGE")  # Images
        self.frame2 = ttk.Frame(root).config(width=200, height=500, relief="RIDGE")  # Buttons
        self.frame3 = ttk.Frame(root).config(width=200, height=500, relief="RIDGE")  # Log

        # Place frames using the grid layout manager
        self.frame1.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.frame2.grid(row=0, column=1, sticky="nsew")
        self.frame3.grid(row=1, column=1, sticky="nsew")

        # Configure row and column weights to make the frames resize properly
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Frame0 contains the plots
        self.frame0 = ttk.Frame(master).config(height=1000, width=1000, relief="RIDGE")

        # Frame1 contains the buttons to control the application execution
        self.frame1 = ttk.Frame(master).config(relief="RIDGE")
        ttk.Button(self.frame1, text="Load", command=self.load_data()).grid(row=0, column=0)
        ttk.Button(self.frame1, text="Register Atlas", command=self.register_atlas()).grid(row=1, column=0)
        ttk.Button(self.frame1, text="Register MRIs", command=self.register_mris()).grid(row=2, column=0)
        ttk. #  to set the radius of the brain mask constraint

    def register_atlas(self):
        self.label.config(text="Uno")

    def register_mris(self):
        self.label.config(text="Eins")

    def load_data(self):
        print("wip")

def main():
    root = Tk()
    app = BrainAlignerGUI(root)
    root.mainloop()


if __name__ == "__main__": main()
