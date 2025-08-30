import socket
import threading

# Store clients as {conn: {"username": str, "group": str}}
clients = {}
messages_buffer = {}  # {group: [messages]}
MAX_BUFFER = 200


def broadcast_message(message, sender_conn=None, group=None):
    """Send message to all clients in the same group (except sender)."""
    for client, info in list(clients.items()):
        if group and info["group"] != group:
            continue
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
    left_already = False
    try:
        # First message: username|group
        first_msg = conn.recv(1024).decode()
        if "|" not in first_msg:
            conn.close()
            return

        username, group = first_msg.split("|", 1)
        username = username.strip()
        group = group.strip()

        # Register client
        clients[conn] = {"username": username, "group": group}
        if group not in messages_buffer:
            messages_buffer[group] = []

        # Announce join
        join_announcement = f"[SERVER]: {username} joined the group."
        broadcast_message(join_announcement, sender_conn=conn, group=group)

        # Main loop
        while True:
            msg = conn.recv(1024).decode()
            if not msg:
                break

            # Handle leave
            if msg.startswith("LEAVE_GROUP|"):
                leave_user = msg.split("|", 1)[1]
                announcement = f"[SERVER]: {leave_user} left the group."
                broadcast_message(announcement, sender_conn=conn, group=group)
                left_already = True
                break

            # Normal chat
            messages_buffer[group].append(msg)
            if len(messages_buffer[group]) > MAX_BUFFER:
                messages_buffer[group].pop(0)

            broadcast_message(msg, sender_conn=conn, group=group)

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")

    finally:
        if conn in clients:
            left_user = clients[conn]["username"]
            left_group = clients[conn]["group"]

            # Only announce if not already announced
            if not left_already and left_group:
                announcement = f"[SERVER]: {left_user} left the group."
                broadcast_message(announcement, sender_conn=conn, group=left_group)

            del clients[conn]

        try:
            conn.close()
        except:
            pass

        print(f"[DISCONNECTED] {addr}")


def start_server(host="127.0.0.1", port=5556):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    print(f"[STARTED] Server listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        print(f"[NEW CONNECTION] {addr}")
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()
