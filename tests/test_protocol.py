"""
Unit tests for protocol.py
Tests message encoding, decoding, and header formatting.
"""

import pytest
from src.protocol import (
    HEADER_LENGTH,
    encode_message,
    decode_header,
    decode_message,
    create_full_message
)


class TestEncodeMessage:

    def test_encode_simple_message(self):

        header, encoded = encode_message("Hello")
        
        # Header should be 10 bytes
        assert len(header) == HEADER_LENGTH
        assert header == b'5         '
        
        # Message should be UTF-8 encoded
        assert encoded == b'Hello'
    
    def test_encode_unicode_message(self):

        message = "Hello 世界 🌍"
        header, encoded = encode_message(message)
        
        # Header should reflect actual byte length, not character length
        expected_length = len(message.encode('utf-8'))
        assert int(header.decode('utf-8').strip()) == expected_length
        assert encoded == message.encode('utf-8')
    
    def test_encode_empty_message(self):

        header, encoded = encode_message("")
        
        assert int(header.decode('utf-8').strip()) == 0
        assert encoded == b''
    
    def test_encode_long_message(self):

        message = "A" * 500
        header, encoded = encode_message(message)
        
        assert int(header.decode('utf-8').strip()) == 500
        assert len(encoded) == 500


class TestDecodeHeader:

    
    def test_decode_valid_header(self):

        header = b'42        '
        length = decode_header(header)
        
        assert length == 42
    
    def test_decode_single_digit_header(self):

        header = b'5         '
        length = decode_header(header)
        
        assert length == 5
    
    def test_decode_max_length_header(self):

        header = b'999999999 '
        length = decode_header(header)
        
        assert length == 999999999


class TestDecodeMessage:

    
    def test_decode_simple_message(self):

        message_bytes = b'Hello World'
        decoded = decode_message(message_bytes)
        
        assert decoded == "Hello World"
    
    def test_decode_unicode_message(self):

        original = "Hello 世界 🌍"
        message_bytes = original.encode('utf-8')
        decoded = decode_message(message_bytes)
        
        assert decoded == original
    
    def test_decode_empty_message(self):

        decoded = decode_message(b'')
        
        assert decoded == ""


class TestCreateFullMessage:
    
    def test_create_full_message_simple(self):

        username = "Alice"
        message = "Hello!"
        
        full_msg = create_full_message(username, message)
        
        # Should have: user_header + username + msg_header + message
        # User header (10) + username (5) + msg header (10) + message (6) = 31 bytes
        expected_length = HEADER_LENGTH + len(username) + HEADER_LENGTH + len(message)
        assert len(full_msg) == expected_length
        
        # Verify structure
        user_header = full_msg[:HEADER_LENGTH]
        assert int(user_header.decode('utf-8').strip()) == len(username)
    
    def test_create_full_message_unicode(self):

        username = "用户"
        message = "消息 🎉"
        
        full_msg = create_full_message(username, message)
        
        # Calculate expected byte lengths (not character counts!)
        user_bytes = len(username.encode('utf-8'))
        msg_bytes = len(message.encode('utf-8'))
        expected_length = HEADER_LENGTH + user_bytes + HEADER_LENGTH + msg_bytes
        
        assert len(full_msg) == expected_length
    
    def test_create_full_message_with_empty_username(self):

        full_msg = create_full_message("", "Hello")
        
        # Should still work with empty username
        assert len(full_msg) == HEADER_LENGTH + 0 + HEADER_LENGTH + 5
    
    def test_create_full_message_with_empty_message(self):

        full_msg = create_full_message("Alice", "")
        
        # Should still work with empty message
        assert len(full_msg) == HEADER_LENGTH + 5 + HEADER_LENGTH + 0


class TestRoundTrip:
    
    def test_encode_decode_roundtrip(self):

        original = "Test message with unicode: 你好"
        
        header, encoded = encode_message(original)
        length = decode_header(header)
        decoded = decode_message(encoded)
        
        assert length == len(encoded)
        assert decoded == original
    
    def test_multiple_messages_roundtrip(self):

        messages = ["Hello", "World", "Test 123", "Unicode: 世界"]
        
        for original in messages:
            header, encoded = encode_message(original)
            decoded = decode_message(encoded)
            assert decoded == original
