"""
Integration tests for chat application.
"""

import pytest
import socket
import threading
import time
from src.protocol import encode_message, decode_header, decode_message, HEADER_LENGTH
from src.server import initialize_server, handle_new_connection, handle_client_message
from src.message_handler import receive_message, send_message


class TestServerClientIntegration:
    
    @pytest.fixture
    def server_setup(self):

        # Use a different port for testing to avoid conflicts
        test_port = 12345
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('127.0.0.1', test_port))
        server_socket.listen()
        
        yield server_socket, test_port
        
        # Cleanup
        server_socket.close()
    
    def test_client_can_connect_to_server(self, server_setup):

        server_socket, test_port = server_setup
        
        # Create client socket
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', test_port))
        
        # Send username
        username = "TestUser"
        user_header, user_data = encode_message(username)
        client.send(user_header + user_data)
        
        # Server accepts connection
        client_sock, client_addr = server_socket.accept()
        
        # Server receives username
        received = receive_message(client_sock)
        
        assert received is not False
        assert decode_message(received['data']) == username
        
        # Cleanup
        client.close()
        client_sock.close()
    
    def test_multiple_clients_can_connect(self, server_setup):

        server_socket, test_port = server_setup
        
        # Create multiple client sockets
        client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        client1.connect(('127.0.0.1', test_port))
        client2.connect(('127.0.0.1', test_port))
        
        # Send usernames
        user1_header, user1_data = encode_message("Alice")
        user2_header, user2_data = encode_message("Bob")
        
        client1.send(user1_header + user1_data)
        client2.send(user2_header + user2_data)
        
        # Server accepts both connections
        server_client1, addr1 = server_socket.accept()
        server_client2, addr2 = server_socket.accept()
        
        # Verify both usernames received
        msg1 = receive_message(server_client1)
        msg2 = receive_message(server_client2)
        
        assert decode_message(msg1['data']) == "Alice"
        assert decode_message(msg2['data']) == "Bob"
        
        # Cleanup
        client1.close()
        client2.close()
        server_client1.close()
        server_client2.close()
    
    def test_message_sending_between_clients(self, server_setup):

        server_socket, test_port = server_setup
        
        # Connect two clients
        alice_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bob_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        alice_client.connect(('127.0.0.1', test_port))
        bob_client.connect(('127.0.0.1', test_port))
        
        # Send usernames
        alice_header, alice_data = encode_message("Alice")
        bob_header, bob_data = encode_message("Bob")
        
        alice_client.send(alice_header + alice_data)
        bob_client.send(bob_header + bob_data)
        
        # Server accepts connections
        alice_server_sock, _ = server_socket.accept()
        bob_server_sock, _ = server_socket.accept()
        
        # Receive usernames on server side
        alice_user = receive_message(alice_server_sock)
        bob_user = receive_message(bob_server_sock)
        
        # Alice sends a message
        test_message = "Hello Bob!"
        msg_header, msg_data = encode_message(test_message)
        alice_client.send(msg_header + msg_data)
        
        # Server receives the message from Alice
        alice_msg = receive_message(alice_server_sock)
        
        # Server broadcasts to Bob (simulate broadcast)
        full_message = alice_user['header'] + alice_user['data'] + alice_msg['header'] + alice_msg['data']
        bob_server_sock.send(full_message)
        
        # Bob receives the message
        # Receive username header
        bob_recv_user_header = bob_client.recv(HEADER_LENGTH)
        user_len = decode_header(bob_recv_user_header)
        bob_recv_username = bob_client.recv(user_len)
        
        # Receive message header
        bob_recv_msg_header = bob_client.recv(HEADER_LENGTH)
        msg_len = decode_header(bob_recv_msg_header)
        bob_recv_message = bob_client.recv(msg_len)
        
        # Verify Bob received correct message from Alice
        assert decode_message(bob_recv_username) == "Alice"
        assert decode_message(bob_recv_message) == test_message
        
        # Cleanup
        alice_client.close()
        bob_client.close()
        alice_server_sock.close()
        bob_server_sock.close()
    
    def test_client_disconnect_handling(self, server_setup):

        server_socket, test_port = server_setup
        
        # Connect client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', test_port))
        
        # Send username
        user_header, user_data = encode_message("TestUser")
        client.send(user_header + user_data)
        
        # Server accepts connection
        server_client, _ = server_socket.accept()
        
        # Receive username
        user_msg = receive_message(server_client)
        assert user_msg is not False
        
        # Client disconnects
        client.close()
        
        # Server tries to receive from closed connection
        result = receive_message(server_client)
        
        # Should return False indicating disconnect
        assert result is False
        
        # Cleanup
        server_client.close()
    
    def test_unicode_message_transmission(self, server_setup):

        server_socket, test_port = server_setup
        
        # Connect client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', test_port))
        
        # Send username with unicode
        username = "用户Alice"
        user_header, user_data = encode_message(username)
        client.send(user_header + user_data)
        
        # Server receives
        server_client, _ = server_socket.accept()
        user_msg = receive_message(server_client)
        
        assert decode_message(user_msg['data']) == username
        
        # Send unicode message
        message = "Hello 世界! 🌍"
        msg_header, msg_data = encode_message(message)
        client.send(msg_header + msg_data)
        
        # Server receives message
        received_msg = receive_message(server_client)
        assert decode_message(received_msg['data']) == message
        
        # Cleanup
        client.close()
        server_client.close()


class TestProtocolCompliance:

    
    def test_header_length_consistency(self):

        messages = ["", "a", "Hello", "A" * 100, "Unicode: 世界"]
        
        for msg in messages:
            header, _ = encode_message(msg)
            assert len(header) == HEADER_LENGTH
    
    def test_message_length_accuracy(self):

        messages = ["Test", "Hello World", "Unicode: 你好世界"]
        
        for msg in messages:
            header, data = encode_message(msg)
            reported_length = decode_header(header)
            actual_length = len(data)
            
            assert reported_length == actual_length
    
    def test_encoding_decoding_symmetry(self):

        test_cases = [
            "Simple message",
            "Message with numbers: 12345",
            "Unicode: 你好世界 🌍",
            "Special chars: !@#$%^&*()",
            ""  # Empty message
        ]
        
        for original in test_cases:
            header, encoded = encode_message(original)
            length = decode_header(header)
            decoded = decode_message(encoded)
            
            assert decoded == original
            assert length == len(encoded)


@pytest.mark.timeout(5)
class TestConnectionTimeout:
    
    def test_connection_timeout(self):
        
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(2)  # 2 second timeout
            
            # Try to connect to non-existent server
            with pytest.raises(Exception):  # Should timeout or refuse
                client.connect(('127.0.0.1', 9999))
        finally:
            client.close()
