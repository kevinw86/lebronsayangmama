import tkinter as tk

class LoginWindow:
    def __init__(self):
        self.username = None
        self.root = tk.Tk()
        self.root.title("Login")
        self.root.geometry("400x300")
        self.root.configure(bg="#1e1e2e")  # dark background

        # --- Title ---
        title_label = tk.Label(
            self.root, text="Welcome to SevenChat 💬",
            font=("Arial", 24, "bold"),
            bg="#1e1e2e", fg="#f8f8f2"
        )
        title_label.pack(pady=30)

        # --- Username Label ---
        username_label = tk.Label(
            self.root, text="Enter Username",
            font=("Arial", 12, "bold"),
            bg="#1e1e2e", fg="#a6e3a1"
        )
        username_label.pack(pady=(10, 5))

        # --- Username Entry ---
        self.username_var = tk.StringVar()
        self.entry = tk.Entry(
            self.root, textvariable=self.username_var,
            font=("Arial", 14),
            bg="#313244", fg="white", insertbackground="white",
            relief="flat", justify="center"
        )
        self.entry.pack(ipady=8, ipadx=10, pady=5)
        self.entry.focus()

        # --- Confirm Button ---
        self.confirm_btn = tk.Button(
            self.root, text="Join Chat",
            font=("Arial", 14, "bold"),
            bg="#89b4fa", fg="#1e1e2e",
            activebackground="#74c7ec",
            activeforeground="black",
            relief="flat", padx=20, pady=10,
            command=self.submit
        )
        self.confirm_btn.pack(pady=25)

        # --- Status Label ---
        self.status_label = tk.Label(
            self.root, text="", font=("Arial", 10),
            bg="#1e1e2e", fg="red"
        )
        self.status_label.pack()

        # Enter key triggers submit
        self.root.bind("<Return>", self.submit)

    def submit(self, event=None):
        username = self.username_var.get().strip()
        if username:
            self.username = username
            self.root.destroy()
        else:
            self.status_label.config(text="⚠ Please enter a username!")

    def run(self):
        self.root.mainloop()
        return self.username
