# Isacc Reaves Tic-Tac-Toe Game 

This is a simple Tic-Tac-Toe game implemented using Python and sockets.

**How to play:**
1. **Start the server:** Run the `server.py` script with '-p PORT' arguments.
    * EX: > python3 server.py -p 5023
    * default server address is 0.0.0.0
3. **Connect clients:** Run the `client.py` script on two different machines or terminals with '-i SERVER_IP/DNS -p PORT' arguments.
    * EX: > python3 client.py -i 0.0.0.0 -p 5023
5. **Play the game:** Players take turns entering their moves. The first player to get three in a row wins!
    * Game will prompt you with the allowed command line inputs

**Functionality**
* server.py
  * Multiple Connection
    * Correcly drops connection greater than 2
  * Win Conidion
    * Able to detect all 8 different win conditions
    * Able to detect a draw condition
  * Announcment
    * Can queue an announcment to clients  
* Client.py
  * Able to accept up to two connections
    * Correcly drops connection greater than 2
  * 

**Files:**
* server.py
  * server python script
* client.py
  * client python script
* SOW.md
  * statement of work markdown
* Requirements.txt
  * libraries required to run scripts
  * should be blank since no external libarries are used
* README.md
  * information about game

**Technologies used:**
* Python
* Sockets
* Selector

**Additional resources:**
* [Link to Python documentation]
* [Link to sockets tutorial]
