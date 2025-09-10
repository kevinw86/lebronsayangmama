import tkinter as tk
from tkinter import ttk
import datetime
import threading
import socket
from notification import NotificationWindow


class ChatWindow:
    def __init__(self, username, ip_address, client, group_name, initial_message=None, notification_system=None):
        self.username = username
        self.client = client
        self.group_name = group_name
        self.initial_message = initial_message
        self.ip_address = ip_address
        self.notification_system = notification_system

        # Mark this group as active in notification system
        if self.notification_system:
            self.notification_system.set_active_group(group_name)

        # --- Main Window ---
        self.root = tk.Tk()
        self.root.title(f"Group Chat - {group_name} ({username})")
        self.root.geometry("800x700")
        self.root.configure(bg="white")

        # --- Main layout: left sidebar and right main area ---
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

        # Current group section
        tk.Label(
            left_sidebar,
            text="Current Group",
            font=("Segoe UI", 10, "bold"),
            bg="#2c3e50",
            fg="#bdc3c7"
        ).pack(pady=(0, 5), anchor="w")

        group_frame = tk.Frame(left_sidebar, bg="#34495e", relief="flat", bd=0)
        group_frame.pack(pady=(0, 25), fill="x")
        
        group_inner = tk.Frame(group_frame, bg="#34495e")
        group_inner.pack(fill="x", padx=15, pady=12)
        
        tk.Label(
            group_inner,
            text=f"💬 {self.group_name}",
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

        # --- Right main area ---
        right_container = tk.Frame(main_container, bg="white")
        right_container.pack(side="left", fill="both", expand=True)

        # --- Header with group name and notification button ---
        header_frame = tk.Frame(right_container, bg="#3498db", height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Header content container
        header_content = tk.Frame(header_frame, bg="#3498db")
        header_content.pack(fill="both", expand=True, padx=25, pady=15)
        
        header = tk.Label(
            header_content,
            text=f"💬 {group_name}",
            font=("Segoe UI", 20, "bold"),
            bg="#3498db",
            fg="white"
        )
        header.pack(side="left", anchor="w")
        
        # Create notification button container with indicator
        notif_container = tk.Frame(header_content, bg="#3498db")
        notif_container.pack(side="right", padx=10)

        # Modern bell icon button
        self.notif_btn = tk.Button(
            notif_container, text="🔔", font=("Segoe UI", 18), 
            bg="#2980b9", fg="white", relief="flat", bd=0,
            padx=12, pady=8, cursor="hand2",
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
        self.indicator_dot.place(in_=self.notif_btn, x=22, y=-2)  # Position at top-right of bell
        self.indicator_dot.place_forget()  # Hide initially

        # --- Back Button (moved to left sidebar bottom) ---
        back_btn = tk.Button(
            left_sidebar,
            text="⬅ Back to Groups",
            font=("Segoe UI", 10, "bold"),
            bg="#e74c3c", fg="white", relief="flat", bd=0,
            padx=15, pady=8, cursor="hand2",
            command=self.back_to_groups
        )
        back_btn.pack(side="bottom", fill="x", pady=(20, 0))
        
        # Hover effects for back button
        back_btn.bind("<Enter>", lambda e: back_btn.configure(bg="#c0392b"))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(bg="#e74c3c"))

        # --- Main chat area with modern styling ---
        chat_main = tk.Frame(right_container, bg="#ecf0f1")
        chat_main.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Chat header section (smaller)
        chat_header_section = tk.Frame(chat_main, bg="#ecf0f1")
        chat_header_section.pack(fill="x", pady=(0, 8))
        
        # --- Scrollable Chat Frame with modern border (bigger) ---
        chat_container = tk.Frame(chat_main, bg="#ecf0f1")
        chat_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Modern chat frame with shadow effect
        chat_border = tk.Frame(chat_container, bg="#bdc3c7", bd=0, relief="flat")
        chat_border.pack(fill="both", expand=True)

        chat_frame = tk.Frame(chat_border, bg="white", bd=0, relief="flat")
        chat_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self.canvas = tk.Canvas(chat_frame, bg="white", highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(
            chat_frame, orient="vertical", command=self.canvas.yview
        )

        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel scrolling to canvas
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # --- Modern message input section ---
        input_section = tk.Frame(chat_main, bg="#ecf0f1")
        input_section.pack(fill="x", pady=(5, 0))

        # Input container
        input_container = tk.Frame(input_section, bg="#ecf0f1")
        input_container.pack(fill="x")

        # Modern entry field with border
        entry_border = tk.Frame(input_container, bg="#bdc3c7", bd=1, relief="solid")
        entry_border.pack(side="left", fill="x", expand=True, padx=(0, 15))

        self.entry = tk.Entry(
            entry_border, font=("Segoe UI", 12), bg="white", fg="#2c3e50",
            relief="flat", bd=0, insertbackground="#2c3e50"
        )
        self.entry.pack(fill="both", expand=True, padx=8, pady=8)

        # Modern send button
        send_btn = tk.Button(
            input_container,
            text="📤 Send",
            font=("Segoe UI", 11, "bold"),
            bg="#27ae60", fg="white", relief="flat", bd=0,
            padx=18, pady=10, cursor="hand2",
            command=self.send_message
        )
        send_btn.pack(side="right")
        
        # Hover effects for send button
        send_btn.bind("<Enter>", lambda e: send_btn.configure(bg="#229954"))
        send_btn.bind("<Leave>", lambda e: send_btn.configure(bg="#27ae60"))

        self.entry.bind("<Return>", self.send_message)

        # --- Start Receiving Messages ---
        if self.initial_message:
            for msg in self.initial_message:
                self.root.after(100, self.process_message, msg)

        threading.Thread(target=self.receive_messages, daemon=True).start()
        # Handle window close (X button)
        self.root.protocol("WM_DELETE_WINDOW", self.back_to_groups)

        # Start checking for notifications
        self.update_notification_indicator()

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

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
        
            # Show/hide the red dot based on notifications from OTHER groups
            if has_notifications:
                self.indicator_dot.place(in_=self.notif_btn, x=22, y=-2)
            else:
                self.indicator_dot.place_forget()

            # Schedule next update
            self.root.after(1000, self.update_notification_indicator)
                
        except Exception as e:
            print(f"[ERROR] Updating notification indicator: {e}")

    def open_notifications(self):
        """Open notification window showing messages from other groups"""
        # Mark notifications as viewed when bell is clicked (hides the red dot)
        if self.notification_system:
            self.notification_system.mark_notifications_as_viewed()
        
        # Then open the notification window
        if self.notification_system:
            unread = self.notification_system.get_unread_messages()
            # Show notifications window with real-time updates
            NotificationWindow(
                self.username, 
                self.ip_address, 
                self.root, 
                unread, 
                self.notification_system
            )
        else:
            # Fallback if no notification system
            notifications = {
                "Sample Group": ["You have new messages from other groups."]
            }
            NotificationWindow(
                self.username, 
                self.ip_address, 
                self.root, 
                notifications
            )
    
    def add_message(self, name, msg, is_me=False):
        timestamp = datetime.datetime.now().strftime("%H:%M")

        row = tk.Frame(self.scrollable_frame, bg="white")
        row.pack(fill="x", pady=(8, 4), padx=20)
        
        # Configure grid columns to push user messages to the right corner
        if is_me:
            row.grid_columnconfigure(0, weight=10)  # Much more weight to left column
            row.grid_columnconfigure(1, weight=1, minsize=200)  # Fixed minimum size for right column
        else:
            row.grid_columnconfigure(0, weight=1, minsize=200)  # Fixed minimum size for left column
            row.grid_columnconfigure(1, weight=10)  # Much more weight to right column

        col = 1 if is_me else 0
        sticky = "ne" if is_me else "nw"
        name_fg = "#27ae60" if is_me else "#3498db"
        bubble_bg = "#d5f4e6" if is_me else "#ebf3fd"
        bubble_border = "#27ae60" if is_me else "#3498db"
        name_anchor = "ne" if is_me else "nw"
        bubble_anchor = "e" if is_me else "w"

        block = tk.Frame(row, bg="white")
        # Push user messages to the very right corner with maximum padding
        padx_value = (100, 5) if is_me else (5, 100)
        block.grid(row=0, column=col, sticky=sticky, padx=padx_value)

        # Modern name label
        tk.Label(
            block,
            text=name,
            font=("Segoe UI", 9, "bold"),
            bg="white",
            fg=name_fg
        ).pack(anchor=name_anchor, pady=(0, 4))

        # Message bubble container for shadow effect
        bubble_container = tk.Frame(block, bg="white")
        bubble_container.pack(anchor=bubble_anchor)
        
        # Shadow effect
        shadow = tk.Frame(
            bubble_container, 
            bg="#d5dbdb", 
            height=1
        )
        shadow.pack(fill="x", pady=(2, 0))
        
        # Modern message bubble
        bubble = tk.Label(
            bubble_container,
            text=msg,
            bg=bubble_bg,
            font=("Segoe UI", 11),
            wraplength=400,
            justify="left",
            padx=15,
            pady=10,
            bd=1,
            relief="solid",
            borderwidth=1,
            highlightbackground=bubble_border,
            highlightcolor=bubble_border,
            highlightthickness=0
        )
        bubble.pack(anchor=bubble_anchor)

        # Modern timestamp
        tk.Label(
            block,
            text=timestamp,
            font=("Segoe UI", 8),
            fg="#7f8c8d",
            bg="white"
        ).pack(anchor=bubble_anchor, pady=(4, 0))

        # Auto-scroll
        self.root.after(50, lambda: self.canvas.yview_moveto(1.0))

    def send_message(self, event=None):
        msg = self.entry.get().strip()
        if msg:
            try:
                formatted_msg = f"{self.username}: {msg}"
                self.client.sendall(formatted_msg.encode())
                self.add_message(self.username, msg, is_me=True)
            except Exception as e:
                print("Send failed:", e)
        self.entry.delete(0, tk.END)
        self.entry.focus()
        
    def process_message(self, msg):
        if msg.startswith("[SERVER]:"):
            announcement = msg.replace("[SERVER]:", "").strip()
            self.add_announcement(announcement)
            return
        
        if msg.startswith("GROUPLIST:"):
            return
            
        if ":" in msg:
            sender, text = msg.split(":", 1)
            self.add_message(sender.strip(), text.strip(), is_me=(sender.strip() == self.username))
        else:
            self.add_message("System", msg, is_me=False)

    def receive_messages(self):
        while True:
            try:
                data = self.client.recv(1024).decode()
                if not data:
                    break

                for msg in data.strip().split("\n"):
                    if msg:
                        self.root.after(0, self.process_message, msg)

            except Exception as e:
                print(f"Receive error: {e}")
                self.root.after(0, self.add_announcement, "Connection to server lost.")
                break

    def add_announcement(self, text):
        row = tk.Frame(self.scrollable_frame, bg="white")
        row.pack(fill="x", pady=10, padx=20)
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)
        row.grid_columnconfigure(2, weight=1)

        # Modern announcement container
        announcement_container = tk.Frame(row, bg="white")
        announcement_container.grid(row=0, column=1, padx=15, sticky="ew")
        
        # Card with rounded effect simulation
        card_shadow = tk.Frame(announcement_container, bg="#d5dbdb", height=2)
        card_shadow.pack(fill="x", pady=(2, 0))
        
        card_frame = tk.Frame(
            announcement_container, 
            bg="#f39c12", 
            relief="flat", 
            bd=1,
            highlightbackground="#e67e22",
            highlightthickness=1
        )
        card_frame.pack(fill="x")
        
        # Card content
        content_frame = tk.Frame(card_frame, bg="#f39c12")
        content_frame.pack(fill="x", padx=20, pady=12)
        
        # System icon
        tk.Label(
            content_frame,
            text="📢",
            font=("Segoe UI", 14),
            bg="#f39c12",
            fg="white"
        ).pack(side="left", padx=(0, 10))
        
        # Announcement text
        ann = tk.Label(
            content_frame,
            text=text,
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#f39c12",
            wraplength=450,
            justify="center"
        )
        ann.pack(side="left", fill="x", expand=True)

        # Auto-scroll
        self.root.after(50, lambda: self.canvas.yview_moveto(1.0))

    def back_to_groups(self):
        try:
            self.client.sendall(f"LEAVE_GROUP|{self.username}".encode())
        except Exception as e:
            print(f"Failed to send LEAVE_GROUP message: {e}")

        # Clear active group from notification system
        if self.notification_system:
            try:
                self.notification_system.set_active_group(None)
            except Exception as e:
                print(f"Error clearing active group: {e}")

        # Close the client socket
        try:
            self.client.close()
        except Exception as e:
            print(f"Error closing client socket: {e}")

        # Destroy window
        self.root.destroy()

    def run(self):
        self.root.mainloop()