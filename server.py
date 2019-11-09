import sys, os, json
from datetime import datetime
from socket import *

IP = sys.argv[1]
port = int(sys.argv[2])

boards = next(os.walk("./board"))[1]

def serve(socket, addr):
	global boards
	message = json.loads(socket.recv(port).decode())
	res = {}
	if "HEAD" not in message:
		res["STATUS"] = 422
		log_entry = addr[0] + ":" + str(addr[1]) + "\t" + datetime.today().strftime("%A %d/%m/%Y %H:%M:%S") + "\t" + "N/A" + "\t"
	else:
		log_entry = addr[0] + ":" + str(addr[1]) + "\t" + datetime.today().strftime("%A %d/%m/%Y %H:%M:%S") + "\t" + message["HEAD"] + "\t"
		if message["HEAD"] == "GET_BOARDS":
			boards = next(os.walk("./board"))[1]  # Should I be retrieving boards again every time?
			if len(boards) == 0:
				res["STATUS"] = 404
			else:
				res["STATUS"] = 200
				res["BODY"] = boards
		elif message["HEAD"] == "POST_MESSAGE":
			if "BOARD" not in message or "TITLE" not in message or "CONTENT" not in message:
				res["STATUS"] = 422
			else:
				if message["BOARD"] not in boards:
					res["STATUS"] = 404  # Board not found
				else:
					res["STATUS"] = 200
					message["TITLE"] = message["TITLE"].replace(" ", "_")
					message["TITLE"] = datetime.today().strftime("%Y%m%d-%H%M%S-") + message["TITLE"]
					try:
						message_file = open("./board/" + message["BOARD"] + "/" + message["TITLE"] + ".txt", "a+")
						message_file.write(message["CONTENT"])
						message_file.close()  # Can I just write the whole thing to a json file? (It would be a lot easier to read them).
					except:
						res["STATUS"] = 400
		elif message["HEAD"] == "GET_MESSAGES":
			res["MESSAGES"] = []
			if "BOARD" not in message:
				res["STATUS"] = 422
			elif message["BOARD"] in boards:
				res["STATUS"] = 200
				i = 0
				while i < 100 and i < len(os.listdir("./board/" + message["BOARD"])):
					message_file = open("./board/" + message["BOARD"] + "/" + os.listdir("./board/" + message["BOARD"])[i], "r")
					res["MESSAGES"].append({"TITLE" : os.listdir("./board/" + message["BOARD"])[i], "CONTENT" : message_file.readline()})
					message_file.close()
					i += 1
			else:
				res["TITLE"] = 404
		else:
			res["STATUS"] = 400  # Bad request
	if res["STATUS"] == 200:
		log_entry += "OK\n"
	else:
		log_entry += "Error\n"
	log_file = open("server.log", "a+")
	log_file.write(log_entry)
	log_file.close()
	res = json.dumps(res)
	socket.send(res.encode())


serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((IP, port))
serverSocket.listen(5)
print("The server is running on " + IP + ":" + str(port))

while True:
	clientSocket, addr = serverSocket.accept()
	serve(clientSocket, addr)
	clientSocket.close()