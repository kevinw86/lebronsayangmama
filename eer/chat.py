import tkinter as tk
from tkinter import ttk
import datetime
import threading


class ChatWindow:
    def __init__(self, username, client, group_name):
        self.username = username
        self.client = client

        # --- Send username to server immediately ---
        try:
            self.client.sendall(self.username.encode())
        except Exception as e:
            print("Failed to send username:", e)

        # --- Main Window ---
        self.root = tk.Tk()
        self.root.title(f"Group Chat - {group_name} ({username})")
        self.root.geometry("500x600")

        # --- Header with group name ---
        header = tk.Label(
            self.root,
            text=group_name,
            font=("Arial", 18, "bold"),
            bg="lightgray",
            pady=10
        )
        header.pack(fill=tk.X)

        # --- Back Button ---
        back_btn = tk.Button(
            self.root,
            text="Back to Groups",
            bg="orange",
            fg="black",
            font=("Arial", 10, "bold"),
            command=self.back_to_groups
        )
        back_btn.pack(pady=5, padx=10, anchor="nw")

        # --- Scrollable Chat Frame ---
        chat_frame = tk.Frame(self.root)
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
        bottom_frame = tk.Frame(self.root, bg="white")
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
        threading.Thread(target=self.receive_messages, daemon=True).start()

    # --- Chat Bubble Helper ---
    def add_message(self, name, msg, is_me=False):
        timestamp = datetime.datetime.now().strftime("%H:%M")

        row = tk.Frame(self.scrollable_frame, bg="white")
        row.pack(fill="x", pady=(6, 2), padx=6)
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)

        col = 1 if is_me else 0
        sticky = "e" if is_me else "w"
        name_fg = "blue" if is_me else "green"
        bubble_bg = "lightblue" if is_me else "lightgreen"
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
                self.client.sendall(f"{self.username}: {msg}".encode())
                self.add_message(self.username, msg, is_me=True)
            except Exception as e:
                print("Send failed:", e)
        self.entry.delete(0, tk.END)
        self.entry.focus()

    # --- Receive Messages ---
    def receive_messages(self):
        while True:
            try:
                msg = self.client.recv(1024).decode()
                if not msg:
                    break

                if msg.startswith("[SERVER]:"):
                    # Announcement (join/leave/system msg)
                    announcement = msg.replace("[SERVER]:", "").strip()
                    self.add_announcement(announcement)
                    continue

                if msg.startswith(self.username + ":"):
                    # skip own (already shown)
                    continue

                sender, text = msg.split(":", 1)
                self.add_message(sender.strip(), text.strip(), is_me=False)
            except:
                break

    # --- Announcement Helper ---
    def add_announcement(self, text):
        row = tk.Frame(self.scrollable_frame, bg="white")
        row.pack(fill="x", pady=6)

        ann = tk.Label(
            row,
            text=text,
            font=("Arial", 10, "italic"),
            fg="gray",
            bg="white"
        )
        ann.pack(anchor="center")

        self.root.after(50, lambda: self.canvas.yview_moveto(1.0))

    # --- Back to Groups ---
    def back_to_groups(self):
        self.root.destroy()

    # --- Run Mainloop ---
    def run(self):
        self.root.mainloop()
