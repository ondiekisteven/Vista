import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from controller_window import ControllerWindow, resource_path
from output import OutputWindow


app = QApplication(sys.argv)
app.setWindowIcon(QIcon(str(resource_path("assets/icon.ico"))))

output = OutputWindow()

controller = ControllerWindow(output)

controller.show()

output.show()

sys.exit(app.exec())