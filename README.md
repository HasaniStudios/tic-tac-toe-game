# Isaac Reaves Tic-Tac-Toe Game 

This is a simple Tic-Tac-Toe game implemented using Python and sockets by Isaac Reaves.

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
    * Correcly drops connections greater than 2.
  * Win Conidion
    * Able to detect all 8 different win conditions of tic tac toe.
    * Able to detect a draw condition.
  * Announcment
    * Can queue an announcment to clients.
  * Prases Turn
    * Recieves turn from player and sends the correct update to each player.       
* Client.py
  * Able to accept up to two connections
    * Correcly drops connection greater than 2.
  * User Interface
    * Displays current board and moves that could be taken.
    * Correctly prompts user whose turn it is.
  * User Input
    * Correctly only allows user to pick between 0-9 inputs on their turn.
    * Correctly allows player to enter B to quit game.
    * Correctly allows player to enter A to restart game only after a game has been player.

**Communication Protocol**
* Bytes 0-2
   * Length of incoming message
   * Reasoning: Allows reciever to take appropriate data out of reciever
* Byte 3
   * Type of message
   * Reasoning: Allows client and server to
* Byte 4-6
   * Seperation bits
   * Reasoning: Allows reciever to parse between header and data
* Byte 7:
   * Data needed for message type
   * Reasoning: Allows for multi-length messages

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
* [https://docs.python.org/3/]
