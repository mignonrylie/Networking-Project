#WHERE TO PICK UP WORKING
#still trying to get the download handshake thing to work
#i think all the correct steps are happening, but not in the correct threads
#gonna have to tag each queue message with an ID
#however for some reason using getpid() returns the same thing for two different threads....
#i don't know why the hell that's happening
#but you can get around this by finding the thread ID of each of the original two threads
#(they already print them)
#and passing them to their two children each. 
#pretty ugly solution but it's all i can come up with.









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
    #server_socket = socket(AF_INET, SOCK_STREAM)
    #server_socket.bind((argv.host, argv.port))
    #server_socket.bind((argv.host, 8081))
    #

    #server_socket2 = socket(AF_INET, SOCK_STREAM)
    #server_socket2.bind((argv.host, 8082))
    #print("Server is listening on port " + str(server_socket2.port))



    #threader(argv.host, 8081)
    #threader(argv.host, 8082)
    q = Queue() #shared by all threads to send messages around
    #task1 = Queue() #used by the queue monitor to tell server thread 1 what to do
    #task2 = Queue() #used by the queue monitor to tell server thread 2 what to do

    #potentially with args q, task1/2
    port8081 = Thread(target=threader, args=('', 8081, q))
    port8082 = Thread(target=threader, args=('', 8082, q)) #argv.host
    #handler = Thread(target=queueMonitor, args=(q, task1, task2))
    port8081.start()
    port8082.start()
    #handler.start()
    port8081.join()
    port8082.join()



def queueMonitor(q, task1, task2) -> None:
    print("queue handler is running")
    me = get_ident()
    if q is not None:
        thread1 = q.get()
        thread2 = q.get()
        print("here's thread 1:")
        print(thread1)
        print("here's thread 2:")
        print(thread2)


   
    if task1 is not None:
        print("here's the thread ID associated with task 1:")
        taskid1 = task1.get()
        print(taskid1)

    if task2 is not None:
        print("here's the thread ID associated with task 2:")
        taskid2 = task2.get()
        print(taskid2)

    #THIS IS SOMETHING IMPORTANT TO KEEP IN THE BACK OF YOUR HEAD
    #so far, it has worked out that thread 1 is always associated with queue 1, and thread 2 with queue 2.
    #so that's how i've written the while True: loop.
    #however, threads are weird and i can't guarantee that this will always be true.
    #so if we run into any issues with the wrong threads recieving commands, try adding extra safeguards here.
    while True:
        if q is not None: #this ensures that only the server tries to access a queue (it'll break if client tries)
                #print(q.qsize())
                if q.qsize() > 0:
                    info = q.get()

                    id = info.id
                    kind = info.kind
                    data = info.data

                    print("recieved " + kind)
                    print(id)


                    if id == thread1:
                        print("this alert was sent from thread 1.")
                        #tell thread 1 what to do
                        #put into the queue: the command and the data.
                        task = qInfo()
                        task.id = me
                        task.kind = kind
                        task.data = data

                        task1.put(task)
                    elif id == thread2:
                        print("this alert was sent form thread 2.")
                    else:
                        print("this shouldn't be possible... there's something wrong with your thread IDs.")


                    #the ID decides which task queue the command will go into.

#potentially q, task
def threader(host, port, q) -> None:
    id = get_ident()
    #q.put(id)



    #task.put(id)


    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', port))

    server_socket.listen()
    #print("Server is listening on port " + str(server_socket.port))
    print("hello")  
    client_sock, client_addr = server_socket.accept()
    print(f"[{ctime()}] Connected to client {client_addr}.")

    
    #both potentially with q, id, task
    sender_thread = Thread(target=serverSender, args=(client_sock, "server_dir", q, id))
    reciever_thread = Thread(target=receiver, args=(client_sock, "server_dir", q, id))

    sender_thread.start()
    reciever_thread.start()
    
    #sender_thread.join()
    #reciever_thread.join()


if __name__ == "__main__":
    main(parse_args())