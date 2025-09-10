import tkinter as tk
from tkinter import ttk
import threading
import time

class NotificationWindow:
    def __init__(self, username, ip_address, parent, notifications=None, notification_system=None):
        self.root = tk.Toplevel(parent)
        self.root.title("Notification")
        self.root.geometry("400x500")
        self.root.configure(bg="#fdf6e3")
        self.username = username
        self.ip_address = ip_address
        self.notification_system = notification_system
        self.update_thread = None
        self.running = True

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.notifications = notifications if notifications else {}

        main_container = tk.Frame(self.root, bg="#fdf6e3")
        main_container.pack(fill=tk.BOTH, expand=True)

        sidebar_container = tk.Frame(main_container, bg="#e0e0e0", bd=2, relief="ridge", width=135)
        sidebar_container.pack(side="left", fill="y")
        sidebar_container.pack_propagate(False)

        left_sidebar = tk.Frame(sidebar_container, bg="white")
        left_sidebar.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(
            left_sidebar,
            text="Username",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#454545"
        ).pack(pady=(10,0), padx=5, anchor="w")

        username_frame = tk.Frame(left_sidebar, bg="#f5f5f5", relief="groove", bd=3, padx=6, pady=6)
        username_frame.pack(pady=(5,15), padx=5, fill="x")
        tk.Label(
            username_frame,
            text=f"{self.username}",
            font=("Arial", 12, "bold"),
            bg="#f5f5f5"
        ).pack(pady=8)

        tk.Label(
            left_sidebar,
            text="IP Address",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#454545"
        ).pack(pady=(0,0), padx=5, anchor="w")

        ip_frame = tk.Frame(left_sidebar, bg="#f5f5f5", relief="groove", bd=3, padx=6, pady=6)
        ip_frame.pack(pady=(5,15), padx=5, fill="x")
        tk.Label(
            ip_frame,
            text=f"{self.ip_address}",
            font=("Arial", 12, "bold"),
            bg="#f5f5f5"
        ).pack(pady=8)

        # Clear all notifications button - only clear when user explicitly clicks
        clear_btn = tk.Button(
            left_sidebar,
            text="Clear All",
            bg="red",
            fg="white",
            font=("Arial", 8, "bold"),
            command=self.clear_all_notifications
        )
        clear_btn.pack(side="bottom", fill="x", padx=5, pady=(5, 0))

        back_btn = tk.Button(
            left_sidebar,
            text="Back",
            bg="orange",
            fg="black",
            font=("Arial", 8, "bold"),
            relief="groove",
            command=self.on_closing
        )
        back_btn.pack(side="bottom", fill="x", padx=5, pady=10)

        right_container = tk.Frame(main_container, bg="#fdf6e3")
        right_container.pack(side="left", fill="both", expand=True)

        header_frame = tk.Frame(right_container, bg="#fdf6e3")
        header_frame.pack(fill="x", pady=10)
        
        tk.Label(
            header_frame,
            text="Notifications",
            font=("Segoe Script", 28, "bold"),
            fg="darkred",
            bg="#fdf6e3"
        ).pack(side="left", expand=True)

        # Auto-refresh indicator
        self.refresh_label = tk.Label(
            header_frame,
            text="🔄 Live",
            font=("Arial", 10, "bold"),
            fg="green",
            bg="#fdf6e3"
        )
        self.refresh_label.pack(side="right", padx=10)

        # Create scrollable frame for notifications
        canvas_frame = tk.Frame(right_container, bg="#fdf6e3")
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg="#fdf6e3", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#fdf6e3")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel to canvas
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Initial display
        self.update_notifications_display()

        # Start real-time updates if notification system is available
        if self.notification_system:
            self.start_real_time_updates()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_closing(self):
        """Handle window close event - auto-clear notifications when window is closed"""
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
        
        # Clear all notifications when notification window is closed
        if self.notification_system:
            self.notification_system.clear_notifications()
            
        self.root.destroy()

    def clear_all_notifications(self):
        """Clear all notifications - only when user explicitly requests"""
        if self.notification_system:
            self.notification_system.clear_notifications()
        self.notifications = {}
        self.update_notifications_display()

    def start_real_time_updates(self):
        """Start background thread for real-time notification updates"""
        def update_loop():
            while self.running:
                try:
                    if self.notification_system:
                        new_notifications = self.notification_system.get_unread_messages()
                        if new_notifications != self.notifications:
                            self.notifications = new_notifications
                            # Schedule UI update on main thread
                            try:
                                self.root.after(0, self.update_notifications_display)
                            except:
                                break  # Window might be destroyed
                    
                    # Update refresh indicator
                    try:
                        self.root.after(0, self.update_refresh_indicator)
                    except:
                        break  # Window might be destroyed
                    
                    time.sleep(1)  # Check for updates every second
                except Exception as e:
                    print(f"[ERROR] Notification update loop: {e}")
                    time.sleep(2)
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()

    def update_refresh_indicator(self):
        """Update the refresh indicator to show activity"""
        if not self.running:
            return
        try:
            current_text = self.refresh_label.cget("text")
            if current_text == "🔄 Live":
                self.refresh_label.config(text="📡 Live")
            else:
                self.refresh_label.config(text="🔄 Live")
        except Exception:
            pass

    def update_notifications_display(self):
        """Update the notifications display"""
        if not self.running:
            return
        try:
            # Clear existing widgets
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            if not self.notifications:
                tk.Label(
                    self.scrollable_frame,
                    text="(No New Notifications)",
                    font=("Courier", 14, "italic"),
                    fg="gray",
                    bg="#fdf6e3"
                ).pack(pady=20)
                return

            # Display notifications by group
            for group, messages in self.notifications.items():
                if not messages:  # Skip empty message lists
                    continue
                    
                # Group header
                group_frame = tk.Frame(self.scrollable_frame, bg="#fdf6e3", relief="solid", bd=1)
                group_frame.pack(fill="x", pady=(10, 5), padx=10)
                
                group_label = tk.Label(
                    group_frame,
                    text=f"📢 Group: {group} ({len(messages)} new)",
                    font=("Courier", 14, "bold"),
                    fg="darkblue",
                    bg="#e6f3ff",
                    relief="raised",
                    bd=1
                )
                group_label.pack(fill="x", pady=5, padx=5)
                
                # Messages for this group
                for i, msg in enumerate(messages[-5:]):  # Show last 5 messages
                    msg_frame = tk.Frame(self.scrollable_frame, bg="#fdf6e3")
                    msg_frame.pack(fill="x", padx=20, pady=2)
                    
                    msg_box = tk.Label(
                        msg_frame,
                        text=f"💬 {msg}",
                        font=("Courier", 10),
                        fg="darkred",
                        bg="#fff5f5",
                        relief="solid",
                        bd=1,
                        wraplength=300,
                        justify="left",
                        anchor="w",
                        padx=8,
                        pady=4
                    )
                    msg_box.pack(fill="x")

            # Auto-scroll to bottom to show newest notifications
            self.root.after(100, lambda: self.canvas.yview_moveto(1.0))
            
        except Exception as e:
            print(f"[ERROR] Updating notification display: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    sample_notifications = {
        "Group1": ["User1: Hello there!", "User2: How are you?"],
        "Group2": ["User3: Meeting at 5pm", "User4: Got it!"]
    }
    NotificationWindow("TestUser", "127.0.0.1", root, sample_notifications)
    root.mainloop()