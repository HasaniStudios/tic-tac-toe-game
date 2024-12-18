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

**Functionality:**
* server.py
  * Multiple Connections
    * Correcly drops connections greater than 2.
  * Win Conidion
    * Able to detect all 8 different win conditions of tic tac toe.
    * Able to detect a draw condition.
    * Lets clients know a win condition has been reached.
  * Announcment
    * Can queue an announcment to clients.
  * Parses messags
    * parses messages recived by clinet by socket and message type or ID.    
  * Parses Turn
    * Recieves turn from player and sends the correct update to each player.
  * Maintains list of clients
  * Beginning trun management
    * server determines who will take the first turn randomly  
  * Manages disconnections
    * Removes player from game data
    * sends an announcmnet to other player
    * If a player is still connected they become player X and wait for another player
  * Player Identification
    * First player to connect is considered player X
    * Second player to connect is considered player O
    * Actualy code does not use X and O to differentiate players and instead users the location in an array.
* client.py
  * Able to accept up to two connections
    * Correcly drops connection greater than 2.
  * User Interface
    * Displays current board and moves that could be taken.
    * Correctly prompts user whose turn it is.
  * User Input
    * Correctly only allows user to pick between 0-9 inputs on their turn.
    * Correctly allows player to enter B to quit game.
    * Correctly allows player to enter A to restart game only after a game has been player.
    * Tells player if they made an incorrect input
  * Turn based gameplay
    * Client is able to determine if it is their turn and allows them to make a move.
  * Win Condition
    * Displays correct win or lose condition
    * Ask player if they would like

**Communication Protocol:**
* Bytes 0-2
   * Length of incoming message
   * Reasoning: Allows reciever to take appropriate data out of reciever
* Byte 3
   * Type of message or message ID
   * Reasoning: Allows client and server to
* Byte 4-6
   * Seperation bits
   * Reasoning: Allows reciever to parse between header and data
* Byte 7:
   * Data needed for message type
   * Reasoning: Allows for multi-length messages

**Server-side Messages:**
* ID:1 - announcment
  * sends a message that should be directly to displayed to the user by there client. 
* ID:2 - update
  * sends a client the updated game board and if their turn is next.
* ID:8 - winner
  * sends the result of the game to the client
  
**Client-side Messages:**
* ID:5 - turn
  * sends turn made to server.
  * turns are from 1-9 based off the tic tac toe gameboard. 
* ID:6 - restart
  * sends a message requesting restart after a conclusion of a game.
  * this allows server to wipe game and tell other client that the game is restarting.
* ID:9 - disconnection
  * sends a message telling the client is disconnecting
  * this allows the server to free resources.
  * It is executed after a keyboard interrupt and when entering B.

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

**Retrospective:**

This is my first true project working with socket programming and honestly it was more enjoyable than I expected. At the beginning of the project I expected it to be a monumental task. It honestly was pretty straight foward and I didn't run into many detremental bugs when programming. When originally programming the project I did not account for a user interface like PyQt or Tkinter to be blocking. Both PyQt and Tkinter, the user interfaces I have the most experince with, both have their own control loops. This means after I wrote my own control loop, if I were to convert it to have a proper user interface I'd need to convert my fully functional command-line control loop to a user interface control loop. With an already functional program that thought of changing all my code was pretty daunting.

However, as previously stated implememnting the control loop of my game worked very well. By figuring out what data needed to be transported to each client and therefore sent to the server it was easy to implemement a different function for each type of recieved message and each type of message to send. 

I originally had a heart beat functionality that would let the server and client know that each other are still there. This wasn't such a bad idea, but I ended up cutting the functionality out since it would complicate the server-client messaging system. This would however detect unwanted disconnections by 

**Additional resources:**
* [https://docs.python.org/3/]
