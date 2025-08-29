import socket
import threading

clients = {}
messages_buffer = []  # still keeps recent messages, but no longer sent on join
MAX_BUFFER = 200


def broadcast_message(message, sender_conn=None):
    """Send message to all clients except sender_conn (if provided)."""
    for client in list(clients.keys()):
        if client == sender_conn:
            continue
        try:
            client.sendall(message.encode())
        except:
            try:
                client.close()
            except:
                pass
            if client in clients:
                del clients[client]


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    username = None
    try:
        # --- First message must be the username ---
        username = conn.recv(2048).decode().strip()
        clients[conn] = username
        print(f"[USERNAME] {addr} is {username}")

        # --- Announce join ---
        join_msg = f"[SERVER]: {username} has joined the chat!"
        broadcast_message(join_msg, sender_conn=conn)

        # --- Main loop ---
        while True:
            msg = conn.recv(2048)
            if not msg:
                break
            try:
                msg = msg.decode()
            except:
                continue

            if ":" not in msg:
                continue

            sender, content = msg.split(":", 1)
            sender = sender.strip()
            content = content.strip()
            formatted = f"{sender}: {content}"

            messages_buffer.append(formatted)
            if len(messages_buffer) > MAX_BUFFER:
                messages_buffer.pop(0)

            broadcast_message(formatted, sender_conn=conn)

    except Exception as e:
        print(f"[ERROR] {addr} {e}")

    finally:
        if conn in clients:
            username = clients[conn]
            del clients[conn]
            leave_msg = f"[SERVER]: {username} has left the chat!"
            broadcast_message(leave_msg)
        try:
            conn.close()
        except:
            pass
        print(f"[DISCONNECTED] {addr}")


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 5556))
    server.listen()
    print("[STARTED] Server listening on 127.0.0.1:5556")

    while True:
        conn, addr = server.accept()
        clients[conn] = None
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()
