# In main.py
from login import LoginWindow
from chat import ChatWindow
from grouplist import GroupListWindow
from network import connect_to_server
import tkinter as tk # <-- ADD THIS
from tkinter import messagebox # <-- ADD THIS

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
            
        while True:
            # Pass the dictionary of joined groups to the window
            group_window = GroupListWindow(self.ip_address, self.joined_groups) # <-- CHANGE THIS
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
                response = chat_client.recv(1024).decode()
                chat_client.settimeout(None) # Reset timeout
                
                # Check if login failed
                if "[SERVER]: Incorrect password." in response or "[SERVER]: Group does not exist." in response:
                    messagebox.showerror("Join Failed", response.replace("[SERVER]:", "").strip())
                    # If we used a stored password and it failed, remove it
                    if selected_group in self.joined_groups:
                        del self.joined_groups[selected_group]
                    chat_client.close()
                    continue # Go back to the group list
                
                # --- If we get here, login was successful! ---
                
                # 1. Store the successful credentials
                self.joined_groups[selected_group] = group_password
                
                # 2. Start the chat, passing the first message (e.g., the welcome message) to it
                chat = ChatWindow(self.username, chat_client, selected_group, initial_message=response)
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