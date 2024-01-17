import socket
import random
import json
from time import sleep
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
from shared import delayRandomTime, mode

colorama_init()
globals()['last_ack'] = -1
globals()['last_seq'] = -1

def drawEvent(app):
    if(app is not None):
        pass
def process_server_message(data, mode):
    message = json.loads(data.decode())
    seq = message['seq']
    ack = message['ack']
    length = message['length']

    # In automatic mode, randomly decide if the packet is lost/corrupted
    if mode == 'auto' and random.choice([True, False,False,False,False]):
        return None

    # In automatic mode, randomly decide if the packet is duplicated
    if mode == 'auto' and random.choice([True, False,False,False,False]):
        return json.dumps({'seq': seq, 'ack': ack, 'length': length}).encode()

    # if ack of server is not equal to client's seq package corrupts
    if mode == 'manual' and globals()['last_ack'] != seq and globals()['last_ack'] != -1:
        return json.dumps({'seq': globals()['last_seq'], 'ack': globals()['last_ack'], 'length': length}).encode()

    new_seq = ack  # New SEQ is the seq ACK
    new_ack = seq + length  # New ACK is the received SEQ plus length

    globals()['last_ack'] = new_ack
    globals()['last_seq'] = new_seq

    return json.dumps({'seq': new_seq, 'ack': new_ack, 'length': length}).encode()
def udp_server(mode,app = None):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = 'localhost'
    server_port = 12345
    server_socket.bind((server_address, server_port))
    timeout = 33  # seconds
    address = -1
    response = None
    print(f"UDP server in {mode} mode up and listening at {server_address} on port {server_port}")
    while True:
        try:
            server_socket.settimeout(timeout)
            data, address = server_socket.recvfrom(4096)
            print(f"{Fore.BLUE}Received: {data.decode()}")
            response = process_server_message(data, mode)
            if response:
                delayRandomTime()
                server_socket.sendto(response, address)
                print(f"{Fore.GREEN} {response} package sent to {address}")
                if(app is not None):
                    app.add_event("host", "client", json.loads(response)['seq'] ,json.loads(response)['ack'], json.loads(response)['length'], "normal")

            else:
                print(f"{Fore.RED} Simulating lost/corrupted packet.")
                if (app is not None):
                    app.add_event("host", "client", 0 ,0, 0, "lost")
        except socket.timeout:
            print(f"{Fore.RED} Server Timeout, resending: {response.decode()}")
            if (app is not None):
                app.add_event("host", "client", 0, 0, 0, "timeout")
            delayRandomTime()
            server_socket.sendto(response, address)
            print(f'{Fore.GREEN} Server sent {response} to client')
            if (app is not None):
                app.add_event("host", "client", json.loads(response)['seq'] ,json.loads(response)['ack'], json.loads(response)['length'], "normal")


udp_server(mode=mode)
