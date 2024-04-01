import os
import sys
import json

from PyQt5.QtWidgets import QApplication, QLabel, QDialog, QWidget, QVBoxLayout
from PyQt5.QtGui import QFont, QFontDatabase, QFontMetrics, QPen, QColor, QPainterPath

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
os.chdir(ROOT_PATH)

SOURCE_PATH = ROOT_PATH + "\\source"
CONFIG_PATH = ROOT_PATH + "\\config"

def load_json(json_name: str) -> dir:
    json_path = CONFIG_PATH + "\\" + json_name
    try:
        return json.load(open(json_path, "r", encoding="utf-8"))
    except:
        raise FileNotFoundError(json_name)
    
def qt5_set_font():
    # 设置字体
    font_id = QFontDatabase.addApplicationFont("fonts\舟方日明体斜体.otf")
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    font = QFont(font_family)
    font.setBold(1000-7)
    font.setPointSize(16)
    # 字体描边
    metrics = QFontMetrics(font)
    pen = QPen(QColor(255, 255, 255))
    path = QPainterPath()
    penwidth = 2

    pen.setWidth(penwidth)
    print(path)

    return font


class SecondWindow(QDialog):
    def __init__(self, message="error", info='?'):
        super().__init__()
        font = qt5_set_font()
        self.setFont(font)

        self.message = message
        self.info = info

        self.setWindowTitle(self.message)
        self.setGeometry(200, 200, 300, 200)
        self.central_widget = QWidget(self) 
        self.label = QLabel(self)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.label)

        self.init_ui()
    def init_ui(self):
        self.label.setText(f"{self.info}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = SecondWindow(info="原神")
    mainWindow.show()
    sys.exit(app.exec_())

