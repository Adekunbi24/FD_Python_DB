

import sys
import pyodbc
import bcrypt
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *

class createcustomer(QDialog):
    def __init__(self):
        super(createcustomer, self).__init__()
        loadUi("CreateCustomer.ui", self)
        self.tabWidget.currentChanged.connect(self.tabChanged)
        self.tabWidget.setTabText(0, "Create")
        self.tabWidget.setTabText(1, "View")
        #self.Create.clicked.connect(self.Createfunction)

    def tabChanged(self):
        print("tab was changed to", self.tabWidget.currentIndex())

    
    def Createfunction(self):
        ID = self.customerID.text().toInt()
        FirstName = self.customerID.text()

                   

# main
app = QApplication(sys.argv)
welcome = createcustomer()
widget = QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")


