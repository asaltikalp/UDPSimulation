import random
from time import sleep
import tkinter as tk
from tkinter import ttk

mode = 'auto'  # auto or manual


def delayRandomTime():
    sleep(random.randint(0, 4))

