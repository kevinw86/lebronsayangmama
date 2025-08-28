import socket
import threading
import tkinter as tk
from tkinter import ttk
import datetime

# --- Networking ---
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5556))

# --- Login Window ---
login = tk.Tk()
login.title("Login")
login.geometry("400x300")

username_var = tk.StringVar()

def submit_username():
    global username
    username = username_var.get().strip()
    if username:
        login.destroy()
    else:
        status_label.config(text="Please enter a username!", fg="red")

title_label = tk.Label(login, text="Login", font=("Arial", 32, "bold"))
title_label.pack(pady=20)

username_label = tk.Label(login, text="Username", font=("Arial", 12, "bold"))
username_label.pack(pady=(10, 5))

username_entry = tk.Entry(login, textvariable=username_var, font=("Arial", 14), width=25, bd=2, relief="solid")
username_entry.pack(pady=5)

confirm_btn = tk.Button(login, text="Confirm", font=("Arial", 14, "bold"),
                        bg="green", fg="black", width=15, height=2,
                        command=submit_username)
confirm_btn.pack(pady=30)

status_label = tk.Label(login, text="", font=("Arial", 10))
status_label.pack()

login.mainloop()

# --- Chat Window ---
root = tk.Tk()
root.title(f"Group Chat - {username}")
root.geometry("500x600")

# --- Header ---
header = tk.Label(root, text="GROUP NAME", font=("Arial", 18, "bold"), bg="lightgray", pady=10)
header.pack(fill=tk.X)

# --- Scrollable chat frame ---
chat_frame = tk.Frame(root)
chat_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(chat_frame, bg="white")
scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="white")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# --- Chat bubbles ---
def add_message(name, msg, is_me=False):
    timestamp = datetime.datetime.now().strftime("%H:%M")

    # One full-width row per message
    row = tk.Frame(scrollable_frame, bg="white")
    row.pack(fill="x", pady=(6, 2), padx=6)

    # Two equal columns: one becomes "spacer" to push the block to a side
    row.grid_columnconfigure(0, weight=1)
    row.grid_columnconfigure(1, weight=1)

    # Side setup
    col        = 1 if is_me else 0   # right for us, left for others
    sticky     = "e" if is_me else "w"
    name_fg    = "blue" if is_me else "green"
    bubble_bg  = "lightblue" if is_me else "lightgreen"

    # Container for name + bubble + timestamp
    block = tk.Frame(row, bg="white")
    block.grid(row=0, column=col, sticky=sticky, padx=6)

    # Username label
    tk.Label(
        block, text=name, font=("Arial", 8, "bold"),
        bg="white", fg=name_fg
    ).pack(anchor=sticky)

    # ✅ Dynamic wraplength based on chat width
    wrap = max(200, int(canvas.winfo_width() * 0.6))

    # Chat bubble
    bubble = tk.Label(
        block, text=msg, bg=bubble_bg, font=("Arial", 12),
        wraplength=wrap,
        justify="left", padx=10, pady=6, bd=1, relief="solid"
    )
    bubble.pack(anchor=sticky, pady=(2, 0))

    # Timestamp
    tk.Label(
        block, text=timestamp, font=("Arial", 7),
        fg="gray", bg="white"
    ).pack(anchor=sticky, pady=(2, 0))

    # Auto-scroll to bottom
    root.after(50, lambda: canvas.yview_moveto(1.0))

# --- Entry + Send ---
bottom_frame = tk.Frame(root, bg="white")
bottom_frame.pack(fill=tk.X, pady=5)

entry = tk.Entry(bottom_frame, font=("Arial", 12))
entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)

def send_message(event=None):
    msg = entry.get().strip()
    if msg:
        client.sendall(f"{username}: {msg}".encode())
        add_message(username, msg, is_me=True)
        entry.delete(0, tk.END)
        entry.focus()

send_btn = tk.Button(bottom_frame, text="Send", font=("Arial", 12, "bold"), bg="green", fg="white", command=send_message)
send_btn.pack(side=tk.RIGHT, padx=10)

entry.bind("<Return>", send_message)

# --- Receive messages ---
def receive_messages():
    while True:
        try:
            msg = client.recv(1024).decode()
            if not msg:
                break
            if msg.startswith(username + ":"):  # skip own (already shown)
                continue
            sender, text = msg.split(":", 1)
            add_message(sender.strip(), text.strip(), is_me=False)
        except:
            break

threading.Thread(target=receive_messages, daemon=True).start()

root.mainloop()
client.close()
