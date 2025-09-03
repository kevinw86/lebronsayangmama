def chat_session(username, ip_address, joined_groups):
    """
    Handles the group selection, connection, and chat loop for the user.
    Returns when the user exits the chat/group list.
    """
    from grouplist import GroupListWindow
    from chat import ChatWindow
    from tkinter import messagebox
    while True:
        group_window = GroupListWindow(username, ip_address, joined_groups)
        selected_group, group_password = group_window.run()
        group_window.root.destroy()

        if not selected_group:
            break

        try:
            chat_client = connect_to_server(host=ip_address)
            login_msg = f"{username}|{selected_group}|{group_password}"
            chat_client.sendall(login_msg.encode())
            chat_client.settimeout(3)
            response = chat_client.recv(4096).decode()
            chat_client.settimeout(None)
            initial_messages = [m for m in response.strip().split("\n") if m]
            if any("Incorrect password" in m or "Group does not exist" in m for m in initial_messages):
                messagebox.showerror("Join Failed", " ".join(initial_messages).replace("[SERVER]:", "").strip())
                if selected_group in joined_groups:
                    del joined_groups[selected_group]
                chat_client.close()
                continue
            joined_groups[selected_group] = group_password
            chat = ChatWindow(username, ip_address, chat_client, selected_group, initial_messages)
            chat.run()
            try:
                chat_client.close()
            except:
                pass
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to chat: {e}")
            break
import socket

def connect_to_server(host="127.0.0.1", port=5556):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    return client
