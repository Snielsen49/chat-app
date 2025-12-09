"""
Chat Server
Handles multiple client connections and message broadcasting.
"""

import socket
import select
from src.message_handler import receive_message, broadcast_message
from src.protocol import decode_message

# Server configuration
HOST = '0.0.0.0'  # Listen on all interfaces 
PORT = 1234


def initialize_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f'Server started on {HOST}:{PORT}')
    return server_socket


def handle_new_connection(server_socket, socket_list, client_dict):

    client_socket, client_address = server_socket.accept()
    
    # Receive username
    user = receive_message(client_socket)
    
    if user is False:
        return
    
    # Add client to tracking structures
    socket_list.append(client_socket)
    client_dict[client_socket] = user
    
    username = decode_message(user['data'])
    print(f'New connection from {client_address[0]}:{client_address[1]}')
    print(f'Username: {username}')


def handle_client_message(client_socket, socket_list, client_dict):

    message = receive_message(client_socket)
    
    # Client disconnected
    if message is False:
        username = decode_message(client_dict[client_socket]['data'])
        print(f'Closed connection from {username}')
        
        socket_list.remove(client_socket)
        del client_dict[client_socket]
        return
    
    # Get client info and broadcast message
    user = client_dict[client_socket]
    username = decode_message(user['data'])
    msg_content = decode_message(message['data'])
    
    print(f'Received message from {username}: {msg_content}')
    
    # Broadcast to all other clients
    broadcast_message(
        client_socket,
        client_dict,
        user['header'],
        user['data'],
        message['header'],
        message['data']
    )


def run_server():
    # Main server loop.
    server_socket = initialize_server()
    socket_list = [server_socket]
    client_dict = {}
    
    print('Waiting for connections...')
    
    while True:
        read_sockets, _, exception_sockets = select.select(
            socket_list, [], socket_list
        )
        
        for notified_socket in read_sockets:
            # New connection
            if notified_socket == server_socket:
                handle_new_connection(server_socket, socket_list, client_dict)
            
            # Existing client message
            else:
                handle_client_message(notified_socket, socket_list, client_dict)
        
        # Handle socket exceptions
        for notified_socket in exception_sockets:
            socket_list.remove(notified_socket)
            del client_dict[notified_socket]


if __name__ == '__main__':
    run_server()
