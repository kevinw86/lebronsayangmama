import tkinter as tk
import socket
from tkinter import simpledialog, messagebox
from network import connect_to_server
import threading
import time

class GroupListWindow:
    def __init__(self, username, ip_address, joined_groups, notification_system=None):
        self.username = username
        self.ip_address = ip_address
        self.joined_groups = joined_groups
        self.notification_system = notification_system
        self.groups = []
        self.selected_group = None
        self.selected_group_password = None
        self.was_closed = False  # Flag to track if window was closed manually

        if self.notification_system:
            self.notification_system.set_group_window(self)

        self.root = tk.Tk()
        self.root.title("Group List")
        self.root.geometry("400x500")
        self.root.configure(bg="white")

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        main_container = tk.Frame(self.root, bg="white")
        main_container.pack(fill=tk.BOTH, expand=True)

        sidebar_container = tk.Frame(main_container, bg="#e0e0e0", bd=2, relief="ridge", width=135)
        sidebar_container.pack(side="left", fill="y")
        sidebar_container.pack_propagate(False)

        left_sidebar = tk.Frame(sidebar_container, bg="white")
        left_sidebar.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(
            left_sidebar,
            text="Username",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#454545"
        ).pack(pady=(10,0), padx=5, anchor="w")

        username_frame = tk.Frame(left_sidebar, bg="#f5f5f5", relief="groove", bd=3, padx=6, pady=6)
        username_frame.pack(pady=(5,15), padx=5, fill="x")
        tk.Label(
            username_frame,
            text=f"{self.username}",
            font=("Arial", 12, "bold"),
            bg="#f5f5f5"
        ).pack(pady=8)

        tk.Label(
            left_sidebar,
            text="IP Address",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#454545"
        ).pack(pady=(0,0), padx=5, anchor="w")

        ip_frame = tk.Frame(left_sidebar, bg="#f5f5f5", relief="groove", bd=3, padx=6, pady=6)
        ip_frame.pack(pady=(5,15), padx=5, fill="x")
        tk.Label(
            ip_frame,
            text=f"{self.ip_address}",
            font=("Arial", 12, "bold"),
            bg="#f5f5f5"
        ).pack(pady=8)

        right_container = tk.Frame(main_container, bg="white")
        right_container.pack(side="left", fill="both", expand=True)

        header_frame = tk.Frame(right_container, bg="white")
        header_frame.pack(fill=tk.X)
        header = tk.Label(
            header_frame, text="Group List",
            font=("Arial", 18, "bold"),
            bg="white", pady=10
        )
        header.pack(side="left", fill=tk.X, expand=True)

        # Create notification button container
        notif_container = tk.Frame(header_frame, bg="white")
        notif_container.pack(side="right", padx=10, pady=5)

        # Bell icon button
        self.notif_btn = tk.Button(
            notif_container, text="🔔", font=("Arial", 16), bg="white", fg="darkred",
            relief="flat", command=self.open_notifications
        )
        self.notif_btn.pack()

        # Small red indicator dot (initially hidden)
        self.indicator_dot = tk.Label(
            notif_container, text="🔴", font=("Arial", 8), bg="white"
        )
        self.indicator_dot.place(in_=self.notif_btn, x=18, y=-2)  # Position at top-right of bell
        self.indicator_dot.place_forget()  # Hide initially

        container = tk.Frame(right_container, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(
            container, orient="vertical", command=self.canvas.yview
        )
        self.group_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.group_frame, anchor="nw")

        self.group_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        self.fetch_groups()
        self.display_groups()

        button_frame = tk.Frame(right_container, bg="white")
        button_frame.pack(side="bottom", fill="x", padx=20, pady=10)

        create_btn = tk.Button(
            button_frame, text="Create Group",
            font=("Arial", 12, "bold"),
            bg="#89b4fa", fg="black",
            command=self.create_group
        )
        create_btn.pack(fill=tk.X, pady=4)

        join_btn = tk.Button(
            button_frame, text="Join Selected Group",
            font=("Arial", 12, "bold"),
            bg="#a6e3a1", fg="black",
            command=self.join_group
        )
        join_btn.pack(fill=tk.X, pady=4)

        delete_btn = tk.Button(
            button_frame, text="Delete Selected Group",
            font=("Arial", 12, "bold"),
            bg="#f38ba8", fg="white",
            command=self.delete_group
        )
        delete_btn.pack(fill=tk.X, pady=4)

        # Start checking for notifications
        self.update_notification_indicator()

    def update_notification_indicator(self):
        """Update the notification indicator dot"""
        try:
            if not self.root.winfo_exists():
                return  # Window destroyed, do nothing
        
            has_notifications = False
            if self.notification_system:
                try:
                    has_notifications = self.notification_system.has_unread_messages()
                except Exception as e:
                    print(f"[ERROR] Checking unread messages: {e}")
        
            # Show/hide the red dot based on notifications
            if has_notifications:
                self.indicator_dot.place(in_=self.notif_btn, x=18, y=-2)
            else:
                self.indicator_dot.place_forget()

            # Schedule next update
            self.root.after(1000, self.update_notification_indicator)
                
        except Exception as e:
            print(f"[ERROR] Updating notification indicator: {e}")

    def on_closing(self):
        """Handle the window close event"""
        self.was_closed = True
        if self.notification_system:
            self.notification_system.set_group_window(None)  # Clear reference in notification system
        try:
            self.root.destroy()
        except Exception as e:
            print(f"[ERROR] Destroying group list window: {e}")

    def open_notifications(self):
        # Mark notifications as viewed when bell is clicked (hides the red dot)
        if self.notification_system:
            self.notification_system.mark_notifications_as_viewed()
        
        # Then open the notification window
        if self.notification_system:
            unread = self.notification_system.get_unread_messages()
            if unread:
                from notification import NotificationWindow
                # Pass notification system but don't clear yet
                NotificationWindow(self.username, self.ip_address, self.root, unread, self.notification_system)
            else:
                notifications = {
                    "Welcome": ["You have no new notifications.", "Welcome to SevenChat!"]
                }
                from notification import NotificationWindow
                NotificationWindow(self.username, self.ip_address, self.root, notifications, self.notification_system)
        else:
            notifications = {
                "Sample": ["You have a new message in Group1.", "Group2 was updated.", "Welcome to SevenChat!"]
            }
            from notification import NotificationWindow
            NotificationWindow(self.username, self.ip_address, self.root, notifications, self.notification_system)

    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def fetch_groups(self):
        client = None
        try:
            client = connect_to_server(host=self.ip_address)
            client.sendall("GETGROUPS".encode())
            client.settimeout(2)
            data = client.recv(4096).decode()
            if data.startswith("GROUPLIST:"):
                group_str = data[len("GROUPLIST:"):].strip()
                self.groups = [g for g in group_str.split(",") if g]
            else:
                self.groups = []
        except Exception as e:
            print(f"Error fetching groups: {e}")
            self.groups = []
        finally:
            if client:
                client.close()

    def display_groups(self):
        for widget in self.group_frame.winfo_children():
            widget.destroy()

        if not self.groups:
            tk.Label(
                self.group_frame, text="No groups found. Create one!",
                font=("Arial", 12), bg="white", fg="gray"
            ).pack(pady=20)
            return

        for idx, group in enumerate(self.groups):
            color = "#a6e3a1" if idx % 2 == 0 else "#f9e2af"
            frame = tk.Frame(
                self.group_frame, bg="white", highlightbackground=color,
                highlightthickness=2, bd=0
            )
            frame.pack(fill=tk.X, expand=True, pady=4, padx=10)
            label = tk.Label(
                frame, text=group, font=("Arial", 14, "bold"),
                bg="white", fg="black", pady=10, anchor="w"
            )
            label.pack(fill=tk.X, expand=True, padx=10)
            frame.bind("<Button-1>", lambda e, g=group: self.select_group(g, e.widget))
            label.bind("<Button-1>", lambda e, g=group: self.select_group(g, e.widget.master))
            frame.bind("<Double-Button-1>", lambda e, g=group: self.open_group(g))
            label.bind("<Double-Button-1>", lambda e, g=group: self.open_group(g))

    def select_group(self, group_name, widget):
        self.selected_group = group_name
        for w in self.group_frame.winfo_children():
            w.config(bg="white")
            for label in w.winfo_children():
                label.config(bg="white")
        
        parent_frame = widget if isinstance(widget, tk.Frame) else widget.master
        parent_frame.config(bg="#fadadd")
        for label in parent_frame.winfo_children():
            label.config(bg="#fadadd")

    def open_group(self, group_name):
        self.selected_group = group_name
        self.join_group()

    def join_group(self):
        if self.selected_group is None:
            messagebox.showwarning("No Group Selected", "Please select a group to join.")
            return
        if self.selected_group in self.joined_groups:
            self.selected_group_password = self.joined_groups[self.selected_group]
            self.root.quit()
            return
        password = simpledialog.askstring("Join Group", f"Enter password for '{self.selected_group}':", show='*')
        if password is not None:
            self.selected_group_password = password
            self.root.quit()

    def create_group(self):
        groupname = simpledialog.askstring("Create Group", "Enter new group name:")
        if not groupname:
            return
        password = simpledialog.askstring("Create Group", "Set group password:", show='*')
        if password is None:
            return
        client = None
        try:
            client = connect_to_server(host=self.ip_address)
            client.sendall(f"CREATEGROUP:{groupname}|{password}".encode())
            client.settimeout(2)
            resp = client.recv(1024).decode()
            if resp:
                messagebox.showinfo("Server Response", resp)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create group: {e}")
        finally:
            if client:
                client.close()
        self.fetch_groups()
        self.display_groups()

    def delete_group(self):
        if self.selected_group is None:
            messagebox.showwarning("No Group Selected", "Please select a group to delete.")
            return
        confirm = messagebox.askyesno("Delete Group", f"Are you sure you want to delete '{self.selected_group}'?")
        if not confirm:
            return
        password = simpledialog.askstring("Delete Group", f"Enter password for '{self.selected_group}':", show='*')
        if password is None:
            return
        client = None
        try:
            client = connect_to_server(host=self.ip_address)
            client.sendall(f"DELETEGROUP:{self.selected_group}|{password}".encode())
            client.settimeout(2)
            resp = client.recv(1024).decode()
            if resp:
                messagebox.showinfo("Server Response", resp)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete group: {e}")
        finally:
            if client:
                client.close()
        self.fetch_groups()
        self.display_groups()

    def run(self):
        self.root.mainloop()
        return self.selected_group, self.selected_group_password