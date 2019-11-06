import sys, json, os
from socket import *

serverIP = sys.argv[1]
serverPort = int(sys.argv[2])

def send(message):
	clientSock = socket(AF_INET, SOCK_STREAM)
	clientSock.connect((serverIP, serverPort))
	clientSock.send(json.dumps(message).encode())
	res = json.loads(clientSock.recv(serverPort))
	clientSock.close()
	return res

def handle_instruction(instr):
	if instr == "POST":
		board = input("Enter the board number: ")
		title = input("Enter the message title: ")
		content = input("Enter the message content: ")
		message = {
				"HEAD" : "POST_MESSAGE",
				"BOARD" : board,
				"TITLE" : title,
				"CONTENT" : content
			}
	elif instr.isdigit():
		# TODO: send a request to the server for the 100 most recent message from that board.
	else:
		print("Invalid instruction")
		print()
		return
	res = send(message)
	if res["STATUS"] == 200:
		print("Instruction successful")
	else:
		print("Error") # TODO: make the error message personalised to the status code
	print()

message = {"HEAD" : "GET_BOARDS"}
boards_res = send(message)
if boards_res["STATUS"] == 200:
	print("successfully retrieved boards")
	print("These are the current message boards:")
	boards = boards_res["BODY"]
	for i in range(len(boards)):
		print(str(i + 1) + ". " + boards[i] + ";", end=" ")

print()
while True:
	instr = input("Enter your instruction: ")
	handle_instruction(instr)