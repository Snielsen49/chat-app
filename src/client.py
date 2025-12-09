"""
Chat Client
Connects to chat server and handles sending/receiving messages.
"""

import socket
import errno
import sys
import threading
from src.protocol import HEADER_LENGTH, encode_message, decode_message, decode_header

# Server configuration
HOST = '127.0.0.1'
PORT = 1234


def receive_messages(client_socket):

    while True:
        try:
            # Receive username header
            user_header = client_socket.recv(HEADER_LENGTH)
            
            # Server closed connection
            if not len(user_header):
                print('\nConnection closed by server')
                sys.exit()
            
            # Get username
            user_length = decode_header(user_header)
            username = client_socket.recv(user_length)
            username_str = decode_message(username)
            
            # Get message header
            msg_header = client_socket.recv(HEADER_LENGTH)
            msg_length = decode_header(msg_header)
            message = client_socket.recv(msg_length)
            message_str = decode_message(message)
            
            # Display message
            print(f'\n{username_str} > {message_str}')
            print('', end='', flush=True)  # Re-prompt for input
            
        except IOError as e:
            # No more messages to receive
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print(f'\nReceiving error: {str(e)}')
                sys.exit()
            continue
            
        except Exception as e:
            print(f'\nError: {str(e)}')
            sys.exit()


def send_message_to_server(client_socket, message: str):

    msg_header, msg_data = encode_message(message)
    client_socket.send(msg_header + msg_data)


def connect_to_server(username: str):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.setblocking(False)
    
    # Send username to server
    user_header, user_data = encode_message(username)
    client_socket.send(user_header + user_data)
    
    print(f'Connected to {HOST}:{PORT} as {username}')
    
    return client_socket


def run_client():
    # Main client loop.
    # Get username
    username = input('Enter your username: ')
    
    if not username:
        print('Username cannot be empty!')
        sys.exit()
    
    # Connect to server
    try:
        client_socket = connect_to_server(username)
    except ConnectionRefusedError:
        print(f'Could not connect to server at {HOST}:{PORT}')
        print('Make sure the server is running.')
        sys.exit()
    except Exception as e:
        print(f'Connection error: {e}')
        sys.exit()
    
    # Start message receiving thread
    receive_thread = threading.Thread(
        target=receive_messages,
        args=(client_socket,),
        daemon=True
    )
    receive_thread.start()
    
    print('\nYou can start sending messages (press Ctrl+C to exit)')
    print('-' * 50)
    
    # Main message sending loop
    try:
        while True:
            message = input('')
            
            if message:
                send_message_to_server(client_socket, message)
                
    except KeyboardInterrupt:
        print('\n\nDisconnecting...')
        client_socket.close()
        sys.exit()


if __name__ == '__main__':
    run_client()
