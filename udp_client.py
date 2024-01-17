import socket
import json
import time
import random
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
from shared import delayRandomTime, mode

colorama_init()


def process_client_auto(seq, ack, length):
    new_seq = ack  # New SEQ is the received ACK
    new_ack = seq + length  # New ACK is the received SEQ plus length
    return json.dumps({'seq': new_seq, 'ack': new_ack, 'length': length}).encode()


def process_client_manual(seq, ack, length):
    inp = list(map(int, input("Enter seq, ack comma seperated").split(',')))
    new_seq = inp[0]
    new_ack = inp[1]
    return json.dumps({'seq': new_seq, 'ack': new_ack, 'length': length}).encode()


def process_client_message(data, mode):
    message = json.loads(data.decode())
    seq = message['seq']
    ack = message['ack']
    length = message['length']
    if (mode == 'auto'):
        return process_client_auto(seq, ack, length)
    else:
        return process_client_manual(seq, ack, length)


def udp_client(mode,app = None):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = 'localhost'
    server_port = 12345
    timeout = 4  # seconds

    max_num_packets = 33
    seq = 1
    ack = 1
    length = 10  # Example length
    ack_received = set()  # Track received acknowledgments
    retries = {}  # Track retries for each packet
    if (mode == 'auto'):
        message = json.dumps({'seq': seq, 'ack': ack, 'length': length}).encode()
    else:
        inp = list(map(int, input("Enter seq, ack comma seperated").split(',')))
        message = json.dumps({'seq': inp[0], 'ack': inp[1], 'length': length}).encode()

    for i in range(0, max_num_packets):
        try:
            delayRandomTime()
            client_socket.sendto(message, (server_address, server_port))

            print(f'{Fore.GREEN}Client sent {message} to server {Style.RESET_ALL}')
            if (app is not None):
                app.add_event("client", "host", json.loads(message)['seq'], json.loads(message)['ack'],
                          json.loads(message)['length'], "normal")
            while True:
                try:
                    client_socket.settimeout(timeout)
                    data, server = client_socket.recvfrom(4096)
                    response = json.loads(data.decode())
                    if response['ack'] in ack_received:
                        print(f"{Fore.YELLOW}Duplicate ACK detected for SEQ {response['seq']} {Style.RESET_ALL}")
                    else:
                        ack_received.add(response['ack'])
                        print(f"{Fore.BLUE}Received: {data.decode()}")
                        message = process_client_message(data=data, mode=mode)
                        break
                except socket.timeout:
                    print(f"{Fore.RED}Timeout, resending: {message.decode()}")
                    if (app is not None):
                        app.add_event("client", "host", 0, 0, 0, "timeout")
                    seq = json.loads(message.decode())['seq']
                    if seq in retries:
                        retries[seq] += 1
                    else:
                        retries[seq] = 0
                    delayRandomTime()
                    client_socket.sendto(message, (server_address, server_port))
                    print(f'{Fore.GREEN}Client sent {message} to server')
                    if (app is not None):
                        app.add_event("client", "host", json.loads(message)['seq'] ,json.loads(message)['ack'], json.loads(message)['length'], "normal")

        finally:
            client_socket.settimeout(None)
        if seq in retries and retries[seq] >= 4:
            print(f"{Fore.RED}Packet {seq} is assumed lost after 4 attempts. {Style.RESET_ALL}")
    client_socket.close()


udp_client(mode=mode)
