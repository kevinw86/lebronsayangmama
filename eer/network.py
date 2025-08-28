import socket

def connect_to_server(host="127.0.0.1", port=5556):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    return client
