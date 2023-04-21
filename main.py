import sys
import pyodbc
import bcrypt
import os, re
import time
import datetime
from PyQt5.QtCore import QDate
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *
from PyQt5.QtCore import QTimer

class DBConnection:
    def __init__(self):
        # Set up the connection string
        server = 'DESKTOP-IF3PE1I\\SQLEXPRESS01'
        database = 'RattlerBank'
        driver = '{ODBC Driver 17 for SQL Server}'
        self.connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;"

    def get_connection(self):
        return pyodbc.connect(self.connection_string)

class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui", self)
        self.db_connection = DBConnection()
        self.login.clicked.connect(self.loginfunction)

    def gotodashboard(self, first_name):
        dashboard = DashboardScreen(first_name, self.db_connection)
        widget.addWidget(dashboard)
        widget.setCurrentIndex(widget.currentIndex()+1 )    

    def loginfunction(self):
        username = self.usernamefield.text()
        first_name = username.split('.')[0]
        first_name = first_name.capitalize()
        password = self.passwordfield.text()

        if len(username) == 0 or len(password) == 0:
           self.error.setText("Please input all fields.")
        else: 
            try:
                # Connect to the database
                conn = self.db_connection.get_connection()
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
                        self.gotodashboard(first_name)
                        self.error.setText("")
                        self.usernamefield.setText("")
                        self.passwordfield.setText("")
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


class DashboardScreen(QDialog):
    def __init__(self, first_name, db_connection):
        super(DashboardScreen, self).__init__()
        loadUi("dashboard.ui", self)
        self.employee_name.setText(f"Welcome, {first_name}")
        self.db_connection = db_connection
        self.search_customer_button.clicked.connect(self.gotosearchcustomer)
        self.acct_services_button.clicked.connect(self.gotoacctservices)
        self.view_acct_button.clicked.connect(self.gotoviewaccount)
        self.transfer_button.clicked.connect(self.gototransfer)
        self.withdrawal_button.clicked.connect(self.gotowithdrawal)
        self.deposit_button.clicked.connect(self.gotodeposit)
        self.logout_button.clicked.connect(self.logout)        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_table)
        self.timer.start(3000) # update every 3 seconds

    def logout(self):
        # Close the current window and return to the dashboard
        self.tableWidget.clearContents()
        self.close()
        widget.removeWidget(self)

    def update_table(self):
        try:
            # Connect to the database
            conn = self.db_connection.get_connection()
            # Create a cursor
            cursor = conn.cursor()

            # Execute a query to retrieve the transactions from the database
            query = """SELECT * FROM Transactions
                       ORDER BY TransactionNo DESC
            """
            cursor.execute(query)

            # Fetch the results
            results = cursor.fetchall()
            print(results)

            # Clear the table widget
            self.tableWidget.setRowCount(0)

            # Iterate over the results and add them to the table widget
            for row_num, row_data in enumerate(results):
                self.tableWidget.insertRow(row_num)
                for col_num, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    self.tableWidget.setItem(row_num, col_num, item)

            # Resize the columns to fit the contents
            self.tableWidget.setColumnWidth(0, 140)
            self.tableWidget.setColumnWidth(1, 130)
            self.tableWidget.setColumnWidth(2, 150)
            self.tableWidget.setColumnWidth(3, 150)
            self.tableWidget.setColumnWidth(4, 140)
            self.tableWidget.setColumnWidth(5, 140)

            # Close the cursor and connection
            cursor.close()
            conn.close()

        except pyodbc.Error as e:
            # Handle any errors that occur during the connection or query execution
            print(f"Error: {str(e)}")

    def gotoacctservices(self):
        acctservices = AccountSerivcesScreen(self.db_connection)
        widget.addWidget(acctservices)
        widget.setCurrentIndex(widget.currentIndex()+1)    
    
    def gotoviewaccount(self):
        viewaccount = ViewAccountScreen(self.db_connection)
        widget.addWidget(viewaccount)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotowithdrawal(self):       
        withdrawal = ViewWithdrawalScreen(self.db_connection)
        widget.addWidget(withdrawal)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotodeposit(self):       
        deposit = ViewDepositScreen(self.db_connection)
        widget.addWidget(deposit)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gototransfer(self):
        transfer = ViewTransferScreen(self.db_connection)
        widget.addWidget(transfer)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotosearchcustomer(self):
        searchcustomer = ViewSearchCustomerScreen(self.db_connection)
        widget.addWidget(searchcustomer)
        widget.setCurrentIndex(widget.currentIndex()+1)        

class ViewAccountScreen(QDialog):
    def __init__(self, db_connection):
        super(ViewAccountScreen, self).__init__()
        loadUi("viewaccount.ui", self)
        self.db_connection = db_connection

        # Connect the acct_search_button to the acct_search function
        self.acct_search_button.clicked.connect(self.acct_search)

        # Connect the close_button to the close_screen function
        self.close_button.clicked.connect(self.close_screen)

    def close_screen(self):
        # Close the current window and return to the dashboard
        self.close()
        widget.removeWidget(self)

    def acct_search(self):
        account_num = self.acct_search_field.text()

        #clear search fields
        self.error.setText("")
        self.account_num.setText("")
        self.account_type.setText("")
        self.branch_num.setText("")
        self.open_date.setText("")
        self.balance.setText("")
        self.customer_name.setText("")
        self.customer_ID.setText("")

        # Clear transaction information
        self.ctrans_table_Widget.clearContents()
        self.ctrans_table_Widget.setRowCount(0)

        # Check if the account number field is empty
        if not account_num:
            self.error.setText("Please enter an account number.")
            return

        # Check if the account number is all digits and less than 10 digits
        if not account_num.isdigit() or len(account_num) > 10:
            self.error.setText("Invalid account number. Please try again.")
            return

        try:
            # Connect to the database
            conn = self.db_connection.get_connection()
            # Create a cursor
            cursor = conn.cursor()

            # Execute the query to get account information
            query = f"""
                SELECT Account.AccountNo, Account.CustomerID, Account.AcctType, Account.BranchNo, 
                    Account.OpenDate, Account.CurrentBalance, Customer.Fname, Customer.Lname
                FROM Account
                INNER JOIN Customer ON Account.CustomerID = Customer.CustomerID
                WHERE Account.AccountNo = ?
            """
            cursor.execute(query, account_num)

            # Get the account information
            account_info = cursor.fetchone()

            if account_info:
                # Display the account information
                self.error.setText("")
                self.account_num.setText(str(account_info[0]))
                self.account_type.setText(account_info[2])
                self.branch_num.setText(str(account_info[3]))
                self.open_date.setText(str(account_info[4]))
                self.balance.setText(str(account_info[5]))
                self.customer_name.setText(f"{account_info[6].capitalize()} {account_info[7].capitalize()}")
                self.customer_ID.setText(str(account_info[1]))

                # Execute the query to get transaction information
                query = """
                    SELECT TransactionNo, AcctNo, TransactionDate, TransactionType, TransactionAmt, UpdatedBalance
                    FROM Transactions
                    WHERE AcctNo = ?
                    ORDER BY TransactionNo DESC
                """
                cursor.execute(query, account_num)

                # Get the transaction information
                transactions = cursor.fetchall()

                # Display the transaction information
                self.ctrans_table_Widget.setRowCount(len(transactions))
                for i, transaction in enumerate(transactions):
                    for j, data in enumerate(transaction):
                        self.ctrans_table_Widget.setItem(i, j, QTableWidgetItem(str(data)))

                            # Resize the columns to fit the contents
                self.ctrans_table_Widget.setColumnWidth(0, 180)
                self.ctrans_table_Widget.setColumnWidth(1, 180)
                self.ctrans_table_Widget.setColumnWidth(2, 180)
                self.ctrans_table_Widget.setColumnWidth(3, 180)
                self.ctrans_table_Widget.setColumnWidth(4, 180)
                self.ctrans_table_Widget.setColumnWidth(5, 180)        

            else:
                # Display error message if account not found
                self.error.setText("Account not found. Please try again.")

            # Close the cursor and connection
            cursor.close()
            conn.close()

        except pyodbc.Error as e:
            # Handle any errors that occur during the connection or query execution
            print(f"Error: {str(e)}")
            self.error.setText("Error occurred while fetching account information.")


class ViewWithdrawalScreen(QDialog):
    def __init__(self, db_connection):
        super(ViewWithdrawalScreen, self).__init__()
        loadUi("withdrawal.ui", self)
        self.db_connection = db_connection

        # Set the current date in the todays_date QLabel object
        self.todays_date.setText(QDate.currentDate().toString())

        # Connect the acct_search_button to the acct_search function
        self.acct_search_button.clicked.connect(self.acct_search)

        # Connect the close_button to the close_screen function
        self.close_button.clicked.connect(self.close_screen)

        # Connect the withdrawal_button to the withdrawal_funds function
        self.withdrawal_button.clicked.connect(self.withdrawal_funds)

    def close_screen(self):
        # Close the current window and return to the dashboard
        self.close()
        widget.removeWidget(self)

    def acct_search(self):
        account_num = self.acct_search_field.text()

        # Check if the account number field is empty
        if not account_num:
            self.error.setText("Please enter an account number.")
            return

        # Check if the account number is all digits and less than 10 digits
        if not account_num.isdigit() or len(account_num) > 10:
            self.error.setText("Invalid account number. Please try again.")
            return

        try:
            # Connect to the database
            conn = self.db_connection.get_connection()
            # Create a cursor
            cursor = conn.cursor()

            # Execute the query to get account information
            query = f"""
                SELECT Account.AccountNo, Account.AcctType, Account.BranchNo, 
                    Account.OpenDate, Account.CurrentBalance, Customer.Fname, Customer.Lname
                FROM Account
                INNER JOIN Customer ON Account.CustomerID = Customer.CustomerID
                WHERE Account.AccountNo = ?
            """
            cursor.execute(query, account_num)

            # Get the account information
            account_info = cursor.fetchone()

            if account_info:
                # Display the account information
                self.error.setText("")
                self.error_2.setText("")
                self.success_msg.setText("")
                self.wd_amt_field.setText("")
                self.confirm_wd_amt_field.setText("")
                self.account_num.setText(str(account_info[0]))
                self.account_type.setText(account_info[1])
                self.branch_num.setText(str(account_info[2]))
                self.open_date.setText(str(account_info[3]))
                self.balance.setText(str(account_info[4]))
                self.customer_name.setText(f"{account_info[5].capitalize()} {account_info[6].capitalize()}")
                self.customer_ID.setText(str(account_info[0]))

            else:
                # Display error message if account not found
                self.error.setText("Account not found. Please try again.")

            # Close the cursor and connection
            cursor.close()
            conn.close()

        except pyodbc.Error as e:
            # Handle any errors that occur during the connection or query execution
            print(f"Error: {str(e)}")
            self.error.setText("Error occurred while fetching account information.")

    def withdrawal_funds(self):
        # Get the withdrawal amount and confirm withdrawal amount
        wd_amt = self.wd_amt_field.text()
        confirm_wd_amt = self.confirm_wd_amt_field.text()

        # Check if the balance field is empty
        if not self.balance.text():
            self.error_2.setText("Please search an account first.")
            return

        # Check if the withdrawal amount field is empty
        if not wd_amt:
            self.error_2.setText("Please enter a withdrawal amount.")
            return

        # Check if the withdrawal amount is a valid number with two decimal places
        try:
            wd_amt = float(wd_amt)
            if not (0 <= wd_amt <= float(self.balance.text())):
                self.error_2.setText("Value exceeds current balance.")
                return
            if not (round(wd_amt, 2) == wd_amt):
                self.error_2.setText("Please enter correct value.")
                return
        except ValueError:
            self.error_2.setText("Please enter a valid withdrawal amount.")
            return

        # Check if the confirm withdrawal amount field is empty
        if not confirm_wd_amt:
            self.error_2.setText("Please confirm the withdrawal amount.")
            return

        # Check if the withdrawal amount matches the confirm withdrawal amount
        if wd_amt != float(confirm_wd_amt):
            self.error_2.setText("Please make sure amounts match.")
            return

        # Get the account number
        account_num = self.account_num.text()

        try:
            # Connect to the database
            conn = self.db_connection.get_connection()
            # Create a cursor
            cursor = conn.cursor()

            # Execute the query to update the account balance
            query = f"""
                UPDATE Account
                SET CurrentBalance = CurrentBalance - ?
                WHERE AccountNo = ?
            """
            cursor.execute(query, (wd_amt, account_num))

            # Commit the transaction
            conn.commit()

            # Update the balance label
            self.balance.setText('{:.2f}'.format(float(self.balance.text()) - wd_amt))
            self.new_balance.setText('{:.2f}'.format(float(self.balance.text())))


            # Display success message
            self.success_msg.setText("Withdrawal successful.")

            # Insert a new row into the Transactions table
            query = f"""
                INSERT INTO Transactions (TransactionNo, AcctNo, TransactionDate, TransactionType, TransactionAmt, UpdatedBalance)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            # Get the current date
            today = datetime.date.today()

            # Get the next transaction number
            query2 = "SELECT MAX(TransactionNo) FROM Transactions"
            cursor.execute(query2)
            max_transaction_no = cursor.fetchone()[0]
            if max_transaction_no is None:
                transaction_no = 1001
            else:
                transaction_no = max_transaction_no + 1
            
            # Set the values for the new row
            values = (transaction_no, account_num, today, "Withdrawal", -wd_amt, float(self.new_balance.text()))
            
            # Execute the query to insert the new row
            cursor.execute(query, values)

            # Commit the transaction
            conn.commit()
                                    
            # Close the cursor and connection
            cursor.close()
            conn.close()

        except pyodbc.Error as e:
            # Handle any errors that occur during the connection or query execution
            print(f"Error: {str(e)}")
            self.error_2.setText("Error occurred while withdrawing funds.")  
    

class ViewDepositScreen(QDialog):
    def __init__(self, db_connection):
        super(ViewDepositScreen, self).__init__()
        loadUi("deposit.ui", self)
        self.db_connection = db_connection

        # Set the current date in the todays_date QLabel object
        self.todays_date.setText(QDate.currentDate().toString())

        # Connect the acct_search_button to the acct_search function
        self.acct_search_button.clicked.connect(self.acct_search)

        # Connect the close_button to the close_screen function
        self.close_button.clicked.connect(self.close_screen)

        # Connect the withdrawal_button to the withdrawal_funds function
        self.deposit_button.clicked.connect(self.deposit_funds)

    def close_screen(self):
        # Close the current window and return to the dashboard
        self.close()
        widget.removeWidget(self)

    def acct_search(self):
        account_num = self.acct_search_field.text()

        # Check if the account number field is empty
        if not account_num:
            self.error.setText("Please enter an account number.")
            return

        # Check if the account number is all digits and less than 10 digits
        if not account_num.isdigit() or len(account_num) > 10:
            self.error.setText("Invalid account number. Please try again.")
            return

        try:
            # Connect to the database
            conn = self.db_connection.get_connection()
            # Create a cursor
            cursor = conn.cursor()

            # Execute the query to get account information
            query = f"""
                SELECT Account.AccountNo, Account.AcctType, Account.BranchNo, 
                    Account.OpenDate, Account.CurrentBalance, Customer.Fname, Customer.Lname
                FROM Account
                INNER JOIN Customer ON Account.CustomerID = Customer.CustomerID
                WHERE Account.AccountNo = ?
            """
            cursor.execute(query, account_num)

            # Get the account information
            account_info = cursor.fetchone()

            if account_info:
                # Display the account information
                self.error.setText("")
                self.error_2.setText("")
                self.success_msg.setText("")
                self.deposit_amt_field.setText("")
                self.confirm_deposit_amt_field.setText("")
                self.account_num.setText(str(account_info[0]))
                self.account_type.setText(account_info[1])
                self.branch_num.setText(str(account_info[2]))
                self.open_date.setText(str(account_info[3]))
                self.balance.setText(str(account_info[4]))
                self.customer_name.setText(f"{account_info[5].capitalize()} {account_info[6].capitalize()}")
                self.customer_ID.setText(str(account_info[0]))

            else:
                # Display error message if account not found
                self.error.setText("Account not found. Please try again.")

            # Close the cursor and connection
            cursor.close()
            conn.close()

        except pyodbc.Error as e:
            # Handle any errors that occur during the connection or query execution
            print(f"Error: {str(e)}")
            self.error.setText("Error occurred while retreiving account information.")

    def deposit_funds(self):
        # Get the deposit amount and confirm withdrawal amount
        deposit_amt = self.deposit_amt_field.text()
        confirm_deposit_amt = self.confirm_deposit_amt_field.text()

        # Check if the balance field is empty
        if not self.balance.text():
            self.error_2.setText("Please search an account first.")
            return

        # Check if the deposit amount field is empty
        if not deposit_amt:
            self.error_2.setText("Please enter a deposit amount.")
            return

        # Check if the deposit amount is a valid number with two decimal places
        try:
            deposit_amt = float(deposit_amt)
            if not (0 < deposit_amt):
                self.error_2.setText("Value must be greater than $0.00.")
                return
            if not (round(deposit_amt, 2) == deposit_amt):
                self.error_2.setText("Please enter correct value.")
                return
        except ValueError:
            self.error_2.setText("Please enter a valid deposit amount.")
            return

        # Check if the confirm deposit amount field is empty
        if not confirm_deposit_amt:
            self.error_2.setText("Please confirm the deposit amount.")
            return

        # Check if the withdrawal amount matches the confirm withdrawal amount
        if deposit_amt != float(confirm_deposit_amt):
            self.error_2.setText("Please make sure amounts match.")
            return
        
        # Clear error message
        self.error_2.setText("")        
        
        # Get the account number
        account_num = self.account_num.text()

        try:
            # Connect to the database
            conn = self.db_connection.get_connection()
            # Create a cursor
            cursor = conn.cursor()

            # Execute the query to update the account balance
            query = f"""
                UPDATE Account
                SET CurrentBalance = CurrentBalance + ?
                WHERE AccountNo = ?
            """
            cursor.execute(query, (deposit_amt, account_num))

            # Commit the transaction
            conn.commit()

            # Update the balance label
            self.balance.setText('{:.2f}'.format(float(self.balance.text()) + deposit_amt))
            self.new_balance.setText('{:.2f}'.format(float(self.balance.text())))

            # Display success message
            self.success_msg.setText("Deposit successful.")

            # Insert a new row into the Transactions table
            query = f"""
                INSERT INTO Transactions (TransactionNo, AcctNo, TransactionDate, TransactionType, TransactionAmt, UpdatedBalance)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            # Get the current date
            today = datetime.date.today()

            # Get the next transaction number
            query2 = "SELECT MAX(TransactionNo) FROM Transactions"
            cursor.execute(query2)
            max_transaction_no = cursor.fetchone()[0]
            if max_transaction_no is None:
                transaction_no = 1001
            else:
                transaction_no = max_transaction_no + 1
            
            # Set the values for the new row
            values = (transaction_no, account_num, today, "Deposit", deposit_amt, float(self.new_balance.text()))
            
            # Execute the query to insert the new row
            cursor.execute(query, values)

            # Commit the transaction
            conn.commit()
                                    
            # Close the cursor and connection
            cursor.close()
            conn.close()

        except pyodbc.Error as e:
            # Handle any errors that occur during the connection or query execution
            print(f"Error: {str(e)}")
            self.error_2.setText("Error occurred while withdrawing funds.")  


class ViewTransferScreen(QDialog):
    def __init__(self, db_connection):
        super(ViewTransferScreen, self).__init__()
        loadUi("transfer.ui", self)
        self.db_connection = db_connection

        # Set the current date in the todays_date QLabel object
        self.todays_date.setText(QDate.currentDate().toString())

        # Connect the acct_search_button to the acct_search function
        self.acct_search_button.clicked.connect(self.acct_search)

        # Connect the close_button to the close_screen function
        self.close_button.clicked.connect(self.close_screen)

        # Connect the withdrawal_button to the withdrawal_funds function
        self.transfer_button.clicked.connect(self.transfer)

    def close_screen(self):
        # Close the current window and return to the dashboard
        self.close()
        widget.removeWidget(self)

    def acct_search(self):
        from_acct_num = self.from_search_field.text()
        to_acct_num = self.to_search_field.text()

        # Check if the from and to account number fields are both empty
        if not from_acct_num and not to_acct_num:
            self.error.setText("Please enter a transfer from and transfer to account.")
            return
        
        # Check if the from account number field is empty
        if not from_acct_num:
            self.error.setText("Please enter a transfer from account.")
            return
        
        # Check if the account number field is empty
        if not to_acct_num:
            self.error.setText("Please enter a transfer to account.")
            return

        # Check if both account number fields are valid
        if not from_acct_num.isdigit() or len(from_acct_num) > 10 or not to_acct_num.isdigit() or len(to_acct_num) > 10:
            self.error.setText("Please enter valid account numbers.")
            return
        
        if not from_acct_num.isdigit() or len(from_acct_num) > 10:
            self.error.setText("Please enter valid from account.")
            return
        
        if not to_acct_num.isdigit() or len(to_acct_num) > 10:
            self.error.setText("Please enter valid to account .")
            return

        self.error.setText("")

        try:
            # Connect to the database
            conn = self.db_connection.get_connection()
            # Create a cursor
            cursor = conn.cursor()

            # Execute the query to get account information for the from account
            if from_acct_num:
                query = f"""
                    SELECT Account.AccountNo, Account.AcctType, Account.BranchNo, 
                        Account.OpenDate, Account.CurrentBalance, Customer.Fname, Customer.Lname
                    FROM Account
                    INNER JOIN Customer ON Account.CustomerID = Customer.CustomerID
                    WHERE Account.AccountNo = ?
                """
                cursor.execute(query, from_acct_num)

                # Get the account information
                account_info = cursor.fetchone()

                if account_info:
                    # Display the account information
                    self.error.setText("")
                    self.account_num.setText(str(account_info[0]))
                    self.account_type.setText(account_info[1])
                    self.branch_num.setText(str(account_info[2]))
                    self.open_date.setText(str(account_info[3]))
                    self.balance.setText(str(account_info[4]))
                    self.customer_name.setText(f"{account_info[5].capitalize()} {account_info[6].capitalize()}")
                    self.customer_ID.setText(str(account_info[0]))

                else:
                    # Display error message if account not found
                    self.error.setText("Account(s) not found. Please check account numbers.")
                    return

            # Execute the query to get account information for the to account
            if to_acct_num:
                query = f"""
                    SELECT Account.AccountNo, Account.AcctType, Account.BranchNo, 
                        Account.OpenDate, Account.CurrentBalance, Customer.Fname, Customer.Lname
                    FROM Account
                    INNER JOIN Customer ON Account.CustomerID = Customer.CustomerID
                    WHERE Account.AccountNo = ?
                """
                cursor.execute(query, to_acct_num)

                # Get the account information
                account_info = cursor.fetchone()

                if account_info:
                    # Display the account information
                    self.error.setText("")
                    self.account_num_2.setText(str(account_info[0]))
                    self.account_type_2.setText(account_info[1])
                    self.branch_num_2.setText(str(account_info[2]))
                    self.open_date_2.setText(str(account_info[3]))
                    self.balance_2.setText(str(account_info[4]))
                    self.customer_name_2.setText(f"{account_info[5].capitalize()} {account_info[6].capitalize()}")
                    self.customer_ID_2.setText(str(account_info[0]))

                else:
                    # Display error message if account not found
                    self.error.setText("Account(s) not found. Please check account numbers.")
                    return

            # Close the cursor and connection
            cursor.close()
            conn.close()

        except pyodbc.Error as e:
            # Handle any errors that occur during the connection or query execution
            print(f"Error: {str(e)}")
            self.error.setText("Error occurred while fetching account information.")

    def transfer(self):
        from_acct_num = self.from_search_field.text()
        to_acct_num = self.to_search_field.text()
        transfer_amt = self.transfer_amt_field.text()
        confirm_transfer_amt = self.confirm_transfer_amt_field.text()

        # Check if the balance field is empty
        self.error_2.setText("")
        if not self.balance.text():
            self.error_2.setText("Please search a transfer from account first.")
            return
        
        # Check if the balance_2 (transfer to) field is empty
        if not self.balance.text():
            self.error_2.setText("Please search a transfer to account first.")
            return
        
        # Check if both transfer and confirm amount fields are empty
        if not transfer_amt and not confirm_transfer_amt:
            self.error_2.setText("Please input transfer and confirm amounts.")
            return

        #Check if transfer amount field is empty
        if not transfer_amt:
            self.error_2.setText("Please enter transfer amount")
            return 

        #Check if confirm amount field is empty
        if not confirm_transfer_amt:
            self.error_2.setText("Please confirm transfer amount.")   
            return         

        # Check if both transfer amount fields are valid
        try:
            transfer_amt = float(transfer_amt)
            confirm_transfer_amt = float(confirm_transfer_amt)
            if not ((transfer_amt and confirm_transfer_amt)<= float(self.balance.text())):
                self.error_2.setText("Transfer value exceeds current balance.")
                return
            if not (0 < (transfer_amt and confirm_transfer_amt)):
                self.error_2.setText("Please enter a transfer value greater than $0.00")
                return
            if not (round(transfer_amt, 2) == transfer_amt and round(confirm_transfer_amt, 2) == confirm_transfer_amt):
                self.error_2.setText("Please enter correct value.")
                return
        except ValueError:
            self.error_2.setText("Please enter a valid transfer and confirm amounts.")
            return

        # Check if transfer amount is valid
        try:
            transfer_amt = float(transfer_amt)
            if not (transfer_amt <= float(self.balance.text())):
                self.error_2.setText("Transfer value exceeds current balance.")
                return
            if not (0 < transfer_amt):
                self.error_2.setText("Please enter a transfer value greater than $0.00")
                return
            if not (round(transfer_amt, 2) == transfer_amt):
                self.error_2.setText("Please enter correct value.")
                return
        except ValueError:
            self.error_2.setText("Please enter a valid transfer amount.")
            return
        
        # Check if confirm amount is valid
        try:
            confirm_transfer_amt = float(confirm_transfer_amt)
            if not (confirm_transfer_amt <= float(self.balance.text())):
                self.error_2.setText("Confirm transfer value exceeds current balance.")
                return
            if not (0 < confirm_transfer_amt):
                self.error_2.setText("Please enter a confirm transfer value greater than $0.00")
                return
            if not (round(confirm_transfer_amt, 2) == confirm_transfer_amt):
                self.error_2.setText("Please enter correct confirm transfer value.")
                return
        except ValueError:
            self.error_2.setText("Please enter a valid confirm transfer amount.")
            return    

        # Check if the transfer amount matches the confirm transfer amount
        if transfer_amt != float(confirm_transfer_amt):
            self.error_2.setText("Please ensure amount anc confirm amount match.")
            return

        try:
            # Connect to the database
            conn = self.db_connection.get_connection()

            # Create a cursor
            cursor = conn.cursor()

            # Withdraw from the from account
            if from_acct_num:
                # Execute the query to update the account balance
                query = f"""
                    UPDATE Account
                    SET CurrentBalance = CurrentBalance - ?
                    WHERE AccountNo = ?
                """
                cursor.execute(query, (transfer_amt, from_acct_num))

                # Commit the transaction
                conn.commit()

                # Update from balance labels
                self.balance.setText(str(float(self.balance.text()) - transfer_amt))                
                self.new_balance_from.setText(str(float(self.balance.text()) - transfer_amt))
                
                # Add a new transaction to the Transactions table
                query = f"""
                    INSERT INTO Transactions (TransactionNo, AcctNo, TransactionDate, TransactionType, TransactionAmt, UpdatedBalance)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                
                # Get the current date
                today = datetime.date.today()

                # Get the next transaction number
                query2 = "SELECT MAX(TransactionNo) FROM Transactions"
                cursor.execute(query2)
                max_transaction_no = cursor.fetchone()[0]
                if max_transaction_no is None:
                    transaction_no = 1000
                else:
                    transaction_no = max_transaction_no + 1
                
                # Set the values for the new row
                values = (transaction_no, from_acct_num, today, "Withdrawal", -transfer_amt, float(self.balance.text()))
                
                # Execute the query to insert the new row
                cursor.execute(query, values)

                # Commit the transaction
                conn.commit()

            # Deposit to the to account
            if to_acct_num:
                # Execute the query to update the account balance
                query = f"""
                    UPDATE Account
                    SET CurrentBalance = CurrentBalance + ?
                    WHERE AccountNo = ?
                """
                cursor.execute(query, (transfer_amt, to_acct_num))

                # Commit the transaction
                conn.commit()

                # Update the balance label
                self.balance_2.setText(str(float(self.balance_2.text()) + transfer_amt))
                self.new_balance_to.setText(str(float(self.balance_2.text()) + transfer_amt))

                # Add a new transaction to the Transactions table
                query = """
                    INSERT INTO Transactions (TransactionNo, AcctNo, TransactionDate, TransactionType, TransactionAmt, UpdatedBalance)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                # Get the current date
                today = datetime.date.today()

                # Get the next transaction number
                query2 = "SELECT MAX(TransactionNo) FROM Transactions"
                cursor.execute(query2)
                max_transaction_no = cursor.fetchone()[0]
                if max_transaction_no is None:
                    transaction_no = 1001
                else:
                    transaction_no = max_transaction_no + 1
                
                # Set the values for the new row
                values = (transaction_no, to_acct_num, today, "Deposit", transfer_amt, float(self.new_balance_to.text()))
                
                # Execute the query to insert the new row
                cursor.execute(query, values)

                # Commit the transaction
                conn.commit()                

            # Display success message
            self.error.setText("")
            self.error_2.setText("")
            self.success_msg.setText("Transfer successful.")

            # Close the cursor and connection
            cursor.close()
            conn.close()

        except pyodbc.Error as e:
            # Handle any errors that occur during the connection or query execution
            print(f"Error: {str(e)}")
            self.error_2.setText("Error occurred while withdrawing funds.")

class AccountSerivcesScreen(QDialog):
    def __init__(self, db_connection):
        super(AccountSerivcesScreen, self).__init__()
        loadUi("acctservicesmenu.ui", self)
        self.db_connection = db_connection
        
        # Connect the close_button to the close_screen function
        self.close_button.clicked.connect(self.close_screen)

        # Connect the acct_search_button to the acct_search function
        self.new_customer_button.clicked.connect(self.gotonewcustomer)

        # Connect the acct_search_button to the acct_search function
        self.update_customer_button.clicked.connect(self.gotoupdatecustomer)

        # Connect the acct_search_button to the acct_search function
        self.close_account_button.clicked.connect(self.gotocloseaccount)        

    def gotonewcustomer(self):
        newcustomer = NewCustomerScreen(self.db_connection)
        widget.addWidget(newcustomer)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotoupdatecustomer(self):
        updatecustomer = ViewSearchCustomerScreen(self.db_connection)
        widget.addWidget(updatecustomer)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotocloseaccount(self):
        closeaccount = CloseAccountCustomerScreen(self.db_connection)
        widget.addWidget(closeaccount)
        widget.setCurrentIndex(widget.currentIndex()+1)                

    def close_screen(self):
        # Close the current window and return to the dashboard
        self.close()
        widget.removeWidget(self)

class ViewSearchCustomerScreen(QDialog):
    def __init__(self, db_connection):
        super(ViewSearchCustomerScreen, self).__init__()
        loadUi("searchcustomer.ui", self)
        widget.setFixedHeight(1399)          
        self.db_connection = db_connection

        self.cancel_button.setVisible(False)
        self.confirm_button.setVisible(False)
        self.update_button.setVisible(False)
        self.confirm_box.setVisible(False)
        self.confirm_text.setVisible(False)
        self.confirm_button2.setVisible(False)
        self.cancel_button2.setVisible(False)        

        # Connect the acct_search_button to the acct_search function
        self.acct_search_button.clicked.connect(self.acct_search)

        # Connect the acct_search_button to the acct_search function
        self.update_button.clicked.connect(self.update_customer)

        # Connect the acct_search_button to the acct_search function
        self.cancel_button.clicked.connect(self.cancel_update)

        # Connect the acct_search_button to the acct_search function
        self.confirm_button.clicked.connect(self.confirm_update)

        # Connect the close_button to the close_screen function
        self.close_button.clicked.connect(self.close_screen)

        # Connect the acct_search_button to the acct_search function
        self.cancel_button2.clicked.connect(self.cancel_update2)

        # Connect the acct_search_button to the acct_search function
        self.confirm_button2.clicked.connect(self.confirm_update2)

    def close_screen(self):
        # Close the current window and return to the dashboard
        self.close()
        widget.removeWidget(self)
        widget.setFixedHeight(800)

    def acct_search(self):
        text = self.search_field.text()
  

        # clear all fields
        self.customer_id_field.setText("")
        self.fname_field.setText("")
        self.mi_field.setText("")
        self.lname_field.setText("")
        self.ssn_field.setText("")
        self.dob_field.setText("")
        self.sex_field.setText("")
        self.dl_field.setText("")
        self.street_num_field.setText("")
        self.street_name_field.setText("")
        self.city_field.setText("")
        self.state_field.setText("")
        self.zip_field.setText("")
        self.phone_num_field.setText("")
        self.email_field.setText("")     

        self.checking_acct_num_field.setText("")    
        self.checking_branch_num_field.setText("")    
        self.checking_open_date.setText("")    
        self.checking_balance_field.setText("")    
        self.routing_num_field.setText("")    

        self.savings_acct_num_field.setText("") 
        self.savings_branch_num_field.setText("") 
        self.savings_open_date_field.setText("") 
        self.savings_balance_field.setText("") 
        self.routing_num_field_savings.setText("") 

        self.error.setText("")
        self.loan_num_field.setText("")
        self.loan_type_field.setText("")
        self.loan_amount_field.setText("")
        self.loan_open_date_field.setText("")
        self.loan_duration_field.setText("")
        self.loan_balance_field.setText("")
        self.interest_rate_field.setText("")
        self.loan_status_field.setText("")
        self.no_loan_error.setText("")

        # Check if the account number field is empty
        if not text:
            self.error.setText("Please enter an account number.")
            return

        # regular expression pattern to match only letters and numbers
        pattern = r"^[a-zA-Z0-9]*$"  
        if not re.match(pattern, text):
            self.error.setText("The input field can only contain letters and numbers. Please try again.")
            return
        
        # Check if DL number is less than than 8 characters        
        if any(char.isalpha() for char in text):
            if len(text) < 8:
                self.error.setText("Entry for DL must be at least 8 characters. Please try again.")
                return       

        # Check if the account number is greater than than 15 characters        
        if len(text) > 15:
            self.error.setText("Entry cannot exceed 15 characters. Please try again.")
            return

        try:
            # Connect to the database
            conn = self.db_connection.get_connection()
            # Create a cursor
            cursor = conn.cursor()

            # Execute the query to get customer information
            query = f"""
                SELECT Customer.CustomerID, Customer.Fname, Customer.Minit, Customer.Lname, Customer.SSN,
                Customer.DOB, Customer.Sex, Customer.DLNum, Customer.StreetNo, Customer.StreetName, Customer.City,
                Customer.State, Customer.Zip, Customer.PhoneNum, Customer.Email
                FROM Customer
                WHERE Customer.CustomerID = ?
                OR Customer.SSN = ?
                OR Customer.DLNum = ?
            """
            cursor.execute(query, text, text, text)

            # Get the checking account information
            customer_info = cursor.fetchone()

            if customer_info:              
                # Display the checking account information
                self.error.setText("")
                self.customer_id_field.setText(str(customer_info[0]))
                self.fname_field.setText(str(customer_info[1]))
                self.mi_field.setText(str(customer_info[2]))
                self.lname_field.setText(str(customer_info[3]))
                self.ssn_field.setText(str(customer_info[4]))
                self.dob_field.setText(str(customer_info[5]))
                self.sex_field.setText(str(customer_info[6]))
                self.dl_field.setText(str(customer_info[7]))
                self.street_num_field.setText(str(customer_info[8]))
                self.street_name_field.setText(str(customer_info[9]))
                self.city_field.setText(str(customer_info[10]))
                self.state_field.setText(str(customer_info[11]))
                self.zip_field.setText(str(customer_info[12]))
                self.phone_num_field.setText(str(customer_info[13]))  
                self.email_field.setText(str(customer_info[14]))                                    

            # Execute the query to get checking account information
            query = f"""
                SELECT Account.AccountNo, Account.BranchNo, Account.OpenDate, Account.CurrentBalance
                FROM Account
                INNER JOIN Customer ON Account.CustomerID = Customer.CustomerID
                WHERE Account.CustomerID = ?
                OR Customer.SSN = ?
                OR Customer.DLNum = ?
            """
            cursor.execute(query, text, text, text)

            # Get the checking account information
            account_info = cursor.fetchone()

            if account_info:              
                # Display the checking account information
                self.error.setText("")
                self.checking_acct_num_field.setText(str(account_info[0]))
                self.checking_branch_num_field.setText(str(account_info[1]))
                self.checking_open_date.setText(str(account_info[2]))
                self.checking_balance_field.setText(str(account_info[3]))
                self.routing_num_field.setText("256074971")
            else:
                # Display error message if customer not found
                self.error.setText("Customer not found.")

            # Execute the query to get savings account information
            query = f"""
                SELECT Account.AccountNo, Account.BranchNo, Account.OpenDate, Account.CurrentBalance
                FROM Account
                INNER JOIN Customer ON Account.CustomerID = Customer.CustomerID
                WHERE (Account.CustomerID = ? 
                OR Customer.SSN = ?
                OR Customer.DLNum = ?) AND Account.AcctType = 'Savings'
            """
            cursor.execute(query, text, text, text)

            # Get the savings account information
            account_info = cursor.fetchone()

            if account_info:              
                # Display the savings account information
                self.error.setText("")
                self.savings_acct_num_field.setText(str(account_info[0]))
                self.savings_branch_num_field.setText(str(account_info[1]))
                self.savings_open_date_field.setText(str(account_info[2]))
                self.savings_balance_field.setText(str(account_info[3]))
                self.routing_num_field_savings.setText("256074971")                

            # Execute the query to get loan account information
            query = f"""
                SELECT Loan.LoanNo, Loan.LoanType, Loan.LoanAmt, Loan.LoanDate,
                Loan.Duration, Loan.LoanBalance, Loan.InterestRate, Loan.Status 
                FROM Loan
                INNER JOIN Customer ON Loan.CustomerID = Customer.CustomerID
                WHERE Customer.CustomerID = ? 
                OR Customer.SSN = ?
                OR Customer.DLNum = ?
            """
            cursor.execute(query, text, text, text)

            # Get the loan account information
            account_info = cursor.fetchone()

            if account_info:              
                # Display the loan account information
                self.error.setText("")
                self.loan_num_field.setText(str(account_info[0]))
                self.loan_type_field.setText(str(account_info[1]))
                self.loan_amount_field.setText(str(account_info[2]))
                self.loan_open_date_field.setText(str(account_info[3]))
                self.loan_duration_field.setText(str(account_info[4]))
                self.loan_balance_field.setText(str(account_info[5]))
                self.interest_rate_field.setText(str(account_info[6]))
                self.loan_status_field.setText(str(account_info[7])) 
                self.no_loan_error.setText("")               

            else:
                # Display error message if customer not found
                self.no_loan_error.setText("No loans on file.")
            # Close the cursor and connection
            cursor.close()
            conn.close()
            self.update_button.setVisible(True)

        except pyodbc.Error as e:
            # Handle any errors that occur during the connection or query execution
            print(f"Error: {str(e)}")
            self.error.setText("Error occurred while fetching account information.")

    def update_customer(self):
        self.search_customer_label.setText("Update Customer")
        # Make text fields editable
        self.fname_field.setEnabled(True)
        self.mi_field.setEnabled(True)
        self.lname_field.setEnabled(True)
        self.ssn_field.setEnabled(True)
        self.dob_field.setEnabled(True)
        self.sex_field.setEnabled(True)
        self.dl_field.setEnabled(True)
        self.street_num_field.setEnabled(True)
        self.street_name_field.setEnabled(True)
        self.city_field.setEnabled(True)
        self.state_field.setEnabled(True)
        self.zip_field.setEnabled(True)
        self.phone_num_field.setEnabled(True)
        self.email_field.setEnabled(True)

        # Change button visibility
        self.cancel_button.setVisible(True)
        self.confirm_button.setVisible(True)
        self.update_button.setVisible(False) 

    def cancel_update(self):
        self.acct_search() 
        self.search_customer_label.setText("View Customer")
        self.error.setText("")
        # Make text fields not editable
        self.fname_field.setEnabled(False)
        self.mi_field.setEnabled(False)
        self.lname_field.setEnabled(False)
        self.ssn_field.setEnabled(False)
        self.dob_field.setEnabled(False)
        self.sex_field.setEnabled(False)
        self.dl_field.setEnabled(False)
        self.street_num_field.setEnabled(False)
        self.street_name_field.setEnabled(False)
        self.city_field.setEnabled(False)
        self.state_field.setEnabled(False)
        self.zip_field.setEnabled(False)
        self.phone_num_field.setEnabled(False)
        self.email_field.setEnabled(False)

        # Make buttons not visible
        self.cancel_button.setVisible(False)
        self.confirm_button.setVisible(False)
        self.update_button.setVisible(False)

    def confirm_update(self): 
        # Validate data fields
        fname = self.fname_field.text().strip().title()
        if not fname.isalpha() or len(fname) > 20:
            self.error.setText("First name must be only letters and less than or equal to 20 characters.")
            return

        mi = self.mi_field.text().strip().upper()
        if not mi.isalpha() or len(mi) != 1:
            self.error.setText("Middle initial must be a single letter.")
            return

        lname = self.lname_field.text().strip().title()
        if not lname.isalpha() or len(lname) > 30:
            self.error.setText("Last name must be only letters and less than or equal to 30 characters.")
            return

        ssn = self.ssn_field.text().strip()
        if not ssn.isdigit() or len(ssn) != 9:
            self.error.setText("SSN must be exactly 9 digits.")
            return

        dob = self.dob_field.text().strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", dob):
            self.error.setText("Date of birth must be in the format YYYY-MM-DD.")
            return

        sex = self.sex_field.text().strip().upper()
        if sex not in ('M', 'F'):
            self.error.setText("Sex must be M or F.")
            return

        dl_num = self.dl_field.text().strip().upper()
        if not re.match(r"^[A-Z]{2}\d{6}$", dl_num):
            self.error.setText("Driver's license number must be 2 uppercase letters followed by 6 digits.")
            return

        street_no = self.street_num_field.text().strip()
        if not street_no.isdigit() or len(street_no) > 10:
            self.error.setText("Street number must be only digits and less than or equal to 10 digits.")
            return

        street_name = self.street_name_field.text().strip().title()
        if not all(c.isalpha() or c.isspace() for c in street_name) or len(street_name) > 30:
            self.error.setText("Street name must be only letters and less than or equal to 30 characters.")
            return

        city = self.city_field.text().strip().title()
        if not all(c.isalpha() or c.isspace() for c in city) or len(city) > 35:    
            self.error.setText("City must be only letters and less than or equal to 35 characters.")
            return

        state = self.state_field.text().strip().upper()
        if state != "TX":
            self.error.setText("State must be TX.")
            return

        zip_code = self.zip_field.text().strip()
        if not zip_code.isdigit() or len(zip_code) != 5:
            self.error.setText("Zip code must be exactly 5 digits.")
            return

        phone_num = self.phone_num_field.text().strip()
        if not phone_num.isdigit() or len(phone_num) != 10:
            self.error.setText("Phone number must be exactly 10 digits.")
            return

        email = self.email_field.text().strip()
        if not re.match(r"^\S+@\S+\.\S+$", email):
            self.error.setText("Email must be in correct format.")
            return

        self.confirm_box.setVisible(True)
        self.confirm_text.setVisible(True)
        self.cancel_button2.setVisible(True)
        self.confirm_button2.setVisible(True) 

    def cancel_update2(self):
        self.acct_search()  
        self.confirm_box.setVisible(False)
        self.confirm_text.setVisible(False)
        self.cancel_button2.setVisible(False)
        self.confirm_button2.setVisible(False)

    def confirm_update2(self):  
        self.confirm_box.setVisible(False)
        self.confirm_text.setVisible(False)
        self.cancel_button2.setVisible(False)
        self.confirm_button2.setVisible(False)

        customer_id = self.customer_id_field.text()
        # Validate data fields
        fname = self.fname_field.text().strip().title()
        if not fname.isalpha() or len(fname) > 20:
            self.error.setText("First name must be only letters and less than or equal to 20 characters.")
            return

        mi = self.mi_field.text().strip().upper()
        if not mi.isalpha() or len(mi) != 1:
            self.error.setText("Middle initial must be a single letter.")
            return

        lname = self.lname_field.text().strip().title()
        if not lname.isalpha() or len(lname) > 30:
            self.error.setText("Last name must be only letters and less than or equal to 30 characters.")
            return

        ssn = self.ssn_field.text().strip()
        if not ssn.isdigit() or len(ssn) != 9:
            self.error.setText("SSN must be exactly 9 digits.")
            return

        dob = self.dob_field.text().strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", dob):
            self.error.setText("Date of birth must be in the format YYYY-MM-DD.")
            return

        sex = self.sex_field.text().strip().upper()
        if sex not in ('M', 'F'):
            self.error.setText("Sex must be M or F.")
            return

        dl_num = self.dl_field.text().strip().upper()
        if not re.match(r"^[A-Z]{2}\d{6}$", dl_num):
            self.error.setText("Driver's license number must be 2 uppercase letters followed by 6 digits.")
            return

        street_no = self.street_num_field.text().strip()
        if not street_no.isdigit() or len(street_no) > 10:
            self.error.setText("Street number must be only digits and less than or equal to 10 digits.")
            return

        street_name = self.street_name_field.text().strip().title()
        if not all(c.isalpha() or c.isspace() for c in street_name) or len(street_name) > 30:
            self.error.setText("Street name must be only letters and less than or equal to 30 characters.")
            return

        city = self.city_field.text().strip().title()
        if not all(c.isalpha() or c.isspace() for c in city) or len(city) > 35:    
            self.error.setText("City must be only letters and less than or equal to 35 characters.")
            return

        state = self.state_field.text().strip().upper()
        if state != "TX":
            self.error.setText("State must be TX.")
            return

        zip_code = self.zip_field.text().strip()
        if not zip_code.isdigit() or len(zip_code) != 5:
            self.error.setText("Zip code must be exactly 5 digits.")
            return

        phone_num = self.phone_num_field.text().strip()
        if not phone_num.isdigit() or len(phone_num) != 10:
            self.error.setText("Phone number must be exactly 10 digits.")
            return

        email = self.email_field.text().strip()
        if not re.match(r"^\S+@\S+\.\S+$", email):
            self.error.setText("Email must be in correct format.")
            return

        try:
            # Connect to the database
            conn = self.db_connection.get_connection()
            # Create a cursor
            cursor = conn.cursor()

            # Execute the query to update customer information
            query = """
                UPDATE Customer
                SET Fname=?, Minit=?, Lname=?, SSN=?, DOB=?, Sex=?, DLNum=?, StreetNo=?, StreetName=?, City=?, State=?, Zip=?, PhoneNum=?, Email=?
                WHERE CustomerID=?
            """
            cursor.execute(query, (fname, mi, lname, ssn, dob, sex, dl_num, street_no, street_name, city, state, zip_code, phone_num, email, customer_id))

            # Commit the transaction
            conn.commit()

            # Close the cursor and connection
            cursor.close()
            conn.close()
            self.update_button.setVisible(True)

            self.success_msg.setText("Update Successful.")
            self.acct_search()
            self.cancel_button.setVisible(False)
            self.confirm_button.setVisible(False)
            self.update_button.setVisible(False)
            self.search_customer_label.setText("View Customer")
            # Make text fields not editable
            self.fname_field.setEnabled(False)
            self.mi_field.setEnabled(False)
            self.lname_field.setEnabled(False)
            self.ssn_field.setEnabled(False)
            self.dob_field.setEnabled(False)
            self.sex_field.setEnabled(False)
            self.dl_field.setEnabled(False)
            self.street_num_field.setEnabled(False)
            self.street_name_field.setEnabled(False)
            self.city_field.setEnabled(False)
            self.state_field.setEnabled(False)
            self.zip_field.setEnabled(False)
            self.phone_num_field.setEnabled(False)
            self.email_field.setEnabled(False)                        

        except pyodbc.Error as e:
            # Handle any errors that occur during the connection or query execution
            print(f"Error: {str(e)}")
            self.error.setText("Error occurred while updating customer information.")                

class NewCustomerScreen(QDialog):
    def __init__(self, db_connection):
        super(NewCustomerScreen, self).__init__()
        loadUi("createcustomer.ui", self)
        widget.setFixedHeight(1399)          
        self.db_connection = db_connection

        # Make confirm box not visible
        self.confirm_box.setVisible(False)
        self.confirm_text.setVisible(False)
        self.cancel_button.setVisible(False)
        self.confirm_button.setVisible(False)

        # Connect the create_customer_button to the create_customer function
        self.create_customer_button.clicked.connect(self.create_customer)

        # Connect the cancel_button to the cancel create function
        self.cancel_button.clicked.connect(self.cancel_create)

        # Connect the confirm_button to the confirm_create function
        self.confirm_button.clicked.connect(self.confirm_create)

        # Connect the close_button to the close_screen function
        self.close_button.clicked.connect(self.close_screen)

    def close_screen(self):
        # Close the current window and return to the dashboard
        self.close()
        widget.removeWidget(self)
        widget.setFixedHeight(800)

    def cancel_create(self):  
        self.confirm_box.setVisible(False)
        self.confirm_text.setVisible(False)
        self.cancel_button.setVisible(False)
        self.confirm_button.setVisible(False)    

    def create_customer(self):
        # Validate data fields
        fname = self.fname_field.text().strip().title()
        if not fname.isalpha() or len(fname) > 20:
            self.error.setText("First name must be only letters and less than or equal to 20 characters.")
            return

        mi = self.mi_field.text().strip().upper()
        if not mi.isalpha() or len(mi) != 1:
            self.error.setText("Middle initial must be a single letter.")
            return

        lname = self.lname_field.text().strip().title()
        if not lname.isalpha() or len(lname) > 30:
            self.error.setText("Last name must be only letters and less than or equal to 30 characters.")
            return

        ssn = self.ssn_field.text().strip()
        if not ssn.isdigit() or len(ssn) != 9:
            self.error.setText("SSN must be exactly 9 digits.")
            return

        dob = self.dob_field.text().strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", dob):
            self.error.setText("Date of birth must be in the format YYYY-MM-DD.")
            return

        sex = self.sex_field.text().strip().upper()
        if sex not in ('M', 'F'):
            self.error.setText("Sex must be M or F.")
            return

        dl_num = self.dl_field.text().strip().upper()
        if not re.match(r"^[A-Z]{2}\d{6}$", dl_num):
            self.error.setText("Driver's license number must be 2 uppercase letters followed by 6 digits.")
            return

        street_no = self.street_num_field.text().strip()
        if not street_no.isdigit() or len(street_no) > 10:
            self.error.setText("Street number must be only digits and less than or equal to 10 digits.")
            return

        street_name = self.street_name_field.text().strip().title()
        if not all(c.isalpha() or c.isspace() for c in street_name) or len(street_name) > 30:
            self.error.setText("Street name must be only letters and less than or equal to 30 characters.")
            return

        city = self.city_field.text().strip().title()
        if not all(c.isalpha() or c.isspace() for c in city) or len(city) > 35:    
            self.error.setText("City must be only letters and less than or equal to 35 characters.")
            return

        state = self.state_field.text().strip().upper()
        if state != "TX":
            self.error.setText("State must be TX.")
            return

        zip_code = self.zip_field.text().strip()
        if not zip_code.isdigit() or len(zip_code) != 5:
            self.error.setText("Zip code must be exactly 5 digits.")
            return

        phone_num = self.phone_num_field.text().strip()
        if not phone_num.isdigit() or len(phone_num) != 10:
            self.error.setText("Phone number must be exactly 10 digits.")
            return

        email = self.email_field.text().strip()
        if not re.match(r"^\S+@\S+\.\S+$", email):
            self.error.setText("Email must be in correct format.")
            return

        savings = self.initial_savings_amt.text().strip()
        if not savings:
            # The field is empty
           self.error.setText("Please enter a value in the Initial Savings field.")
           return
        elif not re.match(r"^\d{1,4}(.\d{2})?$", savings):
            # The value is not a dollar amount with two decimal point precision
            self.error.setText("The value entered in the initial savings field is not a valid dollar amount.")
            return
        elif float(savings) < 20.00:
            # The value is greater than or equal to 10000.00
            self.error.setText("The initial savings deposit must be $20.00 minimum to open an account.")
            return
        elif float(savings) > 10000.00:
            # The value is greater than or equal to 10000.00
            self.error.setText("The initial savings deposit cannot exceed $10,000.00.")
            return        
        else:
            # The value is valid
            self.initial_savings_amt.setText(savings) 

        checking = self.initial_checking_amt.text().strip()
        if not checking:
            # The field is empty
           self.error.setText("Please enter a value in the initial checking field.")
           return
        elif not re.match(r"^\d{1,4}(.\d{2})?$", checking):
            # The value is not a dollar amount with two decimal point precision
            self.error.setText("The value entered in the initial checking field is not a valid dollar amount.")
            return
        elif float(checking) < 0.00:
            # The value is greater than or equal to 10000.00
            self.error.setText("The Initial checking amount must be $0.00 minimum.")
            return
        elif float(checking) > 10000.00:
            # The value is greater than or equal to 10000.00
            self.error.setText("The initial checking deposit cannot exceed $10,000.00.")
            return        
        else:
            # The value is valid
            self.initial_checking_amt.setText(checking)

        self.error.setText("")
        
        # Make confirm box visible
        self.confirm_box.setVisible(True)
        self.confirm_text.setVisible(True)
        self.cancel_button.setVisible(True)
        self.confirm_button.setVisible(True)

    def confirm_create(self):

            # Validate data fields
        fname = self.fname_field.text().strip().title()
        if not fname.isalpha() or len(fname) > 20:
            self.error.setText("First name must be only letters and less than or equal to 20 characters.")
            return

        mi = self.mi_field.text().strip().upper()
        if not mi.isalpha() or len(mi) != 1:
            self.error.setText("Middle initial must be a single letter.")
            return

        lname = self.lname_field.text().strip().title()
        if not lname.isalpha() or len(lname) > 30:
            self.error.setText("Last name must be only letters and less than or equal to 30 characters.")
            return

        ssn = self.ssn_field.text().strip()
        if not ssn.isdigit() or len(ssn) != 9:
            self.error.setText("SSN must be exactly 9 digits.")
            return

        dob = self.dob_field.text().strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", dob):
            self.error.setText("Date of birth must be in the format YYYY-MM-DD.")
            return

        sex = self.sex_field.text().strip().upper()
        if sex not in ('M', 'F'):
            self.error.setText("Sex must be M or F.")
            return

        dl_num = self.dl_field.text().strip().upper()
        if not re.match(r"^[A-Z]{2}\d{6}$", dl_num):
            self.error.setText("Driver's license number must be 2 uppercase letters followed by 6 digits.")
            return

        street_no = self.street_num_field.text().strip()
        if not street_no.isdigit() or len(street_no) > 10:
            self.error.setText("Street number must be only digits and less than or equal to 10 digits.")
            return

        street_name = self.street_name_field.text().strip().title()
        if not all(c.isalpha() or c.isspace() for c in street_name) or len(street_name) > 30:
            self.error.setText("Street name must be only letters and less than or equal to 30 characters.")
            return

        city = self.city_field.text().strip().title()
        if not all(c.isalpha() or c.isspace() for c in city) or len(city) > 35:    
            self.error.setText("City must be only letters and less than or equal to 35 characters.")
            return

        state = self.state_field.text().strip().upper()
        if state != "TX":
            self.error.setText("State must be TX.")
            return

        zip_code = self.zip_field.text().strip()
        if not zip_code.isdigit() or len(zip_code) != 5:
            self.error.setText("Zip code must be exactly 5 digits.")
            return

        phone_num = self.phone_num_field.text().strip()
        if not phone_num.isdigit() or len(phone_num) != 10:
            self.error.setText("Phone number must be exactly 10 digits.")
            return

        email = self.email_field.text().strip()
        if not re.match(r"^\S+@\S+\.\S+$", email):
            self.error.setText("Email must be in correct format.")
            return         

        savings = self.initial_savings_amt.text().strip()
        if not savings:
            # The field is empty
           self.error.setText("Please enter a value in the Initial Savings field.")
           return
        elif not re.match(r"^\d{1,20}(.\d{2})?$", savings):
            # The value is not a dollar amount with two decimal point precision
            self.error.setText("The value entered in the initial savings field is not a valid dollar amount.")
            return
        elif float(savings) < 20.00:
            # The value is greater than or equal to 10000.00
            self.error.setText("The initial savings deposit must be $20.00 minimum to open an account.")
            return
        elif float(savings) > 10000.00:
            # The value is greater than or equal to 10000.00
            self.error.setText("The initial savings deposit cannot exceed $10,000.00.")
            return        
        else:
            # The value is valid
            self.initial_savings_amt.setText(savings) 

        checking = self.initial_checking_amt.text().strip()
        if not checking:
            # The field is empty
           self.error.setText("Please enter a value in the initial checking field.")
           return
        elif not re.match(r"^\d{1,20}(.\d{2})?$", checking):
            # The value is not a dollar amount with two decimal point precision
            self.error.setText("The value entered in the initial checking field is not a valid dollar amount.")
            return
        elif float(checking) < 0.00:
            # The value is greater than or equal to 10000.00
            self.error.setText("The Initial checking amount must be $0.00 minimum.")
            return
        elif float(checking) > 10000.00:
            # The value is greater than or equal to 10000.00
            self.error.setText("The initial checking deposit cannot exceed $10,000.00.")
            return        
        else:
            # The value is valid
            self.initial_checking_amt.setText(checking)

        self.error.setText("")

        try:
            # Connect to the database
            conn = self.db_connection.get_connection()
            # Create a cursor
            cursor = conn.cursor()

            # Execute the query to update customer information
            query = """
                INSERT INTO Customer (CustomerID, Fname, Minit, Lname, SSN, DOB, Sex, DLNum, StreetNo, StreetName, City, State, Zip, PhoneNum, Email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Get the next customer ID number
            query2 = "SELECT MAX(CustomerID) FROM Customer"
            cursor.execute(query2)
            max_ID = cursor.fetchone()
            if max_ID is None:
                max_ID = 1000
            else:
                max_ID =max_ID[0] + 1            
            
            cursor.execute(query, (max_ID, fname, mi, lname, ssn, dob, sex, dl_num, street_no, street_name, city, state, zip_code, phone_num, email))

            # Get the current date
            today = datetime.date.today()

            # Execute the query add customer checking account
            query = """
                INSERT INTO Account (AccountNo, CustomerID, AcctType, BranchNo, OpenDate, CurrentBalance)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            # Get the next customer ID number
            query2 = "SELECT MAX(AccountNo) FROM Account"
            cursor.execute(query2)
            max_acct_num = cursor.fetchone()
            if max_acct_num is None:
                max_acct_num = 1000
            else:
                max_acct_num = max_acct_num[0] + 1            
            
            cursor.execute(query, (max_acct_num, max_ID, "Checking", "1", today, float(checking)))


            self.checking_acct_num_field.setText(str(max_acct_num))
            self.checking_branch_num_field.setText("1")
            self.checking_open_date.setText(str(today))
            self.checking_balance_field.setText(str(checking))
            self.routing_num_field.setText("256074971")


            # Execute the query add customer savings account
            query = """
                INSERT INTO Account (AccountNo, CustomerID, AcctType, BranchNo, OpenDate, CurrentBalance)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            # Get the next customer ID number
            query2 = "SELECT MAX(AccountNo) FROM Account"
            cursor.execute(query2)
            max_acct_num = cursor.fetchone()
            if max_acct_num is None:
                max_acct_num = 1000
            else:
                max_acct_num = max_acct_num[0] + 1            
            
            cursor.execute(query, (max_acct_num, max_ID, "Savings", "1", today, float(savings)))

            # Display the savings account information
            self.error.setText("")
            self.savings_acct_num_field.setText(str(max_acct_num))
            self.savings_branch_num_field.setText("1")
            self.savings_open_date_field.setText(str(today))
            self.savings_balance_field.setText(str(savings))
            self.routing_num_field_savings.setText("256074971") 

            # Commit the transaction
            conn.commit()

            # Close the cursor and connection
            cursor.close()
            conn.close()

            self.customer_id_field.setText(str(max_ID))
            self.success_msg.setText("Account successfully created.")
            self.confirm_box.setVisible(False)
            self.confirm_text.setVisible(False)             
            self.cancel_button.setVisible(False)
            self.confirm_button.setVisible(False)
            self.create_customer_button.setVisible(False)
            self.new_account_label.setText("New Customer Details")
            # Make text fields not editable
            self.initial_savings_amt.setEnabled(False)
            self.initial_checking_amt.setEnabled(False)                        
            self.fname_field.setEnabled(False)
            self.mi_field.setEnabled(False)
            self.lname_field.setEnabled(False)
            self.ssn_field.setEnabled(False)
            self.dob_field.setEnabled(False)
            self.sex_field.setEnabled(False)
            self.dl_field.setEnabled(False)
            self.street_num_field.setEnabled(False)
            self.street_name_field.setEnabled(False)
            self.city_field.setEnabled(False)
            self.state_field.setEnabled(False)
            self.zip_field.setEnabled(False)
            self.phone_num_field.setEnabled(False)
            self.email_field.setEnabled(False)                        

        except pyodbc.Error as e:
            # Handle any errors that occur during the connection or query execution
            print(f"Error: {str(e)}")
            self.error.setText("Error occurred while creating customer account.")        

class CloseAccountCustomerScreen(QDialog):

    def __init__(self, db_connection):
        super(CloseAccountCustomerScreen, self).__init__()
        loadUi("closeaccount.ui", self)
        widget.setFixedHeight(1399)          
        self.db_connection = db_connection

        # make confirm box not visible
        self.confirm_box.setVisible(False)
        self.confirm_text.setVisible(False)
        self.confirm_button.setVisible(False)
        self.cancel_button.setVisible(False) 

        # Connect the acct_search_button to the acct_search function
        self.acct_search_button.clicked.connect(self.acct_search)

        # Connect the close_button to the close_screen function
        self.close_button.clicked.connect(self.close_screen)

        # Connect the close_account_button to the close_account function
        self.close_account_button.clicked.connect(self.close_account)

        # Connect the cancel_button to the cancel close function
        self.cancel_button.clicked.connect(self.cancel_close)

        # Connect the confirm_button to the confirm close function
        #self.confirm_button.clicked.connect(self.confirm_close)
        self.confirm_button.clicked.connect(self.confirm_close)


    def close_screen(self):
        # Close the current window and return to the dashboard
        self.close()
        widget.removeWidget(self)
        widget.setFixedHeight(800)

    def close_account(self):
        text = self.checking_balance_field.text()
        
        # Check if the checking account balance is empty
        if not text:
            self.error.setText("Please search for an account to close.")
            return

        self.confirm_box.setVisible(True)
        self.confirm_text.setVisible(True)
        self.cancel_button.setVisible(True)
        self.confirm_button.setVisible(True)

    def cancel_close(self):  
        self.confirm_box.setVisible(False)
        self.confirm_text.setVisible(False)
        self.cancel_button.setVisible(False)
        self.confirm_button.setVisible(False)
        self.error.setText("")

    def confirm_close(self):      
        print("confirm close function")
        self.checking_balance = float(self.checking_balance_field.text())
        self.savings_balance = float(self.savings_balance_field.text())

        if self.checking_balance > 0 or self.savings_balance > 0:
            self.error.setText("All accounts must carry $0.00 balance to close customer account")
            return

        customer_id = int(self.customer_id_field.text())

        try:
            # Connect to the database
            conn = self.db_connection.get_connection()

            # Create a cursor
            cursor = conn.cursor()

            # Delete the checking account associated with the customer
            query = "DELETE FROM Account WHERE CustomerID = ? AND AcctType = 'Checking'"
            cursor.execute(query, (customer_id,))

            # Delete the savings account associated with the customer
            query = "DELETE FROM Account WHERE CustomerID = ? AND AcctType = 'Savings'"
            cursor.execute(query, (customer_id,))

            # Delete the customer associated with the customer ID
            query = "DELETE FROM Customer WHERE CustomerID = ?"
            cursor.execute(query, (customer_id,))

            # Commit the transaction
            conn.commit()

            # Display success message and close the pop up box
            self.cancel_close()
            self.success_msg.setText("Customer Account Successfully closed.")
            self.close_account_button.setVisible(False)

        except Exception as e:
            # Display error message if an exception occurs
            self.error.setText("An error occurred while processing request.")
            print("Error: " + str(e))
        finally:
            # Close the cursor and database connection
            cursor.close()
            conn.close()    


    def acct_search(self):
        self.success_msg.setText("")
        self.error.setText("")

        text = self.search_field.text()
        # Check if the account number field is empty
        if not text:
            self.error.setText("Please enter an account number.")
            return

        # regular expression pattern to match only letters and numbers
        pattern = r"^[a-zA-Z0-9]*$"  
        if not re.match(pattern, text):
            self.error.setText("The input field can only contain letters and numbers. Please try again.")
            return
 
        # Check if DL number is at least 8 characters        
        if any(char.isalpha() for char in text):
            if len(text) < 8:
                self.error.setText("Entry for DL must be at least 8 characters. Please try again.")
                return       

        # Check if the account number is less than 15 characters        
        if len(text) > 15:
            self.error.setText("Entry cannot exceed 15 characters. Please try again.")
            return

        try:
            # Connect to the database
            conn = self.db_connection.get_connection()
            # Create a cursor
            cursor = conn.cursor()

            # Execute the query to get customer information
            query = f"""
                SELECT Customer.CustomerID, Customer.Fname, Customer.Minit, Customer.Lname, Customer.SSN,
                Customer.DOB, Customer.Sex, Customer.DLNum, Customer.StreetNo, Customer.StreetName, Customer.City,
                Customer.State, Customer.Zip, Customer.PhoneNum, Customer.Email
                FROM Customer
                WHERE Customer.CustomerID = ?
                OR Customer.SSN = ?
                OR Customer.DLNum = ?
            """
            cursor.execute(query, text, text, text)

            # Get the checking account information
            customer_info = cursor.fetchone()

            if customer_info:              
                # Display the checking account information
                self.error.setText("")
                self.customer_id_field.setText(str(customer_info[0]))
                self.fname_field.setText(str(customer_info[1]))
                self.mi_field.setText(str(customer_info[2]))
                self.lname_field.setText(str(customer_info[3]))
                self.ssn_field.setText(str(customer_info[4]))
                self.dob_field.setText(str(customer_info[5]))
                self.sex_field.setText(str(customer_info[6]))
                self.dl_field.setText(str(customer_info[7]))
                self.street_num_field.setText(str(customer_info[8]))
                self.street_name_field.setText(str(customer_info[9]))
                self.city_field.setText(str(customer_info[10]))
                self.state_field.setText(str(customer_info[11]))
                self.zip_field.setText(str(customer_info[12]))
                self.phone_num_field.setText(str(customer_info[13]))  
                self.email_field.setText(str(customer_info[14]))                                    

            # Execute the query to get checking account information
            query = f"""
                SELECT Account.AccountNo, Account.BranchNo, Account.OpenDate, Account.CurrentBalance
                FROM Account
                INNER JOIN Customer ON Account.CustomerID = Customer.CustomerID
                WHERE Account.CustomerID = ?
                OR Customer.SSN = ?
                OR Customer.DLNum = ?
            """
            cursor.execute(query, text, text, text)

            # Get the checking account information
            account_info = cursor.fetchone()

            if account_info:              
                # Display the checking account information
                self.error.setText("")
                self.checking_acct_num_field.setText(str(account_info[0]))
                self.checking_branch_num_field.setText(str(account_info[1]))
                self.checking_open_date.setText(str(account_info[2]))
                self.checking_balance_field.setText(str(account_info[3]))
                self.routing_num_field.setText("256074971")

            # Execute the query to get savings account information
            query = f"""
                SELECT Account.AccountNo, Account.BranchNo, Account.OpenDate, Account.CurrentBalance
                FROM Account
                INNER JOIN Customer ON Account.CustomerID = Customer.CustomerID
                WHERE (Account.CustomerID = ? 
                OR Customer.SSN = ?
                OR Customer.DLNum = ?) AND Account.AcctType = 'Savings'
            """
            cursor.execute(query, text, text, text)

            # Get the savings account information
            account_info = cursor.fetchone()

            if account_info:              
                # Display the savings account information
                self.error.setText("")
                self.savings_acct_num_field.setText(str(account_info[0]))
                self.savings_branch_num_field.setText(str(account_info[1]))
                self.savings_open_date_field.setText(str(account_info[2]))
                self.savings_balance_field.setText(str(account_info[3]))
                self.routing_num_field_savings.setText("256074971")              

            # Execute the query to get loan account information
            query = f"""
                SELECT Loan.LoanNo, Loan.LoanType, Loan.LoanAmt, Loan.LoanDate,
                Loan.Duration, Loan.LoanBalance, Loan.InterestRate, Loan.Status 
                FROM Loan
                INNER JOIN Customer ON Loan.CustomerID = Customer.CustomerID
                WHERE Customer.CustomerID = ? 
                OR Customer.SSN = ?
                OR Customer.DLNum = ?
            """
            cursor.execute(query, text, text, text)

            # Get the loan account information
            account_info = cursor.fetchone()

            if account_info:              
                # Display the loan account information
                self.error.setText("")
                self.loan_num_field.setText(str(account_info[0]))
                self.loan_type_field.setText(str(account_info[1]))
                self.loan_amount_field.setText(str(account_info[2]))
                self.loan_open_date_field.setText(str(account_info[3]))
                self.loan_duration_field.setText(str(account_info[4]))
                self.loan_balance_field.setText(str(account_info[5]))
                self.interest_rate_field.setText(str(account_info[6]))
                self.loan_status_field.setText(str(account_info[7]))                

            # Close the cursor and connection
            cursor.close()
            conn.close()

        except pyodbc.Error as e:
            # Handle any errors that occur during the connection or query execution
            print(f"Error: {str(e)}")
            self.error.setText("Error occurred while fetching account information.")


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
