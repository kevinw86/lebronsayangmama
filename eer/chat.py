import tkinter as tk
from tkinter import ttk
import datetime
import threading
import socket
from notification import NotificationWindow


class ChatWindow:
    def __init__(self, username, ip_address, client, group_name, initial_message=None):
        self.username = username
        self.client = client
        self.initial_message = initial_message
        self.ip_address = ip_address

        # --- Main Window ---
        self.root = tk.Tk()
        self.root.title(f"Group Chat - {group_name} ({username})")
        self.root.geometry("500x600")


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

        # --- Header with group name and notification button ---
        header_frame = tk.Frame(right_container, bg="lightgray")
        header_frame.pack(fill=tk.X)
        header = tk.Label(
            header_frame,
            text=group_name,
            font=("Arial", 18, "bold"),
            bg="lightgray",
            pady=10
        )
        header.pack(side="left", fill=tk.X, expand=True)
        notif_btn = tk.Button(
            header_frame, text="🔔", font=("Arial", 16), bg="lightgray", fg="darkred",
            relief="flat", command=self.open_notifications
        )
        notif_btn.pack(side="right", padx=10, pady=5)

        # --- Back Button (moved to left sidebar bottom) ---
        back_btn = tk.Button(
            left_sidebar,
            text="Back to Groups",
            bg="orange",
            fg="black",
            font=("Arial", 8, "bold"),
            command=self.back_to_groups
        )
        back_btn.pack(side="bottom", fill="x", padx=5, pady=10)

        # --- Scrollable Chat Frame ---
        chat_frame = tk.Frame(right_container)
        chat_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(chat_frame, bg="white")
        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Bottom Entry + Send ---
        bottom_frame = tk.Frame(right_container, bg="white")
        bottom_frame.pack(fill=tk.X, pady=5)

        self.entry = tk.Entry(bottom_frame, font=("Arial", 12))
        self.entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)

        send_btn = tk.Button(
            bottom_frame,
            text="Send",
            font=("Arial", 12, "bold"),
            bg="green",
            fg="white",
            command=self.send_message
        )
        send_btn.pack(side=tk.RIGHT, padx=10)

        self.entry.bind("<Return>", self.send_message)

        # --- Start Receiving Messages ---
        if self.initial_message:
            for msg in self.initial_message:   # ✅ loop through messages individually
                self.root.after(100, self.process_message, msg)

        threading.Thread(target=self.receive_messages, daemon=True).start()
        # Handle window close (X button)
        self.root.protocol("WM_DELETE_WINDOW", self.back_to_groups)


    def open_notifications(self):
        notifications = [
            "You have a new message in this group.",
            "Someone joined the group.",
            "Welcome to SevenChat!"
        ]
        NotificationWindow(self.username, self.ip_address, self.root, notifications)
    # --- Chat Bubble Helper ---
    def add_message(self, name, msg, is_me=False):
        timestamp = datetime.datetime.now().strftime("%H:%M")

        row = tk.Frame(self.scrollable_frame, bg="white")
        row.pack(fill="x", pady=(6, 2), padx=6)
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)

        col = 1 if is_me else 0
        sticky = "ne" if is_me else "nw"  # top right for us, left for others
        name_fg = "green" if is_me else "blue"
        bubble_bg = "lightgreen" if is_me else "lightblue"
        name_anchor = "ne" if is_me else "nw"
        bubble_anchor = "e" if is_me else "w"

        block = tk.Frame(row, bg="white")
        block.grid(row=0, column=col, sticky=sticky, padx=6)

        tk.Label(
            block,
            text=name,
            font=("Arial", 8, "bold"),
            bg="white",
            fg=name_fg
        ).pack(anchor=name_anchor)

        bubble = tk.Label(
            block,
            text=msg,
            bg=bubble_bg,
            font=("Arial", 12),
            wraplength=300,
            justify="left",
            padx=10,
            pady=6,
            bd=1,
            relief="solid"
        )
        bubble.pack(anchor=bubble_anchor, pady=(2, 0))

        tk.Label(
            block,
            text=timestamp,
            font=("Arial", 7),
            fg="gray",
            bg="white"
        ).pack(anchor=bubble_anchor, pady=(2, 0))

        # Auto-scroll
        self.root.after(50, lambda: self.canvas.yview_moveto(1.0))

    # --- Send Message ---
    def send_message(self, event=None):
        msg = self.entry.get().strip()
        if msg:
            try:
                # Send message in format: "username: message"
                formatted_msg = f"{self.username}: {msg}"
                self.client.sendall(formatted_msg.encode())
                self.add_message(self.username, msg, is_me=True)
            except Exception as e:
                print("Send failed:", e)
        self.entry.delete(0, tk.END)
        self.entry.focus()  # Add focus back to entry
        
    def process_message(self, msg):
        """Processes a single message string and adds it to the UI."""
        # Handle server announcements
        if msg.startswith("[SERVER]:"):
            announcement = msg.replace("[SERVER]:", "").strip()
            self.add_announcement(announcement)
            return # Use return instead of continue
        
        # Handle group list responses (shouldn't happen here, but good practice)
        if msg.startswith("GROUPLIST:"):
            return
            
        # Handle normal chat messages (username: message)
        if ":" in msg:
            sender, text = msg.split(":", 1)
            self.add_message(sender.strip(), text.strip(), is_me=(sender.strip() == self.username))
        else:
            # Handle other message formats
            self.add_message("System", msg, is_me=False)

    def receive_messages(self):
        while True:
            try:
                data = self.client.recv(1024).decode()
                if not data:
                    break

                # Split by newline to handle buffered history
                for msg in data.strip().split("\n"):
                    if msg:
                        # Schedule UI-safe call
                        self.root.after(0, self.process_message, msg)

            except Exception as e:
                print(f"Receive error: {e}")
                self.root.after(0, self.add_announcement, "Connection to server lost.")
                break

    # --- Announcement Helper ---
    def add_announcement(self, text):
        row = tk.Frame(self.scrollable_frame, bg="white")
        row.pack(fill="x", pady=6)
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)
        row.grid_columnconfigure(2, weight=1)

        ann = tk.Label(
            row,
            text=text,
            font=("Arial", 10, "italic"),
            fg="gray",
            bg="white",
            wraplength=300
        )
        ann.grid(row=0, column=1, padx=10, sticky="n")

        self.root.after(50, lambda: self.canvas.yview_moveto(1.0))

    def back_to_groups(self):
        try:
            self.client.sendall(f"LEAVE_GROUP|{self.username}".encode())
        except Exception as e:
            print(f"Failed to send LEAVE_GROUP message: {e}")

        # Then destroy window
        self.root.destroy()

    # --- Run Mainloop ---
    def run(self):
        self.root.mainloop()


