import sys, os, json, threading
from datetime import datetime
from socket import *

if len(sys.argv) < 3:  # If the user doesn't supply enough arguments, print error and exit
	print("Error. Please enter IP address and port number")
	exit()

IP = sys.argv[1]
port = sys.argv[2]
if not port.isdigit():  # If the port is not an integer, print error and exit
	print("Error. Port number should be an integer")
	exit()
port = int(port)

boards = next(os.walk("./board"))[1]
if len(boards) == 0:  # If there are no boards, print error and exit.
	print("Error. No message boards defined")
	exit()

lock = threading.Lock()

class ClientSocket(threading.Thread):
	def __init__(self, socket, addr):
		"""Creates space for a ClientSocket thread as well as supplying it with a socket and sender address"""
		threading.Thread.__init__(self)
		self.socket = socket
		self.addr = addr
	def run(self):
		"""Serves a request"""
		global boards, lock  # boards variable contains a list of boards
		# lock variable is used to lock other threads during critical sections
		message = ""
		chunk = self.socket.recv(4096).decode()
		# A message is read in chunks of 4096 characters until it is fully read.
		while len(chunk) == 4096:
			message += chunk
			chunk = self.socket.recv(4096).decode()
		message += chunk
		message = json.loads(message)  # Once the message is received, it is converted form JSON ready to be processed
		res = {}
		if "HEAD" not in message:
			log_entry = self.addr[0] + ":" + str(self.addr[1]) + "\t" + datetime.today().strftime("%A %d/%m/%Y %H:%M:%S") + "\t" + "N/A" + "\t\t"
			# If the message contains no HEAD (instruction), error 422 is returned.
			res["STATUS"] = 422
		else:
			# Log entry string starts with the current time.
			log_entry = self.addr[0] + ":" + str(self.addr[1]) + "\t" + datetime.today().strftime("%A %d/%m/%Y %H:%M:%S") + "\t" + message["HEAD"] + "\t"
			if message["HEAD"] == "GET_BOARDS":
				# If the message head is GET_BOARDS, a list of boards is sent back to the client
				if len(boards) == 0:
					res["STATUS"] = 404  # No boards found.
				else:
					res["STATUS"] = 200
					res["BOARDS"] = boards
			elif message["HEAD"] == "POST_MESSAGE":
				# If the message head is POST_MESSAGE, the message is inserted into the requested board
				if "BOARD" not in message or "TITLE" not in message or "CONTENT" not in message:
					res["STATUS"] = 422  # Unprocessable Entity (information missing)
				else:
					if message["BOARD"] not in boards:
						res["STATUS"] = 404  # Board not found
					else:
						# If all information can be found, the message is inserted into the correct board
						res["STATUS"] = 200
						message["TITLE"] = message["TITLE"].replace(" ", "_")
						message["TITLE"] = datetime.today().strftime("%Y%m%d-%H%M%S-") + message["TITLE"]
						try:
							# A lock is acquired during critical sections (such as file writing)
							# to block other threads from accessing the files at the same time and causing errors
							lock.acquire()
							message_file = open("./board/" + message["BOARD"] + "/" + message["TITLE"] + ".txt", "w+")
							message_file.write(message["CONTENT"])
							message_file.close()
							lock.release()
							# After a thread is done with a file, the lock is released
							# allowing other threads to access the file
						except:
							res["STATUS"] = 400  # Bad request (some issue in the file contents or title)
			elif message["HEAD"] == "GET_MESSAGES":
				# If the message head is GET_MESSAGES, the messages from that board are sent back
				res["MESSAGES"] = []
				if "BOARD" not in message:
					res["STATUS"] = 422  # Unprocessable entity (information missing)
				elif message["BOARD"] in boards:
					res["STATUS"] = 200
					i = 0
					# The messages are sorted by order of date and the top 100 are returned
					files = sorted(os.listdir("./board/" + message["BOARD"]), key=lambda x: os.stat("./board/" + message["BOARD"] + "/" + x).st_mtime)
					while i < 100 and i < len(files):
						# No need for lock here as the thread is just reading from the file
						message_file = open("./board/" + message["BOARD"] + "/" + files[i], "r")
						res["MESSAGES"].append({"TITLE": files[i], "CONTENT": message_file.readline()})
						message_file.close()
						i += 1
				else:
					res["TITLE"] = 404  # Board not found (or no messages in the board)
			else:
				res["STATUS"] = 400  # Bad request (invalid HEAD)
		# Once the request has been processed and the response constructed, the log file is written
		if res["STATUS"] == 200:
			log_entry += "OK\n"
		else:
			log_entry += "Error\n"
		lock.acquire()  # Ones again, a lock is required during this critical section.
		log_file = open("server.log", "a+")
		log_file.write(log_entry)
		log_file.close()
		lock.release()
		res = json.dumps(res)  # The response is converted to JSON and sent back to the client
		self.socket.send(res.encode())
		self.socket.close()  # This is not persistent TCP so once the response has been sent, the socket is closed


serverSocket = socket(AF_INET, SOCK_STREAM)  # Main TCP server socket

try:
	serverSocket.bind((IP, port))
except error as e:  # If there is an error when setting up the server socket, print error and exit.
	print(e)
	exit()

serverSocket.listen(1)
print("The server is running on " + IP + ":" + str(port))
while True:
	clientSocket, addr = serverSocket.accept()
	clientThread = ClientSocket(clientSocket, addr)  # When a client makes a request a new thread is created for them
	clientThread.start()  # The thread is then run until termination (other threads may also run at the same time)
	# This thread-per-client mechanism allows for multiple requests from multiple clients simultaneously
