import tkinter as tk
from tkinter import ttk
import threading
import time

class NotificationWindow:
    def __init__(self, username, ip_address, parent, notifications=None, notification_system=None):
        self.root = tk.Toplevel(parent)
        self.root.title("Notification")
        self.root.geometry("800x700")
        self.root.configure(bg="white")
        self.username = username
        self.ip_address = ip_address
        self.notification_system = notification_system
        self.update_thread = None
        self.running = True

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.notifications = notifications if notifications else {}

        main_container = tk.Frame(self.root, bg="white")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Enhanced sidebar with gradient-like effect (same as grouplist.py)
        sidebar_container = tk.Frame(main_container, bg="#2c3e50", bd=0, relief="flat", width=220)
        sidebar_container.pack(side="left", fill="y")
        sidebar_container.pack_propagate(False)

        # Add a subtle border line
        border_line = tk.Frame(main_container, bg="#34495e", width=2)
        border_line.pack(side="left", fill="y")

        left_sidebar = tk.Frame(sidebar_container, bg="#2c3e50")
        left_sidebar.pack(fill="both", expand=True, padx=20, pady=25)

        # Profile section with modern styling
        profile_header = tk.Label(
            left_sidebar,
            text="👤 Profile",
            font=("Segoe UI", 14, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        profile_header.pack(pady=(0, 20), anchor="w")

        # Username section with modern card design
        tk.Label(
            left_sidebar,
            text="Username",
            font=("Segoe UI", 10, "bold"),
            bg="#2c3e50",
            fg="#bdc3c7"
        ).pack(pady=(0, 5), anchor="w")

        username_frame = tk.Frame(left_sidebar, bg="#34495e", relief="flat", bd=0)
        username_frame.pack(pady=(0, 20), fill="x")
        
        username_inner = tk.Frame(username_frame, bg="#34495e")
        username_inner.pack(fill="x", padx=15, pady=12)
        
        tk.Label(
            username_inner,
            text=f"✉ {self.username}",
            font=("Segoe UI", 12, "bold"),
            bg="#34495e",
            fg="#ecf0f1"
        ).pack(anchor="w")

        # IP Address section with modern card design
        tk.Label(
            left_sidebar,
            text="Server Address",
            font=("Segoe UI", 10, "bold"),
            bg="#2c3e50",
            fg="#bdc3c7"
        ).pack(pady=(0, 5), anchor="w")

        ip_frame = tk.Frame(left_sidebar, bg="#34495e", relief="flat", bd=0)
        ip_frame.pack(pady=(0, 25), fill="x")
        
        ip_inner = tk.Frame(ip_frame, bg="#34495e")
        ip_inner.pack(fill="x", padx=15, pady=12)
        
        tk.Label(
            ip_inner,
            text=f"🌐 {self.ip_address}",
            font=("Segoe UI", 12, "bold"),
            bg="#34495e",
            fg="#ecf0f1"
        ).pack(anchor="w")

        # Status indicator
        status_frame = tk.Frame(left_sidebar, bg="#2c3e50")
        status_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(
            status_frame,
            text="🟢 Online",
            font=("Segoe UI", 10),
            bg="#2c3e50",
            fg="#27ae60"
        ).pack(anchor="w")

        # Action buttons section with modern styling
        button_frame = tk.Frame(left_sidebar, bg="#2c3e50")
        button_frame.pack(side="bottom", fill="x", pady=(20, 0))

        # Notification stats section (new design element)
        stats_frame = tk.Frame(left_sidebar, bg="#2c3e50")
        stats_frame.pack(fill="x", pady=(15, 10))
        
        tk.Label(
            stats_frame,
            text="📊 Notification Stats",
            font=("Segoe UI", 10, "bold"),
            bg="#2c3e50",
            fg="#bdc3c7"
        ).pack(anchor="w", pady=(0, 5))
        
        # Stats display with modern cards
        stats_card = tk.Frame(stats_frame, bg="#34495e", relief="flat", bd=0)
        stats_card.pack(fill="x", pady=(0, 10))
        
        stats_inner = tk.Frame(stats_card, bg="#34495e")
        stats_inner.pack(fill="x", padx=15, pady=8)
        
        # Dynamic notification count
        self.notification_count_label = tk.Label(
            stats_inner,
            text="📬 Total: 0 notifications",
            font=("Segoe UI", 9),
            bg="#34495e",
            fg="#ecf0f1"
        )
        self.notification_count_label.pack(anchor="w")
        
        # Separator line with modern styling
        separator = tk.Frame(left_sidebar, bg="#34495e", height=1)
        separator.pack(fill="x", pady=(10, 15))

        # Clear all notifications button with modern styling
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear All Notifications",
            font=("Segoe UI", 9, "bold"),
            bg="#e74c3c", fg="white", relief="flat", bd=0,
            padx=12, pady=10, cursor="hand2",
            command=self.clear_all_notifications
        )
        clear_btn.pack(fill="x", pady=(0, 8))
        
        # Hover effects for clear button
        clear_btn.bind("<Enter>", lambda e: clear_btn.configure(bg="#c0392b"))
        clear_btn.bind("<Leave>", lambda e: clear_btn.configure(bg="#e74c3c"))

        # Refresh button (new design element)
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Refresh Notifications",
            font=("Segoe UI", 9, "bold"),
            bg="#f39c12", fg="white", relief="flat", bd=0,
            padx=12, pady=10, cursor="hand2",
            command=self.refresh_notifications
        )
        refresh_btn.pack(fill="x", pady=(0, 8))
        
        # Hover effects for refresh button
        refresh_btn.bind("<Enter>", lambda e: refresh_btn.configure(bg="#e67e22"))
        refresh_btn.bind("<Leave>", lambda e: refresh_btn.configure(bg="#f39c12"))

        # Back button with modern styling
        back_btn = tk.Button(
            button_frame,
            text="← Back to Groups",
            font=("Segoe UI", 9, "bold"),
            bg="#95a5a6", fg="white", relief="flat", bd=0,
            padx=12, pady=10, cursor="hand2",
            command=self.on_closing
        )
        back_btn.pack(fill="x")
        
        # Hover effects for back button
        back_btn.bind("<Enter>", lambda e: back_btn.configure(bg="#7f8c8d"))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(bg="#95a5a6"))

        right_container = tk.Frame(main_container, bg="#ecf0f1")
        right_container.pack(side="left", fill="both", expand=True)

        # Modern header with gradient-like styling (same as grouplist.py)
        header_frame = tk.Frame(right_container, bg="#3498db", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Header content container
        header_content = tk.Frame(header_frame, bg="#3498db")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        header = tk.Label(
            header_content, text="🔔 Notifications",
            font=("Segoe UI", 24, "bold"),
            bg="#3498db", fg="white"
        )
        header.pack(side="left", anchor="w")

        # Auto-refresh indicator
        self.refresh_label = tk.Label(
            header_content,
            text="🔄 Live",
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg="#3498db"
        )
        self.refresh_label.pack(side="right", padx=15)

        # Main content area with modern styling
        content_wrapper = tk.Frame(right_container, bg="#ecf0f1")
        content_wrapper.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        # Notifications section header (new design element)
        notifications_header = tk.Frame(content_wrapper, bg="#ecf0f1")
        notifications_header.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            notifications_header, text="Recent Notifications",
            font=("Segoe UI", 16, "bold"),
            bg="#ecf0f1", fg="#2c3e50"
        ).pack(anchor="w")
        
        tk.Label(
            notifications_header, text="Stay updated with your group messages",
            font=("Segoe UI", 11),
            bg="#ecf0f1", fg="#7f8c8d"
        ).pack(anchor="w")

        # Create scrollable frame for notifications with enhanced styling
        canvas_frame = tk.Frame(content_wrapper, bg="#bdc3c7", bd=1, relief="solid")
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(
            canvas_frame, orient="vertical", command=self.canvas.yview,
            bg="#95a5a6", troughcolor="#ecf0f1", width=12
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

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
        self.update_notification_count()

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
        self.update_notification_count()

    def refresh_notifications(self):
        """Manually refresh notifications"""
        if self.notification_system:
            new_notifications = self.notification_system.get_unread_messages()
            self.notifications = new_notifications
            self.update_notifications_display()
            self.update_notification_count()

    def update_notification_count(self):
        """Update the notification count display"""
        try:
            total_count = sum(len(messages) for messages in self.notifications.values())
            group_count = len(self.notifications)
            
            count_text = f"📬 Total: {total_count} messages"
            if group_count > 0:
                count_text += f" from {group_count} groups"
            
            self.notification_count_label.config(text=count_text)
        except Exception as e:
            print(f"[ERROR] Updating notification count: {e}")

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
                                self.root.after(0, self.update_notification_count)
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
                # Enhanced empty state design
                empty_container = tk.Frame(self.scrollable_frame, bg="white")
                empty_container.pack(expand=True, fill="both")
                
                # Center content vertically and horizontally
                center_frame = tk.Frame(empty_container, bg="white")
                center_frame.place(relx=0.5, rely=0.5, anchor="center")
                
                tk.Label(
                    center_frame, text="🔔",
                    font=("Segoe UI", 48), bg="white", fg="#bdc3c7"
                ).pack(pady=(0, 10))
                
                tk.Label(
                    center_frame, text="No New Notifications",
                    font=("Segoe UI", 16, "bold"), bg="white", fg="#2c3e50"
                ).pack()
                
                tk.Label(
                    center_frame, text="You're all caught up! 🎉",
                    font=("Segoe UI", 12), bg="white", fg="#7f8c8d"
                ).pack(pady=(5, 0))
                return

            # Display notifications by group
            for group, messages in self.notifications.items():
                if not messages:  # Skip empty message lists
                    continue
                    
                # Enhanced group header with modern card design
                group_frame = tk.Frame(self.scrollable_frame, bg="white", relief="flat", bd=0)
                group_frame.pack(fill="x", pady=(15, 5), padx=15)
                
                # Group header card with shadow effect
                header_card = tk.Frame(group_frame, bg="#f8f9fa", relief="solid", bd=1,
                                     highlightbackground="#dee2e6", highlightthickness=1)
                header_card.pack(fill="x")
                
                group_label = tk.Label(
                    header_card,
                    text=f"� {group}",
                    font=("Segoe UI", 14, "bold"),
                    fg="white",
                    bg="#3498db",
                    relief="flat",
                    bd=0,
                    padx=15,
                    pady=10
                )
                group_label.pack(fill="x")
                
                # Message count badge
                count_badge = tk.Label(
                    header_card,
                    text=f"💬 {len(messages)} new messages",
                    font=("Segoe UI", 10, "bold"),
                    fg="#2c3e50",
                    bg="#f8f9fa",
                    padx=15,
                    pady=5
                )
                count_badge.pack(fill="x")
                
                # Enhanced messages display
                for i, msg in enumerate(messages[-5:]):  # Show last 5 messages
                    msg_frame = tk.Frame(self.scrollable_frame, bg="white")
                    msg_frame.pack(fill="x", padx=25, pady=3)
                    
                    # Message card with hover effect
                    msg_card = tk.Frame(msg_frame, bg="#f8f9fa", relief="solid", bd=1,
                                      highlightbackground="#dee2e6", highlightthickness=1)
                    msg_card.pack(fill="x")
                    
                    msg_box = tk.Label(
                        msg_card,
                        text=f"💬 {msg}",
                        font=("Segoe UI", 10),
                        fg="#2c3e50",
                        bg="#f8f9fa",
                        relief="flat",
                        bd=0,
                        wraplength=450,
                        justify="left",
                        anchor="w",
                        padx=12,
                        pady=8
                    )
                    msg_box.pack(fill="x")
                    
                    # Add hover effects for message cards
                    msg_card.bind("<Enter>", lambda e, card=msg_card: card.configure(bg="#e9ecef"))
                    msg_card.bind("<Leave>", lambda e, card=msg_card: card.configure(bg="#f8f9fa"))
                    msg_box.bind("<Enter>", lambda e, box=msg_box, card=msg_card: (
                        box.configure(bg="#e9ecef"),
                        card.configure(bg="#e9ecef")
                    ))
                    msg_box.bind("<Leave>", lambda e, box=msg_box, card=msg_card: (
                        box.configure(bg="#f8f9fa"),
                        card.configure(bg="#f8f9fa")
                    ))

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