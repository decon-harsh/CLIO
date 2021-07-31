from os import remove
import socket
from _thread import *
import pickle
import time

# Globally storing in main thread heap
list_of_clients = {}
room_list={}

# Function to join a room 
def join_room(room_number,addr):
    global room_list 

    if room_number in room_list.keys():
        room_list[str(room_number)].add(addr)
        return True
    else:
        return False
    
# Function to create  a room
def create_room():
    global room_list
    
    if len(room_list)==0:
        max_room_num = 999
    else:
        max_room_num = max(list(room_list.keys()))

    # Declaring an empty set, just for key creation
    room_list[str(int(max_room_num)+1)] = set()
    return str(int(max_room_num)+1)

# Thread
def multi_threaded_client(c,addr):
    name_data = c.recv(1024).decode()
    global room_list
    
    c.send(bytes(f"Hey {name_data} What's up?",'utf-8'))
    
    while True:
        try:
            data = c.recv(1024).decode()
                        
            if data and data=="JOIN":
                global room_list

                room_number = c.recv(1024).decode()
                success = join_room(room_number,addr)
                c.send(bytes(str(success),'utf-8'))
                time.sleep(1)
                if success == True:
                    c.send(bytes(f"Welcome to chatroom {room_number}! {name_data}",'utf-8'))

                    while True:
                        try:
                            data = c.recv(5000).decode()
                
                            if not data:
                                remove(addr,room_number)

                            else:
                                message_to_send = f"<{name_data}>$ {data}"

                                # This function broadcasts message to everyone in the room except the sender
                                broadcast(message_to_send,c,room_number,addr)
                
                        except error as e:
                            print(e)
                            remove(addr,room_number)
                            break    

            elif data and data=="LIST":
                global room_list
                data_string = pickle.dumps(room_list) 
                c.send(bytes(data_string))
            
            elif data and data == "CREATE":
                new_room_num = create_room()
                c.send(bytes(new_room_num,'utf-8'))
            
            elif data=="CONTINUE":
                continue

            else:
                break
        
        except error as e:
            print(e)

# Helper Functions
def broadcast(message,c,room_number,addr):
    global room_list
    global list_of_clients
    for clients in room_list[str(room_number)]:
        if clients != addr:
            try:
                c_object = list_of_clients[clients]
                c_object.send(bytes(message,'utf-8'))
            except:
                c_object = list_of_clients[clients]
                c_object.close()
                remove(clients,room_number)

def remove(addr,room_number):
    global room_list
    room_list[str(room_number)].discard(addr)


def main():
    port = 12344
    host = '127.0.0.1'
    ThreadCount = 0
    
    # Server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # This is for reusing same port after keyboard interupt
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

    try:
        s.bind((host, port))  #bind
    except socket.error as e:
        print(str(e))
    s.listen(15)

    print("Server started what to do now?")
    while True:
        c,addr =  s.accept()
        print(f"Connected to {addr}")
        list_of_clients[addr]=c
        start_new_thread(multi_threaded_client,(c,addr))
        ThreadCount += 1

    c.close()
    s.close()    

if __name__ == '__main__':
    main()