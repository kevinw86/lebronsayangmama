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
        self.root.geometry("800x700")
        self.root.configure(bg="white")

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        main_container = tk.Frame(self.root, bg="white")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Enhanced sidebar with gradient-like effect
        sidebar_container = tk.Frame(main_container, bg="#2c3e50", bd=0, relief="flat", width=220)
        sidebar_container.pack(side="left", fill="y")
        sidebar_container.pack_propagate(False)

        # Add a subtle border line
        border_line = tk.Frame(main_container, bg="#34495e", width=2)
        border_line.pack(side="left", fill="y")

        left_sidebar = tk.Frame(sidebar_container, bg="#2c3e50")
        left_sidebar.pack(fill="both", expand=True, padx=20, pady=25)

        # Profile section with modern styling
        profile_header = tk.Label(
            left_sidebar,
            text="👤 Profile",
            font=("Segoe UI", 14, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        profile_header.pack(pady=(0, 20), anchor="w")

        # Username section with modern card design
        tk.Label(
            left_sidebar,
            text="Username",
            font=("Segoe UI", 10, "bold"),
            bg="#2c3e50",
            fg="#bdc3c7"
        ).pack(pady=(0, 5), anchor="w")

        username_frame = tk.Frame(left_sidebar, bg="#34495e", relief="flat", bd=0)
        username_frame.pack(pady=(0, 20), fill="x")
        
        username_inner = tk.Frame(username_frame, bg="#34495e")
        username_inner.pack(fill="x", padx=15, pady=12)
        
        tk.Label(
            username_inner,
            text=f"✉ {self.username}",
            font=("Segoe UI", 12, "bold"),
            bg="#34495e",
            fg="#ecf0f1"
        ).pack(anchor="w")

        # IP Address section with modern card design
        tk.Label(
            left_sidebar,
            text="Server Address",
            font=("Segoe UI", 10, "bold"),
            bg="#2c3e50",
            fg="#bdc3c7"
        ).pack(pady=(0, 5), anchor="w")

        ip_frame = tk.Frame(left_sidebar, bg="#34495e", relief="flat", bd=0)
        ip_frame.pack(pady=(0, 25), fill="x")
        
        ip_inner = tk.Frame(ip_frame, bg="#34495e")
        ip_inner.pack(fill="x", padx=15, pady=12)
        
        tk.Label(
            ip_inner,
            text=f"🌐 {self.ip_address}",
            font=("Segoe UI", 12, "bold"),
            bg="#34495e",
            fg="#ecf0f1"
        ).pack(anchor="w")

        # Status indicator
        status_frame = tk.Frame(left_sidebar, bg="#2c3e50")
        status_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(
            status_frame,
            text="🟢 Online",
            font=("Segoe UI", 10),
            bg="#2c3e50",
            fg="#27ae60"
        ).pack(anchor="w")

        right_container = tk.Frame(main_container, bg="#ecf0f1")
        right_container.pack(side="left", fill="both", expand=True)

        # Modern header with gradient-like styling
        header_frame = tk.Frame(right_container, bg="#3498db", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Header content container
        header_content = tk.Frame(header_frame, bg="#3498db")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        header = tk.Label(
            header_content, text="💬 Group List",
            font=("Segoe UI", 24, "bold"),
            bg="#3498db", fg="white"
        )
        header.pack(side="left", anchor="w")

        # Create notification button container
        notif_container = tk.Frame(header_content, bg="#3498db")
        notif_container.pack(side="right", padx=15)

        # Modern bell icon button with styling
        self.notif_btn = tk.Button(
            notif_container, text="🔔", font=("Segoe UI", 20), 
            bg="#2980b9", fg="white", relief="flat", bd=0,
            padx=15, pady=10, cursor="hand2",
            command=self.open_notifications
        )
        self.notif_btn.pack()

        # Hover effects for notification button
        self.notif_btn.bind("<Enter>", lambda e: self.notif_btn.configure(bg="#1f618d"))
        self.notif_btn.bind("<Leave>", lambda e: self.notif_btn.configure(bg="#2980b9"))

        # Small red indicator dot (initially hidden)
        self.indicator_dot = tk.Label(
            notif_container, text="🔴", font=("Arial", 8), bg="#3498db"
        )
        self.indicator_dot.place(in_=self.notif_btn, x=25, y=-2)  # Position at top-right of bell
        self.indicator_dot.place_forget()  # Hide initially

        # Main content area with modern styling
        content_wrapper = tk.Frame(right_container, bg="#ecf0f1")
        content_wrapper.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        # Groups section header
        groups_header = tk.Frame(content_wrapper, bg="#ecf0f1")
        groups_header.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            groups_header, text="Available Groups",
            font=("Segoe UI", 16, "bold"),
            bg="#ecf0f1", fg="#2c3e50"
        ).pack(anchor="w")
        
        tk.Label(
            groups_header, text="Select a group to join or manage",
            font=("Segoe UI", 11),
            bg="#ecf0f1", fg="#7f8c8d"
        ).pack(anchor="w")

        # Container for scrollable group list
        container = tk.Frame(content_wrapper, bg="#ecf0f1")
        container.pack(fill=tk.BOTH, expand=True, pady=(0, 25))

        # Modern scrollable canvas with border
        canvas_frame = tk.Frame(container, bg="#bdc3c7", bd=1, relief="solid")
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(
            canvas_frame, orient="vertical", command=self.canvas.yview,
            bg="#95a5a6", troughcolor="#ecf0f1", width=12
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

        # Modern action buttons section
        button_frame = tk.Frame(content_wrapper, bg="#ecf0f1")
        button_frame.pack(side="bottom", fill="x", pady=(15, 0))

        # Button styling with modern flat design
        create_btn = tk.Button(
            button_frame, text="➕ Create Group",
            font=("Segoe UI", 10, "bold"),
            bg="#27ae60", fg="white", relief="flat", bd=0,
            padx=15, pady=8, cursor="hand2",
            command=self.create_group
        )
        create_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Hover effects for create button
        create_btn.bind("<Enter>", lambda e: create_btn.configure(bg="#229954"))
        create_btn.bind("<Leave>", lambda e: create_btn.configure(bg="#27ae60"))

        join_btn = tk.Button(
            button_frame, text="🚪 Join Selected Group",
            font=("Segoe UI", 10, "bold"),
            bg="#3498db", fg="white", relief="flat", bd=0,
            padx=15, pady=8, cursor="hand2",
            command=self.join_group
        )
        join_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Hover effects for join button
        join_btn.bind("<Enter>", lambda e: join_btn.configure(bg="#2980b9"))
        join_btn.bind("<Leave>", lambda e: join_btn.configure(bg="#3498db"))

        delete_btn = tk.Button(
            button_frame, text="🗑️ Delete Selected Group",
            font=("Segoe UI", 10, "bold"),
            bg="#e74c3c", fg="white", relief="flat", bd=0,
            padx=15, pady=8, cursor="hand2",
            command=self.delete_group
        )
        delete_btn.pack(fill=tk.X, pady=(0, 0))
        
        # Hover effects for delete button
        delete_btn.bind("<Enter>", lambda e: delete_btn.configure(bg="#c0392b"))
        delete_btn.bind("<Leave>", lambda e: delete_btn.configure(bg="#e74c3c"))

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
            # Modern empty state design
            empty_container = tk.Frame(self.group_frame, bg="white")
            empty_container.pack(expand=True, fill="both", pady=40)
            
            tk.Label(
                empty_container, text="📋",
                font=("Segoe UI", 48), bg="white", fg="#bdc3c7"
            ).pack(pady=(20, 10))
            
            tk.Label(
                empty_container, text="No groups found",
                font=("Segoe UI", 16, "bold"), bg="white", fg="#2c3e50"
            ).pack()
            
            tk.Label(
                empty_container, text="Create your first group to get started!",
                font=("Segoe UI", 12), bg="white", fg="#7f8c8d"
            ).pack(pady=(5, 20))
            return

        for idx, group in enumerate(self.groups):
            # Modern card design for each group - smaller height
            card_frame = tk.Frame(
                self.group_frame, bg="white", relief="flat", bd=0
            )
            card_frame.pack(fill=tk.X, padx=15, pady=4)
            
            # Card shadow effect (simulated with frames)
            shadow_frame = tk.Frame(card_frame, bg="#d5dbdb", height=1)
            shadow_frame.pack(fill="x", side="bottom")
            
            # Main card content
            content_frame = tk.Frame(
                card_frame, bg="#f8f9fa", relief="solid", bd=1,
                highlightbackground="#dee2e6", highlightthickness=1
            )
            content_frame.pack(fill="x", pady=(0, 1))
            
            # Group icon and name - extended layout for longer names
            inner_frame = tk.Frame(content_frame, bg="#f8f9fa")
            inner_frame.pack(fill="x", padx=15, pady=8)
            
            # Group icon - positioned to left with minimal space
            icon_label = tk.Label(
                inner_frame, text="👥", 
                font=("Segoe UI", 16), bg="#f8f9fa"
            )
            icon_label.pack(side="left", padx=(0, 8))
            
            # Group name and info - extended to take more space
            text_frame = tk.Frame(inner_frame, bg="#f8f9fa")
            text_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
            
            name_label = tk.Label(
                text_frame, text=group, 
                font=("Segoe UI", 12, "bold"),
                bg="#f8f9fa", fg="#2c3e50", anchor="w"
            )
            name_label.pack(fill="x", anchor="w")
            
            # Status indicator - aligned left with group name
            status_label = tk.Label(
                text_frame, text="🟢 Active", 
                font=("Segoe UI", 9),
                bg="#f8f9fa", fg="#27ae60", anchor="w"
            )
            status_label.pack(fill="x", anchor="w")
            
            # Bind click events to all elements
            for widget in [card_frame, content_frame, inner_frame, icon_label, text_frame, name_label, status_label]:
                widget.bind("<Button-1>", lambda e, g=group, f=content_frame: self.select_group(g, f))
                widget.bind("<Double-Button-1>", lambda e, g=group: self.open_group(g))
                widget.bind("<Enter>", lambda e, f=content_frame: f.configure(bg="#e9ecef"))
                widget.bind("<Leave>", lambda e, f=content_frame: f.configure(bg="#f8f9fa") if not hasattr(f, '_selected') or not f._selected else None)

    def select_group(self, group_name, widget):
        self.selected_group = group_name
        
        # Reset all cards to unselected state
        for w in self.group_frame.winfo_children():
            for card in w.winfo_children():
                if hasattr(card, 'winfo_children'):
                    for content_frame in card.winfo_children():
                        if isinstance(content_frame, tk.Frame):
                            content_frame.configure(bg="#f8f9fa")
                            content_frame._selected = False
                            # Reset all child frames
                            for child in content_frame.winfo_children():
                                if isinstance(child, tk.Frame):
                                    child.configure(bg="#f8f9fa")
                                    for grandchild in child.winfo_children():
                                        if isinstance(grandchild, (tk.Label, tk.Frame)):
                                            grandchild.configure(bg="#f8f9fa")
        
        # Highlight selected card
        widget.configure(bg="#3498db")
        widget._selected = True
        
        # Update all child elements to match selection color
        for child in widget.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg="#3498db")
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, (tk.Label, tk.Frame)):
                        grandchild.configure(bg="#3498db")
                        if isinstance(grandchild, tk.Label):
                            grandchild.configure(fg="white")

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