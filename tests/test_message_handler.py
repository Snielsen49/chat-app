"""
Unit tests for message_handler.py
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import socket
from src.message_handler import (
    receive_message,
    send_message,
    broadcast_message
)
from src.protocol import encode_message


class TestReceiveMessage:
    
    def test_receive_valid_message(self):

        # Create mock socket
        mock_socket = Mock()
        
        # Simulate receiving header and data
        test_message = "Hello"
        header, data = encode_message(test_message)
        
        mock_socket.recv.side_effect = [header, data]
        
        result = receive_message(mock_socket)
        
        assert result is not False
        assert result['header'] == header
        assert result['data'] == data
    
    def test_receive_empty_header_returns_false(self):

        mock_socket = Mock()
        mock_socket.recv.return_value = b''
        
        result = receive_message(mock_socket)
        
        assert result is False
    
    def test_receive_with_socket_error(self):

        mock_socket = Mock()
        mock_socket.recv.side_effect = socket.error("Connection reset")
        
        result = receive_message(mock_socket)
        
        assert result is False
    
    def test_receive_unicode_message(self):

        mock_socket = Mock()
        
        test_message = "Hello 世界"
        header, data = encode_message(test_message)
        
        mock_socket.recv.side_effect = [header, data]
        
        result = receive_message(mock_socket)
        
        assert result is not False
        assert result['data'] == data


class TestSendMessage:

    
    def test_send_message_success(self):

        mock_socket = Mock()
        header = b'5         '
        data = b'Hello'
        
        send_message(mock_socket, header, data)
        
        # Verify socket.send was called with combined header and data
        mock_socket.send.assert_called_once_with(header + data)
    
    def test_send_empty_data(self):

        mock_socket = Mock()
        header = b'0         '
        data = b''
        
        send_message(mock_socket, header, data)
        
        mock_socket.send.assert_called_once_with(header + data)
    
    def test_send_large_message(self):
 
        mock_socket = Mock()
        large_data = b'A' * 1000
        header = b'1000      '
        
        send_message(mock_socket, header, large_data)
        
        mock_socket.send.assert_called_once()


class TestBroadcastMessage:

    
    def test_broadcast_to_multiple_clients(self):

        # Create mock sockets
        sender = Mock()
        client1 = Mock()
        client2 = Mock()
        client3 = Mock()
        
        client_dict = {
            sender: {'header': b'6         ', 'data': b'Sender'},
            client1: {'header': b'7         ', 'data': b'Client1'},
            client2: {'header': b'7         ', 'data': b'Client2'},
            client3: {'header': b'7         ', 'data': b'Client3'}
        }
        
        user_header = b'6         '
        user_data = b'Sender'
        msg_header = b'5         '
        msg_data = b'Hello'
        
        broadcast_message(
            sender,
            client_dict,
            user_header,
            user_data,
            msg_header,
            msg_data
        )
        
        # Sender should NOT receive the message
        sender.send.assert_not_called()
        
        # All other clients should receive the message
        expected_message = user_header + user_data + msg_header + msg_data
        client1.send.assert_called_once_with(expected_message + b'')
        client2.send.assert_called_once_with(expected_message + b'')
        client3.send.assert_called_once_with(expected_message + b'')
    
    def test_broadcast_with_single_client(self):

        sender = Mock()
        client_dict = {sender: {'header': b'6         ', 'data': b'Sender'}}
        
        broadcast_message(
            sender,
            client_dict,
            b'6         ',
            b'Sender',
            b'5         ',
            b'Hello'
        )
        
        # Sender should not receive their own message
        sender.send.assert_not_called()
    
    def test_broadcast_excludes_sender(self):

        sender = Mock()
        receiver = Mock()
        
        client_dict = {
            sender: {'header': b'6         ', 'data': b'Sender'},
            receiver: {'header': b'8         ', 'data': b'Receiver'}
        }
        
        broadcast_message(
            sender,
            client_dict,
            b'6         ',
            b'Sender',
            b'11        ',
            b'Test message'
        )
        
        # Only receiver should get the message
        sender.send.assert_not_called()
        assert receiver.send.call_count == 1
    
    def test_broadcast_with_unicode(self):

        sender = Mock()
        client1 = Mock()
        
        client_dict = {
            sender: {'header': b'5         ', 'data': 'Alice'.encode('utf-8')},
            client1: {'header': b'3         ', 'data': 'Bob'.encode('utf-8')}
        }
        
        msg = "Hello 世界"
        user_header, user_data = encode_message("Alice")
        msg_header, msg_data = encode_message(msg)
        
        broadcast_message(
            sender,
            client_dict,
            user_header,
            user_data,
            msg_header,
            msg_data
        )
        
        # Client should receive the unicode message
        client1.send.assert_called_once()


class TestMessageHandlerIntegration:

    
    def test_send_and_receive_flow(self):

        # Create mock socket
        mock_socket = Mock()
        
        # Test message
        test_message = "Integration test"
        header, data = encode_message(test_message)
        
        # Send message
        send_message(mock_socket, header, data)
        
        # Verify send
        mock_socket.send.assert_called_once_with(header + data)
        
        # Simulate receive
        mock_socket.recv.side_effect = [header, data]
        result = receive_message(mock_socket)
        
        # Verify received data matches sent data
        assert result['header'] == header
        assert result['data'] == data
