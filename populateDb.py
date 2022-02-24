import csv
import sqlite3 as sqlite3
from sqlite3 import Error

with open("some_champs.txt", "r") as f:
    csvFile = csv.reader(f)
    con = None
    try:
        con = sqlite3.connect("storage.db")
    except Error as e:
        print(e)
    
    sql = "CREATE TABLE IF NOT EXISTS champions(name text PRIMARY KEY, rock integer, paper integer, scissor integer NOT NULL)"

    c = con.cursor()

    c.execute(sql)
    con.commit()

    for line in csvFile:
        sqlRow = f"INSERT INTO champions (name, rock, paper, scissor) VALUES ('{line[0]}', {int(line[1])}, {int(line[2])}, {int(line[3])});"
        c.execute(sqlRow)
        con.commit()
