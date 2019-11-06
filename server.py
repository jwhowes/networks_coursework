'''TODO (for client and server, in order):
	1. POST
	2. Get a list of 100 most recent messages (response option 1 from client)
	3. QUIT
'''

import sys
import os
import json
from socket import *

port = int(sys.argv[2])
IP = sys.argv[1]

def serve(socket, addr):
	message = json.loads(socket.recv(port).decode())
	res = {}
	if message["HEAD"] == "GET_BOARDS":
		res["STATUS"] = 200
		res["BODY"] = json.dumps(next(os.walk("./board"))[1])
	elif message["HEAD"] == "POST_MESSAGE":
		res["STATUS"] = 200
		print(message)
	else:
		res["STATUS"] = 400 #bad request
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