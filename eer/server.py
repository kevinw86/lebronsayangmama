import socket
import threading

# List to keep track of connected clients
clients = []

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    while True:
        try:
            msg = conn.recv(1024).decode()
            if not msg:
                break
            print(f"[{addr}] {msg}")
            # Broadcast to all other clients
            for client in clients:
                if client != conn:
                    client.sendall(msg.encode())
        except:
            break
    conn.close()
    clients.remove(conn)
    print(f"[DISCONNECTED] {addr} disconnected.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("192.168.1.100", 5555))
    server.listen()
    print("[STARTED] Server listening on 192.168.1.100:5555")
    while True:
        conn, addr = server.accept()
        clients.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
