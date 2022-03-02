import csv
from socket import AF_INET, SO_REUSEADDR, SOCK_STREAM, gethostname, socket
import sqlite3
from sqlite3 import Error
from ssl import SOL_SOCKET

from rich.table import Table

import pickle
from constants import B_DONE, B_INPUT, B_MESSAGE, DB_GETMATCH, DB_INSERTMATCH, DB_GETCHAMPS

from champlistloader import load_some_champs

sock = socket(AF_INET, SOCK_STREAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock.bind(('localhost', 1201))

HEADERSIZE = 10
con = None
try:
    con = sqlite3.connect("storage.db")
except Error as e:
    print("Couldn't connect to database")


def getMatchHistory():
    sql = """SELECT * FROM matches;"""
    try:
        c = con.cursor()
        c.execute(sql)
        con.commit()
    except Error as e:
        print(e)

    results = c.fetchall()

    matchHistory = Table(title="Match History")

    matchHistory.add_column("Match Id", style="cyan")
    matchHistory.add_column("Red Score", style="red")
    matchHistory.add_column("Blue Score", style="blue")
    matchHistory.add_column("Red champs", style="red")
    matchHistory.add_column("Blue champs", style="blue")


    for row in results[-3:]:
        matchHistory.add_row(str(row[0]), str(row[1]), str(row[2]), f"{row[3]}, {row[4]}", f"{row[5]}, {row[6]}")

    return matchHistory

def insertMatch(match):

    red_score, blue_score = match.score

    sql = f"""
    INSERT INTO matches (redScore, blueScore, Rc1, Rc2, Bc1, Bc2) 
    VALUES ({red_score}, {blue_score}, '{match.red_team.champions[0].name}', '{match.red_team.champions[1].name}', '{match.blue_team.champions[0].name}', '{match.blue_team.champions[1].name}');"""

    try:
        c = con.cursor()
        c.execute(sql)
        con.commit()
    except Error as e:
        print(e)

if __name__ == '__main__':

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

        sql2 = "CREATE TABLE IF NOT EXISTS matches(matchId INTEGER PRIMARY KEY , redScore integer, blueScore integer, Rc1 text, Rc2 text, Bc1 text, Bc2 text);"
        c.execute(sql2)

        for line in csvFile:
            sqlRow = f"INSERT INTO champions (name, rock, paper, scissor) VALUES ('{line[0]}', {int(line[1])}, {int(line[2])}, {int(line[3])});"
            try:
                c.execute(sqlRow)
                con.commit()
            except Error as e:
                print(e)






    while True:
        sock.listen()
        (cs, ip) = sock.accept()
        cs.send(B_MESSAGE + "Database connected!".encode() + B_DONE)
        message = bytes()
        while True:
            data = cs.recv(1024)

            if data == DB_GETCHAMPS:
                champs = load_some_champs()
                msg = pickle.dumps(champs)
                msg = bytes(f"{len(msg):<{HEADERSIZE}}", "utf-8") + msg
                cs.send(msg)
            elif data == DB_INSERTMATCH:
                firstIter = True
                full = b""    
                while True:
                    response = cs.recv(1024)
                    if firstIter:
                        msgLen = int(response[:HEADERSIZE])
                        firstIter = False
                    full += response

                    if len(full) - HEADERSIZE == msgLen:
                        print("Got the final match")
                        match = pickle.loads(full[HEADERSIZE:])
                        insertMatch(match)
                        break
                break
            elif data ==DB_GETMATCH:
                match = getMatchHistory()
                msg = pickle.dumps(match)
                msg = bytes(f"{len(msg):<{HEADERSIZE}}", "utf-8") + msg
                cs.send(msg)
                print("sent match history")

