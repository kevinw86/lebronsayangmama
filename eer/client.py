import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

# --- Networking ---
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5555))

# --- Login Window ---
login = tk.Tk()
login.title("Login")
login.geometry("400x300")

username_var = tk.StringVar()

def submit_username():
    global username
    username = username_var.get().strip()
    if username:
        login.destroy()  # close login window
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

login.mainloop()  # wait until login closes


# --- Chat Window ---
root = tk.Tk()
root.title(f"Instant Messenger - {username}")

chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state="disabled", width=50, height=20)
chat_area.pack(padx=10, pady=10)

entry = tk.Entry(root, width=40)
entry.pack(side=tk.LEFT, padx=10, pady=10)

def send_message():
    msg = entry.get()
    if msg.strip():
        full_msg = f"{username}: {msg}"
        client.sendall(full_msg.encode())
        entry.delete(0, tk.END)

send_btn = tk.Button(root, text="Send", command=send_message)
send_btn.pack(side=tk.LEFT, padx=5)

def receive_messages():
    while True:
        try:
            msg = client.recv(1024).decode()
            if not msg:
                break
            chat_area.config(state="normal")
            chat_area.insert(tk.END, f"{msg}\n")
            chat_area.config(state="disabled")
            chat_area.see(tk.END)
        except:
            break

threading.Thread(target=receive_messages, daemon=True).start()

root.mainloop()
client.close()
