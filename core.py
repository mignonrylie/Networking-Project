import argparse
import os
import pickle
#import wave    get rifd of wave
import scipy.io.wavfile
import numpy

from dill import dumps, loads #are we allowed to use libraries that require installing?

from PIL import Image, UnidentifiedImageError
from socket import socket, AF_INET, SOCK_STREAM
from time import ctime
from utils import *



#upload is currently broken. wave likely isn't necessary, as are dill, scipy, and numpy.
#look into uploading by converting all files to byte streams with pickle


#wave for handling .WAV audio files
#queue for letting the different server processes talk to each other for download

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

    if tokens[0] == "CONNECT": #done
        print("You are already connected. Try a different command.")
        return sanitizeInput()

    elif tokens[0] == "UPLOAD": #done
        if len(tokens) < 2:
            print("Please include the name of the file you wish to upload:")
        else:
            return ":UPLOAD: " + tokens[1]

    elif tokens[0] == "DOWNLOAD": #done
        if len(tokens) < 2:
            print("Please include the name of the file you wish to download.")
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
        #img = Image.open(filename)
        img = open(filename, 'wb')
        message = {
            PACKET_HEADER: ":UPLOAD:",
            PACKET_PAYLOAD: {
                "filename": filename,
                "img": img
            }
        }
    except UnidentifiedImageError:
        #try:
        #audio = wave.open(filename)
        audio = scipy.io.wavfile.read(filename)
        message = {
            PACKET_HEADER: ":UPLOAD:",
            PACKET_PAYLOAD: {
                "filename": filename,
                "audio": audio
            }
        }

        #except:
        #    pass

        #print("exception handled")
        #pass
    #PIL.UnidentifiedImageError
    if message:
        try:
            send_msg(conn, pickle.dumps(message))
        except TypeError:
            send_msg(conn, dumps(message))

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

def sender(conn: socket, home_dir: str) -> None:
    """Function that will be used in a thread to handle any outgoing messages to
       the provided socket connection.

    Args:
        conn (socket): Socket connection to send messages to.
        home_dir (str): Directory where the client/server's data will be stored.
    """
    while True:
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


def handle_received_message(message: dict, home_dir: str) -> None:
    """Function that takes a message and then executes the appropriate actions to
       do the proper functionality in response.

    Args:
        message (dict): The message provided by the connected device.
        home_dir (str): Directory of this client/server's data (in case of uploading).
    """
    if message is not None:
        #filehead = message[PACKET_HEADER]
        #print(f"[{ctime()}] Message header '{filehead}' received!") #debug
        if message[PACKET_HEADER] == ":UPLOAD:":
            # (1) Get just the filename without the prefacing path.
            # (2) Get the PIL image object.
            # (3) Save the image to the device's directory.
            filename = message[PACKET_PAYLOAD]["filename"].split(os.sep)[-1]

            with open(f"{home_dir}\{filename}") as file:
                file.write(message[PACKET_PAYLOAD]["img"])

            """
            try:
                image = message[PACKET_PAYLOAD]["img"]
                #image.save(f"{home_dir}\{filename}")
                
            except KeyError:
                #try:
                audio, rate = message[PACKET_PAYLOAD]["audio"]
                scipy.io.wavfile.write(filename, numpy.array(rate), numpy.array(audio))
                
                #except:
            """
            print(f"[{ctime()}] Saved file '{filename}' to your directory!")
        elif message[PACKET_HEADER] == ":DOWNLOAD:":
            filename = message[PACKET_PAYLOAD]["filename"].split(os.sep)[-1]
            fileSent = bool(0)

            #Check if filename is on current directory
            fileOnDir = os.path.exists(f"{home_dir}\{filename}")

            #If file is on directory, send to Client 1, if not, check with Client 2
            if (fileOnDir == True):
                print(f"Sending '{filename}'...")
                #Todo: Actually send file
                fileSent = bool(1)
            else:
                print(f"File not found on server, reaching out to client two...")

            #Conf message
            if (fileSent == bool(1)):
                print(f"[{ctime()}] Sent file '{filename}' to client!")
            else:
                print(f"[{ctime()}] Could not find '{filename}'!") 
        else:
            print(f"{message[PACKET_PAYLOAD]}")


def receiver(conn: socket, home_dir: str) -> None:
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
            handle_received_message(received_msg, home_dir)
        except KeyboardInterrupt:
            conn.close()
