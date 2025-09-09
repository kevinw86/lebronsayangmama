import socket
import threading
from tkinter import messagebox

def chat_session(username, ip_address, joined_groups):
    """
    Handles the group selection, connection, and chat loop for the user.
    Returns when the user exits the chat/group list.
    """
    from grouplist import GroupListWindow
    from chat import ChatWindow
    
    # CREATE: Enhanced notification system
    notification_system = EnhancedNotificationSystem(username, ip_address, joined_groups)
    
    while True:
        group_window = GroupListWindow(username, ip_address, joined_groups, notification_system)
        selected_group, group_password = group_window.run()
        # group_window.run() blocks until window closed or selection made
        try:
            group_window.root.destroy()
            notification_system.set_group_window(None)

        except:
            pass
        
        if not selected_group:
            notification_system.stop()
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
            
            # Set active group and start monitoring
            notification_system.set_active_group(selected_group)
            notification_system.start_monitoring_other_groups()
            
            chat = ChatWindow(username, ip_address, chat_client, selected_group, initial_messages, notification_system)
            chat.run()
            
            # Clear active group
            notification_system.set_active_group(None)
            
            try:
                chat_client.close()
            except:
                pass
                
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to chat: {e}")
            break


class EnhancedNotificationSystem:
    def __init__(self, username, ip_address, joined_groups):
        self.username = username
        self.ip_address = ip_address
        self.joined_groups = joined_groups
        self.active_group = None
        self.unread_messages = {}  # {group: [messages]}
        self.group_window = None
        self.running = True
        self.monitoring_threads = {}  # {group: thread}
        self.monitoring_active = False
        self.lock = threading.Lock()  # protect unread_messages and related state
    
    def set_active_group(self, group_name):
        """Set which group is currently active (chat window open)"""
        old_active = self.active_group
        self.active_group = group_name
        
        # Clear unread messages for now-active group
        if group_name:
            with self.lock:
                if group_name in self.unread_messages:
                    del self.unread_messages[group_name]
            # schedule UI update on main thread if possible
            if self.group_window and hasattr(self.group_window, "root"):
                try:
                    self.group_window.root.after(0, self.group_window.update_notification_indicator)
                except Exception:
                    pass
        
        # If switching from one group to another, restart monitoring
        if old_active != group_name and self.monitoring_active:
            self.restart_monitoring()
    
    def set_group_window(self, group_window):
        """Set reference to group list window for updating notifications"""
        self.group_window = group_window
    
    def add_notification(self, group, message):
        """Add a notification for a specific group (thread-safe)"""
        # Don't add notification for active group
        if group == self.active_group:
            return
        
        with self.lock:
            if group not in self.unread_messages:
                self.unread_messages[group] = []
            
            # Only keep last 10 messages per group to avoid memory issues
            self.unread_messages[group].append(message)
            if len(self.unread_messages[group]) > 10:
                self.unread_messages[group].pop(0)
        
        # Schedule UI update safely on main thread
        if self.group_window and hasattr(self.group_window, "root"):
            try:
                self.group_window.root.after(0, self.group_window.update_notification_indicator)
            except Exception:
                # if scheduling fails, ignore (can't update UI from here)
                pass
    
    def get_unread_messages(self):
        """Get all unread messages (thread-safe copy)"""
        with self.lock:
            # return a shallow copy to avoid callers mutating our internal lists
            copy = {g: list(msgs) for g, msgs in self.unread_messages.items()}
        return copy
    
    def clear_notifications(self):
        """Clear all notifications"""
        with self.lock:
            self.unread_messages.clear()
        if self.group_window and hasattr(self.group_window, "root"):
            try:
                self.group_window.root.after(0, self.group_window.update_notification_indicator)
            except Exception:
                pass
    
    def start_monitoring_other_groups(self):
        """Start monitoring other groups for new messages"""
        self.monitoring_active = True
        self.restart_monitoring()
    
    def restart_monitoring(self):
        """Restart monitoring threads for non-active groups"""
        # Stop existing monitoring threads
        # (we join briefly to give them a chance to finish)
        for thread in self.monitoring_threads.values():
            if thread.is_alive():
                try:
                    thread.join(timeout=0.1)
                except Exception:
                    pass
        self.monitoring_threads.clear()
        
        # Start monitoring for each joined group except the active one
        for group in list(self.joined_groups.keys()):
            if group != self.active_group and self.running:
                thread = threading.Thread(
                    target=self.monitor_group, 
                    args=(group,), 
                    daemon=True
                )
                thread.start()
                self.monitoring_threads[group] = thread
    
    def monitor_group(self, group_name):
        """Monitor a specific group for new messages"""
        client = None
        try:
            # Create connection with a special notification username
            client = connect_to_server(host=self.ip_address)
            password = self.joined_groups.get(group_name, "")
            login_msg = f"{self.username}_notify|{group_name}|{password}"
            client.sendall(login_msg.encode())
            client.settimeout(2)
        
            # Read and ignore initial messages
            try:
                initial_data = client.recv(4096).decode()
            except socket.timeout:
                initial_data = ""
            except Exception:
                initial_data = ""
        
            client.settimeout(1.0)  # Short timeout for monitoring
        
            while self.running and group_name != self.active_group:
                try:
                    data = client.recv(1024).decode()
                    if data:
                        # Process new messages
                        for msg in data.strip().split("\n"):
                            if msg and ":" in msg:
                                sender, text = msg.split(":", 1)
                                sender = sender.strip()
                                text = text.strip()
                                # Filter out _notify join/leave messages
                                if sender.endswith("_notify"):
                                    continue
                                if "joined the group" in text or "left the group" in text:
                                    continue
                                if sender != self.username:  # Don't notify for our own messages
                                    self.add_notification(group_name, msg)
            
                except socket.timeout:
                    continue  # Normal timeout, keep monitoring
                except Exception as e:
                    print(f"Monitoring error for {group_name}: {e}")
                    break

        except Exception as e:
            print(f"Failed to start monitoring for {group_name}: {e}")

        finally:
            if client:
                try:
                    client.close()
                except:
                    pass


    
    def stop(self):
        """Stop the notification system"""
        self.running = False
        self.monitoring_active = False
        
        # Wait for monitoring threads to finish
        for thread in self.monitoring_threads.values():
            if thread.is_alive():
                try:
                    thread.join(timeout=1.0)
                except Exception:
                    pass


def connect_to_server(host="127.0.0.1", port=5556):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    return client
