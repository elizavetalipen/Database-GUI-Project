# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QFileDialog
from PyQt5.QtWidgets import QLabel, QLineEdit, QInputDialog, QErrorMessage, QMessageBox, QTableWidgetItem
from PyQt5 import uic
import mysql.connector as sql
import sys
import csv
from databasetools import get_connection, read_csv, get_data_list
from databasetools import insert_data, delete_data, update_data


class App(QWidget):
    
    def __init__(self):
        super(App, self).__init__()
        self.show_ui()
        
        
    def validate(self):
        ''' Attempts to establish connection to database'''
        
        self.username = self.ui.lineEdit_user.text()
        self.psw = self.ui.lineEdit_psw.text()
        self.dbname = self.ui.lineEdit_dbname.text()
        self.tablename = self.ui.lineEdit_tablename.text()
        msg = QMessageBox()
        try:
            # trying connect to table
            self.setup_table(self.tablename, self.dbname, self.psw, self.username)
            msg.setText('Successfully connected!')
            msg.exec_()
            self.show_ui(table=True,filename='design/dbgui.ui')
            
        except Exception as e:
            print(e)
            msg.setText("Connection Error! Access denied")
            msg.setInformativeText("Please check entered data")
            msg.exec_()
            
        
    def show_ui(self,table = False, filename="design/logingui.ui"):
        
        self.ui=uic.loadUi(filename)
        self.ui.show()
        if table:
            self.show_table()
            # set up buttons
            self.ui.exitButton.clicked.connect(self.show_ui)
            self.ui.dbButton.clicked.connect(self.change_database)
            self.ui.tableButton.clicked.connect(self.change_table)
            self.ui.fileButton1.clicked.connect(self.load_file)
            self.ui.fileButton2.clicked.connect(self.save_file)
            self.ui.deleteButton.clicked.connect(self.delete_record)
            self.ui.saveButton.clicked.connect(self.save_changes)
        else:
            self.ui.loginButton.clicked.connect(self.validate)
      
            
        
    def setup_table(self, tablename, dbname, psw, username):

        query = 'select * from ' + tablename
        self.table = get_data_list(get_connection(dbname, psw, username), query)
        self.cols = list(self.table[1])  # table column names 
        self.records = list(self.table[0])  # list of table records
        
        
    def show_table(self):
        ''' Shows table content'''
        
        self.ui.tableWidget.setHorizontalHeaderLabels(self.cols)
        self.ui.tableWidget.setColumnCount(len(self.cols)) 
        self.ui.tableWidget.setRowCount(len(self.records)) 
        row_count = 0
        for row in self.records:
            for i in range(len(self.cols)):
                self.ui.tableWidget.setItem(row_count, i,  QTableWidgetItem(str(row[i])))
            row_count += 1
     
            
    def get_tableWidget_data(self):
       ''' Gets a list of a table widget rows'''
       
       recs, data = [], []
       for i in range(self.ui.tableWidget.rowCount()):
           for j in range(self.ui.tableWidget.columnCount()):
               recs.append(self.ui.tableWidget.item(i,j).text())
               
       n = self.ui.tableWidget.columnCount()      
       for i in range(0, len(recs),n):
           data.append(recs[i:i+n])
       return data
    
           
    def refresh(self):
        self.setup_table(self.tablename, self.dbname, self.psw, self.username)
        self.ui.tableWidget.clear()
        self.show_table()
      
     
    def change_table(self):
        ''' Switch to another table in current database '''
        try:
            self.tablename = self.ui.tableEdit.text()
            self.refresh()
            self.ui.tableEdit.clear()
        except Exception:
            self.ui.tableEdit.setText("Incorrect table name!")
      
            
    def change_database(self):
         ''' Switch to another database and choose new table '''
         try:
             self.dbname = self.ui.dbEdit.text()

             query = f'''select table_name from information_schema.tables 
             where table_type = 'BASE TABLE' and table_schema = '{self.dbname}' 
             and table_schema not in ('information_schema','mysql', 'performance_schema','sys') 
             order by table_name; '''
             
             # getting a list of all tables of the database
             tables =  get_data_list(get_connection(self.dbname, self.psw, self.username), query)[0]
             tables, listitems =  list(map(str,tables)), [] # to the right format
             for table in tables:
                 item = ''.join(s for s in table if s.isalnum())
                 listitems.append(item)
            
             item, ok = QInputDialog.getItem(self, "Choose a table","Table:", listitems, 0, False)
             if ok and item:
                self.tablename = item
                self.refresh()
                self.ui.dbEdit.clear()
                
         except Exception as e:
             print(e)
             self.ui.dbEdit.setText("Incorrect database name!")
     
             
    def save_file(self):
        ''' Save current table to a csv file'''
        
        msg = QMessageBox()
        fname, ok = QInputDialog.getText(self,  "Input path to file", "File path: ", QLineEdit.Normal, "")
        
        if ok and fname:
            try:
                with open(str(fname), 'w') as f:
                    writer = csv.writer(f, lineterminator='\n')
                    writer.writerow(self.cols) #column names - first line
                    
                    for tup in self.records:
                        writer.writerow(tup)
                        
                msg.setText('File Saved')
                msg.setInformativeText("Current table was written to a csv file")
                msg.exec_()
                
            except Exception as e:
                msg.setText('Error')
                msg.setInformativeText(str(e))
                msg.exec_()
      
                
    def load_file(self):
        ''' Load table data from a csv file '''
        file, ok = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()",
                                                       "", "CSV Files (*.csv);;")
        if ok:
            data = read_csv(fname=file)
            cols = data[0]
            filerecords = data[1::]
            self.ui.tableWidget.clear()
            self.ui.tableWidget.setColumnCount(len(cols)) 
            self.ui.tableWidget.setRowCount(len(filerecords)) 
            row_count = 0
            for row in filerecords:
                for i in range(len(cols)):
                    self.ui.tableWidget.setItem(row_count, i,  QTableWidgetItem(str(row[i])))
                row_count += 1
     
            
    def delete_record(self):
        ''' Delete selected row from table and database'''
        try:
            # getting selected row as list
            cur_row = self.ui.tableWidget.selectedItems()
            cur_row = [i.text() for i in cur_row]
            id_name = self.cols[0]
            # sending query to database
            del_query = f'delete from {self.tablename} where {id_name} = {cur_row[0]}'
            cur_con = get_connection(self.dbname, self.psw, self.username)
            cur_con.reset_session()
            cursor = cur_con.cursor()
            cursor.execute(del_query)
            cur_con.commit()
            # refreshing the view
            self.refresh()
            
        except Exception as e:
            print(e)
            msg = QMessageBox()
            msg.setText("Error")
            msg.setInformativeText("Note that first column of a table must be an ID")
            msg.exec_()
      
            
    def save_changes(self):
        ''' Save changes from working area to database '''
        
        tableWidget_data = self.get_tableWidget_data()
        changed_vals, del_records = [], []
        
        try:
            # if some records were deleted
            if len(tableWidget_data) < len(self.records):
                
                for i in range(len(self.records)):
                    rec = list(self.records[i])
                    for j in range(len(rec)):
                        rec[j] = str(rec[j])
                        
                        if rec[j] == 'None':
                            rec[j] = ''
                    if rec not in tableWidget_data:
                        del_records.append(rec)
                        
                for rec in del_records:
                    changed_vals.append(int(rec[0]))
                        
                del_query = f'delete from {self.tablename} where {self.cols[0]} in '
                del_query = del_query + str(tuple(changed_vals)) 
                cur_con = get_connection(self.dbname, self.psw, self.username)
                delete_data(cur_con, del_query)
                self.refresh()
                
            # if new records were added
            if len(tableWidget_data) > len(self.records):
                # appending
                new_records = tableWidget_data[len(self.records):]
                vals_count = '('+'%s,'*(len(new_records[0])-1)+'%s);'
                insert_query = f'insert ignore into {self.tablename} values ' + vals_count
                insert_data(get_connection(self.dbname, self.psw, self.username), insert_query, new_records)
                self.refresh()
                
            # checking if any cells were udated
            for i in range(len(tableWidget_data)):
                self.records[i] = list(self.records[i])
                if self.records[i] != tableWidget_data[i]:
                        
                    idd = self.records[i][0] # id
                            
                    for j in range(len(tableWidget_data[i])):
                        if str(self.records[i][j]) != tableWidget_data[i][j]:
                                    
                            colname = self.cols[j]
                            val = str(tableWidget_data[i][j])
                            if val != '':
                                changed_vals.append((colname,val, idd))
              
            for vals in changed_vals:
                colname, val, i = vals[0], vals[1], vals[2]
                upd_query = f'update {self.tablename} set {colname} = "{val}" where {self.cols[0]} = {i}; '
                update_data(get_connection(self.dbname, self.psw, self.username), upd_query)
                
        except Exception as e:
            print(e)
            msg = QMessageBox()
            msg.setText("Error")
            msg.setInformativeText("Note that first column of a table must be an ID")
            msg.exec_()
            

          
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    w = App()
    app.exec_() 

