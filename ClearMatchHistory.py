import csv
import sqlite3 as sqlite3
from sqlite3 import Error
import sys


con = None
try:
    con = sqlite3.connect("storage.db")
except Error as e:
    print(e)

c = con.cursor()


sqlClear = "DELETE FROM matches"
c.execute(sqlClear)
con.commit()
