'''TODO:
	* Work on implementing recvall better
'''
import sys, json
from socket import *

boards = []
serverIP = sys.argv[1]
serverPort = int(sys.argv[2])

def send(message):
	"""Sends a message to the server and returns the response"""
	clientSock = socket(AF_INET, SOCK_STREAM)
	if clientSock.connect_ex((serverIP, serverPort)) != 0:  # If the server is not online, an error is returned
		print("Error. Port unavailable")
		exit()
	clientSock.send(json.dumps(message).encode())  # The message is sent as a single encoded JSON object
	res = ""
	chunk = clientSock.recv(4096).decode()
	# Server responses are taken in chunks of 4096 until the entire response is received
	while len(chunk) == 4096:
		res += chunk
		chunk = clientSock.recv(4096).decode()
	res += chunk
	res = json.loads(res)  # Server response is converted to JSON for later processing
	clientSock.close()  # Once the server's response has been fully received, the TCP socket is closed
	return res

def GET_BOARDS():
	"""Processes a GET_BOARDS request"""
	global boards
	message = {"HEAD": "GET_BOARDS"}
	res = send(message)  # Sends a GET_BOARDS request to the server
	if res["STATUS"] == 200:
		# If there was no error, the boards are printed for the user
		print("Successfully retrieved boards")
		print("These are the current message boards:")
		boards = res["BOARDS"]
		for i in range(len(boards)):
			print(str(i + 1) + ". " + boards[i] + ";", end=" ")
		print()
	# If the server returned an error status codes, they are printed for the user
	elif res["STATUS"] == 422:
		print("Error 422. Unprocessable entity (missing or invalid data)")
	elif res["STATUS"] == 404:
		print("Couldn't get boards")
		exit()

def POST_MESSAGE():
	"""Processes a POST_MESSAGE request"""
	# All data is taken as input from the user
	board = input("Enter the board number: ")
	title = input("Enter the message title: ")
	content = input("Enter the message content: ")
	# If the board input by the user is not a number or the board number is invalid, a 404 error is printed
	if not board.isdigit():
		print("Error 404. Board not found")
		return
	if int(board) < 0 or int(board) > len(boards):
		print("Error 404. Board not found")
		return
	# If the board number is valid, a POST_MESSAGE request is constructed and sent to the server
	message = {
			"HEAD": "POST_MESSAGE",
			"BOARD": boards[int(board) - 1],
			"TITLE": title,
			"CONTENT": content
		}
	res = send(message)
	# Any errors are printed
	if res["STATUS"] == 200:
		print("Post successful")
	elif res["STATUS"] == 404:
		print("Error 404. Board not found")
	elif res["STATUS"] == 400:
		print("Error 400. Invalid token in message title")
	elif res["STATUS"] == 422:
		print("Error 422. Unprocessable entity (missing or invalid data)")
	else:
		print("Error")

def GET_MESSAGES(board_num):
	"""Processes a GET_MESSAGES request"""
	if board_num <= 0 or board_num > len(boards):  # If the board number is invalid, a 404 error is printed
		print("Error 404. Board not found")
		return
	# A GET_MESSAGES request is constructed and sent to the server
	message = {
				"HEAD": "GET_MESSAGES",
				"BOARD": boards[board_num - 1]
			}
	res = send(message)
	if res["STATUS"] == 200:
		# If there were no errors, the messages of the board are printed
		if len(res["MESSAGES"]) > 0:
			print("Success. Here are the messages: ")
			for message in res["MESSAGES"]:
				print()
				print("    " + message["TITLE"])
				print("        " + message["CONTENT"])
		else:
			print("There are no messages in that board")
	# Any errors are printed
	elif res["STATUS"] == 404:
		print("Error 404. Board not found")
	elif res["STATUS"] == 422:
		print("Error 422. Unprocessable entity (missing or invalid data)")
	else:
		print("Error")

def handle_instruction(instr):
	"""Processes user inputs"""
	if instr == "POST":
		POST_MESSAGE()
	elif instr.isdigit():
		GET_MESSAGES(int(instr))
	elif instr == "QUIT":
		exit()  # If a quit command is given, the client program exits.
	else:
		print("Error 400. Bad request")
	print()

GET_BOARDS()  # When the client first connects, a GET_BOARDS request is submitted to print the boards for the user

while True:
	# The client processes user requests until a QUIT command is given
	instr = input("Enter your instruction: ")
	handle_instruction(instr)