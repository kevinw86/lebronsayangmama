import tkinter as tk
from tkinter import ttk

class NotificationWindow:
    def __init__(self, username, ip_address, parent, notifications=None):
        self.root = tk.Toplevel(parent)
        self.root.title("Notification")
        self.root.geometry("400x500")
        self.root.configure(bg="#fdf6e3")
        self.username = username
        self.ip_address = ip_address

        self.notifications = notifications if notifications else []

        # --- Main layout: left sidebar and right main area ---
        main_container = tk.Frame(self.root, bg="#fdf6e3")
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

        # --- Back Button (bottom of sidebar) ---
        back_btn = tk.Button(
            left_sidebar,
            text="Back",
            bg="orange",
            fg="black",
            font=("Arial", 8, "bold"),
            relief="groove",
            command=self.root.destroy
        )
        back_btn.pack(side="bottom", fill="x", padx=5, pady=10)

        # --- Right main area ---
        right_container = tk.Frame(main_container, bg="#fdf6e3")
        right_container.pack(side="left", fill="both", expand=True)

        # --- Title ---
        tk.Label(
            right_container,
            text="Notification",
            font=("Segoe Script", 28, "bold"),
            fg="darkred",
            bg="#fdf6e3"
        ).pack(pady=10)

        # --- Section Frame ---
        section_frame = tk.Frame(right_container, bg="#fdf6e3", highlightbackground="black", highlightthickness=1)
        section_frame.pack(fill="x", padx=20, pady=5)

        # --- Notifications List ---
        if not self.notifications:
            tk.Label(
                section_frame,
                text="(No Notifications)",
                font=("Courier", 12, "italic"),
                fg="darkred",
                bg="#fdf6e3"
            ).pack(pady=10)
        else:
            for notif in self.notifications:
                box = tk.Label(
                    section_frame,
                    text=f"({notif})",
                    font=("Courier", 12),
                    fg="darkred",
                    bg="#fdf6e3",
                    relief="solid",
                    bd=1,
                    width=35,
                    height=2
                )
                box.pack(pady=8, padx=10)


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # hide root window
    sample_notifications = ["Notification 1...", "Notification 2...", "Notification 3..."]
    NotificationWindow(root,  sample_notifications)
    root.mainloop()
