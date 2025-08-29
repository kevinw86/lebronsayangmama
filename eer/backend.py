import socket
import threading

# Track connected clients as dict {conn: username}
clients = {}

def broadcast(msg, sender_conn=None):
    """Send message to all clients except the sender (if given)."""
    for conn in clients:
        if conn != sender_conn:
            try:
                conn.sendall(msg.encode())
            except:
                conn.close()
                remove_client(conn)

def remove_client(conn):
    """Remove client safely."""
    if conn in clients:
        username = clients[conn]
        del clients[conn]
        print(f"[DISCONNECTED] {username}")
        broadcast(f"[SYSTEM]: {username} left the chat")

def handle_client(conn, addr):
    try:
        # First message should be username
        username = conn.recv(1024).decode().strip()
        if not username:
            conn.close()
            return

        clients[conn] = username
        print(f"[NEW CONNECTION] {username} ({addr}) connected.")
        broadcast(f"[SYSTEM]: {username} joined the chat", sender_conn=conn)

        while True:
            msg = conn.recv(1024).decode()
            if not msg:
                break
            print(f"[{username}] {msg}")
            broadcast(f"{username}: {msg}", sender_conn=conn)
    except:
        pass
    finally:
        remove_client(conn)
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 5556))
    server.listen()
    print("[STARTED] Server listening on 127.0.0.1:5556")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()

if __name__ == "__main__":
    start_server()
