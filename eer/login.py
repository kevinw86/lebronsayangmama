import tkinter as tk


class LoginWindow:
    def __init__(self):
        self.username = None
        self.ip_address = None

        self.root = tk.Tk()
        self.root.title("SevenChat - Login")
        self.root.geometry("400x400")
        self.root.configure(bg="#1e1e2e")  # dark background

        # --- Logo / Title (speech bubble style) ---
        bubble = tk.Label(
            self.root, text="💬 SevenChat",
            font=("Arial", 20, "bold"),
            bg="#89b4fa", fg="#1e1e2e",
            padx=20, pady=10
        )
        bubble.pack(pady=(30, 40))

        # --- Username Label ---
        username_label = tk.Label(
            self.root, text="Username",
            font=("Arial", 12, "bold"),
            bg="#1e1e2e", fg="#a6e3a1"
        )
        username_label.pack(pady=(5, 2))

        # --- Username Entry ---
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(
            self.root, textvariable=self.username_var,
            font=("Arial", 14),
            bg="#313244", fg="white", insertbackground="white",
            relief="flat", justify="center"
        )
        self.username_entry.pack(ipady=8, ipadx=10, pady=5)
        self.username_entry.focus()

        # --- IP Address Label ---
        ip_label = tk.Label(
            self.root, text="IP Address",
            font=("Arial", 12, "bold"),
            bg="#1e1e2e", fg="#a6e3a1"
        )
        ip_label.pack(pady=(10, 2))

        # --- IP Address Entry ---
        self.ip_var = tk.StringVar()
        self.ip_entry = tk.Entry(
            self.root, textvariable=self.ip_var,
            font=("Arial", 14),
            bg="#313244", fg="white", insertbackground="white",
            relief="flat", justify="center"
        )
        self.ip_entry.pack(ipady=8, ipadx=10, pady=5)

        # --- Confirm Button ---
        self.confirm_btn = tk.Button(
            self.root, text="Login",
            font=("Arial", 14, "bold"),
            bg="#89b4fa", fg="#1e1e2e",
            activebackground="#74c7ec",
            activeforeground="black",
            relief="flat", padx=20, pady=10,
            command=self.submit
        )
        self.confirm_btn.pack(pady=30)

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
        ip_address = self.ip_var.get().strip()

        if username and ip_address:
            self.username = username
            self.ip_address = ip_address
            self.root.destroy()
        else:
            self.status_label.config(text="⚠ Please enter username and IP address!")

    def run(self):
        self.root.mainloop()
        return self.username, self.ip_address


# Example usage
if __name__ == "__main__":
    login = LoginWindow()
    user, ip = login.run()
    print("Username:", user)
    print("IP Address:", ip)
