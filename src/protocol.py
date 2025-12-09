HEADER_LENGTH = 10

def encode_message(message: str) -> tuple:

    encoded_msg = message.encode('utf-8')
    header = f'{len(encoded_msg):<{HEADER_LENGTH}}'.encode('utf-8')
    return header, encoded_msg


def decode_header(header_bytes: bytes) -> int:

    return int(header_bytes.decode('utf-8').strip())


def decode_message(message_bytes: bytes) -> str:

    return message_bytes.decode('utf-8')


def create_full_message(username: str, message: str) -> bytes:

    user_header, user_encoded = encode_message(username)
    msg_header, msg_encoded = encode_message(message)
    return user_header + user_encoded + msg_header + msg_encoded
