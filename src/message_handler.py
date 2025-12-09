import socket
from src.protocol import HEADER_LENGTH, decode_header, decode_message


def receive_message(client_socket):

    try:
        header = client_socket.recv(HEADER_LENGTH)

        # Connection closed
        if not len(header):
            return False
        
        # Get message length and data
        msg_length = decode_header(header)
        data = client_socket.recv(msg_length)
        
        return {'header': header, 'data': data}
        
    except socket.error as e:
        print(f"Socket error: {e}")
        return False


def send_message(client_socket, header: bytes, data: bytes):

    client_socket.send(header + data)


def broadcast_message(sender_socket, client_dict, user_header, user_data, msg_header, msg_data):

    full_message = user_header + user_data + msg_header + msg_data
    
    for client_socket in client_dict:
        # Don't send back to sender
        if client_socket != sender_socket:
            send_message(client_socket, full_message, b'')
