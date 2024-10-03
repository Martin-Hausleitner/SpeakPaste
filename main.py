# main.py
import tkinter as tk
from transcriber_app import TranscriberApp
import faulthandler
import logging

def main():
    # Aktivieren des Fault Handlers
    faulthandler.enable()

    # Konfiguration des Loggings
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    root = tk.Tk()
    app = TranscriberApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
