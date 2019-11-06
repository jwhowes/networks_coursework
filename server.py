'''TODO (for client and server, in order):
	* Get a list of 100 most recent messages (response option 1 from client)
	* QUIT
	* Logging
'''

import sys, os, json
from datetime import datetime
from socket import *

IP = sys.argv[1]
port = int(sys.argv[2])

boards = next(os.walk("./board"))[1]

def serve(socket, addr):
	message = json.loads(socket.recv(port).decode())
	res = {}
	if message["HEAD"] == "GET_BOARDS":
		res["STATUS"] = 200
		res["BODY"] = boards
	elif message["HEAD"] == "POST_MESSAGE":
		if message["BOARD"].isdigit():
			if int(message["BOARD"]) > len(boards):
				res["STATUS"] = 404
			else:
				res["STATUS"] = 200
				message["TITLE"] = message["TITLE"].replace(" ", "_")
				message["TITLE"] = datetime.today().strftime("%Y%m%d-%H%M%S-") + message["TITLE"]
				message_file = open("./board/" + boards[int(message["BOARD"]) - 1] + "/" + message["TITLE"] + ".txt", "w+")
				message_file.write(message["CONTENT"])
				message_file.close()  # Can I just write the whole thing to a json file? (It would be a lot easier to read them).
		else:
			res["STATUS"] = 422
	else:
		res["STATUS"] = 400  # Bad request
	res = json.dumps(res)
	socket.send(res.encode())


serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((IP, port))
serverSocket.listen(5)
print("The server is listening on " + IP + ":" + str(port))

while True:
	clientSocket, addr = serverSocket.accept()
	serve(clientSocket, addr)
	clientSocket.close()