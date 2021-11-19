from core import *
from threading import Thread

'''
Server with a working upload feature and back-to-back texting.
One thing to note, this implementation does not have a
graceful "exit" procedure (feel free to implement one). So to
end a run with this code, you will need to use CTRL+C for both
the server and the client.
'''


def main(argv) -> None:
    # Initialize the server socket that a client will connect to.
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((argv.host, argv.port))

    # Wait to establish a connection with a client that tries to connect.~
    server_socket.listen()
    print('Socket is listening...')

    client_sock, client_addr = server_socket.accept()
    print(f"[{ctime()}] Connected to client {client_addr}.")

    # Initialize the threads for both sending/receiving functionalities and then
    # start the threads. The purpose of this is to allow the server to have a more
    # seamless communication with the client on the other end. Otherwise, communication
    # becomes more complicated.
    sender_thread = Thread(target=sender, args=(client_sock, "server_dir"))
    receiver_thread = Thread(target=receiver, args=(client_sock, "server_dir"))

    # Start and join the threads.
    sender_thread.start()
    receiver_thread.start()
    sender_thread.join()
    receiver_thread.join()


if __name__ == "__main__":
    main(parse_args())
