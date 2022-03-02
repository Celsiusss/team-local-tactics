from core import Champion
import sqlite3
from sqlite3 import Error

def _parse_champ(res) -> Champion:
    name, rock, paper, scissors = res[0], res[1], res[2], res[3]
    return Champion(name, float(rock), float(paper), float(scissors))


def from_db(con) -> dict[str, Champion]:
    champions = {}
    sql = "SELECT * FROM champions;"
    curs = con.cursor()
    curs.execute(sql)
    result = curs.fetchall()

    for res in result:
            champ = _parse_champ(res)
            champions[champ.name] = champ
    return champions


def load_some_champs():
    con = None
    try:
        con = sqlite3.connect("storage.db")
    except Error as e:
        print(e)
        return None
    

    return from_db(con)
