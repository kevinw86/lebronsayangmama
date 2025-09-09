import tkinter as tk
import socket
from tkinter import simpledialog, messagebox
from network import connect_to_server # Import the connection function

class GroupListWindow:
    def __init__(self, username, ip_address, joined_groups):
        self.username = username
        self.ip_address = ip_address
        self.joined_groups = joined_groups
        self.groups = []
        self.selected_group = None
        self.selected_group_password = None

        # --- The rest of the __init__ method is the same ---
        self.root = tk.Tk()
        self.root.title("Group List")
        self.root.geometry("400x500")
        self.root.configure(bg="white")


        # --- Main layout: left sidebar and right main area ---
        main_container = tk.Frame(self.root, bg="white")
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- Left Sidebar ---
        sidebar_container = tk.Frame(main_container, bg="#e0e0e0", bd=2, relief="ridge", width=135)
        sidebar_container.pack(side="left", fill="y")
        sidebar_container.pack_propagate(False)

        left_sidebar = tk.Frame(sidebar_container, bg="white")
        left_sidebar.pack(fill="both", expand=True, padx=16, pady=16)

        # Username label above box
        tk.Label(
            left_sidebar,
            text="Username",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#454545"
        ).pack(pady=(10,0), padx=5, anchor="w")

        # Username box
        username_frame = tk.Frame(left_sidebar, bg="#f5f5f5", relief="groove", bd=3, padx=6, pady=6)
        username_frame.pack(pady=(5,15), padx=5, fill="x")
        tk.Label(
            username_frame,
            text=f"{self.username}",
            font=("Arial", 12, "bold"),
            bg="#f5f5f5"
        ).pack(pady=8)

        # IP Address label above box
        tk.Label(
            left_sidebar,
            text="IP Address",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#454545"
        ).pack(pady=(0,0), padx=5, anchor="w")

        # IP Address box
        ip_frame = tk.Frame(left_sidebar, bg="#f5f5f5", relief="groove", bd=3, padx=6, pady=6)
        ip_frame.pack(pady=(5,15), padx=5, fill="x")
        tk.Label(
            ip_frame,
            text=f"{self.ip_address}",
            font=("Arial", 12, "bold"),
            bg="#f5f5f5"
        ).pack(pady=8)

        # --- Right main area ---
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

        # Notification button (after group list is displayed)
        notif_btn = tk.Button(
            header_frame, text="🔔", font=("Arial", 16), bg="white", fg="darkred",
            relief="flat", command=self.open_notifications
        )
        notif_btn.pack(side="right", padx=10, pady=5)

        # --- Scrollable group list ---
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

        # Initial fetch and display
        self.fetch_groups()
        self.display_groups()

        # --- Action buttons at the bottom ---
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

    def open_notifications(self):
        notifications = []
        client = None
        try:
            client = connect_to_server(host=self.ip_address)
            client.sendall(f"GETNOTIFICATIONS:{self.username}".encode())
            client.settimeout(2)
            data = client.recv(4096).decode()
            if data.startswith("NOTIFICATIONS:"):
                notif_str = data[len("NOTIFICATIONS:"):].strip()
                notifications = [n for n in notif_str.split("||") if n]
        except Exception as e:
            print(f"Error fetching notifications: {e}")
        finally:
            if client:
                client.close()
        from notification import NotificationWindow
        NotificationWindow(self.username, self.ip_address, self.root, notifications)

    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def fetch_groups(self):
        client = None
        try:
            # Create a NEW connection just for this task
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
                client.close() # Always close the temporary connection

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
        # Visual feedback for selection
        for w in self.group_frame.winfo_children():
            w.config(bg="white")
            for label in w.winfo_children():
                label.config(bg="white")
        
        # Find the parent frame to highlight
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
        # Check if we already have a password for this group
        if self.selected_group in self.joined_groups:
            self.selected_group_password = self.joined_groups[self.selected_group]
            self.root.quit() # Join automatically
            return
        password = simpledialog.askstring("Join Group", f"Enter password for '{self.selected_group}':", show='*')
        if password is not None: # Check for cancel button
            self.selected_group_password = password
            self.root.quit()


    def create_group(self):
        groupname = simpledialog.askstring("Create Group", "Enter new group name:")
        if not groupname:
            return
        password = simpledialog.askstring("Create Group", "Set group password:", show='*')
        if password is None: # User cancelled
            return
        client = None
        try:
            # Create a NEW connection for this task
            client = connect_to_server(host=self.ip_address)
            # The backend needs to handle CREATEGROUP as a first message.
            client.sendall(f"CREATEGROUP:{groupname}|{password}".encode())
            client.settimeout(2)
            resp = client.recv(1024).decode()
            if resp:
                messagebox.showinfo("Server Response", resp)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create group: {e}")
        finally:
            if client:
                client.close() # Always close the connection
        # After attempting to create, refresh the group list
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
            # The backend needs to handle DELETEGROUP as a first message.
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
        # After attempting to delete, refresh the group list
        self.fetch_groups()
        self.display_groups()

    def run(self):
        self.root.mainloop()
        return self.selected_group, self.selected_group_password