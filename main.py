import sys
import pyodbc
import bcrypt
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
#from PyQt5.QtWidgets import QDialog, QApplication, QWidget

class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui", self)
        self.login.clicked.connect(self.loginfunction)

    def loginfunction(self):
        username = self.usernamefield.text()
        password = self.passwordfield.text()

        if len(username) == 0 or len(password) == 0:
           self.error.setText("Please input all fields.")

        else: 
            
            try:
                # Set up the connection string
                server = 'DESKTOP-IF3PE1I\\SQLEXPRESS01'
                database = 'RattlerBank'
                SS_username = 'DESKTOP-IF3PE1I\\andys'
                SS_password = ''
                driver = '{ODBC Driver 17 for SQL Server}'
                connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;"

                # Connect to the database
                conn = pyodbc.connect(connection_string)

                # Create a cursor
                cursor = conn.cursor()

                # Execute a query
                query = "SELECT Password FROM Employee WHERE Username = ?"
                cursor.execute(query, username)

                # Fetch the results
                result_pass = cursor.fetchone()[0]
                if result_pass == password:
                    print("Successfully logged in.")
                    self.error.setText("")
                else:
                    self.error.setText("Invalid username or password.")
                    
                # Close the cursor and connection
                cursor.close()
                conn.close()

                # Print the results
                print(result_pass)

            except pyodbc.Error as e:
                # Handle any errors that occur during the connection or query execution
                print(f"Error: {str(e)}")
                self.error.setText("Invalid login credentials.")           


# main
app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget = QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
