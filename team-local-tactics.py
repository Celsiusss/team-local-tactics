import uuid
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from champlistloader import load_some_champs
from core import Champion, Match, Shape, Team

from socket import AF_INET, SO_REUSEADDR, SOCK_STREAM, gethostname, socket
from ssl import SOL_SOCKET

from constants import B_DONE, B_INPUT, B_MESSAGE, DB_GETCHAMPS, DB_GETMATCH, DB_INSERTMATCH

import sqlite3
from sqlite3 import Error

import pickle

HEADERSIZE = 10

def send_to_player(num, message):
    psockets[num].send(B_MESSAGE + message.encode() + B_DONE)

def send_to_all(message):
    for sock in psockets:
        sock.send(B_MESSAGE + message.encode() + B_DONE)

def request_input(num, message):
    psockets[num].send(B_INPUT + message.encode() + B_DONE)
    return recieve_from(num)

def recieve_from(num):
    while True:
        data = psockets[num].recv(1024)
        if data:
            return data.decode()


def enough_players():
    return len(psockets) == 2

def storeMatch(match: Match):
    msg = pickle.dumps(match)
    msg = bytes(f"{len(msg):<{HEADERSIZE}}", "utf-8") + msg
    dbSock.send(DB_INSERTMATCH)
    dbSock.send(msg)

def getChamps():
    msg = DB_GETCHAMPS
    dbSock.send(msg)
    fullResponse = b""
    firstIter =  True
    while True:
        response = dbSock.recv(1024)
        if firstIter:
            print("Got champs from DB")
            msglen = int(response[:HEADERSIZE])
            firstIter = False

        fullResponse += response
        if len(fullResponse) - HEADERSIZE == msglen:
            print("Got all the champs")

            champs = pickle.loads(fullResponse[HEADERSIZE:])
            return champs



def print_available_champs(champions: dict[Champion]) -> None:

    # Create a table containing available champions
    available_champs = Table(title='Available champions')

    # Add the columns Name, probability of rock, probability of paper and
    # probability of scissors
    available_champs.add_column("Name", style="cyan", no_wrap=True)
    available_champs.add_column("prob(:raised_fist-emoji:)", justify="center")
    available_champs.add_column("prob(:raised_hand-emoji:)", justify="center")
    available_champs.add_column("prob(:victory_hand-emoji:)", justify="center")

    # Populate the table
    for champion in champions.values():
        available_champs.add_row(*champion.str_tuple)
    

    console = Console(force_terminal=False)
    with console.capture() as capture:
        console.print(available_champs)

    send_to_all(capture.get())
    print(capture.get())


def input_champion(playerId: int,
                    prompt: str,
                    color: str,
                    champions: dict[Champion],
                    player1: list[str],
                    player2: list[str]) -> None:

    # Prompt the player to choose a champion and provide the reason why
    # certain champion cannot be selected
    while True:
        match request_input(playerId, f'[{color}]{prompt}'):
            case name if name not in champions:
                send_to_player(playerId, f'The champion {name} is not available. Try again.')
            case name if name in player1:
                send_to_player(playerId, f'{name} is already in your team. Try again.')
            case name if name in player2:
                send_to_player(playerId, f'{name} is in the enemy team. Try again.')
            case _:
                player1.append(name)
                send_to_all(f"Player {playerId + 1} chose {name}!")
                break


def print_match_summary(match: Match) -> None:

    EMOJI = {
        Shape.ROCK: ':raised_fist-emoji:',
        Shape.PAPER: ':raised_hand-emoji:',
        Shape.SCISSORS: ':victory_hand-emoji:'
    }

    # For each round print a table with the results
    for index, round in enumerate(match.rounds):

        # Create a table containing the results of the round
        round_summary = Table(title=f'Round {index+1}')

        # Add columns for each team
        round_summary.add_column("Red",
                                 style="red",
                                 no_wrap=True)
        round_summary.add_column("Blue",
                                 style="blue",
                                 no_wrap=True)

        # Populate the table
        for key in round:
            red, blue = key.split(', ')
            round_summary.add_row(f'{red} {EMOJI[round[key].red]}',
                                  f'{blue} {EMOJI[round[key].blue]}')


        console = Console(force_terminal=False)
        with console.capture() as capture:
            console.print(round_summary)
        send_to_all(capture.get())


    # Print the score
    red_score, blue_score = match.score
    send_to_all(f'Red: {red_score}\n'
          f'Blue: {blue_score}')

    # Print the winner
    if red_score > blue_score:
        send_to_all('\n[red]Red victory! :grin:')
    elif red_score < blue_score:
        send_to_all('\n[blue]Blue victory! :grin:')
    else:
        send_to_all('\nDraw :expressionless:')

    storeMatch(match)


def start_game() -> None:

    send_to_all('\n'
          'Welcome to [bold yellow]Team Local Tactics[/bold yellow]!'
          '\n'
          'Each player choose a champion each time.'
          '\n')

    champions = getChamps()
    print_available_champs(champions)
    print('\n')

    player1 = []
    player2 = []

    # Champion selection
    for _ in range(2):
        input_champion(0, 'Player 1', 'red', champions, player1, player2)
        input_champion(1, 'Player 2', 'blue', champions, player2, player1)

    print('\n')

    # Match
    match = Match(
        Team([champions[name] for name in player1]),
        Team([champions[name] for name in player2])
    )
    match.play()

    # Print a summary
    print_match_summary(match)


def showHistory():
    msg = DB_GETMATCH
    dbSock.send(msg)

    firstIter = True
    full = b""
    while True:
        response = dbSock.recv(1024)
        if firstIter:
            msgLen = int(response[:HEADERSIZE])
            firstIter = False
        full += response

        if len(full) - HEADERSIZE == msgLen:
            print("Got the match history")
            matchHistory = pickle.loads(full[HEADERSIZE:])
            break


    console = Console(force_terminal=False)
    with console.capture() as capture:
        console.print(matchHistory)
    return capture.get()




psockets = []



sock = socket(AF_INET, SOCK_STREAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

sock.bind(('localhost', 1200))

dbSock = socket(AF_INET, SOCK_STREAM)

dbSock.connect(('localhost', 1201))


if __name__ == '__main__':
    sock.listen()
    print(dbSock.recv(1024))
    while True:
        (cs, ip) = sock.accept()
        psockets.append(cs)
        print(f"Player {len(psockets)} connected")

        cs.send(B_MESSAGE + f"Connected as player {len(psockets)}".encode() + B_DONE)
        cs.send(B_MESSAGE + f"Last three matches played: \n{showHistory()}".encode() + B_DONE)

        if enough_players():
            start_game()
            sock.close()
            break
