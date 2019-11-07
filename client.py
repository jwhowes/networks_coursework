'''TODO:
	* Make the error message personalised to the status code
'''
import sys, json, os
from socket import *

boards = []
serverIP = sys.argv[1]
serverPort = int(sys.argv[2])

def send(message):
	clientSock = socket(AF_INET, SOCK_STREAM)
	clientSock.connect((serverIP, serverPort))
	clientSock.send(json.dumps(message).encode())
	res = json.loads(clientSock.recv(serverPort))
	clientSock.close()
	return res

def GET_BOARDS():
	global boards
	message = {"HEAD" : "GET_BOARDS"}
	res = send(message)
	if res["STATUS"] == 200:
		print("successfully retrieved boards")
		print("These are the current message boards:")
		boards = res["BODY"]
		for i in range(len(boards)):
			print(str(i + 1) + ". " + boards[i] + ";", end=" ")
		print()
	else:
		print("Couldn't get boards")
		exit()

def POST_MESSAGE():
	board = input("Enter the board number: ")
	title = input("Enter the message title: ")
	content = input("Enter the message content: ")
	message = {
			"HEAD" : "POST_MESSAGE",
			"BOARD" : board,
			"TITLE" : title,
			"CONTENT" : content
		}
	res = send(message)
	if res["STATUS"] == 200:
		print("Post successful")
	else:
		print("Error")

def GET_MESSAGES(board_num):
	if board_num <= 0 or board_num > len(boards):
		print("Board not found")
		return
	message = {
				"HEAD" : "GET_MESSAGES",
				"BOARD" : boards[board_num - 1]
			}
	res = send(message)
	if res["STATUS"] == 200:
		if len(res["MESSAGES"]) > 0:
			print("Success. Here are the messages: ")
			for message in res["MESSAGES"]:
				print()
				print("    " + message["TITLE"])
				print("        " + message["CONTENT"])
		else:
			print("There are no messages in that boad")
	else:
		print("Error")

def handle_instruction(instr):
	if instr == "POST":
		POST_MESSAGE()
	elif instr.isdigit():
		GET_MESSAGES(int(instr))
	elif instr == "QUIT":
		exit()
	else:
		print("Invalid instruction")
	print()

GET_BOARDS()

while True:
	instr = input("Enter your instruction: ")
	handle_instruction(instr)