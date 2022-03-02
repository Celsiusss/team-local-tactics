# team-local-tactics
A game for the mandatory assignment

### Autors
 - Daniel Svalestad Liland
 - ROlf Martin Glomsrud


# Running the application:


## Step 1:
 - Run populateDb.py to populate the database of champions from some_champs.txt file
 - If you wish the clear the history in the database run populateDb.py with -cm flag

## Step 2:
 - Run db.py to initate the database server (this does not need to be restarted every game)
 - Run team-local-tactics.py to initiate the server
 - Then run client.py twice to connect two clients to the server
 - If you wish to run another game rerun team-local-tactics.py and two clients, db.py does not need to be restarted!
