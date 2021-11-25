from core import *
from threading import Thread

'''
Server with a working upload feature and back-to-back texting.
One thing to note, this implementation does not have a
graceful "exit" procedure (feel free to implement one). So to
end a run with this code, you will need to use CTRL+C for both
the server and the client.
'''

def threader(server_socket) -> None:
    server_socket.listen()
    client_sock, client_addr = server_socket.accept()
    print(f"[{ctime()}] Connected to client {client_addr}.")

    sender_thread = Thread(target=sender, args=(client_sock, "server_dir"))
    reciever_thread = Thread(target=receiver, args=(client_sock, "server_dir"))

    sender_thread.start()
    reciever_thread.start()


def main(argv) -> None:
    # Initialize the server socket that a client will connect to.
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((argv.host, argv.port))

    threader(server_socket)
    threader(server_socket)



if __name__ == "__main__":
    main(parse_args())
