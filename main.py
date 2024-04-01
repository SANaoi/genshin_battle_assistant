# -*- coding: utf-8 -*-

import os
import sys

from PyQt5.QtWidgets import QApplication

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_PATH)
os.chdir(ROOT_PATH)

from source.app_core import CountdownApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CountdownApp()
    window.show()
    sys.exit(app.exec_())