
import argparse
import os
import pickle
from queue import Queue
#import wave    get rifd of wave
#import scipy.io.wavfile
#import numpy

import threading
from threading import *

#from dill import dumps, loads #are we allowed to use libraries that require installing?

from PIL import Image, UnidentifiedImageError
from socket import socket, AF_INET, SOCK_STREAM
from time import ctime
from utils import *



#upload is currently broken. wave likely isn't necessary, as are dill, scipy, and numpy.
#look into uploading by converting all files to byte streams with pickle


#wave for handling .WAV audio files
#queue for letting the different server processes talk to each other for download

class qInfo:
    id = None
    kind = None
    data = None

def deleteFile(tokens) -> None:
    path = tokens[1]
    path = "client_dir/" + path
    try:
        os.remove(path)
    except FileNotFoundError:
        raise #this lets the original menu function handle the error, but it breaks when called from sanitizeInput






















def sanitizeInput() -> str:
    raw = input()
    tokens = raw.split()
    """
    try:
        command = tokens[0]
    except IndexError:
        print("Please enter a command.")
        return sanitizeInput()"""
    if tokens[0] == "CONNECT": #done
        print("You are already connected. Try a different command.")
        return sanitizeInput()

    elif tokens[0] == "UPLOAD": #done
        if len(tokens) < 2:
            print("Please include the name of the file you wish to upload:")
            return sanitizeInput()
        else:
            return ":UPLOAD: " + tokens[1]

    elif tokens[0] == "DOWNLOAD": #done
        if len(tokens) < 2:
            print("Please include the name of the file you wish to download.")
            return sanitizeInput()
        else:
            return ":DOWNLOAD: " + tokens[1]

    elif tokens[0] == "DELETE": #done
    #if it's a command that doesn't result in a message being sent, recursion is necessary to ensure that
    #the sender function has something to send, and it doesn't break.
        if len(tokens) < 2:
            print("Please include the name of the file you wish to delete.")
            return sanitizeInput()
        else:
            try:
                deleteFile(tokens)
            except FileNotFoundError:
                print("File not found.")
                return sanitizeInput()


    elif tokens[0] == "DIR": #done
        #enable for server directory
        print(os.listdir('client_dir'))
        return sanitizeInput()

    else:
        return raw















def parse_args() -> argparse.Namespace:
    """Simple function that parses command-line arguments. Currently supports args
       for hostname and port number.

    Returns:
        argparse.Namespace: Arguments for establishing client-server connection.
    """
    args = argparse.ArgumentParser()
    args.add_argument("-p", "--port", type=int, default=8080)
    args.add_argument("-n", "--host", type=str, default="localhost")
    return args.parse_args()

















#detect unsupported files and give warning?
def upload(conn: socket, filename: str) -> None:
    """Prepares a message to be sent with an IMAGE file attached to it.

    Args:
        conn (socket): Socket to send message with image to.
        filename (str): Name of the file.
    """
    
    try:
        img = Image.open(filename)
        #img = open(filename, 'wb')
        message = {
            PACKET_HEADER: ":UPLOAD:",
            PACKET_PAYLOAD: {
                "filename": filename,
                "img": img
            }
        }
    except UnidentifiedImageError:
        try:
            txt = open(filename)
            message = {
                PACKET_HEADER: ":"
            }
        except:
            pass
    if message:
        try:
            send_msg(conn, pickle.dumps(message))
        except TypeError:
            #send_msg(conn, dumps(message))
            print("TypeError")


















def downloadReq(conn: socket, filename: str) -> None:
    """Sends a basic download request with a filename
    """
    message = {
        PACKET_HEADER: ":DOWNLOAD:",
        PACKET_PAYLOAD: {
            "filename": filename
        }
    }
    if message:
        send_msg(conn, pickle.dumps(message))

#whichever function calls this must pass q
#whatever gets pushed to the queue must be tagged with the thread's socket number to guarantee that it actually gets sent to the other client
#though the task queue is not used here, it must be included so that it can be passed to the function where it IS used.
#potential other parameters: q = None, id = None, task = None
def sender(conn: socket, home_dir: str) -> None:
    """Function that will be used in a thread to handle any outgoing messages to
       the provided socket connection.

    Args:
        conn (socket): Socket connection to send messages to.
        home_dir (str): Directory where the client/server's data will be stored.
    """
    while True:
        """
        #this should only ever be added to by the queue manager, but it wouldn't be a bad idea to check the ID regardless
        #oh wait this thread doesn't know the queue's ID.
        #well, just keep this in mind as a potential bug fix later
        if task is not None:
            #so the thread doesn't seem to be getting its task.
            #that i believe is happening is that the queue manager is correctly putting the task in the queue,
            #but the thread is at a point where it's waiting for user input.
            #so it isn't able to check the queue.


            #i think what i'll do to fix this is set a timer.
            #on each calling of sender, a timer will be set in which the thread does not except continuously check the queue.
            #i don't want this timer to be too long, so it can accept user input.
            #but a server doesn't need to be able to accept user input, does it?

            if task.qsize() > 0:
                print("I've recieved a task!")

                task = task.get()
                kind = task.kind
                data = task.data

                print("the task is to:")
                print(kind)
                print(task)
        

        
        if q is not None: #this ensures that only the server tries to access a queue (it'll break if client tries)
            print(q.qsize())
            if q.qsize() > 0:

            info = q.get() #checking if there is a message from the other thread in the queue.
            #this works! the other thread successfully gets what is put from the other thread.
            print(info)
            if info[1] == "request":
                filename = q.get()
                #send request to the client
                print("gonna try to send a message to the client")
                message = {
                    PACKET_HEADER: ":REQUEST:",
                    PACKET_PAYLOAD: filename
                }
                if message:
                        send_msg(conn, pickle.dumps(message))"""

        try:
            #message = input(f"[{ctime()}] ")
            message = sanitizeInput()
            try:
                command = message.split()[0]
            except AttributeError:
                pass
            if command == ":UPLOAD:":
                filename = message.split()[1]
                upload(conn, f"{home_dir}\{filename}")
            elif command == ":DOWNLOAD:":
                filename = message.split()[1]
                downloadReq(conn, filename)
            else:
                message = {
                    PACKET_HEADER: ":MESSAGE:",
                    PACKET_PAYLOAD: message
                }
                if message:
                    send_msg(conn, pickle.dumps(message))
        except KeyboardInterrupt:
            conn.close()
            raise


















def serverSender(conn: socket, home_dir: str, q = None, id = None) -> None:
    #the server doesn't actually need to recieve user input, it just has to respond to an incoming message.
    #i don't think the server should ever need to send a message except for the download situation
    #so i think this function will be continuously checking the queue.
    print("my id is " + str(id))
    print("uhhhhhhh hellooooooooo")
    while True:
        if q is not None:
            if q.qsize() > 0:

                req = q.get()
                kind = req.kind
                reqid = req.id
                data = req.data
                print("I received a req " + kind)
                #print("the data is " + data)
                print("the id is " + str(reqid) + " and my id is " + str(id))

                
                #lock = threading.RLock
                #con = threading.Condition(lock)
                lock = threading.Lock()
                #lock.acquire()
                
                if reqid == id:
                    print("the IDs are the same")
                    q.put(req)
                    #threading.Condition.wait(lock)
                    #con.wait()
                    #lock = threading.Lock
                    print(str(id) + "is locking itself.")
                    lock.acquire()
                else:
                    print("the IDs are different, so I'm going to process this.")

                #if the request's id matches the current ID, just put it back in the queue.
                #only do anything if it came from the other thread.


                #kind should ALWAYS be defined.
                #ie the only things that should ever be pushed to the queue are qInfo objects.
                    if kind == "request":
                        message = {
                            PACKET_HEADER: ":REQUEST:",
                            PACKET_PAYLOAD: data
                        }
                        if message:
                            send_msg(conn, pickle.dumps(message))
                            #release()

                    elif kind == "response":
                        message = {
                            PACKET_HEADER: ":RESPONSE:", #this originally said REQUEST
                            PACKET_PAYLOAD: data#[PACKET_PAYLOAD]
                        }
                        if message:
                            send_msg(conn, pickle.dumps(message))
                            #print(PACKET_PAYLOAD)
                            #release()
                    #threading.notify_all()
                    #con.notify_all()
                    if lock.locked():
                        print("the other thread was locked, so I unlocked it")
                        lock.release()
                        #lock.release()
                """
        try:

            #message = sanitizeInput()
            try:
                command = message.split()[0]
            except AttributeError:
                pass
            if command == ":UPLOAD:":
                filename = message.split()[1]
                upload(conn, f"{home_dir}\{filename}")
            elif command == ":DOWNLOAD:":
                filename = message.split()[1]
                downloadReq(conn, filename)
            else:
                message = {
                    PACKET_HEADER: ":MESSAGE:",
                    PACKET_PAYLOAD: message
                }
                if message:
                    send_msg(conn, pickle.dumps(message))
        except KeyboardInterrupt:
            conn.close()
            raise"""



















#whichever function calls this must pass q.
#potential other parameters: q = None, conn = None, id = None
def handle_received_message(message: dict, home_dir: str, q = None, conn = None, id = None) -> None:
    #in the server, this will call sender to respond appropriately.
    #"call" sender via the queue 


    """Function that takes a message and then executes the appropriate actions to
       do the proper functionality in response.

    Args:
        message (dict): The message provided by the connected device.
        home_dir (str): Directory of this client/server's data (in case of uploading).
    """
    if message is not None:
        #filehead = message[PACKET_HEADER]
        #print(f"[{ctime()}] Message header '{filehead}' received!") #debug
        if message[PACKET_HEADER] == ":UPLOAD:": #client should never recieve one of these, only the server can recieve uploads.
            # (1) Get just the filename without the prefacing path.
            # (2) Get the PIL image object.
            # (3) Save the image to the device's directory.
            filename = message[PACKET_PAYLOAD]["filename"].split(os.sep)[-1]

            #this needs to be tweaked to work for any arbitrary file.
            #with open(f"{home_dir}\{filename}") as file:
            #    file.write(message[PACKET_PAYLOAD]["img"])

            
            try:
                image = message[PACKET_PAYLOAD]["img"]
                image.save(f"{home_dir}\{filename}")
                
            except KeyError:
                #try:
                audio, rate = message[PACKET_PAYLOAD]["audio"]
                scipy.io.wavfile.write(filename, numpy.array(rate), numpy.array(audio))
                
                #except:
            
            print(f"[{ctime()}] Saved file '{filename}' to your directory!")

        elif message[PACKET_HEADER] == ":DOWNLOAD:": #the client should only ever be sending this to the server.
            filename = message[PACKET_PAYLOAD]["filename"].split(os.sep)[-1]
            fileSent = bool(0)

            #Check if filename is on current directory
            fileOnDir = os.path.exists(f"{home_dir}\{filename}")

            #If file is on directory, send to Client 1, if not, check with Client 2
            if (fileOnDir == True):
                print(f"Sending '{filename}'...")
                #Todo: Actually send file
                fileSent = bool(1)
            else: #if the file doesn't exist on the server, this is one of the cases in which the server should send a message
                #it will call serversender() in the other thread?
                #oh so maybe it should just push the info to the queue, (which will be constantly checked in serversender)
                #and then it'll know to send.
                print(f"File not found on server, reaching out to client two...")

                info = qInfo()
                info.id = id
                info.kind = "request"
                info.data = filename

                q.put(info)

                """
                #reach out to client two:
                #push "request" to the queue along with the message. (there may be a way to work this wihtout an initial queue message, but not gonna mess with that rn.)
                #this function must recieve q.

                #tag the queue with the current PPID so it knows whether to call the other thread
                #info = {os.getppid(), "request", filename}

                #announce that a request needs to happen.
                info = qInfo()
                info.id = id
                info.kind = "request"
                info.data = filename

                #q.put("request") #if you choose to combine REQUEST with this, make sure to include an if q not none to make sure only the server does this.
                #q.put(filename)
                q.put(info)
                print("pushed " + str(id) + " request " + filename + " to queue")"""

            #Conf message
            if (fileSent == bool(1)):
                print(f"[{ctime()}] Sent file '{filename}' to client!")
            else:
                print(f"[{ctime()}] Could not find '{filename}'!") 

        elif message[PACKET_HEADER] == ":REQUEST:":
            #server should not ever recieve one of these.
            #client should reply with a response, detailing whether or not it contains the file.
            #this could possibly just be done with DOWNLOAD.
            print("i've recieved a request")
            #check whether the requested file exists on the client.
            #if it does, send it to the server with a :RESPONSE: header
            #if not, still reply with the :RESPONSE: header, but include no data (possibly specifically setting the data to None?)
            filename = message[PACKET_PAYLOAD]
            if os.path.exists(f"{home_dir}\{filename}"):
                print("I have this file!")

                #todo: fix this
                #upload won't know how to make sure to tag it with a :RESPONSE: header
                #upload(conn, f"{home_dir}\{filename}")
                img = Image.open(f"{home_dir}\{filename}")
                message = {
                    PACKET_HEADER: ":RESPONSE:",
                    PACKET_PAYLOAD: {
                        "filename": filename,
                        "img": img
                    }
                }
                send_msg(conn, pickle.dumps(message))
        
            else:
                print("I don't have this file.")
                #send message with response header with empty data
                message = {
                        PACKET_HEADER: ":RESPONSE:",
                        PACKET_PAYLOAD: ":none:"
                    }
                if message:
                    send_msg(conn, pickle.dumps(message))
                


            pass

        elif message[PACKET_HEADER] == ":RESPONSE:":
            #server should just push "response" and the message to the queue.
            if q is not None: 
                print("My client has told me whether or not it has the file!")




                info = qInfo()
                info.id = id
                info.kind = "response"
                info.data = message[PACKET_PAYLOAD]


                print(info.data)
                q.put(info)
            #client should process the message: if there is a file, save it. if not, say that it couldn't be found.
            #this will also result in a queue push resulting in action in the other thread's serversender.
            else:
                print("here's what the client got:")
                print(message[PACKET_PAYLOAD])
                data = message[PACKET_PAYLOAD]

                if data == ":none:":
                    print("The other client didn't have the file you requested!")
                else:
                    #todo: save the file
                    pass

        else:
            print(f"{message[PACKET_PAYLOAD]}")



















#though the task queue is not used here, it must be included so that it can be passed to the function where it IS used.
#it might not actually be needed here? i'll look into it.
#potential other parameters: q = None, id = None, task = None
def receiver(conn: socket, home_dir: str, q = None, id = None) -> None:
    print("my id is " + str(id))
    """
    if q is not None: #this ensures that only the server tries to access a queue (it'll break if client tries)
            print(q.qsize())
            if q.qsize() > 0:
                print("something has been put in the queue!")
                info = q.get()
                id = info[0]
                kind = info[1]
                data = info[2]
                print(id)
                print(kind)
                print(data)
                """
    """Function that will be used in a thread to handle any incoming messages from
       the provided socket connection.

    Args:
        conn (socket): Socket connection to listen to.
        home_dir (str): Directory where the client/server's data will be stored.
    """
    while True:
        try:
            received_msg = recv_msg(conn)
            received_msg = pickle.loads(received_msg)
            # potentially with q, conn, id
            handle_received_message(received_msg, home_dir, q, conn, id)
        except KeyboardInterrupt:
            conn.close()

"""
def queueMonitor(q) -> None:
    if q is not None: #this ensures that only the server tries to access a queue (it'll break if client tries)
            print(q.qsize())
            if q.qsize() > 0:
                print("something has been put in the queue!")
                info = q.get()
                id = info[0]
                kind = info[1]
                data = info[2]
                print(id)
                print(kind)
                print(data)
                """