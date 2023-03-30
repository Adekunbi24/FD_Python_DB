import sys
import pyodbc
import bcrypt
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *

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
                driver = '{ODBC Driver 17 for SQL Server}'
                connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;"

                # Connect to the database
                conn = pyodbc.connect(connection_string)

                # Create a cursor
                cursor = conn.cursor()

                # Execute a query to retrieve the hashed password from the database
                query = "SELECT Password FROM Employee WHERE Username = ?"
                cursor.execute(query, username)

                # Fetch the results
                result_pass = cursor.fetchone()
                if result_pass is not None:
                    hashed_password = result_pass[0].encode('utf-8')
                    # Use bcrypt library to check if the password matches
                    if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                        print("Successfully logged in.")
                        self.error.setText("")
                    else:
                        self.error.setText("Invalid username or password.")
                else:
                    self.error.setText("Invalid username or password.")
                    
                # Close the cursor and connection
                cursor.close()
                conn.close()

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
