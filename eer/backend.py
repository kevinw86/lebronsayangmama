import socket
import threading

clients = {}
groups = {}  # groupname: {"password": str, "members": [conn]}
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


def send_group_list():
    group_list = ",".join(groups.keys())
    for client in clients:
        try:
            client.sendall(f"GROUPLIST:{group_list}".encode())
        except:
            pass


def handle_client(conn, addr):
    left_already = False
    current_group = None
    
    try:
        # Read the first message
        first_msg = conn.recv(1024).decode().strip()
        if not first_msg:
            conn.close()
            return
            
        print(f"[DEBUG] {addr} first message: '{first_msg}'")

        # Handle initial requests that are NOT chat logins
        if first_msg == "GETGROUPS":
            group_list = ",".join(groups.keys())
            try:
                conn.sendall(f"GROUPLIST:{group_list}".encode())
                print(f"[GROUP LIST SENT] to {addr}")
            except Exception as e:
                print(f"[ERROR] Sending group list to {addr}: {e}")
            return # This connection's job is done

        # Handle CREATEGROUP command
        if first_msg.startswith("CREATEGROUP:"):
            try:
                # Parse the message "CREATEGROUP:name|password"
                _, data = first_msg.split(":", 1)
                name, password = data.split("|", 1)
                
                # Check if group already exists
                if name in groups:
                    conn.sendall("[SERVER]: Group with that name already exists.".encode())
                else:
                    # Create the new group
                    groups[name] = {"password": password, "members": []}
                    messages_buffer[name] = [] # Initialize the buffer for the new group
                    conn.sendall(f"[SERVER]: Group '{name}' created successfully.".encode())
                    print(f"[GROUP CREATED] Name: {name}, by {addr}")
            
            except Exception as e:
                # Handle incorrect format
                try:
                    conn.sendall("[SERVER]: Invalid CREATEGROUP format.".encode())
                except:
                    pass
                print(f"[ERROR] Invalid CREATEGROUP from {addr}: {e}")
            
            return # This connection's job is done
        
        if first_msg.startswith("DELETEGROUP:"):
            try:
                _, data = first_msg.split(":", 1)
                name, password = data.split("|", 1)
                name = name.strip()
                password = password.strip()
                print(f"[DELETEGROUP] Request for: '{name}' (all groups: {list(groups.keys())})")
                if name not in groups:
                    conn.sendall("[SERVER]: Group does not exist.".encode())
                elif groups[name]["password"] != password:
                    conn.sendall("[SERVER]: Incorrect password.".encode())
                else:
                    # Remove group and its messages
                    del groups[name]
                    if name in messages_buffer:
                        del messages_buffer[name]
                    conn.sendall(f"[SERVER]: Group '{name}' deleted.".encode())
                    print(f"[GROUP DELETED] Name: {name}, by {addr}")
            except Exception as e:
                try:
                    conn.sendall("[SERVER]: Invalid DELETEGROUP format.".encode())
                except:
                    pass
                print(f"[ERROR] Invalid DELETEGROUP from {addr}: {e}")
            return

        # If not a command, assume it's a chat login attempt
        if "|" not in first_msg:
            try:
                conn.sendall("[SERVER]: Invalid login format.".encode())
            except:
                pass
            conn.close()
            return
            
        parts = first_msg.split("|")
        username = parts[0].strip()
        group = parts[1].strip()
        password = parts[2].strip() if len(parts) > 2 else ""
        current_group = group

        # Password check (Only for joining, not creating)
        if group not in groups:
            try:
                conn.sendall("[SERVER]: Group does not exist.".encode())
            except:
                pass
            conn.close()
            return
            
        if groups[group]["password"] != password:
            try:
                conn.sendall("[SERVER]: Incorrect password.".encode())
            except:
                pass
            conn.close()
            return

        # Register client
        clients[conn] = {"username": username, "group": group}
        if conn not in groups[group]["members"]:
            groups[group]["members"].append(conn)

        if group in messages_buffer and messages_buffer[group]:
            for buffered_msg in messages_buffer[group][-30:]:
                try:
                    conn.sendall((buffered_msg + "\n").encode())
                except:
                    pass

        # Check if this is a monitoring connection - don't announce if so
        is_monitor = "__monitor" in username
        
        # Announce join to group (only for real users, not monitors)
        if not is_monitor:
            join_announcement = f"[SERVER]: {username} joined the group."
            broadcast_message(join_announcement, sender_conn=conn, group=group)

        # Send welcome message and recent messages
        welcome_msg = f"[SERVER]: Welcome {username} to {group}!"
        try:
            conn.sendall((welcome_msg + "\n").encode())
        except:
            pass
        
        # Main message loop
        while True:
            try:
                msg = conn.recv(1024).decode().strip()
                if not msg:
                    break

                if msg.startswith("LEAVE_GROUP|"):
                    leave_user = msg.split("|", 1)[1]
                    # Don't announce leaving for monitor connections
                    if not "__monitor" in leave_user:
                        announcement = f"[SERVER]: {leave_user} left the group."
                        broadcast_message(announcement, sender_conn=conn, group=group)
                    left_already = True
                    break
                    
                # Don't store messages from monitor connections in buffer
                if not is_monitor:
                    messages_buffer[group].append(msg)
                    if len(messages_buffer[group]) > MAX_BUFFER:
                        messages_buffer[group].pop(0)
                    
                broadcast_message(msg, sender_conn=conn, group=group)

            except Exception as e:
                print(f"[ERROR] in message loop: {e}")
                break

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")

    finally:
        if conn in clients:
            left_user = clients[conn]["username"]
            left_group = clients[conn]["group"]
            is_monitor = "__monitor" in left_user

            # Only announce leaving for real users, not monitors
            if not left_already and left_group and not is_monitor:
                announcement = f"[SERVER]: {left_user} left the group."
                try:
                    broadcast_message(announcement, sender_conn=conn, group=left_group)
                except:
                    pass

            if left_group in groups and conn in groups[left_group]["members"]:
                groups[left_group]["members"].remove(conn)
            
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