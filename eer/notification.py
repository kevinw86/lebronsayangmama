import tkinter as tk
from tkinter import ttk

class NotificationWindow:
    def __init__(self, parent, notifications=None):
        self.root = tk.Toplevel(parent)
        self.root.title("Notification")
        self.root.geometry("400x500")
        self.root.configure(bg="#fdf6e3")  # light grid-like background

        self.notifications = notifications if notifications else []

        # --- Title ---
        tk.Label(
            self.root,
            text="Notification",
            font=("Segoe Script", 28, "bold"),
            fg="darkred",
            bg="#fdf6e3"
        ).pack(pady=10)

        # --- Section Frame ---
        section_frame = tk.Frame(self.root, bg="#fdf6e3", highlightbackground="black", highlightthickness=1)
        section_frame.pack(fill="x", padx=20, pady=5)

        # Section title
        tk.Label(
            section_frame,
            text="Notification",
            font=("Courier", 14, "bold"),
            fg="black",
            bg="#fdf6e3"
        ).pack(fill="x", pady=5)

        ttk.Separator(section_frame, orient="horizontal").pack(fill="x", padx=10, pady=5)

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

        # --- Back Button ---
        tk.Button(
            self.root,
            text="Back",
            font=("Arial", 12, "bold"),
            relief="groove",
            command=self.root.destroy
        ).pack(side="left", padx=20, pady=20)


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # hide root window
    sample_notifications = ["Notification 1...", "Notification 2...", "Notification 3..."]
    NotificationWindow(root, sample_notifications)
    root.mainloop()
