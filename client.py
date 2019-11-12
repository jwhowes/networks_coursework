'''TODO:
	* Work on implementing recvall better
'''
import sys, json, os
from socket import *

boards = []
serverIP = sys.argv[1]
serverPort = int(sys.argv[2])

def send(message):
	clientSock = socket(AF_INET, SOCK_STREAM)
	if clientSock.connect_ex((serverIP, serverPort)) != 0:
		print("Error. Port unavailable")
		exit()
	clientSock.send(json.dumps(message).encode())
	res = ""
	chunk = clientSock.recv(4096).decode()
	while len(chunk) == 4096:
		res += chunk
		chunk = clientSock.recv(4096).decode()
	res += chunk
	res = json.loads(res)
	clientSock.close()
	return res

def GET_BOARDS():
	global boards
	message = {"HEAD" : "GET_BOARDS"}
	res = send(message)
	if res["STATUS"] == 200:
		print("Successfully retrieved boards")
		print("These are the current message boards:")
		boards = res["BODY"]
		for i in range(len(boards)):
			print(str(i + 1) + ". " + boards[i] + ";", end=" ")
		print()
	elif res["STATUS"] == 422:
		print("Error 422. Unprocessable entity (missing or invalid data)")
	elif res["STATUS"] == 404:
		print("Couldn't get boards")
		exit()

def POST_MESSAGE():
	board = input("Enter the board number: ")
	title = input("Enter the message title: ")
	content = input("Enter the message content: ")
	if not board.isdigit():
		print("Error 404. Board not found")
		return
	if int(board) < 0 or int(board) > len(boards):
		print("Error 404. Board not found")
		return
	message = {
			"HEAD" : "POST_MESSAGE",
			"BOARD" : boards[int(board) - 1],
			"TITLE" : title,
			"CONTENT" : content
		}
	res = send(message)
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
	if board_num <= 0 or board_num > len(boards):
		print("Error 404. Board not found")
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
			print("There are no messages in that board")
	elif res["STATUS"] == 404:
		print("Error 404. Board not found")
	elif res["STATUS"] == 422:
		print("Error 422. Unprocessable entity (missing or invalid data)")
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
		print("Error 400. Bad request")
	print()

GET_BOARDS()

while True:
	instr = input("Enter your instruction: ")
	handle_instruction(instr)