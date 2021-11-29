from core import *
from threading import Thread, get_ident, get_native_id

'''
Server with a working upload feature and back-to-back texting.
One thing to note, this implementation does not have a
graceful "exit" procedure (feel free to implement one). So to
end a run with this code, you will need to use CTRL+C for both
the server and the client.
'''

def main(argv) -> None:
    # Initialize the server socket that a client will connect to.
    q = Queue() #shared by all threads to send messages around

    port8081 = Thread(target=threader, args=('', 8081, q))
    port8082 = Thread(target=threader, args=('', 8082, q))

    port8081.start()
    port8082.start()

    port8081.join()
    port8082.join()

def threader(host, port, q) -> None:
    id = get_ident()

    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', port))

    server_socket.listen()
    client_sock, client_addr = server_socket.accept()
    print(f"[{ctime()}] Connected to client {client_addr}.")

    sender_thread = Thread(target=serverSender, args=(client_sock, "server_dir", q, id))
    reciever_thread = Thread(target=receiver, args=(client_sock, "server_dir", q, id))

    sender_thread.start()
    reciever_thread.start()

if __name__ == "__main__":
    main(parse_args())