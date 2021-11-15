from core import *
from threading import Thread


def processMenu(opt):
	tokens = opt.split()

	if tokens[0] == "CONNECT":
		#connect, check for ip and server port, should be default if blank
		print("you want to connect")

	elif tokens[0] == "UPLOAD":
		#upload, filename is required
		if len(tokens) < 2:
			print("Please include the name of the file you wish to upload.")

	elif tokens[0] == "DOWNLOAD":
		#download, filename is required
		if len(tokens) < 2:
			print("Please include the name of the file you wish to download.")

	elif tokens[0] == "DELETE":
		if len(tokens) < 2:
			print("Please include the name of the file you wish to delete.")
		else:
			path = tokens[1]
			path = "client_dir/" + path
			#handle file names with spaces in them
			try:
				os.remove(path)
			except FileNotFoundError:
				print("File not found.")

	elif tokens[0] == "DIR":
		print(os.listdir('client_dir'))

	else: print("Command not recognized.")

def main(argv) -> None:
    # Connect to a server waiting for a connection. Note: the server must be activated
    # first (otherwise an error will be thrown).


    print("Here are the available options:")
    print("CONNECT server_IP_address server_port")
    print("UPLOAD filename")
    print("DOWNLOAD filename")
    print("DELETE filename")
    print("DIR")
    print("Note: you must enter the name of the command in all caps.")
    opt = input()
    processMenu(opt)



    conn = socket(AF_INET, SOCK_STREAM)
    conn.connect((argv.host, argv.port))
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


if __name__ == "__main__":
    main(parse_args())
