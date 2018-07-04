
import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import *

import matplotlib
matplotlib.use("Qt5Agg")

from interface import MainApp
from optimization import Optimizer


def yesno_input(question):
    answer = input(question)
    while answer not in ["y", "n"]:
        print("Sorry, what did you say? ")
        answer = input(question)
    return answer


app = QApplication(sys.argv)

app.processEvents()

ex = MainApp()
ex.setFocus()
app.exec_()

ex.close()

# initializes the optimizer class
OPT = Optimizer(ex.config, ex.config_conf, ex.config_sted, autoquality=ex.autoquality, autopref=ex.autopref, thrash_data=ex.thrash_data)
# run the optimization routine
more_regions = True
readjust = False
while more_regions:
    OPT.run(readjust)
    answer = yesno_input("Do you want to select more regions and continue? (y/n) ")
    more_regions = (answer == "y")
    if more_regions:
        answer = yesno_input("Do you want to readjust focus parameters? (y/n) ")
        readjust = (answer == "y")
