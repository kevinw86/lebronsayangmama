# In main.py
from login import LoginWindow
from chat import ChatWindow
from grouplist import GroupListWindow
from network import connect_to_server
import tkinter as tk
from tkinter import messagebox
from notification import NotificationWindow

class ChatApp:
    def __init__(self):
        self.username = None
        self.ip_address = None
        self.joined_groups = {} # <-- ADD THIS DICTIONARY to store {group_name: password}
        
    def run(self):
        # Login
        login = LoginWindow()
        self.username, self.ip_address = login.run()
        if not self.username or not self.ip_address:
            return

        # Directly show group list and handle chat loop
        while True:
            group_window = GroupListWindow(self.username, self.ip_address, self.joined_groups)
            selected_group, group_password = group_window.run()
            group_window.root.destroy()

            if not selected_group:
                break

            # --- CONNECTION AND VALIDATION LOGIC ---
            try:
                chat_client = connect_to_server(host=self.ip_address)

                # Send login info
                login_msg = f"{self.username}|{selected_group}|{group_password}"
                chat_client.sendall(login_msg.encode())

                # Wait for the server's first response to validate
                chat_client.settimeout(3) # Wait up to 3 seconds for a response
                response = chat_client.recv(4096).decode()
                chat_client.settimeout(None) # Reset timeout

                # Split into individual messages
                initial_messages = [m for m in response.strip().split("\n") if m]

                # Check if login failed
                if any("Incorrect password" in m or "Group does not exist" in m for m in initial_messages):
                    messagebox.showerror("Join Failed", " ".join(initial_messages).replace("[SERVER]:", "").strip())
                    if selected_group in self.joined_groups:
                        del self.joined_groups[selected_group]
                    chat_client.close()
                    continue

                # --- Login success ---
                self.joined_groups[selected_group] = group_password

                # Start chat, passing ALL initial messages
                chat = ChatWindow(self.username, self.ip_address, chat_client, selected_group, initial_messages)
                chat.run()

                try:
                    chat_client.close()
                except:
                    pass

            except Exception as e:
                messagebox.showerror("Connection Error", f"Could not connect to chat: {e}")
                break

if __name__ == "__main__":
    app = ChatApp()
    app.run()