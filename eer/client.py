import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

# Networking setup
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("10.194.82.63", 5555))

# GUI setup
root = tk.Tk()
root.title("Instant Messenger")

chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state="disabled", width=50, height=20)
chat_area.pack(padx=10, pady=10)

entry = tk.Entry(root, width=40)
entry.pack(side=tk.LEFT, padx=10, pady=10)

def send_message():
    msg = entry.get()
    if msg.strip():
        client.sendall(msg.encode())
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

# Start receiving in a separate thread
threading.Thread(target=receive_messages, daemon=True).start()

root.mainloop()
client.close()
