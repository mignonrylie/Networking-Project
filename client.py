#import sys
#import traceback

from core import *
from threading import Thread

#here's a comment 2

connected = 0

def commandConnect(argv):

	conn = socket(AF_INET, SOCK_STREAM)
	try:
		conn.connect((argv.host, argv.port))
	except ConnectionRefusedError:
		print("Unable to connect.")
	else:
		connected = 1;

		print("You now have access to the following commands:")
		print("UPLOAD filename")
		print("DOWNLOAD filename")
		print("Or simply type the message you'd like to send.")
		print(f"[{ctime()}] Connected to server '{argv.host}:{argv.port}'.")

		# Initialize the threads for both sending/receiving functionalities and then
		# start the threads. The purpose of this is to allow the client to have a more
		# seamless communication with the server on the other end. Otherwise, communication
		# becomes more complicated.
		sender_thread = Thread(target=sender, args=(conn, "client_dir"))
		receiver_thread = Thread(target=receiver, args=(conn, "client_dir"))

		# Start and join the threads.
		sender_thread.start()
		receiver_thread.start()
		sender_thread.join()
		receiver_thread.join()



def processMenu(opt, argv):
	tokens = opt.split()

	if tokens[0] == "CONNECT":
		#connect, check for ip and server port, should be default if blank
		if len(tokens) > 1:
			#get ip
			argv.host = tokens[1]
			#handle something? it should be treated as a string no matter what, i think.

			if len(tokens) > 2:
				#get port
				try:
					port = tokens[2]
					port = int(port)
				except ValueError:
					print("Invalid port; 8080 will be used")
				else:
					argv.port = port
		commandConnect(argv)

	elif tokens[0] == "UPLOAD":
		print("You must connect first before this command can be used.")

	elif tokens[0] == "DOWNLOAD":
		print("You must connect first before this command can be used.")

	elif tokens[0] == "DELETE":
		if len(tokens) < 2:
			print("Please include the name of the file you wish to delete.")
		else:
			try:
				deleteFile(tokens)
			except FileNotFoundError:
				print("File not found.")
			"""
		else:
			path = tokens[1]
			path = "client_dir/" + path
			#handle file names with spaces in them
			try:
				os.remove(path)
			except FileNotFoundError:
				print("File not found.")"""

	elif tokens[0] == "DIR":
		print(os.listdir('client_dir'))

	else: print("Command not recognized.")

def main(argv) -> None:
    # Connect to a server waiting for a connection. Note: the server must be activated
    # first (otherwise an error will be thrown).

	print("These are the currently available commands:")
	print("CONNECT server_IP_address server_port")
	print("DELETE filename")
	print("DIR")

	while not(connected):
		processMenu(input(f">"), argv)


if __name__ == "__main__":
    main(parse_args())
