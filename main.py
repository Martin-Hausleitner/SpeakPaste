# main.py
import tkinter as tk
from transcriber_app import TranscriberApp

def main():
    root = tk.Tk()
    app = TranscriberApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
