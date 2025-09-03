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

        # Delegate group/chat logic to network.py
        from network import chat_session
        chat_session(self.username, self.ip_address, self.joined_groups)

if __name__ == "__main__":
    app = ChatApp()
    app.run()