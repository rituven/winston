import sys
from PyQt4.QtGui import *
#from PyQt4.QtWidgets import *
from PyQt4.QtCore import *
from core.Messenger import *
from core.Events import *
from alexa import AlexaService

class QTApp(QWidget):
 
    def __init__(self):
        super(QWidget, self).__init__()
        self.title = 'Winston'
        self.setWindowTitle(self.title)
        self.setGeometry(100,100,800,400)
        self.btn = QPushButton('', self)
        self.alexaService = AlexaService()
        self.messenger = getMessenger()
        self.initUI()
 
    def initUI(self):
        b = QLabel(self)
        b.setText("Hi, I am Winston. How can I help you?")
        b.move(50,40)
        self.btn.setCheckable(True)
        self.btn.setIcon(QIcon('media/Alexa_passive.jpg'))
        self.btn.setIconSize(QSize(150,150))
        self.btn.setObjectName("Alexa")
        self.btn.move(100,70)
        self.btn.pressed.connect(self.on_press)
        self.btn.released.connect(self.on_release)
        self.btn.clicked.connect(self.on_click)
 
        self.show()
 
    @pyqtSlot()
    def on_click(self):
        sending_button = self.sender()
        data = {'App': str(sending_button.objectName())}
        self.messenger.postEvent(Events.UI_BTN_CLICKED, data)
 
    @pyqtSlot()
    def on_press(self):
        sending_button = self.sender()
        data = {'App': str(sending_button.objectName())}
        self.btn.setIcon(QIcon('media/Alexa_active.jpg'))
        self.btn.setCheckable(False);
        self.messenger.postEvent(Events.UI_BTN_PRESSED, data)
 
    @pyqtSlot()
    def on_release(self):
        sending_button = self.sender()
        data = {'App': str(sending_button.objectName())}
        self.btn.setIcon(QIcon('media/Alexa_passive.jpg'))
        self.btn.setCheckable(True);
        self.messenger.postEvent(Events.UI_BTN_RELEASED, data)
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QTApp()
    app.exec_()
    delMessenger()
    sys.exit()

