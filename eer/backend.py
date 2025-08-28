import socket
import threading
import time

# ...existing code...
clients = {}                # conn -> username (None until registered)
messages_buffer = []        # stored as plain "username: message" strings
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
    try:
        # ensure we have an entry for this connection
        clients[conn] = None

        # Immediately send buffered messages to the newly connected socket
        # so the new client sees previous messages from others before it sends.
        for old_msg in messages_buffer:
            try:
                conn.sendall(old_msg.encode())
                time.sleep(0.01)
            except:
                # if sending buffered history fails, just continue
                pass

        # Now enter normal receive loop
        while True:
            raw = conn.recv(2048)
            if not raw:
                break
            try:
                msg = raw.decode()
            except:
                continue

            # expect messages in "username: content" form
            if ":" not in msg:
                continue

            sender, content = msg.split(":", 1)
            sender = sender.strip()
            content = content.strip()
            formatted = f"{sender}: {content}"

            # register username on first real message and broadcast join notice
            if clients.get(conn) is None:
                clients[conn] = sender
                join_msg = f"[SERVER]: {sender} has joined the chat!"
                # notify other clients about join (don't send to the joining client)
                broadcast_message(join_msg, sender_conn=conn)

            # store in buffer and broadcast the chat message to others
            messages_buffer.append(formatted)
            if len(messages_buffer) > MAX_BUFFER:
                messages_buffer.pop(0)

            broadcast_message(formatted, sender_conn=conn)

    except Exception as e:
        print(f"[ERROR] {addr} {e}")

    finally:
        # cleanup
        username = clients.pop(conn, None)
        if username:
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
        # spawn handler thread
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
# ...existing code...