import tkinter as tk
import socket
from tkinter import simpledialog, messagebox
from network import connect_to_server # Import the connection function

class GroupListWindow:
    def __init__(self, ip_address, joined_groups): # <-- CHANGE THIS
        self.ip_address = ip_address
        self.joined_groups = joined_groups # <-- ADD THIS
        self.groups = []
        self.selected_group = None
        self.selected_group_password = None

        # --- The rest of the __init__ method is the same ---
        self.root = tk.Tk()
        self.root.title("Group List")
        self.root.geometry("400x500")
        self.root.configure(bg="white")

        header = tk.Label(
            self.root, text="Group List",
            font=("Arial", 18, "bold"),
            bg="white", pady=10
        )
        header.pack(fill=tk.X)

        container = tk.Frame(self.root, bg="white")
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
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set) # Link scrollbar

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # Buttons
        create_btn = tk.Button(
            self.root, text="Create Group",
            font=("Arial", 12, "bold"),
            bg="#89b4fa", fg="black",
            command=self.create_group
        )
        create_btn.pack(pady=10, ipadx=10, ipady=5, fill=tk.X, padx=20)

        join_btn = tk.Button(
            self.root, text="Join Selected Group",
            font=("Arial", 12, "bold"),
            bg="#a6e3a1", fg="black",
            command=self.join_group
        )
        join_btn.pack(pady=(0,20), ipadx=10, ipady=5, fill=tk.X, padx=20)

        # Initial fetch and display
        self.fetch_groups()
        self.display_groups()

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
            # We'll add this logic to backend.py
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

    def run(self):
        self.root.mainloop()
        return self.selected_group, self.selected_group_password