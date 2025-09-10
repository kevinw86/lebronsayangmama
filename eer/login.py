import tkinter as tk


class LoginWindow:
    def __init__(self):
        self.username = None
        self.ip_address = None

        self.root = tk.Tk()
        self.root.title("SevenChat - Login")
        self.root.geometry("400x400")
        self.root.configure(bg="#2c3e50")

        bubble = tk.Label(
            self.root, text="💬 SevenChat",
            font=("Arial", 20, "bold"),
            bg="#5d6d7e", fg="#ecf0f1",
            padx=20, pady=10, relief="raised", bd=3
        )
        bubble.pack(pady=(30, 40))

        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(
            self.root, textvariable=self.username_var,
            font=("Arial", 14),
            bg="#34495e", fg="#aab7b8", insertbackground="white",
            relief="raised", bd=3, justify="center"
        )
        self.username_entry.pack(ipady=8, ipadx=10, pady=(20, 5))
        self.username_entry.insert(0, "✉ Username")
        self.username_entry.bind("<FocusIn>", self.on_username_focus_in)
        self.username_entry.bind("<FocusOut>", self.on_username_focus_out)

        self.ip_var = tk.StringVar()
        self.ip_entry = tk.Entry(
            self.root, textvariable=self.ip_var,
            font=("Arial", 14),
            bg="#34495e", fg="white", insertbackground="white",
            relief="raised", bd=3, justify="center",
        )
        self.ip_entry.pack(ipady=8, ipadx=10, pady=(15, 5))
        self.ip_entry.insert(0, "127.0.0.1")
        # Remove the focus bindings for IP field since it's now fixed
        # self.ip_entry.bind("<FocusIn>", self.on_ip_focus_in)
        # self.ip_entry.bind("<FocusOut>", self.on_ip_focus_out)

        self.confirm_btn = tk.Button(
            self.root, text="Login",
            font=("Arial", 14, "bold"),
            bg="#5d6d7e", fg="#ecf0f1",
            activebackground="#7f8c8d",
            activeforeground="black",
            relief="raised", bd=3, padx=20, pady=10,
            command=self.submit, cursor="hand2"
        )
        self.confirm_btn.pack(pady=30)

        # Add hover effects to button
        self.confirm_btn.bind("<Enter>", self.on_button_hover)
        self.confirm_btn.bind("<Leave>", self.on_button_leave)

        # Add hover effects to entry fields
        self.username_entry.bind("<Enter>", self.on_entry_hover)
        self.username_entry.bind("<Leave>", self.on_entry_leave)
        self.ip_entry.bind("<Enter>", self.on_entry_hover)
        self.ip_entry.bind("<Leave>", self.on_entry_leave)

        self.status_label = tk.Label(
            self.root, text="", font=("Arial", 10),
            bg="#2c3e50", fg="red"
        )
        self.status_label.pack()

        self.root.bind("<Return>", self.submit)

    def on_username_focus_in(self, event):
        """Clear placeholder when username field is focused"""
        if self.username_entry.get() == "✉ Username":
            self.username_entry.delete(0, tk.END)
            self.username_entry.configure(fg="white")

    def on_username_focus_out(self, event):
        """Restore placeholder if username field is empty"""
        if self.username_entry.get() == "":
            self.username_entry.insert(0, "✉ Username")
            self.username_entry.configure(fg="#aab7b8")

    def on_ip_focus_in(self, event):
        """Clear placeholder when IP field is focused"""
        if self.ip_entry.get() == "🔒 IP Address":
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.configure(fg="white")

    def on_ip_focus_out(self, event):
        """Restore placeholder if IP field is empty"""
        if self.ip_entry.get() == "":
            self.ip_entry.insert(0, "🔒 IP Address")
            self.ip_entry.configure(fg="#aab7b8")

    def on_button_hover(self, event):
        """Button hover effect"""
        self.confirm_btn.configure(bg="#7f8c8d", fg="#2c3e50")

    def on_button_leave(self, event):
        """Button leave effect"""
        self.confirm_btn.configure(bg="#5d6d7e", fg="#ecf0f1")

    def on_entry_hover(self, event):
        """Entry hover effect"""
        event.widget.configure(bg="#4a6741")

    def on_entry_leave(self, event):
        """Entry leave effect"""
        event.widget.configure(bg="#34495e")

    def submit(self, event=None):
        username = self.username_var.get().strip()
        ip_address = self.ip_var.get().strip()

        # Check if username placeholder is still there or field is empty
        if username == "✉ Username" or username == "":
            username = ""
        
        # IP address is now fixed to 127.0.0.1, so we don't need to check for placeholder
        if username and ip_address:
            self.username = username
            self.ip_address = ip_address
            self.root.destroy()
        else:
            if not username:
                self.status_label.config(text="⚠ Please enter username!")
            else:
                self.status_label.config(text="⚠ Server IP address is required!")

    def run(self):
        self.root.mainloop()
        return self.username, self.ip_address


if __name__ == "__main__":
    login = LoginWindow()
    user, ip = login.run()
    print("Username:", user)
    print("IP Address:", ip)